from __future__ import annotations

from typing import Any

import pytest
from pyparsing import ParseException, ParseResults

from rdflib import Graph, Literal, Namespace, URIRef, Variable
from rdflib.plugins import sparql
from rdflib.plugins.sparql.operators import (
    register_custom_function,
    unregister_custom_function,
)
from rdflib.plugins.sparql.parser import parseQuery


def _assert_builtin_functions(report, expected) -> None:
    # Compound keywords have no specified word-boundary convention.
    aliases = {
        "lang_matches": "langmatches",
        "data_type": "datatype",
        "b_node": "bnode",
        "str_len": "strlen",
        "u_case": "ucase",
        "l_case": "lcase",
        "str_starts": "strstarts",
        "str_ends": "strends",
        "str_before": "strbefore",
        "str_after": "strafter",
        "time_zone": "timezone",
        "str_dt": "strdt",
        "str_lang": "strlang",
        "str_uuid": "struuid",
    }
    actual = report.functions
    assert isinstance(actual, frozenset)
    normalized = frozenset(aliases.get(name, name) for name in actual)
    assert normalized == frozenset(expected)
    assert len(actual) == len(normalized)
    assert report.as_dict()["functions"] == sorted(actual)
    for name in actual:
        assert report.uses(name.upper())
        assert report.categories_for(name.replace("_", "-")) == frozenset({"functions"})


def test_reports_query_form_patterns_and_solution_modifiers() -> None:
    report = sparql.extract_query_features(
        """
        PREFIX ex: <urn:ex:>
        SELECT DISTINCT ?s (COUNT(?o) AS ?count)
        FROM <urn:default> FROM NAMED <urn:named>
        WHERE {
          GRAPH <urn:graph> {
            ?s ex:p/ex:q ?o
            OPTIONAL { ?s ex:label ?label }
            FILTER(?o >= 2 && STRLEN(STR(?label)) > 0)
            BIND(LCASE(STR(?label)) AS ?lower)
          }
          { ?s ex:left ?x } UNION { ?s ex:right ?x }
          MINUS { ?s ex:blocked true }
          VALUES ?x { 1 2 }
          { SELECT DISTINCT ?s WHERE { ?s ex:nested ?nested } LIMIT 0 }
        }
        GROUP BY ?s
        HAVING(COUNT(?o) > 1)
        ORDER BY DESC(?count)
        LIMIT 10 OFFSET 3
        """
    )

    assert report.query_form == "select"
    assert {
        "graph",
        "optional",
        "filter",
        "bind",
        "union",
        "minus",
        "values",
        "property_path",
        "subquery",
    } == report.patterns
    assert {"distinct", "group", "having", "order", "limit", "offset"} == (
        report.modifiers
    )
    _assert_builtin_functions(report, {"str", "strlen", "lcase"})
    assert report.aggregates == frozenset({"count"})
    assert (
        frozenset({">=", ">", "&&"})
        <= report.operators
        <= frozenset({">=", ">", "&&", "/"})
    )
    assert report.default_graphs == (URIRef("urn:default"),)
    assert report.named_graphs == (URIRef("urn:named"),)
    assert report.variables == frozenset(
        Variable(name) for name in ("s", "o", "count", "label", "lower", "x", "nested")
    )
    categories = ("patterns", "modifiers", "functions", "aggregates", "operators")
    pairs = [
        (category, feature)
        for category in categories
        for feature in sorted(getattr(report, category))
    ]
    assert list(report.iter_features()) == pairs
    assert report.feature_count == len(pairs) == len(set(pairs))
    for category in categories:
        assert isinstance(getattr(report, category), frozenset)
        assert report.as_dict()[category] == sorted(getattr(report, category))


def test_nested_subquery_and_service_features_are_not_hidden() -> None:
    report = sparql.extract_query_features(
        """
        PREFIX ex: <urn:ex:>
        SELECT * WHERE {
          SERVICE SILENT ?endpoint {
            GRAPH ?graph { ?s ex:remote ?remote FILTER(ABS(?remote) < 4) }
          }
          VALUES ?listed { <urn:item> }
          { SELECT ?s WHERE {
            ?s ex:value ?v
            FILTER EXISTS { ?s ex:extra ?inside FILTER(CONTAINS(?inside, 'x')) }
          } }
          FILTER NOT EXISTS {
            ?s ex:blocked ?reason BIND(UCASE(?reason) AS ?upper)
          }
        }
        """
    )
    assert report.patterns == frozenset(
        {
            "service",
            "graph",
            "values",
            "subquery",
            "filter",
            "exists",
            "not_exists",
            "bind",
        }
    )
    assert report.uses("SERVICE")
    assert report.uses("not-exists")
    _assert_builtin_functions(report, {"abs", "contains", "ucase"})
    assert report.operators == frozenset({"<"})
    assert report.variables == frozenset(
        Variable(name)
        for name in (
            "s",
            "remote",
            "v",
            "inside",
            "reason",
            "upper",
            "endpoint",
            "graph",
            "listed",
        )
    )


@pytest.mark.parametrize(
    ("query", "form", "extra_variables"),
    [
        ("ASK", "ask", ()),
        (
            "CONSTRUCT { ?s ?template_p ?template_o }",
            "construct",
            ("template_p", "template_o"),
        ),
        ("DESCRIBE ?target", "describe", ("target",)),
    ],
    ids=("ask", "construct", "describe"),
)
def test_all_query_forms_are_identified(
    query: str, form: str, extra_variables: tuple[str, ...]
) -> None:
    report = sparql.extract_query_features(
        query + " FROM <urn:z> FROM <urn:a> FROM <urn:z> "
        "FROM NAMED <urn:n> FROM NAMED <urn:n> WHERE { ?s ?p ?o }"
    )
    assert report.query_form == form
    assert report.default_graphs == (URIRef("urn:z"), URIRef("urn:a"), URIRef("urn:z"))
    assert report.named_graphs == (URIRef("urn:n"), URIRef("urn:n"))
    assert report.variables == frozenset(
        Variable(name) for name in ("s", "p", "o", *extra_variables)
    )


def test_custom_function_iri_and_builtin_are_distinguished() -> None:
    report = sparql.extract_query_features(
        "SELECT * WHERE { ?s ?p ?o "
        "FILTER(<urn:function>(?o) || <filter>(?o) || RAND() > 0.5) }"
    )
    assert "urn:function" in report.functions
    assert "rand" in report.functions
    assert {"||", ">"} <= report.operators
    assert report.categories_for("filter") == frozenset({"patterns", "functions"})
    assert report.categories_for("FILTER") == frozenset({"patterns"})
    assert report.feature_count == len(list(report.iter_features())) == 6

    for iri, alternatives in (
        ("some-fn", ("SOME-FN", "some_fn")),
        ("SomeFn", ("somefn", "SOMEFN")),
        ("some_fn", ("some-fn", "SOME_FN")),
        ("filter", ("FILTER", "Filter")),
        ("str", ("STR", "Str")),
    ):
        query = f"SELECT (<{iri}>(RAND()) AS ?x) WHERE {{}}"
        for source in (query, parseQuery(query)):
            report = sparql.extract_query_features(source)
            assert report.functions == frozenset({iri, "rand"})
            assert report.uses_all((iri, "RAND"))
            assert report.categories_for(iri) == frozenset({"functions"})
            assert not report.uses_any(alternatives)
            for alternative in alternatives:
                assert report.categories_for(alternative) == frozenset()

    for query in (
        "SELECT (<str>(STR(?x)) AS ?y) WHERE {}",
        "SELECT (STR(?x) AS ?b) (<str>(?x) AS ?c) WHERE {}",
    ):
        for source in (query, parseQuery(query)):
            report = sparql.extract_query_features(source)
            assert report.functions == frozenset({"str"})
            assert report.uses_all(("str", "STR"))
            assert report.categories_for("STR") == frozenset({"functions"})


def test_prefixed_functions_resolve_without_mutating_initial_namespaces() -> None:
    initial = {"ex": Namespace("urn:initial:")}
    snapshot = dict(initial)
    supplied = sparql.extract_query_features(
        "SELECT * FROM ex:g FROM NAMED ex:n WHERE { ?s ?p ?o FILTER(ex:normalize(?o)) }",
        init_ns=initial,
    )
    declared = sparql.extract_query_features(
        "PREFIX ex: <urn:declared:> "
        "SELECT * FROM ex:g FROM NAMED ex:n WHERE { ?s ?p ?o FILTER(ex:normalize(?o)) }",
        init_ns=initial,
    )
    assert supplied.functions == frozenset({"urn:initial:normalize"})
    assert declared.functions == frozenset({"urn:declared:normalize"})
    assert supplied.default_graphs == (URIRef("urn:initial:g"),)
    assert supplied.named_graphs == (URIRef("urn:initial:n"),)
    assert declared.default_graphs == (URIRef("urn:declared:g"),)
    assert declared.named_graphs == (URIRef("urn:declared:n"),)
    assert initial == snapshot


def test_parse_query_output_is_accepted_without_reparsing() -> None:
    parsed = parseQuery("SELECT ?s WHERE { ?s ?p ?o }")
    report = sparql.extract_query_features(parsed)
    assert report.query_form == "select"
    assert report.variables == frozenset({Variable("s"), Variable("p"), Variable("o")})


def test_report_is_immutable_and_dictionary_output_is_deterministic() -> None:
    from rdflib.plugins.sparql import QueryFeatures

    report = sparql.extract_query_features(
        "SELECT ?z ?a WHERE { ?z ?p ?a FILTER(STR(?a) = STR(?z)) }"
    )
    assert report.as_dict()["variables"] == ["a", "p", "z"]
    assert isinstance(report, QueryFeatures)
    original = report.as_dict()
    for name in original:
        with pytest.raises((AttributeError, TypeError)):
            setattr(report, name, None)
        with pytest.raises((AttributeError, TypeError)):
            delattr(report, name)
    assert report.as_dict() == original


def test_feature_lookup_helpers_normalize_names_and_preserve_categories() -> None:
    report = sparql.extract_query_features(
        "SELECT (COUNT(?o) AS ?n) WHERE { ?s ?p ?o FILTER(STR(?o) != '') }"
    )
    assert report.uses_all(["FILTER", "count", "STR"])
    assert report.uses_any(["service", "!="])
    assert not report.uses_all(["filter", "missing"])
    assert not report.uses_any(["missing-a", "missing-b"])
    assert report.categories_for("count") == frozenset({"aggregates"})
    assert report.categories_for("missing") == frozenset()
    assert list(report.iter_features()) == [
        ("patterns", "filter"),
        ("functions", "str"),
        ("aggregates", "count"),
        ("operators", "!="),
    ]
    assert report.feature_count == 4
    assert report.is_aggregate_query


def test_invalid_query_and_invalid_input_keep_parser_errors_distinct() -> None:
    for query in ("SELECT WHERE {", "ASK { ?s ?p ?o } trailing"):
        with pytest.raises(ParseException):
            sparql.extract_query_features(query)
    with pytest.raises(TypeError):
        sparql.extract_query_features(42)  # type: ignore[arg-type]
    unsupported_values: tuple[Any, ...] = (
        None,
        [],
        {},
        ParseResults(),
        ParseResults([[]]),
    )
    for unsupported in unsupported_values:
        with pytest.raises(TypeError):
            sparql.extract_query_features(unsupported)


def test_plain_groups_predicates_and_legal_variable_names_are_not_misclassified() -> (
    None
):
    report = sparql.extract_query_features(
        "SELECT ?__agg_user WHERE { { ?__agg_user <urn:p> ?o ; "
        "<urn:q> [ <urn:r> ?o ] } } LIMIT 0"
    )
    assert report.patterns == frozenset()
    assert report.modifiers == frozenset({"limit"})
    assert report.variables == frozenset({Variable("__agg_user"), Variable("o")})
    assert not report.is_aggregate_query


def test_nested_modifiers_and_offset_only_are_reported_exactly() -> None:
    report = sparql.extract_query_features(
        "SELECT REDUCED ?s WHERE { "
        "{ SELECT DISTINCT ?s WHERE { ?s ?p ?o } LIMIT 0 } } OFFSET 0 "
        "VALUES ?s { <urn:s> }"
    )
    assert report.modifiers == frozenset({"reduced", "distinct", "limit", "offset"})
    assert report.patterns == frozenset({"subquery", "values"})
    offset = sparql.extract_query_features("SELECT * WHERE { ?s ?p ?o } OFFSET 0")
    assert offset.modifiers == frozenset({"offset"})
    grouped = sparql.extract_query_features("SELECT ?s WHERE { ?s ?p ?o } GROUP BY ?s")
    assert grouped.is_aggregate_query
    assert grouped.aggregates == frozenset()
    for inner, aggregates in (
        ("SELECT ?s WHERE { ?s ?p ?o } GROUP BY ?s", frozenset()),
        ("SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }", frozenset({"count"})),
    ):
        nested = sparql.extract_query_features("SELECT * WHERE { { " + inner + " } }")
        assert nested.is_aggregate_query
        assert nested.aggregates == aggregates


def test_all_aggregate_families_are_reported_without_duplicates() -> None:
    report = sparql.extract_query_features(
        "SELECT (COUNT(*) AS ?n) (SUM(?o) AS ?total) (MIN(?o) AS ?lo) "
        "(MAX(?o) AS ?hi) (AVG(?o) AS ?mean) (SAMPLE(?o) AS ?sample) "
        "(GROUP_CONCAT(STR(?o)) AS ?joined) WHERE { ?s ?p ?o } "
        "HAVING(COUNT(*) > 0)"
    )
    assert report.aggregates == frozenset(
        {"count", "sum", "min", "max", "avg", "sample", "group_concat"}
    )
    assert report.is_aggregate_query
    assert report.uses("GROUP-CONCAT")
    assert report.as_dict()["aggregates"] == sorted(report.aggregates)


@pytest.mark.parametrize(
    "predicate",
    ["<urn:p>|<urn:q>", "^<urn:p>", "!<urn:p>", "<urn:p>?", "<urn:p>*", "<urn:p>+"],
)
def test_property_path_operators_are_detected(predicate: str) -> None:
    for body in (
        f"?s {predicate} ?o",
        f"?s <urn:plain> ?x ; {predicate} ?o",
        f"?s <urn:plain> [ {predicate} ?o ]",
    ):
        query = f"SELECT * WHERE {{ {body} }}"
        for source in (query, parseQuery(query)):
            report = sparql.extract_query_features(source)
            assert report.patterns == frozenset({"property_path"})


def test_base_prefixes_and_dataset_order_work_for_text_and_parsed_inputs() -> None:
    query = (
        "BASE <https://example.test/> PREFIX ex: <ns/> "
        "SELECT * FROM ex:g FROM <other> FROM ex:g "
        "FROM NAMED ex:n FROM NAMED <named-other> FROM NAMED ex:n "
        "WHERE { ?s ?p ?o FILTER(<Some-Fn>(?o)) }"
    )
    parsed = parseQuery(query)
    before = repr(parsed)
    for source in (query, parsed):
        report = sparql.extract_query_features(source)
        assert report.default_graphs == (
            URIRef("https://example.test/ns/g"),
            URIRef("https://example.test/other"),
            URIRef("https://example.test/ns/g"),
        )
        assert report.named_graphs == (
            URIRef("https://example.test/ns/n"),
            URIRef("https://example.test/named-other"),
            URIRef("https://example.test/ns/n"),
        )
        data = report.as_dict()
        assert data["default_graphs"] == [
            "https://example.test/ns/g",
            "https://example.test/other",
            "https://example.test/ns/g",
        ]
        assert data["named_graphs"] == [
            "https://example.test/ns/n",
            "https://example.test/named-other",
            "https://example.test/ns/n",
        ]
        assert all(
            type(iri) is str for iri in data["default_graphs"] + data["named_graphs"]
        )
        data["default_graphs"].clear()
        assert len(report.default_graphs) == 3
        assert report.functions == frozenset({"https://example.test/Some-Fn"})
        assert report.uses("https://example.test/Some-Fn")
        assert not report.uses("https://example.test/some-fn")
        assert report.categories_for("https://example.test/Some-Fn") == frozenset(
            {"functions"}
        )
    assert repr(parsed) == before

    query = (
        "BASE <https://example.test/root/> PREFIX ex: <#> "
        "SELECT * FROM ex:g FROM NAMED ex:n "
        "WHERE { ?s ?p ?o FILTER(ex:normalize(?o)) }"
    )
    for source in (query, parseQuery(query)):
        report = sparql.extract_query_features(source)
        assert report.default_graphs == (URIRef("https://example.test/root/#g"),)
        assert report.named_graphs == (URIRef("https://example.test/root/#n"),)
        assert report.functions == frozenset({"https://example.test/root/#normalize"})

    for query, suffixes in (
        (
            "BASE <https://example.test/root/> "
            "SELECT * FROM <path/graph:one> FROM NAMED <path/named:one> "
            "WHERE { ?s ?p ?o FILTER(<path/fn:one>(?o)) }",
            ("path/graph:one", "path/named:one", "path/fn:one"),
        ),
        (
            "BASE <https://example.test/root/> PREFIX ex: <path/ns:> "
            "SELECT * FROM ex:g FROM NAMED ex:n "
            "WHERE { ?s ?p ?o FILTER(ex:fn(?o)) }",
            ("path/ns:g", "path/ns:n", "path/ns:fn"),
        ),
    ):
        expected = ["https://example.test/root/" + suffix for suffix in suffixes]
        for source in (query, parseQuery(query)):
            report = sparql.extract_query_features(source)
            assert report.default_graphs == (URIRef(expected[0]),)
            assert report.named_graphs == (URIRef(expected[1]),)
            assert report.functions == frozenset({expected[2]})


def test_reusing_a_parsed_query_does_not_retain_initial_namespaces() -> None:
    parsed = parseQuery("SELECT * WHERE { ?s ?p ?o FILTER(ex:fn(?o)) }")
    before = repr(parsed)
    first = sparql.extract_query_features(
        parsed, init_ns={"ex": Namespace("urn:first:")}
    )
    second = sparql.extract_query_features(
        parsed, init_ns={"ex": Namespace("urn:second:")}
    )
    assert first.functions == frozenset({"urn:first:fn"})
    assert second.functions == frozenset({"urn:second:fn"})
    assert repr(parsed) == before


def test_operator_lookup_preserves_symbols_and_unary_signs() -> None:
    report = sparql.extract_query_features(
        "SELECT * WHERE { ?s ?p ?x FILTER("
        "?x NOT IN (1, 2) && (?x - 1) / 2 >= +?x && -?y != 0 || !BOUND(?z)) "
        "FILTER(?x IN (2, 3) && ?x + 1 <= ?y * 2 && ?x = ?y && ?x < 9 && ?y > 0) }"
    )
    expected = {
        "not_in",
        "in",
        "&&",
        "-",
        "+",
        "*",
        "/",
        ">=",
        "<=",
        "=",
        "<",
        ">",
        "unary+",
        "unary-",
        "!=",
        "||",
        "!",
    }
    assert report.operators == frozenset(expected)
    assert report.uses_all(expected)
    assert report.uses("NOT-IN")
    assert report.uses_all([])
    assert not report.uses_any([])


def test_report_schema_and_category_order_include_modifiers() -> None:
    report = sparql.extract_query_features(
        "SELECT DISTINCT ?z ?a WHERE { ?z ?p ?a FILTER(isIRI(?a) && sameTerm(?a, ?z)) } LIMIT 0"
    )
    expected = {
        "query_form": "select",
        "patterns": ["filter"],
        "modifiers": ["distinct", "limit"],
        "functions": ["is_iri", "same_term"],
        "aggregates": [],
        "operators": ["&&"],
        "variables": ["a", "p", "z"],
        "default_graphs": [],
        "named_graphs": [],
    }
    assert report.as_dict() == expected

    for spelling in ("IS_IRI", "is_iri", "Is_IrI", "is-iri", "IS-IRI"):
        assert report.uses(spelling)
        assert report.categories_for(spelling) == frozenset({"functions"})
    assert report.uses_all(["SaMe_TeRm", "DiStInCt", "LiMiT"])
    categories = ("patterns", "modifiers", "functions", "aggregates", "operators")
    for category in (*categories, "variables"):
        assert isinstance(getattr(report, category), frozenset)
    assert list(report.iter_features()) == [
        (category, name) for category in categories for name in expected[category]
    ]
    assert report.feature_count == 6
    copied = report.as_dict()
    functions = copied["functions"]
    assert isinstance(functions, list)
    functions.append("missing")
    assert not report.uses("missing")
    assert report.as_dict() == expected


def test_expression_features_in_projection_group_having_and_order() -> None:
    report = sparql.extract_query_features(
        "SELECT (CONCAT(?projected, 'x') AS ?alias) WHERE { ?s ?p ?o } "
        "GROUP BY ?projected (UCASE(?grouped) AS ?bucket) "
        "HAVING(STRLEN(MAX(?having)) > 0) ORDER BY LCASE(?ordered)"
    )
    _assert_builtin_functions(report, {"concat", "ucase", "strlen", "lcase"})
    assert report.aggregates == frozenset({"max"})
    assert report.modifiers == frozenset({"group", "having", "order"})
    assert report.operators == frozenset({">"})
    assert report.variables == frozenset(
        Variable(name)
        for name in (
            "projected",
            "alias",
            "s",
            "p",
            "o",
            "grouped",
            "bucket",
            "having",
            "ordered",
        )
    )


@pytest.mark.parametrize(
    "expressions",
    [
        {
            "ABS(-2)": "abs",
            "CEIL(1.2)": "ceil",
            "FLOOR(1.2)": "floor",
            "ROUND(1.2)": "round",
            "RAND()": "rand",
        },
        {
            "STR(1)": "str",
            "LANG('a'@en)": "lang",
            "LANGMATCHES('en', '*')": "langmatches",
            "DATATYPE(1)": "datatype",
            "STRLEN('abc')": "strlen",
            "UCASE('a')": "ucase",
            "LCASE('A')": "lcase",
            "CONCAT('a', 'b')": "concat",
            "SUBSTR('abc', 1)": "substr",
            "REPLACE('abc', 'a', 'b')": "replace",
            "ENCODE_FOR_URI('a b')": "encode_for_uri",
            "CONTAINS('abc', 'b')": "contains",
            "STRSTARTS('abc', 'a')": "strstarts",
            "STRENDS('abc', 'c')": "strends",
            "STRBEFORE('abc', 'b')": "strbefore",
            "STRAFTER('abc', 'b')": "strafter",
            "REGEX('abc', 'b')": "regex",
        },
        {
            "NOW()": "now",
            "YEAR(?date)": "year",
            "MONTH(?date)": "month",
            "DAY(?date)": "day",
            "HOURS(?date)": "hours",
            "MINUTES(?date)": "minutes",
            "SECONDS(?date)": "seconds",
            "TIMEZONE(?date)": "timezone",
            "TZ(?date)": "tz",
        },
        {
            "IRI('urn:a')": "iri",
            "URI('urn:a')": "uri",
            "BNODE()": "bnode",
            "STRDT('a', <urn:type>)": "strdt",
            "STRLANG('a', 'en')": "strlang",
            "isIRI(<urn:a>)": "is_iri",
            "isURI(<urn:a>)": "is_uri",
            "isBLANK(?node)": "is_blank",
            "isLITERAL('a')": "is_literal",
            "isNUMERIC(1)": "is_numeric",
            "sameTerm(1, 1)": "same_term",
        },
        {
            "MD5('a')": "md5",
            "SHA1('a')": "sha1",
            "SHA256('a')": "sha256",
            "SHA384('a')": "sha384",
            "SHA512('a')": "sha512",
            "UUID()": "uuid",
            "STRUUID()": "struuid",
        },
        {
            "IF(true, 1, 2)": "if",
            "COALESCE(?missing, 1)": "coalesce",
            "BOUND(?value)": "bound",
        },
    ],
    ids=[
        "numeric",
        "strings",
        "dates",
        "terms",
        "hashes-and-identifiers",
        "conditional",
    ],
)
def test_builtin_families_are_reported(expressions: dict[str, str]) -> None:
    projection = " ".join(
        f"({expression} AS ?result{index})"
        for index, expression in enumerate(expressions)
    )
    report = sparql.extract_query_features(f"SELECT {projection} WHERE {{}}")
    _assert_builtin_functions(report, expressions.values())
    assert report.aggregates == frozenset()


def test_inspection_does_not_invoke_evaluation_hooks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    function_calls = []
    evaluation_calls = []
    iri = URIRef("urn:inspection:observe")

    def observe(*args):
        function_calls.append(args)
        return Literal("observed")

    def observe_evaluation(context, part):
        evaluation_calls.append(part.name)
        raise NotImplementedError

    for name in tuple(sparql.CUSTOM_EVALS):
        monkeypatch.delitem(sparql.CUSTOM_EVALS, name)
    monkeypatch.setitem(sparql.CUSTOM_EVALS, "inspection-observer", observe_evaluation)
    register_custom_function(iri, observe)
    query = "SELECT (<urn:inspection:observe>(1) AS ?answer) WHERE {}"
    try:
        assert list(Graph().query(query)) == [(Literal("observed"),)]
        assert function_calls and evaluation_calls
        function_calls.clear()
        evaluation_calls.clear()
        for source in (query, parseQuery(query)):
            report = sparql.extract_query_features(source)
            assert report.functions == frozenset({str(iri)})
            assert report.variables == frozenset({Variable("answer")})
            assert not function_calls
            assert not evaluation_calls
    finally:
        unregister_custom_function(iri)
