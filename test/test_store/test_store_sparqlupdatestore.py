import re
from urllib.request import urlopen

import pytest

from rdflib import BNode, ConjunctiveGraph, Graph, Literal, URIRef
from test.data import BOB, CHEESE, HATES, LIKES, MICHEL, PIZZA, TAREK

HOST = "http://localhost:3031"
DB = "/db/"

# this assumes SPARQL1.1 query/update endpoints running locally at
# http://localhost:3031/db/
#
# The ConjunctiveGraph tests below require that the SPARQL endpoint renders its
# default graph as the union of all known graphs! This is incompatible with the
# endpoint behavior required by our Dataset tests in test_dataset.py, so you
# need to run a second SPARQL endpoint on a non standard port,
# e.g. fuseki started with:
# ./fuseki-server --port 3031 --memTDB --update --set tdb:unionDefaultGraph=true /db

# THIS WILL DELETE ALL DATA IN THE /db dataset

graphuri = URIRef("urn:example:graph")
othergraphuri = URIRef("urn:example:othergraph")

try:
    assert len(urlopen(HOST).read()) > 0
except Exception:
    pytest.skip(f"{HOST} is unavailable.", allow_module_level=True)


@pytest.fixture
def get_graph():
    longMessage = True  # noqa: F841
    graph = ConjunctiveGraph("SPARQLUpdateStore")

    root = HOST + DB
    graph.open((root + "sparql", root + "update"))

    # clean out the store
    for c in graph.contexts():
        c.remove((None, None, None))
        assert len(c) == 0

    yield graph

    graph.close()


def test_simple_graph(get_graph):
    graph = get_graph
    g = graph.get_context(graphuri)
    g.add((TAREK, LIKES, PIZZA))
    g.add((BOB, LIKES, PIZZA))
    g.add((BOB, LIKES, CHEESE))

    g2 = graph.get_context(othergraphuri)
    g2.add((MICHEL, LIKES, PIZZA))

    assert len(g) == 3, "graph contains 3 triples"
    assert len(g2) == 1, "other graph contains 1 triple"

    r = g.query("SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }")
    assert len(list(r)) == 2, "two people like PIZZA"

    r = g.triples((None, LIKES, PIZZA))
    assert len(list(r)) == 2, "two people like PIZZA"

    # Test initBindings
    r = g.query(
        "SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }",
        initBindings={"s": TAREK},
    )
    assert len(list(r)) == 1, "i was asking only about TAREK"

    r = g.triples((TAREK, LIKES, PIZZA))
    assert len(list(r)) == 1, "i was asking only about TAREK"

    r = g.triples((TAREK, LIKES, CHEESE))
    assert len(list(r)) == 0, "TAREK doesn't like CHEESE"

    g2.add((TAREK, LIKES, PIZZA))
    g.remove((TAREK, LIKES, PIZZA))
    r = g.query("SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }")
    assert len(list(r)) == 1, "only BOB LIKES PIZZA"


def test_conjunctive_default(get_graph):
    graph = get_graph
    g = graph.get_context(graphuri)
    g.add((TAREK, LIKES, PIZZA))
    g2 = graph.get_context(othergraphuri)
    g2.add((BOB, LIKES, PIZZA))
    g.add((TAREK, HATES, CHEESE))

    assert 2 == len(g), "graph contains 2 triples"

    # the following are actually bad tests as they depend on your endpoint,
    # as pointed out in the sparqlstore.py code:
    #
    # For ConjunctiveGraphs, reading is done from the "default graph" Exactly
    # what this means depends on your endpoint, because SPARQL does not offer a
    # simple way to query the union of all graphs as it would be expected for a
    # ConjuntiveGraph.
    ##
    # Fuseki/TDB has a flag for specifying that the default graph
    # is the union of all graphs (tdb:unionDefaultGraph in the Fuseki config).
    assert (
        len(graph) == 3
    ), "default union graph should contain three triples but contains:\n%s" % list(
        graph
    )

    r = graph.query("SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }")
    assert len(list(r)) == 2, "two people like PIZZA"

    r = graph.query(
        "SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }",
        initBindings={"s": TAREK},
    )
    assert len(list(r)) == 1, "i was asking only about TAREK"

    r = graph.triples((TAREK, LIKES, PIZZA))
    assert len(list(r)) == 1, "i was asking only about TAREK"

    r = graph.triples((TAREK, LIKES, CHEESE))
    assert len(list(r)) == 0, "TAREK doesn't like CHEESE"

    g2.remove((BOB, LIKES, PIZZA))

    r = graph.query("SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }")
    assert len(list(r)) == 1, "only TAREK LIKES PIZZA"


def test_u_update(get_graph):
    graph = get_graph
    graph.update(
        "INSERT DATA { GRAPH <urn:example:graph> { <urn:example:michel> <urn:example:likes> <urn:example:pizza> . } }"
    )

    g = graph.get_context(graphuri)
    assert 1 == len(g), "graph contains 1 triples"


def test_u_update_with_initns(get_graph):
    graph = get_graph
    graph.update(
        "INSERT DATA { GRAPH ns:graph { ns:michel ns:likes ns:pizza . } }",
        initNs={"ns": URIRef("urn:example:")},
    )

    g = graph.get_context(graphuri)
    assert set(g.triples((None, None, None))) == set(
        [(MICHEL, LIKES, PIZZA)]
    ), "only MICHEL LIKES PIZZA"


def test_update_with_init_bindings(get_graph):
    graph = get_graph
    graph.update(
        "INSERT { GRAPH <urn:example:graph> { ?a ?b ?c . } } WherE { }",
        initBindings={
            "a": URIRef("urn:example:michel"),
            "b": URIRef("urn:example:likes"),
            "c": URIRef("urn:example:pizza"),
        },
    )

    g = graph.get_context(graphuri)
    assert set(g.triples((None, None, None))) == set(
        [(MICHEL, LIKES, PIZZA)]
    ), "only MICHEL LIKES PIZZA"


def test_update_with_blank_node(get_graph):
    graph = get_graph
    graph.update(
        "INSERT DATA { GRAPH <urn:example:graph> { _:blankA <urn:example:type> <urn:example:Blank> } }"
    )
    g = graph.get_context(graphuri)
    for t in g.triples((None, None, None)):
        assert isinstance(t[0], BNode)
        assert t[1].n3() == "<urn:example:type>"
        assert t[2].n3() == "<urn:example:Blank>"


def test_update_w_with_blank_node_serialize_and_parse(get_graph):
    graph = get_graph
    graph.update(
        "INSERT DATA { GRAPH <urn:example:graph> { _:blankA <urn:example:type> <urn:example:Blank> } }"
    )
    g = graph.get_context(graphuri)
    string = g.serialize(format="ntriples")
    raised = False
    try:
        Graph().parse(data=string, format="ntriples")
    except Exception as e:  # noqa: F841
        raised = True
    assert raised is False, "Exception raised when parsing: " + string


def test_multiple_update_with_init_bindings(get_graph):
    graph = get_graph
    graph.update(
        "INSERT { GRAPH <urn:example:graph> { ?a ?b ?c . } } WHERE { };"
        "INSERT { GRAPH <urn:example:graph> { ?d ?b ?c . } } WHERE { }",
        initBindings={
            "a": URIRef("urn:example:michel"),
            "b": URIRef("urn:example:likes"),
            "c": URIRef("urn:example:pizza"),
            "d": URIRef("urn:example:bob"),
        },
    )

    g = graph.get_context(graphuri)
    assert set(g.triples((None, None, None))) == set(
        [(MICHEL, LIKES, PIZZA), (BOB, LIKES, PIZZA)]
    ), "MICHEL and BOB like PIZZA"


def test_named_graph_update(get_graph):
    graph = get_graph
    g = graph.get_context(graphuri)
    r1 = "INSERT DATA { <urn:example:michel> <urn:example:likes> <urn:example:pizza> }"
    g.update(r1)
    assert set(g.triples((None, None, None))) == set(
        [(MICHEL, LIKES, PIZZA)]
    ), "only MICHEL LIKES PIZZA"

    r2 = (
        "DELETE { <urn:example:michel> <urn:example:likes> <urn:example:pizza> } "
        + "INSERT { <urn:example:bob> <urn:example:likes> <urn:example:pizza> } WHERE {}"
    )
    g.update(r2)
    assert set(g.triples((None, None, None))) == set(
        [(BOB, LIKES, PIZZA)]
    ), "only BOB LIKES PIZZA"

    says = URIRef("urn:says")

    # Strings with unbalanced curly braces
    tricky_strs = ["With an unbalanced curly brace %s " % brace for brace in ["{", "}"]]
    for tricky_str in tricky_strs:
        r3 = (
            """INSERT { ?b <urn:says> "%s" }
        WHERE { ?b <urn:example:likes> <urn:example:pizza>} """
            % tricky_str
        )
        g.update(r3)

    values = set()
    for v in g.objects(BOB, says):
        values.add(str(v))
    assert values == set(tricky_strs)

    # Complicated Strings
    r4strings = []
    r4strings.append(r'''"1: adfk { ' \\\" \" { "''')
    r4strings.append(r'''"2: adfk } <foo> #éï \\"''')

    r4strings.append(r"""'3: adfk { " \\\' \' { '""")
    r4strings.append(r"""'4: adfk } <foo> #éï \\'""")

    r4strings.append(r'''"""5: adfk { ' \\\" \" { """''')
    r4strings.append(r'''"""6: adfk } <foo> #éï \\"""''')
    r4strings.append('"""7: ad adsfj \n { \n sadfj"""')

    r4strings.append(r"""'''8: adfk { " \\\' \' { '''""")
    r4strings.append(r"""'''9: adfk } <foo> #éï \\'''""")
    r4strings.append("'''10: ad adsfj \n { \n sadfj'''")

    r4 = "\n".join(
        ["INSERT DATA { <urn:example:michel> <urn:says> %s } ;" % s for s in r4strings]
    )
    g.update(r4)
    values = set()
    for v in g.objects(MICHEL, says):
        values.add(str(v))
    assert values == set(
        [
            re.sub(
                r"\\(.)",
                r"\1",
                re.sub(r"^'''|'''$|^'|'$|" + r'^"""|"""$|^"|"$', r"", s),
            )
            for s in r4strings
        ]
    )

    # IRI Containing ' or #
    # The fragment identifier must not be misinterpreted as a comment
    # (commenting out the end of the block).
    # The ' must not be interpreted as the start of a string, causing the }
    # in the literal to be identified as the end of the block.
    r5 = """INSERT DATA { <urn:example:michel> <urn:example:hates> <urn:example:foo'bar?baz;a=1&b=2#fragment>, "'}" }"""

    g.update(r5)
    values = set()
    for v in g.objects(MICHEL, HATES):
        values.add(str(v))
    assert values == set(["urn:example:foo'bar?baz;a=1&b=2#fragment", "'}"])

    # Comments
    r6 = """
        INSERT DATA {
            <urn:example:bob> <urn:example:hates> <urn:example:bob> . # No closing brace: }
            <urn:example:bob> <urn:example:hates> <urn:example:michel>.
        }
    #Final { } comment"""

    g.update(r6)
    values = set()
    for v in g.objects(BOB, HATES):
        values.add(v)
    assert values == set([BOB, MICHEL])


def test_named_graph_update_with_init_bindings(get_graph):
    graph = get_graph
    g = graph.get_context(graphuri)
    r = "INSERT { ?a ?b ?c } WHERE {}"
    g.update(r, initBindings={"a": MICHEL, "b": LIKES, "c": PIZZA})
    assert set(g.triples((None, None, None))) == set(
        [(MICHEL, LIKES, PIZZA)]
    ), "only MICHEL LIKES PIZZA"


def test_empty_named_graph(get_graph):
    graph = get_graph
    empty_graph_iri = "urn:empty-graph-1"
    graph.update("CREATE GRAPH <%s>" % empty_graph_iri)
    named_graphs = [
        str(r[0]) for r in graph.query("SELECT ?name WHERE { GRAPH ?name {} }")
    ]
    # Some SPARQL endpoint backends (like TDB) are not able to find empty named graphs
    # (at least with this query)
    if empty_graph_iri in named_graphs:
        assert empty_graph_iri in [str(g.identifier) for g in graph.contexts()]


def test_empty_literal(get_graph):
    graph = get_graph
    # test for https://github.com/RDFLib/rdflib/issues/457
    # also see test_issue457.py which is sparql store independent!
    g = graph.get_context(graphuri)
    g.add(
        (
            URIRef("http://example.com/s"),
            URIRef("http://example.com/p"),
            Literal(""),
        )
    )

    o = tuple(g)[0][2]
    assert o == Literal(""), repr(o)
