import rdflib


def test_issue1769_numeric_string_to_literal():

    assert rdflib.util.from_n3("-5") == rdflib.term.Literal(
        '-5', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#integer')
    )

    assert rdflib.util.from_n3("-5.5") == rdflib.term.Literal(
        '-5.5', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#decimal')
    )

    assert rdflib.util.from_n3("4.2E9") == rdflib.term.Literal(
        '4.2E9', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#double')
    )

    assert rdflib.util.from_n3("1.23E-7") == rdflib.term.Literal(
        '1.23e-07',
        datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#double'),
    )
