# -*- coding: UTF-8 -*-
import json
from rdflib import ConjunctiveGraph
from rdflib.compare import isomorphic
from rdflib.plugins.parsers.jsonld import to_rdf
from rdflib.plugins.serializers.jsonld import from_rdf
from rdflib.plugins.shared.jsonld.keys import CONTEXT, GRAPH

# monkey-patch N-Quads parser via it's underlying W3CNTriplesParser to keep source bnode id:s ..
from rdflib.plugins.parsers.ntriples import W3CNTriplesParser, r_nodeid, bNode


def _preserving_nodeid(self, bnode_context=None):
    if not self.peek("_"):
        return False
    return bNode(self.eat(r_nodeid).group(1))


DEFAULT_PARSER_VERSION = 1.0


def do_test_json(suite_base, cat, num, inputpath, expectedpath, context, options):
    input_uri = suite_base + inputpath
    input_obj = _load_json(inputpath)
    input_graph = ConjunctiveGraph()
    to_rdf(
        input_obj,
        input_graph,
        base=input_uri,
        context_data=context,
        generalized_rdf=True,
    )
    expected_json = _load_json(expectedpath)
    use_native_types = True  # CONTEXT in input_obj
    result_json = from_rdf(
        input_graph,
        context,
        base=input_uri,
        use_native_types=options.get("useNativeTypes", use_native_types),
        use_rdf_type=options.get("useRdfType", False),
    )

    def _prune_json(data):
        if CONTEXT in data:
            data.pop(CONTEXT)
        if GRAPH in data:
            data = data[GRAPH]
        # def _remove_empty_sets(obj):
        return data

    expected_json = _prune_json(expected_json)
    result_json = _prune_json(result_json)

    _compare_json(expected_json, result_json)


def do_test_parser(suite_base, cat, num, inputpath, expectedpath, context, options):
    input_uri = suite_base + inputpath
    input_obj = _load_json(inputpath)
    old_nodeid = W3CNTriplesParser.nodeid
    # monkey patch nodeid fn in NTriplesParser
    W3CNTriplesParser.nodeid = _preserving_nodeid
    try:
        expected_graph = _load_nquads(expectedpath)
    finally:
        W3CNTriplesParser.nodeid = old_nodeid
    result_graph = ConjunctiveGraph()
    requested_version = options.get("specVersion")
    version = DEFAULT_PARSER_VERSION
    if requested_version:
        if requested_version == "json-ld-1.1":
            version = 1.1
        elif requested_version == "json-ld-1.0":
            version = 1.0
    to_rdf(
        input_obj,
        result_graph,
        context_data=context,
        base=options.get("base", input_uri),
        version=version,
        generalized_rdf=options.get("produceGeneralizedRdf", False),
    )
    assert isomorphic(result_graph, expected_graph), "Expected:\n%s\nGot:\n%s" % (
        expected_graph.serialize(),
        result_graph.serialize(),
    )


def do_test_serializer(suite_base, cat, num, inputpath, expectedpath, context, options):
    input_uri = suite_base + inputpath
    old_nodeid = W3CNTriplesParser.nodeid
    # monkey patch nodeid fn in NTriplesParser
    W3CNTriplesParser.nodeid = _preserving_nodeid
    try:
        input_graph = _load_nquads(inputpath)
    finally:
        W3CNTriplesParser.nodeid = old_nodeid
    expected_json = _load_json(expectedpath)
    result_json = from_rdf(
        input_graph,
        context,
        base=input_uri,
        use_native_types=options.get("useNativeTypes", False),
        use_rdf_type=options.get("useRdfType", False),
    )
    _compare_json(expected_json, result_json)


def _load_nquads(source):
    graph = ConjunctiveGraph()
    with open(source) as f:
        data = f.read()
    graph.parse(data=data, format="nquads")
    return graph


def _load_json(source):
    with open(source) as f:
        return json.load(f)


def _to_ordered(obj):
    if isinstance(obj, list):
        # NOTE: use type in key to handle mixed
        # lists of e.g. bool, int, float.
        return sorted(
            (_to_ordered(lv) for lv in obj),
            key=lambda x: (_ord_key(x), type(x).__name__),
        )
    if not isinstance(obj, dict):
        return obj
    return sorted((k, _to_ordered(v)) for k, v in obj.items())


def _ord_key(x):
    if isinstance(x, dict) and "@id" in x:
        return x["@id"]
    else:
        return x


def _dump_json(obj):
    return json.dumps(
        obj, indent=4, separators=(",", ": "), sort_keys=True, check_circular=True
    )


def _compare_json(expected, result):
    expected = json.loads(_dump_json(expected))
    result = json.loads(_dump_json(result))
    assert _to_ordered(expected) == _to_ordered(
        result
    ), "Expected JSON:\n%s\nGot:\n%s" % (_dump_json(expected), _dump_json(result))
