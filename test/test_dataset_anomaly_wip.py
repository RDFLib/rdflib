import pytest
import os
from pprint import pformat
from rdflib import (
    logger,
    BNode,
    Graph,
    ConjunctiveGraph,
    Dataset,
    Literal,
    Namespace,
    OWL,
    URIRef,
)
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID


timblcardn3 = open(
    os.path.join(os.path.dirname(__file__), "consistent_test_data", "timbl-card.n3")
).read()


sportquadsnq = open(
    os.path.join(os.path.dirname(__file__), "consistent_test_data", "sportquads.nq")
).read()


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

michel = URIRef("urn:michel")
tarek = URIRef("urn:tarek")
bob = URIRef("urn:bob")
likes = URIRef("urn:likes")
hates = URIRef("urn:hates")
pizza = URIRef("urn:pizza")
cheese = URIRef("urn:cheese")

c1 = URIRef("urn:context-1")
c2 = URIRef("urn:context-2")


# # INCLUDED FROM ELSEWEHERE BUT KEEP FOR A DIFFERENT TEST CONEXT
# # Graph.subjects and Graph.predicates should return only unique values
# @pytest.mark.skip
# def test_issue837_return_uniques_memory():
#     mgraph = Graph()

#     mgraph.parse(data=timblcardn3, format="n3")
#     g = mgraph.skolemize()
#     assert len(list(g.subjects())) > 0
#     triples = list(g.triples((None, None, None)))

#     sgraph = Graph(store="SPARQLUpdateStore", identifier=URIRef("context0"))
#     sgraph.open(configuration="http://localhost:3030/db/update")
#     for triple in triples:
#         sgraph.add(triple)

#     qgraph = Graph(
#         store="SPARQLStore", identifier=URIRef("http://server/unset-base/context0")
#     )
#     qgraph.open(configuration="http://localhost:3030/db/sparql")
#     logger.debug(f"{pformat(list(qgraph.subjects(unique=True)))}")

# # NOT RELEVANT JUST YET
# @pytest.mark.skip
# def test_dataset_default_graph_and_contexts_with_namespace_bound():
#     ds = Dataset()

#     # ADD ONE TRIPLE *without context* to the default graph

#     # ds.bind("", "urn:", True)
#     ds.add((tarek, likes, pizza))

#     logger.debug(f"\n\nTRIG serialization\n{ds.serialize(format='trig')}")

#     # logger.debug(f"\n\nTRIG serialization\n{repr(ds.serialize(format='trig'))}")

#     # assert repr(ds.serialize(format="trig")) == repr(
#     #     "@prefix ns1: <urn:> .\n"
#     #     "\n"
#     #     "ns1:default {\n"
#     #     "    ns1:tarek ns1:likes ns1:pizza .\n"
#     #     "}\n"
#     #     "\n"
#     # )

#     logger.debug(f"\n\nXML serialization\n{ds.serialize(format='trix')}")

#     # logger.debug(
#     #     f"\n\nXML serialization\n{repr(dataset_default_graph.serialize(format='xml'))}"
#     # )

#     # assert repr(dataset_default_graph.serialize(format="xml")) == repr(
#     #     '<?xml version="1.0" encoding="utf-8"?>\n'
#     #     "<rdf:RDF\n"
#     #     '   xmlns="urn:"\n'
#     #     '   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n'
#     #     ">\n"
#     #     '  <rdf:Description rdf:about="urn:tarek">\n'
#     #     '    <likes rdf:resource="urn:pizza"/>\n'
#     #     "  </rdf:Description>\n"
#     #     "</rdf:RDF>\n"
#     # )


# operator.ior(a, b)
# operator.__ior__(a, b)

#     a = ior(a, b) is equivalent to a |= b.


@pytest.mark.skip
def test_issue371_graph_name_doesnt_match_specified_identifier():

    # STATUS: FIXED no longer an issue

    from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

    # https://github.com/RDFLib/rdflib/issues/167#issuecomment-873620457

    # Note that this is also observed when using Dataset instances. In particular,

    store = SPARQLUpdateStore(
        query_endpoint="http://localhost:3030/db/sparql",
        update_endpoint="http://localhost:3030/db/update",
    )
    g = Graph(
        store=store,
        identifier=URIRef("urn:context-0"),
    )
    g.parse(data="""<urn:tarek> <urn:likes> <urn:michel> .""", format="turtle")

    assert g.identifier == URIRef("urn:context-0")

    res = g.query("SELECT * {{?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")

    lres = list(res)

    assert len(lres) == 1

    assert lres == [
        (URIRef("urn:tarek"), URIRef("urn:likes"), URIRef("urn:michel"), None)
    ]
    # logger.debug(f"res: {list(res)}")

    g.update("CLEAR ALL")

    res = g.query("SELECT * {{?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")

    # res = g.query("SELECT DISTINCT ?NAME { GRAPH ?NAME { ?s ?p ?o } }")

    assert len(list(res)) == 0


@pytest.mark.skip
def test_issue424_parse_insert_into_uri_queries_sparqlstore():

    # STATUS: FIXED no longer an issue

    from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

    # https://github.com/RDFLib/rdflib/issues/167#issuecomment-873620457

    # Note that this is also observed when using Dataset instances. In particular,

    store = SPARQLUpdateStore(
        query_endpoint="http://localhost:3030/db/sparql",
        update_endpoint="http://localhost:3030/db/update",
    )

    store.update(
        "INSERT INTO <urn:context-0> { <urn:tarek> <urn:likes> <urn:pizza> . } "
    )

    # INSERT INTO <urn:sparql:tests:insert:informative2>
    # {
    # <#book4> <http://purl.org/dc/elements/1.1/title> "SPARQL 1.0 Tutorial" .
    # }

    store.update(
        "INSERT DATA { GRAPH <urn:context-1> { <urn@tarek> <urn:likes> <urn:pizza> } }"
    )

    # PREFIX dc:  <http://purl.org/dc/elements/1.1/>
    # PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    # INSERT INTO <http://example/bookStore2>
    #  { ?book ?p ?v }
    # WHERE
    #   { GRAPH  <http://example/bookStore>
    #        { ?book dc:date ?date .
    #          FILTER ( ?date < "2000-01-01T00:00:00"^^xsd:dateTime )
    #          ?book ?p ?v
    #   } }

    # PREFIX dcterms: <http://purl.org/dc/terms/>

    # INSERT DATA {
    #     GRAPH <http://example/shelf_A> {
    #         <http://example/author> dcterms:name "author" .
    #         <http://example/book> dcterms:title "book" ;
    #         dcterms:author <http://example/author> .
    #     }
    # }


@pytest.mark.skip
def test_issue424_parse_insert_into_uri_queries_dataset():
    # OWL = Namespace("http://www.w3.org/2002/07/owl#")

    g = Graph()
    # g.namespace_manager.bind("owl", URIRef("http://www.w3.org/2002/07/owl#"))
    # g.namespace_manager.bind("xsd", URIRef("http://www.w3.org/2001/XMLSchema#"))

    qres = g.query(
        """
    PREFIX foaf:    <http://xmlns.com/foaf/0.1/>
    PREFIX dbpprop: <http://dbpedia.org/property/>

    SELECT ?place (AVG(?rain) as ?avgRain)
    WHERE{
      VALUES ?rainPred {
        dbpprop:janRainMm dbpprop:febRainMm dbpprop:marRainMm dbpprop:aprRainMm
        dbpprop:mayRainMm dbpprop:junRainMm dbpprop:julRainMm dbpprop:augRainMm
        dbpprop:sepRainMm dbpprop:octRainMm dbpprop:novRainMm dbpprop:decRainMm
      }
      SERVICE <https://dbpedia.org/sparql> {
         ?place ?rainPred ?rain .
      }
    }
    GROUP BY ?place
    HAVING (COUNT(?rain) = 12)
    ORDER BY ?avgRain
    """
    )

    for row in qres:
        logger.debug(f"row {row}")


@pytest.mark.skip
def test_issue802():
    from rdflib.extras.visualizegraph import visualize_graph

    turtle_1 = """

    @prefix ex: <http://www.ex.org/> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

    ex:a ex:x _:p1 , _:p2 .

    _:p1 ex:y ( _:i1 _:i2 _:i3 _:i4 ) .

    _:p2 ex:z _:p1 .

    """

    g1 = Graph()
    g1.parse(data=turtle_1, format="ttl")
    # logger.debug(f" len(g) {len(g1)}\n{g1.serialize(format='ttl')}")
    # visualize_graph(g1, "turtle1", shortMode=True, format1="jpg")

    g2 = Graph()
    g2.parse(data=g1.serialize(format="ttl"), format="ttl")
    # # logger.debug(f" len(g) {len(g2)}\n{g2.serialize(format='nt')}")
    visualize_graph(g2, "turtle2", shortMode=True, format1="jpg")


@pytest.mark.skip
def test_issue767_readonlygraphaggregate_aggregate_namespaces():
    import rdflib

    g = rdflib.Graph()

    h = rdflib.graph.ReadOnlyGraphAggregate([g])

    ns = rdflib.Namespace("http://example.org/")
    g.bind("ex", ns)
    # g.add((rdflib.Literal("fish"), rdflib.OWL.differentFrom, rdflib.Literal("bird")))
    g.add((URIRef(ns + "fish"), rdflib.OWL.differentFrom, URIRef(ns + "bird")))

    h = rdflib.graph.ReadOnlyGraphAggregate([g])

    # logger.debug(f"g:\n{pformat(sorted(list(g.namespaces())))}")
    assert len(list(g.namespaces())) == 28

    # logger.debug(f"g:\n{pformat(sorted(list(h.namespaces())))}")
    assert len(list(h.namespaces())) == 27


@pytest.mark.skip
def test_read_owl_in_rdfxml():
    g = Graph().parse(
        location="https://raw.githubusercontent.com/buildingSMART/ifcOWL/master/IFC2X3_Final.owl",
        format="xml",
    )
    logger.debug(f"ntriples {len(g)}")


@pytest.mark.skip
def test_foo():
    Graph().parse(
        data="<https://arche-curation.acdh-dev.oeaw.ac.at/api/8458> <https://vocabs.acdh.oeaw.ac.at/schema#hasIdentifier> <make\\u0020me> .",
        format="nt",
    )
