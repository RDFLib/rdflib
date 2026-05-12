from rdflib.void import generateVoID
from rdflib import Graph, URIRef


data = (
    "@prefix void: <http://rdfs.org/ns/void#> .\n"
    "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
    "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
    "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
    "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
    "@prefix dcterms: <http://purl.org/dc/terms/> .\n"
    "@prefix foaf: <http://xmlns.com/foaf/0.1/> .\n"
    "@prefix wv: <http://vocab.org/waiver/terms/norms> .        \n"
    "@prefix sd: <http://www.w3.org/ns/sparql-service-description#> .\n"
    "@prefix : <#> .\n"
    "\n"
    ":DBpedia a void:Dataset;\n"
    '    dcterms:title "DBPedia";\n'
    '    dcterms:description "RDF data extracted from Wikipedia";\n'
    "    dcterms:contributor :FU_Berlin;\n"
    "    dcterms:contributor :University_Leipzig;\n"
    "    dcterms:contributor :OpenLink_Software;\n"
    "    dcterms:contributor :DBpedia_community;\n"
    "    dcterms:source <http://dbpedia.org/resource/Wikipedia>;\n"
    '    dcterms:modified "2008-11-17"^^xsd:date;\n'
    "    .\n"
    ":FU_Berlin a foaf:Organization;\n"
    '    rdfs:label "Freie Universität Berlin";\n'
    "    foaf:homepage <http://www.fu-berlin.de/>;\n"
    "    .\n"
)

dataset = URIRef("http://dbpedia.org")
res = Graph(identifier=URIRef("urn:example:voidresults"))
g = Graph().parse(data=data, format="n3")


def test_generatevoid_distinct():

    _res, _ds = generateVoID(g, dataset, res)

    assert isinstance(_res, Graph)


def test_generatevoid_indistinct():

    _res, _ds = generateVoID(g, dataset, res, distinctForPartitions=False)

    assert isinstance(_res, Graph)


def test_generatevoid_nodataset():

    _res, _ds = generateVoID(g, res)

    assert isinstance(_res, Graph)


def test_generatevoid_nores():

    _res, _ds = generateVoID(g)

    assert isinstance(_res, Graph)
