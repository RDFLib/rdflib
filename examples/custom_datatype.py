"""
RDFLib can map between RDF data-typed literals and Python objects.

Mapping for integers, floats, dateTimes, etc. are already added, but
you can also add your own.

This example shows how :meth:`rdflib.term.bind` lets you register new
mappings between literal datatypes and Python objects
"""


from rdflib import Graph, Literal, Namespace, XSD
from rdflib import term

if __name__ == "__main__":

    # Complex numbers are not registered by default
    # No custom constructor/serializer needed since
    # complex('(2+3j)') works fine
    term.bind(XSD.complexNumber, complex)

    # Create a complex number RDFlib Literal
    EG = Namespace("http://example.com/")
    c = complex(2, 3)
    l = Literal(c)

    # Add it to a graph
    g = Graph()
    g.add((EG.mysubject, EG.myprop, l))
    # Print the triple to see what it looks like
    print(list(g)[0])
    # prints: (
    #           rdflib.term.URIRef('http://example.com/mysubject'),
    #           rdflib.term.URIRef('http://example.com/myprop'),
    #           rdflib.term.Literal(
    #               '(2+3j)',
    #               datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#complexNumber')
    #           )
    #         )

    # Round-trip through n3 serialize/parse
    g2 = Graph().parse(data=g.serialize())

    l2 = list(g2)[0]
    print(l2)

    # Compare with the original python complex object (should be True)
    # l2[2] is the object of the triple
    print(l2[2].value == c)
