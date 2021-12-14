import pytest
import os
import sys
import shutil
from tempfile import gettempdir
from pprint import pformat
from rdflib import logger, Literal, ConjunctiveGraph, Graph, Dataset, URIRef
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID

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
def test_firstreport():

    # STATUS: FIXME Remains an issue

    from rdflib import Dataset, URIRef

    d = Dataset()
    g = d.parse(data="<a:a> <b:b> <c:c> .", format="turtle", publicID=URIRef("g:g"))
    logger.debug("After parse:")
    for h in d.graphs():
        logger.debug(f"\n{pformat(h, width=120)}")
    if g.identifier not in d.graphs():
        logger.debug("g has not been added to Dataset")


# @pytest.mark.skip
def test__issue_713_query_on_ds_yields_no_results():

    # STATUS: FIXME Remains an issue

    data = """
    <http://data.yyx.me/jack> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_a> .
    <http://data.yyx.me/david> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_b> .
    """

    ds = Dataset()
    g = Graph(identifier="subgraph")
    g.parse(data=data, format="n3")
    ds.add_graph(g)

    # yields 0 results from this query
    assert (
        len(list(ds.query("""SELECT ?s ?p ?o WHERE {GRAPH <subgraph> { ?s ?p ?o }}""")))
        == 0  # noqa: W503
    )

    # yields 2 results from this query
    # assert (
    #     len(list(ds.query("""SELECT ?g ?s ?p ?o WHERE { GRAPH ?g { ?s ?p ?o }}""")))
    #     == 2  # noqa: W503
    # )

    # FIXME: no, it doesn't, it yields 0
    assert (
        len(list(ds.query("""SELECT ?g ?s ?p ?o WHERE { GRAPH ?g { ?s ?p ?o }}""")))
        == 0  # noqa: W503
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
    logger.debug(f"""len(d) {len(d)}""")
    logger.debug(f"""{i_new} {i_trad}""")


@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test__issue_758_sparqlstore_is_incorrectly_readonly(get_dataset):

    # STATUS: FIXME Remains an issue

    #  Cannot enumerate dataset graphs #758

    dataset = Dataset(store="SPARQLStore")

    dataset.open("http://localhost:3030/db/query")

    # Incorrectly raises TypeError: SPARQL Store is read only
    try:
        for g in dataset.graphs():
            print(g)
    except TypeError as e:
        assert repr(e) == """TypeError('The SPARQL store is read only')"""


# @pytest.mark.skip
def test_issue939_parse_return_inconsistent_type():

    # STATUS: FIXED Not an issue

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
    g = ConjunctiveGraph()

    g.parse(data=test_ttl, format="turtle")
    assert type(g) is ConjunctiveGraph  # <class 'rdflib.graph.ConjunctiveGraph'>

    g = ConjunctiveGraph()
    x = g.parse(data=test_ttl, format="turtle")

    # The reported would like x to be the ConjunctiveGraph or that type
    assert type(x) is ConjunctiveGraph


# @pytest.mark.skip
def test_issue167_clarify_context_element_needs_final_clarification(
    get_conjunctivegraph,
):

    #  Clarify confusion around type of context element in ConjunctiveGraphs and context aware stores #167

    # gromgull, 2011-08-20T07:58:07.000Z

    # In the ConjunctiveGraph, the context field is assumed to be a graph
    # with the identifier set to the URI of the context, i.e. this is what
    # happens if you create context like this:

    # g = ConjunctiveGraph()
    # uri1 = URIRef("http://example.org/mygraph1")
    # uri2 = URIRef("http://example.org/mygraph2")

    # bob = URIRef(u'urn:bob')
    # likes = URIRef(u'urn:likes')
    # pizza = URIRef(u'urn:pizza')

    # g.get_context(uri1).add((bob, likes, pizza))
    # g.get_context(uri2).add((bob, likes, pizza))

    # Now g.contexts() returns a generator over some graphs.

    # Now, for code working on the store level, i.e. serializers and parsers,
    # there should perhaps not be any graph objects?

    # I came across this when looking at the nquad parser, here:

    # https://github.com/RDFLib/rdflib/blob/master/rdflib/plugins/parsers/nquads.py#L106

    # This adds context as simply an URI ref.

    # I added a "work-around" to make the conjunctivegraph.contexts generator work "correctly" here:

    # I've semi-fixed this in the last two commits.

    # If you work with the ConjunctiveGraph class directly:

    # g = ConjunctiveGraph()
    # g.get_context('urn:1').add( ( s, p, o ) )

    # You end up with a Graph object in the store, with identifier set
    # to the URIRef "urn:1".

    # I dont know saving the whole graph+store in the store is the best
    # way to do it, saving just the identifier seems much cleaner.

    # AND - I can now mix and match stores in one ConjunctiveGraph
    # - I am not even sure what this could mean:

    g = get_conjunctivegraph

    g.get_context(c1).add((bob, likes, pizza))
    g.get_context(c2).add((bob, likes, pizza))

    g1 = ConjunctiveGraph()
    g2 = ConjunctiveGraph()

    g1.get_context("urn:a").add((tarek, likes, pizza))

    g2.addN([(bob, likes, cheese, g1.get_context("urn:a"))])

    # assert g2.store != g2.get_context("urn:a").store
    # OLD: True
    # NEW: False

    assert g2.store == g2.get_context("urn:a").store

    # Hmm ...

    # In [43]: list(g1.contexts())[0]
    # Out[43]: <Graph identifier=urn:a (<class 'rdflib.graph.Graph'>)>

    # In [44]: list(list(g1.contexts())[0])
    # Out[44]:
    # [(rdflib.term.BNode('Nae2ff5ac0056427e852347e0a58ff925'),
    #   rdflib.term.BNode('N7c8cbd571a51409e8a92c2870a30eddd'),
    #   rdflib.term.BNode('Nbc486ecd9a5b46d5913dafdc4458fc3f'))]

    # In [45]: list(g1.get_context('urn:a'))
    # Out[45]:
    # [(rdflib.term.URIRef(u'a'),
    #   rdflib.term.URIRef(u'b'),
    #   rdflib.term.URIRef(u'c'))]

    # This is no good :)

    # *********** What was Gromgull expecting? ******************

    ctx = list(g1.contexts())[0]
    logger.debug(f"cj contexts\n{ctx}")
    # OLD <Graph identifier=urn:a (<class 'rdflib.graph.Graph'>)>
    # NEW <urn:a> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'Memory'].

    ctx = list(list(g1.contexts())[0])
    logger.debug(f"cj contexts\n{ctx}")
    # OLD [(rdflib.term.BNode('Nae2ff5ac0056427e852347e0a58ff925'), rdflib.term.BNode('N7c8cbd571a51409e8a92c2870a30eddd'), rdflib.term.BNode('Nbc486ecd9a5b46d5913dafdc4458fc3f'))]
    # NEW [(rdflib.term.URIRef('urn:tarek'), rdflib.term.URIRef('urn:likes'), rdflib.term.URIRef('urn:pizza'))]

    ctx = list(g1.get_context("urn:a"))
    logger.debug(f"cj contexts\n{ctx}")
    # [(rdflib.term.URIRef('urn:tarek'), rdflib.term.URIRef('urn:likes'), rdflib.term.URIRef('urn:pizza'))]


# @pytest.mark.skip
def test_issue_167_sparqlupdatestore_compatibility(get_dataset):

    # STATUS: FIXED no longer an issue

    # https://github.com/RDFLib/rdflib/issues/167#issuecomment-873620457

    # Note that this is also observed when using Dataset instances. In particular,

    from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

    ds = Dataset()
    for quad in list_of_nquads:
        ds.add(quad)
    quads = ds.quads((None, None, None, None))  # Fourth term is identifier

    store = SPARQLUpdateStore()
    store.open("http://localhost:3030/db/update")
    store.addN(quads)  # Expects four term to be graph

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
def test_issue1275_clear_default(get_conjunctivegraph):

    # STATUS: FIXME Remains an issue

    #  CLEAR DEFAULT statement erases named graphs #1275
    # DEFAULT graph is the default unnamed graph, so the triple we store
    # in the named graph before should not be removed, but it apparently is.

    from rdflib.namespace import SDO, RDFS

    graph = get_conjunctivegraph

    graph.add(
        (
            SDO.title,
            RDFS.subPropertyOf,
            RDFS.label,
            URIRef("https://example.org"),
        )
    )

    assert list(graph)

    graph.update("CLEAR DEFAULT")

    logger.debug(f"list(graph)\n{pformat(list(graph), width=80)}")

    # assert list(graph)  # Here is where the test fails


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

    for n, k in [
        ("json-ld", "jsonld"),
        ("nquads", "nq"),
        ("trix", "trix"),
        ("trig", "trig"),
    ]:
        logger.debug(f"{k}\n{ds.serialize(format=n)}")

    # Output is conformant and as expected

    logger.debug(f"trig\n{ds.serialize(format='trig')}")

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

    logger.debug(f"trig\n{ds.serialize(format='trig')}")

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
    #  trig export of multiple graphs assigns wrong prefixes to prefixedNames #679

    # I wanted to add that I see this behavior even in the case of parsing a dataset
    # with a single graph in nquads format and serializing as trig with no special characters.

    # STATUS: FIXED? no longer an issue

    ds = get_dataset
    ds.parse(data=nquads, format="nquads")
    logger.debug(f"trig\n{ds.serialize(format='trig')}")


# @pytest.mark.skip
def test_cg_parse_of_datasets_with_default_graph(get_conjunctivegraph):

    # STATUS: FIXME remains an issue

    cg = get_conjunctivegraph
    cg.parse(
        format="nquads",
        data="""
    <http://example.org/a> <http://example.org/ns#label> "A" .
    <http://example.org/b> <http://example.org/ns#label> "B" <http://example.org/b/> .
    """,
    )

    # assert len(cg.default_context) == 1  # fails
    assert len(cg.default_context) == 0  # incorrectly passes

    logger.debug(f"trig\n{cg.serialize(format='trig')}")

    # @prefix ns1: <http://example.org/ns#> .

    # <http://example.org/b/> {
    #     <http://example.org/b> ns1:label "B" .
    # }

    # {
    #     <http://example.org/a> ns1:label "A" .
    # }


# @pytest.mark.skip
def test_issue353_nquads_default_graph(get_conjunctivegraph):

    # STATUS: FIXME remains an issue

    cg = get_conjunctivegraph

    data = """
    <http://example.org/s1> <http://example.org/p1> <http://example.org/o1> .
    <http://example.org/s2> <http://example.org/p2> <http://example.org/o2> .
    <http://example.org/s3> <http://example.org/p3> <http://example.org/o3> <http://example.org/g3> .
    """

    publicID = URIRef("http://example.org/g0")

    cg.parse(data=data, format="nquads", publicID=publicID)

    quads = [q for q in cg.quads((None, None, None, None))]

    # Should only be 2 quads in default graph but all three are returned

    # assert len(quads) == 2  # incorrectly fails
    assert len(quads) == 3  # incorrectly passes

    logger.debug(f"quads\n{pformat(quads, width=80)}")

    logger.debug(f"nquads_default\n{cg.serialize(format='nquads')}")

    assert len(cg) == 3, len(cg)
    assert len(list(cg.contexts())) == 2, len(list(cg.contexts()))
    assert len(cg.get_context(publicID)) == 2, len(cg.get_context(publicID))


# @pytest.mark.skip
def test_ds_capable_parse(get_dataset):

    # STATUS: FIXED no longer an issue

    ds = get_dataset
    trigfile = os.path.join(os.path.dirname(__file__), "nquads.rdflib", "test7.trig")
    ds.parse(location=trigfile)  # RDF file type worked out by guess_format()
    logger.debug(f"trig\n{ds.serialize(format='trig')}")


# @pytest.mark.skip
def test_issue_698_len_ds():
    """

    # STATUS: FIXME remains an issue

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
    assert len(ds) == 0  # incorrect, should be 631


# @pytest.mark.skip
def test_issue_301_dataset_does_not_parse(get_dataset):

    # STATUS: FIXED no longer an issue

    from rdflib import URIRef

    d = get_dataset

    g = d.parse(data="<a:a> <b:b> <c:c> .", format="turtle", publicID=URIRef("g:g"))

    logger.debug("After parse:")
    for h in d.contexts():
        logger.debug(h)
    if g not in d.contexts():
        logger.debug("g not in contexts")
    for h in d.contexts():
        logger.debug(h in d.contexts())


# @pytest.mark.skip
def test_issue319_add_graph_as_dataset_default(get_dataset):

    # STATUS: FIXME remains an issue

    """
    Given a Graph, can it be used as default graph for a Dataset? #319

    # uholzer ...

    # Imagine, you are given a Graph, maybe created with Graph() or maybe
    # backed by some arbitrary store. Maybe, for some reason you need a
    # Dataset and you want your Graph to be the default graph of this
    # Dataset. The Dataset should not and will not need to contain any other
    # graphs.

    # Is there a straightforward way to achieve this without copying all
    # triples? As far as I know, Dataset needs a context_aware and
    # graph_aware store, so it is not possible to just create a Dataset
    # backed by the same store. Graham Klyne is interested in this because he
    # wants to provide a SPARQL endpoint for a given rdflib.Graph, but my
    # implementation of a SPARQL endpoint requires a Dataset. I don't really
    # like to implement support for plain graphs, so I wonder whether there
    # is a simple solution.

    # Also, I wonder whether it would be useful to have a true union of
    # several graphs backed by different stores.

    # uholzer ...
    # There is a discrepancy between Graph and Dataset (note that the parsed
    # triple is missing from the Dataset serialization):
    #
    # It is clear to me why this happens. ConjunctiveGraph parses into a fresh
    # graph and Dataset inherits this behaviour. For ConjunctiveGraphs one does
    # not observe the above, because the default is the union and hence contains
    # the fresh graph.


    gromgull ...
    Am I right in assuming that the only bit missing of this is that if you
    parse some context-aware rdf format into a dataset, and your input file
    contains several graphs, they may not all appear? If so, we should close
    and make a new issue for that. With less comments :)


    gromgull ...
    The biggest problem I see is that the dataset has no way of persisting the
    list of graphs that exist. The dataset as implemented now both allows empty
    graphs to exist, and allows the store to contain triples in graphs that do
    not exist. This extra knowledge must be stored somewhere. The CG doesn't
    have this problem as it simply exposes the quads saved in the store.
    """

    ds = get_dataset

    logger.debug(f"\n####### contexts on initialisation: {list(ds.contexts())}")

    ds.parse(data="<a> <b> <c>.", format="turtle")

    logger.debug(f"\n####### contexts after parse: {list(ds.contexts())}")

    logger.debug(ds.serialize(format="turtle"))

    logger.debug(f"quads:\n{list(ds.quads((None, None, None, None)))}")

    for c in ds.contexts():
        logger.debug(f"\n>>>>> {c.identifier}:\n{c.serialize(format='xml')}")

    # default_graph = ds.get_context(URIRef("urn:x-rdflib:default"))
    # logger.debug(f"default_graph: {default_graph}")

    # [a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'IOMemory']].
    # <urn:x-rdflib:default> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'IOMemory'].


# @pytest.mark.skip
def test_issue319_add_graph_as_conjunctivegraph_default(get_conjunctivegraph):

    # STATUS: FIXME remains an issue

    cg = get_conjunctivegraph
    cg.parse(data="<a> <b> <c>.", format="turtle")
    logger.debug(cg.serialize(format="turtle"))

    logger.debug(f"len ds contexts {len(list(cg.contexts()))}")
    for c in cg.contexts():
        logger.debug(f"c {c.identifier}")

    # [a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'IOMemory']].
    # <urn:x-rdflib:default> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'IOMemory'].
