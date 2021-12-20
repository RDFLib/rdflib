import pytest
import os
import sys
import shutil
from tempfile import gettempdir
import warnings
from pprint import pformat
from rdflib import logger, Literal, ConjunctiveGraph, Graph, Dataset, RDFS, SDO, URIRef
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


@pytest.mark.skip
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
    assert repr(ctx) == "<Graph identifier=urn:a (<class 'rdflib.graph.Graph'>)>"

    ctx = list(list(g1.contexts())[0])
    assert (
        repr(ctx)
        == "[(rdflib.term.URIRef('urn:tarek'), rdflib.term.URIRef('urn:likes'), rdflib.term.URIRef('urn:pizza'))]"
    )

    ctx = list(g1.get_context("urn:a"))
    assert (
        repr(ctx)
        == "[(rdflib.term.URIRef('urn:tarek'), rdflib.term.URIRef('urn:likes'), rdflib.term.URIRef('urn:pizza'))]"
    )
    # [(rdflib.term.URIRef('urn:tarek'), rdflib.term.URIRef('urn:likes'), rdflib.term.URIRef('urn:pizza'))]


@pytest.mark.skip
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

    # Incorrect, should not be empty
    assert list(graph) == []


@pytest.mark.skip
def test_issue353_nquads_default_graph(get_conjunctivegraph):

    # STATUS: FIXME remains an issue

    data = """
    <http://example.org/s1> <http://example.org/p1> <http://example.org/o1> .
    <http://example.org/s2> <http://example.org/p2> <http://example.org/o2> .
    <http://example.org/s3> <http://example.org/p3> <http://example.org/o3> <http://example.org/g3> .
    """
    publicID = URIRef("http://example.org/g0")

    cg = get_conjunctivegraph
    cg.parse(data=data, format="nquads", publicID=publicID)

    with pytest.raises(AssertionError):
        assert len([q for q in cg.quads((None, None, None, None))]) == 2
        warnings.warn(
            "test_dataset_anomalies::test_issue353_nquads_default_graph - Should only be 2 quads in default graph but all three are returned"
        )


@pytest.mark.skip
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
    graphs to exist, and allows the store t o contain triples in graphs that do
    not exist. This extra knowledge must be stored somewhere. The CG doesn't
    have this problem as it simply exposes the quads saved in the store.
    """

    ds = get_dataset
    assert len(list(ds.contexts())) == 1

    ds.parse(data="<a> <b> <c> .", format="ttl")
    with pytest.raises(AssertionError):
        assert len(list(ds.contexts())) == 1
        warnings.warn(
            "test_issue319_add_graph_as_dataset_default, length of dataset contexts should be "
        )


@pytest.mark.skip
def test_issue319_add_graph_as_conjunctivegraph_default(get_conjunctivegraph):

    # STATUS: FIXME remains an issue

    cg = get_conjunctivegraph
    assert len(list(cg.contexts())) == 0

    cg.parse(data="<a> <b> <c>.", format="turtle")
    assert len(list(cg.contexts())) == 1


@pytest.mark.skip
def test_issue811_using_from_and_from_named_on_conjunctivegraph_behaves_not_standard_conform(
    get_conjunctivegraph,
):
    # STATUS: FIXME remains an issue
    """
    I want to use `FROM` and `FROM NAMED` in a SPARQL query to select the default
    graph resp. named graphs to execute the query on. But the RDFlib
    implementation does not act as it is described in the SPARQL 1.1
    specification especially the section "13.2 Specifying RDF Datasets"
    (https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#specifyingDataset)

    To demonstrate this behavior, I've created an MWE:

    ```
    #!/usr/bin/env python3

    import rdflib.plugins.sparql
    from rdflib import ConjunctiveGraph

    data = '''
    <urn:a> <urn:a> <urn:a> <urn:a> .
    <urn:b> <urn:b> <urn:b> <urn:b> .
    <urn:c> <urn:c> <urn:c> <urn:c> .
    '''

    if __name__ == "__main__":
        rdflib.plugins.sparql.SPARQL_DEFAULT_GRAPH_UNION = False  # Line A
        rdflib.plugins.sparql.SPARQL_LOAD_GRAPHS = False
        graph = ConjunctiveGraph()
        graph.parse(data=data, format='nquads')
        result = graph.query("SELECT * {?s ?p ?o}")               # Line B
        for resrow in result:
            print(resrow)
    ```

    Running this code behaves as expected, while I will show derived examples in
    the following, by altering Line A and Line B:

    **1. Replacing the Default Graph**

        rdflib.plugins.sparql.SPARQL_DEFAULT_GRAPH_UNION = True       # Line A
        result = graph.query("SELECT * FROM <urn:b> {?s ?p ?o}")      # Line B

    - What I see: returns all three statements.
    - What I expect: Only the statement `<urn:b> <urn:b> <urn:b>` as result
    - Why is the actual result not correct?:

    > A SPARQL query may specify the dataset to be used for matching by using the
      FROM clause and the FROM NAMED clause to describe the RDF dataset. If a
      query provides such a dataset description, then it is used in place of any
      dataset that the query service would use if no dataset description is
      provided in a query.

    > (https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#specifyingDataset)

    **2. Specifying a Named Graph but Querying the Default Gaph**

        rdflib.plugins.sparql.SPARQL_DEFAULT_GRAPH_UNION = True         # Line A
        result = graph.query("SELECT * FROM NAMED <urn:b> { ?s ?p ?o}") # Line B

    - What I see: returns all three statements.
    - What I expect: no result
    - Why is the actual result not correct?:

    > If there is no FROM clause, but there is one or more FROM NAMED clauses,
      then the dataset includes an empty graph for the default graph.

    > (https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#specifyingDataset)


    **3. Specifying a Named Graph**

        rdflib.plugins.sparql.SPARQL_DEFAULT_GRAPH_UNION = False                   # Line A
        result = graph.query("SELECT * FROM NAMED <urn:b> { GRAPH ?g {?s ?p ?o}}") # Line B

    - What I see: returns all three statements.
    - What I expect: Only the statement `<urn:b> <urn:b> <urn:b> <urn:b>` as result
    - Why is the actual result not correct?: Because this is the idea of `NAMED
      GRAPH` to specify a named graph to query.

    > A query can supply IRIs for the named graphs in the RDF Dataset using the
      FROM NAMED clause. Each IRI is used to provide one named graph in the RDF
      Dataset.

    > (https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#specifyingDataset)

    Because I think all of these three cases are related to each other I've put
    them into one issue, but sure they could also be split into three issues.

    """

    import rdflib.plugins.sparql

    data = """
    <urn:a> <urn:a> <urn:a> <urn:a> .
    <urn:b> <urn:b> <urn:b> <urn:b> .
    <urn:c> <urn:c> <urn:c> <urn:c> .
    """

    rdflib.plugins.sparql.SPARQL_DEFAULT_GRAPH_UNION = False  # Line A
    rdflib.plugins.sparql.SPARQL_LOAD_GRAPHS = False

    graph = get_conjunctivegraph
    graph.parse(data=data, format="nquads")
    assert len(graph) > 0
    # logger.debug(f"graph: {graph.serialize(format='trig')}")

    results = graph.query("SELECT * {?s ?p ?o .}")  # Line B
    assert len(results) == 0

    # Set default graph as UNION, INCORRECT resulta
    rdflib.plugins.sparql.SPARQL_DEFAULT_GRAPH_UNION = True  # Line A

    results = graph.query("SELECT * {?s ?p ?o .}")  # Line B
    assert len(results) == 3

    results = graph.query("SELECT * FROM <urn:b> {?s ?p ?o}")  # Line B
    assert len(results) == 3, "should be 1 triple"
    # logger.debug(f"results:\n\n{pformat(list(results), width=120)}")

    # Set default graph as NON-UNION, CORRECT resulta
    rdflib.plugins.sparql.SPARQL_DEFAULT_GRAPH_UNION = False  # Line A
    results = graph.query("SELECT * FROM <urn:b> {?s ?p ?o}")  # Line B
    assert len(results) == 1, "should be one triple"

    # logger.debug(f"results:\n\n{pformat(list(results), width=120)}")


@pytest.mark.skip
def test_issue371_default_parse_fails():
    # g1 = Graph(store="SPARQLUpdateStore", identifier=DATASET_DEFAULT_GRAPH_ID)

    g = Graph(store="SPARQLUpdateStore")
    g.open(configuration="http://localhost:3030/db/update")
    with pytest.raises(Exception):
        g.parse(data="""<urn:tarek> <urn:likes> <urn:michel> .""", format="turtle")
    """
    rdflib/graph.py:430: in add
        self.__store.add((s, p, o), self.identifier, quoted=False)
            o          = rdflib.term.URIRef('urn:michel')
            p          = rdflib.term.URIRef('urn:likes')
            s          = rdflib.term.URIRef('urn:tarek')
            self       = <Graph identifier=Ne40ad6edbf2d4e77b455e93e4afc247f (<class 'rdflib.graph.Graph'>)>
            triple     = (rdflib.term.URIRef('urn:tarek'), rdflib.term.URIRef('urn:likes'), rdflib.term.URIRef('urn:michel'))
    rdflib/plugins/stores/sparqlstore.py:632: in add
        q = "INSERT DATA { GRAPH %s { %s } }" % (nts(context), triple)
            context    = rdflib.term.BNode('Ne40ad6edbf2d4e77b455e93e4afc247f')
            nts        = <function _node_to_sparql at 0x7f7e647d90d0>
            obj        = rdflib.term.URIRef('urn:michel')
            predicate  = rdflib.term.URIRef('urn:likes')
            quoted     = False
            self       = <rdflib.plugins.stores.sparqlstore.SPARQdef test_issue371_validation_of_quads_at_graph_addn_doesnt_work_as_expected():LUpdateStore object at 0x7f7e647a91f0>
            spo        = (rdflib.term.URIRef('urn:tarek'), rdflib.term.URIRef('urn:likes'), rdflib.term.URIRef('urn:michel'))
            subject    = rdflib.term.URIRef('urn:tarek')
            triple     = '<urn:tarek> <urn:likes> <urn:michel> .'
    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

    node = rdflib.term.BNode('Ne40ad6edbf2d4e77b455e93e4afc247f')

        def _node_to_sparql(node) -> str:
            if isinstance(node, BNode):
    >           raise Exception(
                    "SPARQLStore does not support BNodes! "
                    "See http://www.w3.org/TR/sparql11-query/#BGPsparqlBNodes"
                )
    E           Exception: SPARQLStore does not support BNodes! See http://www.w3.org/TR/sparql11-query/#BGPsparqlBNodes

    node       = rdflib.term.BNode('Ne40ad6edbf2d4e77b455e93e4afc247f')

    rdflib/plugins/stores/sparqlstore.py:33: Exception
    """


@pytest.mark.skip
def test_issue371_default_add_fails():
    g = Graph(store="SPARQLUpdateStore")
    g.open(configuration="http://localhost:3030/db/update")
    with pytest.raises(Exception):
        g.add((tarek, likes, pizza))
    """
    rdflib/graph.py:430: in add
        self.__store.add((s, p, o), self.identifier, quoted=False)
            o          = rdflib.term.URIRef('urn:pizza')
            p          = rdflib.term.URIRef('urn:likes')
            s          = rdflib.term.URIRef('urn:tarek')
            self       = <Graph identifier=Nbd8634401091472eacd82cc48a827ad2 (<class 'rdflib.graph.Graph'>)>
            triple     = (rdflib.term.URIRef('urn:tarek'), rdflib.term.URIRef('urn:likes'), rdflib.term.URIRef('urn:pizza'))
    rdflib/plugins/stores/sparqlstore.py:632: in add
        q = "INSERT DATA { GRAPH %s { %s } }" % (nts(context), triple)
            context    = rdflib.term.BNode('Nbd8634401091472eacd82cc48a827ad2')
            nts        = <function _node_to_sparql at 0x7f2879ea4700>
            obj        = rdflib.term.URIRef('urn:pizza')
            predicate  = rdflib.term.URIRef('urn:likes')
            quoted     = False
            self       = <rdflib.plugins.stores.sparqlstore.SPARQLUpdateStore object at 0x7f2879ec4fd0>
            spo        = (rdflib.term.URIRef('urn:tarek'), rdflib.term.URIRef('urn:likes'), rdflib.term.URIRef('urn:pizza'))
            subject    = rdflib.term.URIRef('urn:tarek')
            triple     = '<urn:tarek> <urn:likes> <urn:pizza> .'
    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

    node = rdflib.term.BNode('Nbd8634401091472eacd82cc48a827ad2')

        def _node_to_sparql(node) -> str:
            if isinstance(node, BNode):
    >           raise Exception(
                    "SPARQLStore does not support BNodes! "
                    "See http://www.w3.org/TR/sparql11-query/#BGPsparqlBNodes"
                )
    E           Exception: SPARQLStore does not support BNodes! See http://www.w3.org/TR/sparql11-query/#BGPsparqlBNodes

    node       = rdflib.term.BNode('Nbd8634401091472eacd82cc48a827ad2')
    """


def get_graphnames():
    g = Graph(store="SPARQLStore")
    g.open(configuration="http://localhost:3030/db/sparql")
    res = g.query("SELECT DISTINCT ?NAME { GRAPH ?NAME { ?s ?p ?o } }")
    return res


@pytest.mark.skip
def test_issue371_graph_name_doesnt_match_specified_identifier():
    sg = Graph(store="SPARQLUpdateStore", identifier=URIRef("context-0"))
    sg.open(configuration="http://localhost:3030/db/update")
    sg.parse(data="""<urn:tarek> <urn:likes> <urn:michel> .""", format="turtle")

    assert sg.identifier == URIRef("context-0")

    graphnames = list(get_graphnames())
    assert sg.identifier != graphnames[0][0]

    # qg = Graph(store="SPARQLStore", identifier=URIRef("context-0"))
    qg = Graph(
        store="SPARQLStore",
        # identifier=URIRef("context-0"),
        identifier=URIRef("http://server/unset-base/context-0"),
    )
    qg.open(configuration="http://localhost:3030/db/sparql")
    res = qg.query("SELECT * {{?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }} LIMIT 25")

    assert len(list(res)) == 1

    graphnames = list(get_graphnames())
    assert graphnames[0][0] == URIRef("http://server/unset-base/context-0")

    sg.update("CLEAR ALL")


@pytest.mark.skip
def test_issue371_validation_of_quads_at_graph_addn_doesnt_work_as_expected():
    """
    I've found that `Graph.addN()` method with `SPARQLUpdateStore` doesn't work as
    expected. A quad is a set of subject, predicate, object and context and,
    according to the spec [1], context should be an IRI. But as I see from the
    code [2], context should be an instance of the Graph which is wrong.

    So if we set context as a URIRef `Graph.addN()` ignores the quad and if we set
    context as an instance of the Graph then it sends a malformed query:

    INSERT DATA {
        GRAPH <[a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'SPARQLUpdateStore']].>
        {
            <http://example.com/resource/1>
            <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>
            <http://xmlns.com/foaf/0.1/Agent> .
        }
    }

    [1] https://www.w3.org/TR/sparql11-query
    [2] https://github.com/RDFLib/rdflib/blob/eaa353fe7c403c81a519991b87fc71a7ee7b436a/rdflib/graph.py#L432

    """

    sg = ConjunctiveGraph(
        store="SPARQLUpdateStore", identifier=DATASET_DEFAULT_GRAPH_ID
    )
    sg.open(configuration="http://localhost:3030/db/update")

    sg.parse(data="""<urn:tarek> <urn:likes> <urn:michel> .""", format="turtle")

    sg.add((tarek, likes, pizza))
    sg.add((tarek, likes, cheese))

    # sg.addN(list_of_nquads)

    # res = get_graphnames()
    # logger.debug(f"\n\n{pformat(list(res))}")

    sg.update("CLEAR ALL")


@pytest.mark.skip
def test_issue1277_clear_named(get_conjunctivegraph):
    """Test @base directive with no slash after colon."""
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

    # Fails:
    #     raise ParseException(instring, loc, self.errmsg, self)
    #     E   pyparsing.ParseException: Expected end of text, found 'C'
    #         (at char 0), (line:1, col:1)

    import pyparsing

    with pytest.raises(pyparsing.ParseException):
        graph.update(
            r"CLEAR GRAPH ?g", initBindings={"g": URIRef("https://example.org")}
        )

    # assert not list(graph)  # should be successful
