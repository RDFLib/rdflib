from rdflib import RDF, RDFS, URIRef


def test_definednamespace_dir():
    x = dir(RDF)

    values = [
        RDF.nil,
        RDF.direction,
        RDF.first,
        RDF.language,
        RDF.object,
        RDF.predicate,
        RDF.reifies,
        RDF.rest,
        RDF.subject,
        RDF.type,
        RDF.value,
        RDF.Alt,
        RDF.Bag,
        RDF.CompoundLiteral,
        RDF.List,
        RDF.Property,
        RDF.Seq,
        RDF.Statement,
        RDF.HTML,
        RDF.JSON,
        RDF.PlainLiteral,
        RDF.XMLLiteral,
        RDF.langString,
    ]

    assert len(values) == len(x)

    for value in values:
        assert value in x


def test_rdf12_namespace_terms() -> None:
    assert RDF.reifies == URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#reifies")
    assert RDFS.Proposition == URIRef(
        "http://www.w3.org/2000/01/rdf-schema#Proposition"
    )
    assert RDFS.Proposition in dir(RDFS)
