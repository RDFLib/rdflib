from rdflib import Dataset, URIRef

michel = URIRef("urn:example:michel")
tarek = URIRef("urn:example:tarek")
likes = URIRef("urn:example:likes")
pizza = URIRef("urn:example:pizza")


def test_dataset_default_graph_and_contexts_with_namespace_bound():

    ds = Dataset()

    ds.bind("", "urn:example:", True)

    # ADD ONE TRIPLE *without context* to the default graph
    ds.add((tarek, likes, pizza))

    assert (
        str(ds.serialize(format="trig"))
        == "@prefix : <urn:example:> .\n@prefix ns1: <urn:x-rdflib:> .\n\n"
        "{\n"
        "    :tarek :likes :pizza .\n"
        "}\n"
        "\n"
    )

    assert (
        str(ds.serialize(format="trix")) == '<?xml version="1.0" encoding="utf-8"?>\n'
        "<TriX\n"
        '  xmlns:brick="https://brickschema.org/schema/Brick#"\n'
        '  xmlns:csvw="http://www.w3.org/ns/csvw#"\n'
        '  xmlns:dc="http://purl.org/dc/elements/1.1/"\n'
        '  xmlns:dcat="http://www.w3.org/ns/dcat#"\n'
        '  xmlns:dcmitype="http://purl.org/dc/dcmitype/"\n'
        '  xmlns:dcterms="http://purl.org/dc/terms/"\n'
        '  xmlns:dcam="http://purl.org/dc/dcam/"\n'
        '  xmlns:doap="http://usefulinc.com/ns/doap#"\n'
        '  xmlns:foaf="http://xmlns.com/foaf/0.1/"\n'
        '  xmlns:odrl="http://www.w3.org/ns/odrl/2/"\n'
        '  xmlns:geo="http://www.opengis.net/ont/geosparql#"\n'
        '  xmlns:org="http://www.w3.org/ns/org#"\n'
        '  xmlns:owl="http://www.w3.org/2002/07/owl#"\n'
        '  xmlns:prof="http://www.w3.org/ns/dx/prof/"\n'
        '  xmlns:prov="http://www.w3.org/ns/prov#"\n'
        '  xmlns:qb="http://purl.org/linked-data/cube#"\n'
        '  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n'
        '  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"\n'
        '  xmlns:schema="https://schema.org/"\n'
        '  xmlns:sh="http://www.w3.org/ns/shacl#"\n'
        '  xmlns:skos="http://www.w3.org/2004/02/skos/core#"\n'
        '  xmlns:sosa="http://www.w3.org/ns/sosa/"\n'
        '  xmlns:ssn="http://www.w3.org/ns/ssn/"\n'
        '  xmlns:time="http://www.w3.org/2006/time#"\n'
        '  xmlns:vann="http://purl.org/vocab/vann/"\n'
        '  xmlns:void="http://rdfs.org/ns/void#"\n'
        '  xmlns:xsd="http://www.w3.org/2001/XMLSchema#"\n'
        '  xmlns:xml="http://www.w3.org/XML/1998/namespace"\n'
        '  xmlns:ns1="urn:x-rdflib:"\n'
        '  xmlns="http://www.w3.org/2004/03/trix/trix-1/"\n'
        ">\n"
        "  <graph>\n"
        "    <uri>urn:x-rdflib:default</uri>\n"
        "    <triple>\n"
        "      <uri>urn:example:tarek</uri>\n"
        "      <uri>urn:example:likes</uri>\n"
        "      <uri>urn:example:pizza</uri>\n"
        "    </triple>\n"
        "  </graph>\n"
        "</TriX>\n"
    )
