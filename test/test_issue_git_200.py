import rdflib

import nose.tools

def test_broken_add(): 

    g=rdflib.Graph()
    nose.tools.assert_raises(AssertionError, lambda : g.add((1,2,3)))
    nose.tools.assert_raises(AssertionError, lambda : g.addN([(1,2,3,g)]))


if __name__=='__main__':
    import nose, sys
    nose.main(defaultTest=sys.argv[0])
