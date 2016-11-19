"""

RDFLib can map between data-typed literals and python objects.

Mapping for integers, floats, dateTimes, etc. are already added, but
you can also add your own.

This example shows how :meth:`rdflib.term.bind` lets you register new
mappings between literal datatypes and python objects

"""


from rdflib import Graph, Literal, Namespace, XSD
from rdflib.term import bind

if __name__=='__main__':

    # complex numbers are not registered by default
    # no custom constructor/serializer needed since
    # complex('(2+3j)') works fine
    bind(XSD.complexNumber, complex)

    ns=Namespace("urn:my:namespace:")

    c=complex(2,3)

    l=Literal(c)

    g=Graph()
    g.add((ns.mysubject, ns.myprop, l))

    n3=g.serialize(format='n3')

    # round-trip through n3

    g2=Graph()
    g2.parse(data=n3, format='n3')

    l2=list(g2)[0][2]

    print(l2)

    print(l2.value == c) # back to a python complex object
