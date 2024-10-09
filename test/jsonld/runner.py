import json

from rdflib import BNode, ConjunctiveGraph
from rdflib.compare import isomorphic
from rdflib.parser import InputSource
from rdflib.plugins.parsers.jsonld import JsonLDParser, to_rdf

# monkey-patch N-Quads parser via it's underlying W3CNTriplesParser to keep source bnode id:s ..
from rdflib.plugins.parsers.ntriples import W3CNTriplesParser, r_nodeid
from rdflib.plugins.serializers.jsonld import from_rdf
from rdflib.plugins.shared.jsonld.keys import CONTEXT, GRAPH


def _preserving_nodeid(self, bnode_context=None):
    if not self.peek("_"):
        return False
    return BNode(self.eat(r_nodeid).group(1))


DEFAULT_PARSER_VERSION = 1.0


def make_fake_urlinputsource(input_uri, format=None, suite_base=None, options={}):
    local_url = input_uri.replace("https://w3c.github.io/json-ld-api/tests/", "./")
    if (index := local_url.find("#")) > -1:
        # Strip off the optional fragment identifier
        local_url = local_url[0:index]
    try:
        f = open(local_url, "rb")
    except FileNotFoundError:
        f = None
    source = InputSource(input_uri)
    source.setPublicId(input_uri)
    source.setByteStream(f)
    source.url = input_uri
    source.links = []
    if local_url.endswith((".jsonld", ".jldt")):
        source.content_type = "application/ld+json"
    elif local_url.endswith(".html"):
        source.content_type = "text/html"
    else:
        source.content_type = "application/json"
    source.format = format
    if options:
        if "httpLink" in options:
            source.links.append(options["httpLink"])
        if "contentType" in options:
            source.content_type = options["contentType"]
        if "redirectTo" in options:
            redir = suite_base + options["redirectTo"]
            local_redirect = redir.replace(
                "https://w3c.github.io/json-ld-api/tests/", "./"
            )
            if f:
                f.close()
            try:
                f = open(local_redirect, "rb")
            except FileNotFoundError:
                f = None
            source.setByteStream(f)
            source.url = redir
            source.setPublicId(redir)
            source.setSystemId(redir)
    return source


def do_test_json(suite_base, cat, num, inputpath, expectedpath, context, options):
    input_uri = suite_base + inputpath
    input_graph = ConjunctiveGraph()
    if cat == "remote-doc":
        input_src = make_fake_urlinputsource(
            input_uri, format="json-ld", suite_base=suite_base, options=options
        )
        p = JsonLDParser()
        p.parse(
            input_src,
            input_graph,
            base=input_src.getPublicId(),
            context_data=context,
            generalized_rdf=True,
        )
    else:
        input_obj = _load_json(inputpath)
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
        base="./",  # deliberately set base different to the input base
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
    if cat == "remote-doc":
        input_src = make_fake_urlinputsource(
            input_uri, format="json-ld", options=options
        )
        p = JsonLDParser()
        p.parse(
            input_src,
            result_graph,
            base=input_uri,
            context_data=context,
            generalized_rdf=True,
        )
    else:
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


def do_test_html(suite_base, cat, num, inputpath, expectedpath, context, options):
    input_uri = suite_base + inputpath
    input_graph = ConjunctiveGraph()

    input_src = make_fake_urlinputsource(
        input_uri, format="json-ld", suite_base=suite_base, options=options
    )

    context = _load_json(context) if context else context

    # Get test options from the manifest
    base = options.get("base", input_src.getPublicId())
    extract_all_scripts = options.get("extractAllScripts", False)

    p = JsonLDParser()
    p.parse(
        input_src,
        input_graph,
        base=base,
        context=context,
        generalized_rdf=True,
        extract_all_scripts=extract_all_scripts,
    )

    if expectedpath.endswith(".nq"):
        expected_graph = _load_nquads(expectedpath)

    elif expectedpath.endswith(".jsonld"):
        expected_graph = ConjunctiveGraph()
        with open(expectedpath) as f:
            data = f.read()
        expected_graph.parse(data=data, format="json-ld")

    # TODO: Change test from graph comparison to json comparison
    # The html test cases combine testing for JSON-LD extraction from the HTML
    # along with testing for other algorithms (compact/flatten), which we do
    # not currently support. In order to test extraction only, we currently
    # perform a graph comparison. Consider changing this to a json comparison
    # once the processing algorithms are implemented.

    assert isomorphic(input_graph, expected_graph), "Expected:\n%s\nGot:\n%s" % (
        expected_graph.serialize(),
        input_graph.serialize(),
    )


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
        obj, indent=2, separators=(",", ": "), sort_keys=True, check_circular=True
    )


def _compare_json(expected, result):
    expected = json.loads(_dump_json(expected))
    result = json.loads(_dump_json(result))
    assert _to_ordered(expected) == _to_ordered(
        result
    ), "Expected JSON:\n%s\nGot:\n%s" % (_dump_json(expected), _dump_json(result))
