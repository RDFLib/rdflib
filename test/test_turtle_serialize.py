import rdflib
from rdflib.py3compat import b

def testTurtleFinalDot(): 
    """
    https://github.com/RDFLib/rdflib/issues/282
    """

    g = rdflib.Graph()
    u = rdflib.URIRef("http://ex.org/bob.")
    g.bind("ns", "http://ex.org/")
    g.add( (u, u, u) )
    s=g.serialize(format='turtle')
    assert b("ns:bob.") not in s


if __name__ == "__main__":
    import nose, sys
    nose.main(defaultTest=sys.argv[0])
