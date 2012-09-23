
import rdflib
import rdflib.compare


from nose.exc import SkipTest

try: 
    from test_nt_suite import all_nt_files
except: 
    from test.test_nt_suite import all_nt_files

"""
Test round-tripping by all serializers/parser that are registerd. 
This means, you may test more than just core rdflib!

run with no arguments to test all formats + all files
run with a single argument, to test only that format, i.e. "n3"
run with three arguments to test round-tripping in a given format and reading a single file in the given format, i.e.: 

python test/test_roundtrip.py xml nt test/nt/literals-02.nt 

tests roundtripping through rdf/xml with only the literals-02 file

"""


SKIP= [ 
    ('xml', 'test/nt/qname-02.nt'), # uses a property that cannot be qname'd
]



def roundtrip(e, verbose=False):
    infmt,testfmt,source=e

    g1=rdflib.ConjunctiveGraph()

    g1.parse(source,format=infmt)
    
    s=g1.serialize(format=testfmt)

    if verbose: 
        print "S:"
        print s

    g2=rdflib.ConjunctiveGraph()
    g2.parse(data=s, format=testfmt)

    if verbose: 
        print "Diff:"
        for t in g1-g2: 
            print t

        print "G1"
        for t in sorted(g1): print t
        print "--------------------------------\nG2:"
        for t in sorted(g2): print t

    assert rdflib.compare.isomorphic(g1,g2)


formats=None

def test_cases(): 
    global formats 
    if not formats:
        serializers=set(x.name for x in rdflib.plugin.plugins(None, rdflib.plugin.Serializer))
        parsers=set(x.name for x in rdflib.plugin.plugins(None, rdflib.plugin.Parser))
        formats=parsers.intersection(serializers)

    for testfmt in formats:
            
        for f,infmt in all_nt_files():
            if (testfmt,f) not in SKIP:
                yield roundtrip, (infmt, testfmt,f)
    

if __name__ == "__main__":

    import sys
    import nose
    if len(sys.argv)==1: 
        nose.main(defaultTest=sys.argv[0])
    elif len(sys.argv)==2: 
        
        import test.test_roundtrip
        test.test_roundtrip.formats=[sys.argv[1]]
        nose.main(defaultTest=sys.argv[0], argv=sys.argv[:1])
    else: 
        roundtrip((sys.argv[2],sys.argv[1],sys.argv[3]), verbose=True)
