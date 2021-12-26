import pytest
import os
import sys
import shutil
import re
from tempfile import gettempdir
from pprint import pformat
from rdflib import logger, Literal, ConjunctiveGraph, Graph, Dataset, RDFS, URIRef
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID
from pathlib import Path
from urllib.error import URLError, HTTPError

michel = URIRef("urn:michel")
tarek = URIRef("urn:tarek")
bob = URIRef("urn:bob")
likes = URIRef("urn:likes")
hates = URIRef("urn:hates")
pizza = URIRef("urn:pizza")
cheese = URIRef("urn:cheese")

c1 = URIRef("urn:context-1")
c2 = URIRef("urn:context-2")


# store = "BerkeleyDB"
# store = "SQLiteLSM"
# store = "LevelDB"

nquads = """\
<http://example.com/resource/student_10> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://example.com/ontology/Student> <http://example.org/graph/students> .
<http://example.com/resource/student_10> <http://xmlns.com/foaf/0.1/name> "Venus Williams"                                       <http://example.org/graph/students> .
<http://example.com/resource/student_20> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://example.com/ontology/Student> <http://example.org/graph/students> .
<http://example.com/resource/student_20> <http://xmlns.com/foaf/0.1/name> "Demi Moore"                                           <http://example.org/graph/students> .
<http://example.com/resource/sport_100> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://example.com/ontology/Sport>    <http://example.org/graph/sports> .
<http://example.com/resource/sport_100> <http://www.w3.org/2000/01/rdf-schema#label> "Tennis"                                    <http://example.org/graph/sports> .
<http://example.com/resource/student_10> <http://example.com/ontology/practises> <http://example.com/resource/sport_100>         <http://example.org/graph/practise> .
"""

list_of_nquads = [
    (
        URIRef("http://example.com/resource/student_10"),
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        URIRef("http://example.com/ontology/Student"),
        URIRef("http://example.org/graph/students"),
    ),
    (
        URIRef("http://example.com/resource/student_10"),
        URIRef("http://xmlns.com/foaf/0.1/name"),
        Literal("Venus Williams"),
        URIRef("http://example.org/graph/students"),
    ),
    (
        URIRef("http://example.com/resource/student_20"),
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        URIRef("http://example.com/ontology/Student"),
        URIRef("http://example.org/graph/students"),
    ),
    (
        URIRef("http://example.com/resource/student_20"),
        URIRef("http://xmlns.com/foaf/0.1/name"),
        Literal("Demi Moore"),
        URIRef("http://example.org/graph/students"),
    ),
    (
        URIRef("http://example.com/resource/sport_100"),
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        URIRef("http://example.com/ontology/Sport"),
        URIRef("http://example.org/graph/sports"),
    ),
    (
        URIRef("http://example.com/resource/sport_100"),
        URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
        Literal("Tennis"),
        URIRef("http://example.org/graph/sports"),
    ),
    (
        URIRef("http://example.com/resource/student_10"),
        URIRef("http://example.com/ontology/practises"),
        URIRef("http://example.com/resource/sport_100"),
        URIRef("http://example.org/graph/practise"),
    ),
]


@pytest.fixture(
    # scope="function", params=["default", "BerkeleyDB", "SQLiteLSM", "LevelDB", "SQLAlchemy"]
    scope="function",
    params=["default"],
)
def get_dataset(request):
    store = request.param
    tmppath = os.path.join(gettempdir(), f"test_{store.lower()}")
    graph = Dataset(store=store)
    graph.open(tmppath, create=True)
    # tmppath = mkdtemp()
    if store != "default" and graph.store.is_open():
        # delete the graph for each test!
        graph.remove((None, None, None))
        for c in graph.contexts():
            c.remove((None, None, None))
            assert len(c) == 0
            graph.remove_graph(c)
    # logger.debug(f"Using store {graph.store}")
    yield graph

    graph.close()
    if os.path.isdir(tmppath):
        shutil.rmtree(tmppath)
    else:
        try:
            os.remove(tmppath)
        except Exception:
            pass


@pytest.fixture(
    # scope="function", params=["default", "BerkeleyDB", "SQLiteLSM", "LevelDB", "SQLAlchemy"]
    scope="function",
    params=["default"],
)
def get_conjunctivegraph(request):
    store = request.param
    tmppath = os.path.join(gettempdir(), f"test_{store.lower()}")
    graph = ConjunctiveGraph(store=store)
    graph.open(tmppath, create=True)
    # tmppath = mkdtemp()
    if store != "default" and graph.store.is_open():
        # delete the graph for each test!
        graph.remove((None, None, None))
        for c in graph.contexts():
            c.remove((None, None, None))
            assert len(c) == 0
            graph.remove_graph(c)
    # logger.debug(f"Using store {graph.store}")
    yield graph

    graph.close()
    if os.path.isdir(tmppath):
        shutil.rmtree(tmppath)
    else:
        try:
            os.remove(tmppath)
        except Exception:
            pass


# @pytest.mark.skip
def test_issue_301_dataset_does_not_parse(get_dataset):

    # STATUS: FIXED, no longer an issue

    d = get_dataset

    g = d.parse(data="<a:a> <b:b> <c:c> .", format="turtle", publicID=URIRef("g:g"))

    assert g == d.get_context(g.identifier)


# @pytest.mark.skip
def test_issue_query_on_ds_yields_no_results():

    # STATUS: FIXED no longer an issue

    data = """
    <http://data.yyx.me/jack> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_a> .
    <http://data.yyx.me/david> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_b> .
    """

    ds = Dataset()
    g = Graph(identifier="subgraph")
    g.parse(data=data, format="n3")
    ds.add_graph(g)

    # yields 2 results from this query
    assert (
        len(list(ds.query("""SELECT ?s ?p ?o WHERE {GRAPH <subgraph> { ?s ?p ?o }}""")))
        == 2  # noqa: W503
    )

    # yields 2 results from this query
    assert (
        len(list(ds.query("""SELECT ?g ?s ?p ?o WHERE { GRAPH ?g { ?s ?p ?o }}""")))
        == 2  # noqa: W503
    )


# @pytest.mark.skip
def test_iter_pr1382_add_iter_to_ds(get_dataset):
    d = get_dataset

    # STATUS: FIXED not an issue

    """
    PR 1382: adds __iter__ to Dataset
    Test assumes PR chnages have been applied
    """

    uri_a = URIRef("https://example.com/a")
    uri_b = URIRef("https://example.com/b")
    uri_c = URIRef("https://example.com/c")
    uri_d = URIRef("https://example.com/d")

    d.add_graph(URIRef("https://example.com/g1"))
    d.add((uri_a, uri_b, uri_c, URIRef("https://example.com/g1")))
    d.add(
        (uri_a, uri_b, uri_c, URIRef("https://example.com/g1"))
    )  # pointless addition: duplicates above

    d.add_graph(URIRef("https://example.com/g2"))
    d.add((uri_a, uri_b, uri_c, URIRef("https://example.com/g2")))
    d.add((uri_a, uri_b, uri_d, URIRef("https://example.com/g1")))  # new, uri_d

    # traditional iterator
    i_trad = 0
    for t in d.quads((None, None, None)):
        i_trad += 1

    # new Dataset.__iter__ iterator
    i_new = 0
    for t in d:
        i_new += 1

    assert i_new == i_trad  # both should be 3
    assert i_new == 3


# @pytest.mark.skip
def test_issue939_parse_return_inconsistent_type():

    # STATUS: FIXED Not an issue (probably)

    # The parse function of ConjunctiveGraph modify in place the
    # ConjunctiveGraph but return a Graph object. This is a minor issue but
    # it can create issues down the road if the parse methode is called like
    # so g = g.parse(source="test.ttl", format='turtle')

    # Demonstration:

    # from rdflib import Graph, ConjunctiveGraph

    # g = ConjunctiveGraph()
    # g.parse(source="test.ttl", format='turtle')
    # print(type(g)) # <class 'rdflib.graph.ConjunctiveGraph'>

    # g = ConjunctiveGraph()
    # g = g.parse(source="test.ttl", format='turtle')
    # print(type(g)) # <class 'rdflib.graph.Graph'>

    test_ttl = """@base <http://purl.org/linkedpolitics/MembersOfParliament_background> .
    @prefix lpv: <vocabulary/> .
    <EUmember_1026>
        a lpv:MemberOfParliament ."""

    # Support this idiom ...
    g = ConjunctiveGraph().parse(data=test_ttl, format="turtle")
    assert type(g) is ConjunctiveGraph  # <class 'rdflib.graph.ConjunctiveGraph'>

    # The reported would like x to be the ConjunctiveGraph or that type

    assert type(g) is ConjunctiveGraph


@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_issue_167_sparqlupdatestore_compatibility(get_dataset):

    # STATUS: FIXED no longer an issue

    # https://github.com/RDFLib/rdflib/issues/167#issuecomment-873620457

    # Note that this is also observed when using Dataset instances. In particular,

    from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

    store = SPARQLUpdateStore(
        query_endpoint="http://localhost:3030/db/sparql",
        update_endpoint="http://localhost:3030/db/update",
    )

    ds = Dataset(store=store)
    # ds.parse(data=sportquadsnq, format="nquads")

    ds.update("CLEAR ALL")

    ds.addN(list_of_nquads)

    # assert (
    #     repr(list(ds.contexts()))
    #     == "[<Graph identifier=http://example.org/graph/students (<class 'rdflib.graph.Graph'>)>, <Graph identifier=http://example.org/graph/practise (<class 'rdflib.graph.Graph'>)>, <Graph identifier=http://example.org/graph/sports (<class 'rdflib.graph.Graph'>)>, <Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>]"
    # )

    assert len(list(ds.contexts())) == 4

    # Used to be the case but no longer - fixes

    # Data from fuseki (urn:context-1 from previous update)

    # Dataset size

    # graph name:                           triples:

    # default graph                         0
    # urn:context-1                         1
    # http://example.org/graph/practise     1
    # http://example.org/graph/sports       2
    # http://example.org/graph/students     4


# @pytest.mark.skip
def test_issue679_trig_export(get_dataset):

    # STATUS: FIXED? no longer an issue

    #  trig export of multiple graphs assigns wrong prefixes to prefixedNames #679
    ds = get_dataset
    graphs = [(URIRef("urn:tg1"), "A"), (URIRef("urn:tg2"), "B")]

    for i, n in graphs:
        # g = Graph(identifier=i)
        g = ds.get_context(i)
        a = URIRef("urn:{}#S".format(n))
        b = URIRef("urn:{}#p".format(n))
        c = Literal(chr(0xF23F1))
        d = Literal(chr(0x66))
        e = Literal(chr(0x23F2))
        g.add((a, b, c))
        g.add((a, b, d))
        g.add((a, b, e))
        # ds.graph(g)

    # for n, k in [
    #     ("json-ld", "jsonld"),
    #     ("nquads", "nq"),
    #     ("trix", "trix"),
    #     ("trig", "trig"),
    # ]:
    #     logger.debug(f"{k}\n{ds.serialize(format=n)}")

    # Output is conformant and as expected

    # logger.debug(
    #     f"test_issue679_trig_export trig\n{ds.serialize(format='trig')}"
    # )

    # DEBUG    rdflib:test_dataset_anomalies.py:1190 trig
    # @prefix ns1: <urn:> .
    # @prefix ns2: <urn:A#> .
    # @prefix ns3: <urn:B#> .
    # @prefix ns4: <urn:x-rdflib:> .

    # ns1:tg1 {
    #     ns2:S ns2:p "f",
    #             "⏲",
    #             "󲏱" .
    # }

    # ns1:tg2 {
    #     ns3:S ns3:p "f",
    #             "⏲",
    #             "󲏱" .
    # }

    # logger.debug(f"trig\n{ds.serialize(format='trig')}")

    # DEBUG    rdflib:test_dataset_anomalies.py:1191 trig
    # @prefix ns1: <urn:> .
    # @prefix ns2: <urn:A#> .
    # @prefix ns3: <urn:B#> .
    # @prefix ns4: <urn:x-rdflib:> .

    # ns1:tg1 {
    #     ns2:S ns2:p "f",
    #             "⏲",
    #             "󲏱" .
    # }

    # ns1:tg2 {
    #     ns3:S ns3:p "f",
    #             "⏲",
    #             "󲏱" .
    # }


# @pytest.mark.skip
def test_trig_export_reopen(get_dataset):

    # STATUS: FIXED? no longer an issue

    #  trig export of multiple graphs assigns wrong prefixes to prefixedNames #679

    # I wanted to add that I see this behavior even in the case of parsing a dataset
    # with a single graph in nquads format and serializing as trig with no special characters.

    ds = get_dataset
    ds.parse(data=nquads, format="nquads")
    # logger.debug(
    #     f"test_trig_export_reopen trig\n{ds.serialize(format='trig')}"
    # )


# @pytest.mark.skip
def test_ds_capable_parse(get_dataset):

    # STATUS: FIXED no longer an issue

    ds = get_dataset
    trigfile = os.path.join(
        os.path.dirname(__file__), "consistent_test_data", "testdata01.trig"
    )
    ds.parse(location=trigfile)  # RDF file type worked out by guess_format()
    assert len(list(ds.quads((None, None, None, None)))) == 2


trig_example = """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
 @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
 @prefix swp: <http://www.w3.org/2004/03/trix/swp-1/> .
 @prefix dc: <http://purl.org/dc/elements/1.1/> .
 @prefix ex: <http://www.example.org/vocabulary#> .
 @prefix : <http://www.example.org/exampleDocument#> .

 :G1 { :Monica ex:name "Monica Murphy" .
       :Monica ex:homepage <http://www.monicamurphy.org> .
       :Monica ex:email <mailto:monica@monicamurphy.org> .
       :Monica ex:hasSkill ex:Management }

 :G2 { :Monica rdf:type ex:Person .
       :Monica ex:hasSkill ex:Programming }

 :G3 { :G1 swp:assertedBy _:w1 .
       _:w1 swp:authority :Chris .
       _:w1 dc:date "2003-10-02"^^xsd:date .
       :G2 swp:quotedBy _:w2 .
       :G3 swp:assertedBy _:w2 .
       _:w2 dc:date "2003-09-03"^^xsd:date .
       _:w2 swp:authority :Chris .
       :Chris rdf:type ex:Person .
       :Chris ex:email <mailto:chris@bizer.de> }
"""


# @pytest.mark.skip
def test_issue1244_inconsistent_default_parse_format_dataset(get_dataset):
    """
    # STATUS: Fixed

    #  ashleysommer commented on 5 Feb

    We recently changed the Graph.parse() method's format parameter to
    default of turtle instead of XML. This is because turtle is now a much
    more popular file format for Graph data.

    However we overlooked that the ConjunctiveGraph and Dataset classes each
    have their own overloaded parse() method, and they still use 'xml' as
    the default format if none is given.

    The simple thing to do would be simply replace "xml" with "turtle" on
    those too, but looking closer that may not be wise. Because
    ConjuctiveGraph and Dataset are both multi-graph containers and Turtle
    is not multi-graph capable. So usually when you are doing
    ConjunctiveGraph.parse() you will not be expecting a turtle file, but
    more likely .trig or .jsonld.

    Should we change the default format on these to something else, or leave
    it on XML?

    # white-gecko commented on 5 Feb

    I think trig would be good
    """

    ds = get_dataset

    # Parse trig data and file
    ds.parse(data=trig_example)

    # Trig default
    ds.parse(Path("./test/consistent_test_data/testdata02.trig").absolute().as_uri())

    # Parse nquads file
    ds.parse(Path("./test/nquads.rdflib/example.nquads").absolute().as_uri())

    # Parse Trix file
    ds.parse(Path("./test/trix/nokia_example.trix").absolute().as_uri())

    # files
    try:
        ds.parse(__file__)  # here we are trying to parse a Python file!!
    except Exception as e:
        # logger.debug(f"Exception {repr(e)}")
        assert repr(e).startswith("""ParserError("Could not guess RDF format""")

    # .nt can be parsed by Turtle Parser
    ds.parse("test/nt/anons-01.nt")

    # RDF/XML
    ds.parse("test/rdf/datatypes/test001.rdf")  # XML

    # bad filename but set format
    ds.parse("test/rdf/datatypes/test001.borked", format="xml")

    # strings
    ds = get_dataset

    try:
        ds.parse(data="rubbish")
    except Exception as e:
        assert repr(e).startswith("""ParserError('Could not guess RDF format""")

    # Turtle - guess format
    ds.parse(
        data="<http://example.com/a> <http://example.com/a> <http://example.com/a> ."
    )

    # Turtle - format given
    ds.parse(
        data="<http://example.com/a> <http://example.com/a> <http://example.com/a> .",
        format="turtle",
    )

    # URI
    ds = get_dataset

    # only getting HTML
    try:
        ds.parse(location="https://www.google.com")
    except Exception as e:
        # logger.debug(f"Exception {repr(e)}")
        assert (
            repr(e)
            == """PluginException("No plugin registered for (text/html, <class 'rdflib.parser.Parser'>)")"""
        )

    try:
        ds.parse(location="http://www.w3.org/ns/adms.ttl")
        ds.parse(location="http://www.w3.org/ns/adms.rdf")
    except (URLError, HTTPError):
        # this endpoint is currently not available, ignore this test.
        pass

    try:
        # persistent Australian Government online RDF resource without a file-like ending
        ds.parse(location="https://linked.data.gov.au/def/agrif?_format=text/turtle")
    except (URLError, HTTPError):
        # this endpoint is currently not available, ignore this test.
        pass


# @pytest.mark.skip
def test_issue1244_inconsistent_default_parse_format_conjunctivegraph(
    get_conjunctivegraph,
):
    # STATUS: Fixed

    cg = get_conjunctivegraph

    # Parse trig data and file
    cg.parse(data=trig_example)

    # Trig default
    cg.parse(Path("./test/consistent_test_data/testdata01.trig").absolute().as_uri())

    # Parse nquads file
    cg.parse(Path("./test/nquads.rdflib/example.nquads").absolute().as_uri())

    # Parse Trix file
    cg.parse(Path("./test/trix/nokia_example.trix").absolute().as_uri())

    # files
    try:
        cg.parse(__file__)  # here we are trying to parse a Python file!!
    except Exception as e:
        # logger.debug(f"Exception {repr(e)}")
        assert repr(e).startswith("""ParserError("Could not guess RDF format""")

    # .nt can be parsed by Turtle Parser
    cg.parse("test/nt/anons-01.nt")
    # RDF/XML
    cg.parse("test/rdf/datatypes/test001.rdf")  # XML
    # bad filename but set format
    cg.parse("test/rdf/datatypes/test001.borked", format="xml")

    # strings
    cg = get_conjunctivegraph

    try:
        cg.parse(data="rubbish")
    except Exception as e:
        # logger.debug(f"Exception {repr(e)}")
        assert repr(e).startswith("""ParserError('Could not guess RDF format""")

    # Turtle - default
    cg.parse(
        data="<http://example.com/a> <http://example.com/a> <http://example.com/a> ."
    )

    # Turtle - format given
    cg.parse(
        data="<http://example.com/a> <http://example.com/a> <http://example.com/a> .",
        format="turtle",
    )

    # URI
    cg = get_conjunctivegraph

    # only getting HTML
    try:
        cg.parse(location="https://www.google.com")
    except Exception as e:
        assert (
            repr(e)
            == """PluginException("No plugin registered for (text/html, <class 'rdflib.parser.Parser'>)")"""
        )

    from urllib.error import URLError, HTTPError

    try:
        cg.parse(location="http://www.w3.org/ns/adms.ttl")
        cg.parse(location="http://www.w3.org/ns/adms.rdf")
    except (URLError, HTTPError):
        # this endpoint is currently not available, ignore this test.
        pass

    try:
        # persistent Australian Government online RDF resource without a file-like ending
        cg.parse(location="https://linked.data.gov.au/def/agrif?_format=text/turtle")
    except (URLError, HTTPError):
        # this endpoint is currently not available, ignore this test.
        pass


# @pytest.mark.skip
def test_issue_698_len_ds():
    """

    # STATUS: FIXED no longer an issue

    Dataset.graph should not allow adding random graphs to the store #698
    gromgull commented on 24 Jan 2017

    You can pass an existing graph into the dataset. This will then be
    added directly.

    But there is no guarantee this new graph has the same store, and the
    triples will not be copied over.

    """
    from rdflib import Graph
    from rdflib.namespace import FOAF

    # Create dissociated graph
    foaf = Graph(identifier=FOAF)
    foaf.parse("http://xmlns.com/foaf/spec/index.rdf", format="xml")

    ds = Dataset()

    ds.add_graph(foaf)

    assert len(list(ds.contexts())) == 2
    assert len(foaf) == 631
    # with pytest.raises(AssertionError):
    #     assert len(ds) == 631
    assert len(ds) == 631
    # logger.debug(
    #     f" CONTEXT IDENTIFIERS {pformat([c.identifier for c in list(ds.contexts())])}"
    # )


# # @pytest.mark.skip
def test_issue1396_store_query_and_update_methods_queryGraph_parameter_does_not_support_conjunctivegraph_and_dataset_dataset(
    get_dataset,
):
    # STATUS: FIXED no longer an issue - probably

    ds = get_dataset

    # There are no triples in any context, so dataset length == 0
    assert len(ds) == 0

    # The default graph is a context so the length of ds.contexts() == 1
    assert len(list(ds.contexts())) == 1

    # Only the default graph exists and is yielded by ds.contexts()
    assert (
        repr(list(ds.contexts()))
        == "[<Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>]"
    )

    # only the default graph exists and is properly identified as DATASET_DEFAULT_GRAPH_ID
    assert set(x.identifier for x in ds.contexts()) == set([DATASET_DEFAULT_GRAPH_ID])

    dataset_default_graph = ds.get_context(DATASET_DEFAULT_GRAPH_ID)
    # logger.debug(f"\n\nDATASET_DEFAULT_GRAPH\n{repr(dataset_default_graph)}")
    assert (
        repr(dataset_default_graph)
        == "<Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>"
    )

    ds.update("INSERT DATA { <urn:tarek> <urn:hates> <urn:pizza> . }")

    assert len(list(ds.contexts())) == 1

    # Only the default graph exists and is yielded by ds.contexts()
    assert (
        repr(list(ds.contexts()))
        == "[<Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>]"
    )

    # There is one triple in the context, so dataset length == 1
    assert len(ds) == 1


# # @pytest.mark.skip
def test_issue1396_store_query_and_update_methods_queryGraph_parameter_does_not_support_namedgraph_and_dataset_dataset(
    get_dataset,
):
    # STATUS: FIXED no longer an issue - probably

    ds = get_dataset

    # There are no triples in any context, so dataset length == 0
    assert len(ds) == 0

    # The default graph is a context so the length of ds.contexts() == 1
    assert len(list(ds.contexts())) == 1

    # Only the default graph exists and is yielded by ds.contexts()
    assert (
        repr(list(ds.contexts()))
        == "[<Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>]"
    )

    # only the default graph exists and is properly identified as DATASET_DEFAULT_GRAPH_ID
    assert set(x.identifier for x in ds.contexts()) == set([DATASET_DEFAULT_GRAPH_ID])

    dataset_default_graph = ds.get_context(DATASET_DEFAULT_GRAPH_ID)
    # logger.debug(f"\n\nDATASET_DEFAULT_GRAPH\n{repr(dataset_default_graph)}")
    assert (
        repr(dataset_default_graph)
        == "<Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>"
    )

    # INSERT into NAMED GRAPH

    ds.update(
        "INSERT DATA { GRAPH <urn:context1> { <urn:tarek> <urn:hates> <urn:pizza> . } }"
    )

    assert len(list(ds.contexts())) == 2

    # Only the default graph exists and is yielded by ds.contexts()
    assert repr(list(ds.contexts())) in [
        "[<Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>, <Graph identifier=urn:context1 (<class 'rdflib.graph.Graph'>)>]",
        "[<Graph identifier=urn:context1 (<class 'rdflib.graph.Graph'>)>, <Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>]",
    ]

    # There is one triple in the context, so dataset length == 1
    assert len(ds) == 1


# @pytest.mark.skip
def test_issue1396_store_query_and_update_methods_queryGraph_parameter_does_not_support_conjunctivegraph_and_dataset_conjunctivegraph(
    get_conjunctivegraph,
):

    # STATUS: FIXED no longer an issue - probably

    cg = get_conjunctivegraph

    # There are no triples in any context, so dataset length == 0
    assert len(cg) == 0

    # The default graph is a context so the length of ds.contexts() == 1
    assert len(list(cg.contexts())) == 0

    assert repr(list(cg.contexts())) == "[]"

    dataset_default_graph = cg.get_context(DATASET_DEFAULT_GRAPH_ID)

    assert (
        repr(dataset_default_graph)
        #        == "<Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>"
    )

    cg.update("INSERT DATA { <urn:tarek> <urn:hates> <urn:pizza> . }")

    assert len(list(cg.contexts())) == 1

    assert re.match(
        r"\[<Graph identifier=N(.*?) \(<class 'rdflib\.graph\.Graph'>\)>]",
        repr(list(cg.contexts())),
    )

    # There is one triple in the context, so dataset length == 1
    assert len(cg) == 1


# @pytest.mark.skip
def test_dataset_add_graph(get_dataset):

    # Status: FIXED no longer an issue

    data = """
    <http://data.yyx.me/jack> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_a> .
    <http://data.yyx.me/david> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_b> .
    """

    g = Graph(identifier="subgraph")
    g.parse(data=data, format="n3")
    assert len(g) == 2

    ds = get_dataset
    ds.add_graph(g)

    # yields 2 results from this query
    assert (
        len(list(ds.query("""SELECT ?s ?p ?o WHERE {GRAPH <subgraph> { ?s ?p ?o }}""")))
        == 2  # noqa: W503
    )

    # yields 0 results from this query
    assert (
        len(list(ds.query("""SELECT ?g ?s ?p ?o WHERE { GRAPH ?g { ?s ?p ?o }}""")))
        == 2  # noqa: W503
    )

    sg = ds.get_context("subgraph")
    assert len(sg) == 2


def test_issue652_sum_of_conjunctive_graphs_is_not_conjunctive_graph(
    get_conjunctivegraph,
):
    # STATUS: FIXED no longer an issue

    # Sum of conjunctive graphs is not conjunctive graph #652
    g1 = get_conjunctivegraph
    g2 = get_conjunctivegraph

    assert type(g1 + g2) == ConjunctiveGraph


# @pytest.mark.skip
def test_issue1396_store_query_and_update_methods_querygraph_parameter_does_not_support_conjunctivegraph_and_dataset_dataset(
    get_dataset,
):
    """
    1. With `query` and `Dataset`.

    `Dataset(store="MyCustomStore").update("INSERT DATA {}")` will call the
    underlying `MyCustomStore` with the parameter `queryGraph=BNode
    ("abcde")` with `BNode("abcde")` the dataset `identifier` instead of
    `queryGraph=URI("urn:x-rdflib-default")` that identifies the default graph
    and is used by the basic triple insertion and deletion method.

    With this parameter the `Store` query evaluator will query the `_:abcde` graph
    even if the triples are by default added in the default graph identified by
    `<urn:x-rdflib-default>`.

    3. With `update` and `Dataset`.

    Similarly to the `query` method the `queryGraph` parameter is set to the
    Dataset `identifier` and not `URI("urn:x-rdflib-default")` so the update is
    evaluated against the `_:abcde` graph even if triples are by default added to
    the default graph(`<urn:x-rdflib-default>`) by the `add` method.

    """
    ds = get_dataset
    # logger.debug(f"DS contexts {list(ds.contexts())}")
    # logger.debug(f"DS default context {ds.default_context.identifier}")
    # DS contexts [<Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>]
    # DS default context urn:x-rdflib-default

    ds.update("INSERT DATA {<urn:tarek> <urn:likes> <urn:pizza> .}")
    # logger.debug(f"DS contexts {list(ds.contexts())}")
    # logger.debug(f"DS default context {ds.default_context.identifier}")

    ds.query("SELECT * {?s ?p ?o .}")

    """
    Logger output:

    test/test_dataset_graph_ops.py::test_issue1396_store_query_and_update_methods_querygraph_parameter_does_not_support_conjunctivegraph_and_dataset_dataset[default]
    -------------------------------- live log setup --------------------------------
    DEBUG    rdflib:test_dataset_graph_ops.py:113 Using store <rdflib.plugins.stores.memory.Memory object at 0x7fa0407bf640>
    -------------------------------- live log call ---------------------------------
    DEBUG    rdflib:test_dataset_graph_ops.py:440 DS contexts [<Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>]
    DEBUG    rdflib:test_dataset_graph_ops.py:441 DS default context urn:x-rdflib-default
    DEBUG    rdflib.graph:graph.py:1370 store has update True and use_store_provided True
    DEBUG    rdflib.graph:graph.py:1376 Graph: update:: store.update INSERT DATA {<urn:tarek> <urn:likes> <urn:pizza> .} initNs 27 initBindings {} queryGraph urn:x-rdflib-default kwargs {}
    DEBUG    rdflib:memory.py:559 Memory: update:: update INSERT DATA {<urn:tarek> <urn:likes> <urn:pizza> .} initNs 27 initBindings {} queryGraph urn:x-rdflib-default kwargs {}
    DEBUG    rdflib.graph:graph.py:1387 However, NotImplementedError so passing the buck
    DEBUG    rdflib.graph:graph.py:1393 Graph: update:: processor.graph.identifier urn:x-rdflib-default
    DEBUG    rdflib.graph:graph.py:1397 Graph: update:: processor.update <rdflib.plugins.sparql.processor.SPARQLUpdateProcessor object at 0x7fa0407b8df0> INSERT DATA {<urn:tarek> <urn:likes> <urn:pizza> .} initBindings {} initNs 27 kwargs {}
    DEBUG    rdflib:test_dataset_graph_ops.py:444 DS contexts [<Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>]
    DEBUG    rdflib:test_dataset_graph_ops.py:445 DS default context urn:x-rdflib-default
    DEBUG    rdflib.graph:graph.py:1325 store has query True and use_store_provided True
    DEBUG    rdflib.graph:graph.py:1330 Graph: query:: store.query SELECT * {?s ?p ?o .} initNs 27 initBindings {} queryGraph urn:x-rdflib-default kwargs {}
    DEBUG    rdflib:memory.py:553 Memory: query:: update SELECT * {?s ?p ?o .} initNs 27 initBindings {} queryGraph urn:x-rdflib-default kwargs {}
    DEBUG    rdflib.graph:graph.py:1341 However, NotImplementedError so passing the buck
    DEBUG    rdflib.graph:graph.py:1349 Graph: query:: processor.graph.identifier urn:x-rdflib-default
    DEBUG    rdflib.graph:graph.py:1353 Graph: query:: processor.query <rdflib.plugins.sparql.processor.SPARQLProcessor object at 0x7fa040599940> SELECT * {?s ?p ?o .} initBindings {} initNs 27 kwargs {}
    PASSED                                                                   [ 66%]
    """


# @pytest.mark.skip
def test_issue1396_store_query_and_update_methods_querygraph_parameter_does_not_support_conjunctivegraph_and_dataset_conjunctivegraph(
    get_conjunctivegraph,
):
    """
    `ConjunctiveGraph(store="MyCustomStore").update("INSERT DATA {}")` will call
    the underlying `MyCustomStore` with the parameter `queryGraph="__UNION__"`.

    With only this information the underlying store does not know what is the
    identifier of the `ConjunctiveDataset` default graph in which the triples
    should be added if the update contains an `INSERT` or a `LOAD` action.
    """
    cg = get_conjunctivegraph
    # logger.debug(f"CG contexts {list(cg.contexts())}")
    assert list(cg.contexts()) == []
    # logger.debug(f"CG default context {cg.default_context.identifier}")

    cg.update("INSERT DATA {<urn:tarek> <urn:likes> <urn:pizza> .}")
    # logger.debug(f"CG contexts {list(cg.contexts())}")
    # logger.debug(f"CG default context {cg.default_context.identifier}")    assert list(cg.contexts()) != []

    cg.query("SELECT * {?s ?p ?o .}")

    """
    Logger output:
    ============================= test session starts ==============================
    test/test_dataset_graph_ops.py::test_issue1396_store_query_and_update_methods_querygraph_parameter_does_not_support_conjunctivegraph_and_dataset_conjunctivegraph[default]
    -------------------------------- live log call ---------------------------------
    DEBUG    rdflib:test_dataset_graph_ops.py:491 CG contexts []
    DEBUG    rdflib:test_dataset_graph_ops.py:493 CG default context N1bd29e866be8449c8c6fa4ae824b0838
    DEBUG    rdflib.graph:graph.py:1370 store has update True and use_store_provided True
    DEBUG    rdflib.graph:graph.py:1376 Graph: update:: store.update INSERT DATA {<urn:tarek> <urn:likes> <urn:pizza> .} initNs 27 initBindings {} queryGraph __UNION__ kwargs {}
    DEBUG    rdflib:memory.py:559 Memory: update:: update INSERT DATA {<urn:tarek> <urn:likes> <urn:pizza> .} initNs 27 initBindings {} queryGraph __UNION__ kwargs {}
    DEBUG    rdflib.graph:graph.py:1387 However, NotImplementedError so passing the buck
    DEBUG    rdflib.graph:graph.py:1393 Graph: update:: processor.graph.identifier N1bd29e866be8449c8c6fa4ae824b0838
    DEBUG    rdflib.graph:graph.py:1397 Graph: update:: processor.update <rdflib.plugins.sparql.processor.SPARQLUpdateProcessor object at 0x7f2e38b32d60> INSERT DATA {<urn:tarek> <urn:likes> <urn:pizza> .} initBindings {} initNs 27 kwargs {}
    DEBUG    rdflib:test_dataset_graph_ops.py:496 CG contexts [<Graph identifier=N1bd29e866be8449c8c6fa4ae824b0838 (<class 'rdflib.graph.Graph'>)>]
    DEBUG    rdflib:test_dataset_graph_ops.py:497 CG default context N1bd29e866be8449c8c6fa4ae824b0838
    DEBUG    rdflib.graph:graph.py:1325 store has query True and use_store_provided True
    DEBUG    rdflib.graph:graph.py:1330 Graph: query:: store.query SELECT * {?s ?p ?o .} initNs 27 initBindings {} queryGraph __UNION__ kwargs {}
    DEBUG    rdflib:memory.py:553 Memory: query:: update SELECT * {?s ?p ?o .} initNs 27 initBindings {} queryGraph __UNION__ kwargs {}
    DEBUG    rdflib.graph:graph.py:1341 However, NotImplementedError so passing the buck
    DEBUG    rdflib.graph:graph.py:1349 Graph: query:: processor.graph.identifier N1bd29e866be8449c8c6fa4ae824b0838
    DEBUG    rdflib.graph:graph.py:1353 Graph: query:: processor.query <rdflib.plugins.sparql.processor.SPARQLProcessor object at 0x7f2e389139d0> SELECT * {?s ?p ?o .} initBindings {} initNs 27 kwargs {}
    PASSED                                                                   [100%]
    """


@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test__issue_758_sparqlstore_is_incorrectly_readonly(get_dataset):

    # STATUS: FIXME Remains an issue

    #  Cannot enumerate dataset graphs #758

    dataset = Dataset(store="SPARQLStore")

    dataset.open("http://localhost:3030/db/query")

    # Incorrectly raises TypeError: SPARQL Store is read only

    # DEVNOTE FIXME: *this* is the appopriate pytest idiom
    with pytest.raises(TypeError):
        for g in dataset.graphs():
            print(g)
    # for g in dataset.graphs():
    #     # logger.debug(f"SPARQLStore: {g}")
    #     print(g)

    # """TypeError('The SPARQL store is read only')"""


# @pytest.mark.skip
def test_issue1188_with_two_graphs():
    g1 = Graph()
    g2 = Graph()
    u = URIRef("http://example.com/foo")
    g1.add([u, RDFS.label, Literal("foo")])
    g1.add([u, RDFS.label, Literal("bar")])

    g2.add([u, RDFS.label, Literal("foo")])
    g2.add([u, RDFS.label, Literal("bing")])
    assert len(g1 + g2) == 3  # adds bing as label
    assert len(g1 - g2) == 1  # removes foo
    assert len(g1 * g2) == 1  # only foo
    g1 += g2  # now g1 contains everything
    assert len(g1) == 3
    assert len(g1) == 3


# @pytest.mark.skip
def test_issue1188_with_conjunctivegraph_and_graph(get_conjunctivegraph):
    # STATUS: PASS
    g1 = get_conjunctivegraph
    g2 = Graph()
    u = URIRef("http://example.com/foo")
    g1.add([u, RDFS.label, Literal("foo")])
    g1.add([u, RDFS.label, Literal("bar")])

    g2.add([u, RDFS.label, Literal("foo")])
    g2.add([u, RDFS.label, Literal("bing")])

    assert len(g1 + g2) == 3  # adds bing as label
    assert len(g1 - g2) == 1  # removes foo
    assert len(g1 * g2) == 1  # only foo

    g1 += g2  # now g1 contains everything
    assert len(g1) == 3


@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_issue_371_validation_of_quads_at_graph_addn_doesnt_work_as_expected_sparqlstore():

    # STATUS: FIXED no longer an issue

    from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

    store = SPARQLUpdateStore(
        query_endpoint="http://localhost:3030/db/sparql",
        update_endpoint="http://localhost:3030/db/update",
    )

    store.addN(list_of_nquads)

    triples = store.triples(
        (None, None, None), context=URIRef("http://example.org/graph/students")
    )

    ntriples = [triple for triple in triples]

    assert len(ntriples) == 4

    tquad = (
        (
            URIRef("http://example.com/resource/student_10"),
            URIRef("http://xmlns.com/foaf/0.1/name"),
            Literal("Venus Williams"),
        ),
        None,
    )

    assert tquad in ntriples

    store.update("CLEAR ALL")


# @pytest.mark.skip
def test_issue_371_validation_of_quads_at_graph_addn_doesnt_work_as_expected_ds():

    # STATUS: FIXED no longer an issue

    ds = Dataset()
    ds.addN(list_of_nquads)

    quads = list(
        ds.quads((None, None, None, URIRef("http://example.org/graph/students")))
    )

    assert len(quads) == 4

    tquad = (
        URIRef("http://example.com/resource/student_10"),
        URIRef("http://xmlns.com/foaf/0.1/name"),
        Literal("Venus Williams"),
        URIRef("http://example.org/graph/students"),
    )

    assert tquad in quads


@pytest.mark.skip
def test_issue167_clarify_context_element_needs_final_clarification_repo():

    # Works as expected these days

    g1 = ConjunctiveGraph()
    g2 = ConjunctiveGraph()

    g1.get_context("urn:a").add((tarek, likes, cheese))
    g2.addN([(michel, likes, pizza, g1.get_context("urn:a"))])

    assert g2.store == g2.get_context("urn:a").store

    assert (
        repr(list(g1.contexts())[0])
        == "<Graph identifier=urn:a (<class 'rdflib.graph.Graph'>)>"
    )

    assert list(list(g1.contexts())[0]) == [
        (URIRef("urn:tarek"), URIRef("urn:likes"), URIRef("urn:cheese"))
    ]

    assert list(g1.get_context("urn:a")) == [
        (
            URIRef("urn:tarek"),
            URIRef("urn:likes"),
            URIRef("urn:cheese"),
        )
    ]
