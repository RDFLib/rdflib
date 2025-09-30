from rdflib import Graph, Namespace, URIRef

# https://github.com/RDFLib/rdflib/issues/3237
# Test that the ns1 prefix is not generated when the base is set.
mns = Namespace("http://my-namespace.net/")


def test_turtle():
    g = Graph(base="http://my-base.net/")
    g.add((mns.foo, URIRef("http://my-base.net/my-predicate"), mns.bar))
    result = g.serialize(format="text/turtle")
    assert (
        result
        == """@base <http://my-base.net/> .

<http://my-namespace.net/foo> <my-predicate> <http://my-namespace.net/bar> .

"""
    )


def test_longturtle():
    g = Graph(base="http://my-base.net/")
    g.add((mns.foo, URIRef("http://my-base.net/my-predicate"), mns.bar))
    result = g.serialize(format="longturtle", canon=True)
    assert (
        result
        == """BASE <http://my-base.net/>

<http://my-namespace.net/foo>
    <my-predicate> <http://my-namespace.net/bar> ;
.
"""
    ), print(result)
