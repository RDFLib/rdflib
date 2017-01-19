import rdflib

"""
In py3, some objects are not comparable. When the turtle serializer tries to sort them everything breaks.

* Timezone aware datetime objects and "naive" datetime objects are not comparable

https://github.com/RDFLib/rdflib/issues/648
https://github.com/RDFLib/rdflib/issues/613

* DocumentFragment
https://github.com/RDFLib/rdflib/issues/676

"""


def test_sort_dates():

    g = rdflib.Graph()
    y = '''@prefix ex: <http://ex.org> .
ex:X ex:p "2016-01-01T00:00:00"^^<http://www.w3.org/2001/XMLSchema#dateTime>, "2016-01-01T00:00:00Z"^^<http://www.w3.org/2001/XMLSchema#dateTime> . '''

    p=g.parse(data=y, format="turtle")
    p.serialize(format="turtle")


def test_sort_docfrag():

    g = rdflib.Graph()
    y = '''@prefix ex: <http://ex.org> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
ex:X ex:p "<h1>hi</h1>"^^rdf:HTML, "<h1>ho</h1>"^^rdf:HTML  . '''

    p=g.parse(data=y, format="turtle")
    p.serialize(format="turtle")

if __name__ == '__main__':

    test_sort_docfrag()
