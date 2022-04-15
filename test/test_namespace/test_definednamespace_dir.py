from rdflib import RDF


def test_definednamespace_dir():
    x = dir(RDF)

    values = [
        RDF.nil,
        RDF.direction,
        RDF.first,
        RDF.language,
        RDF.object,
        RDF.predicate,
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
