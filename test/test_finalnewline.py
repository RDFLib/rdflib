
from rdflib import ConjunctiveGraph, URIRef
import rdflib.plugin

from six import b

def testFinalNewline():
    """
    http://code.google.com/p/rdflib/issues/detail?id=5
    """
    import sys
    import platform
    if getattr(sys, 'pypy_version_info', None) or platform.system() == 'Java':
        from nose import SkipTest
        raise SkipTest(
            'Testing under pypy and Jython2.5 fails to detect that ' + \
            'IOMemory is a context_aware store')

    graph=ConjunctiveGraph()
    graph.add((URIRef("http://ex.org/a"),
               URIRef("http://ex.org/b"),
               URIRef("http://ex.org/c")))

    failed = set()
    for p in rdflib.plugin.plugins(None, rdflib.plugin.Serializer):
        v = graph.serialize(format=p.name)
        lines = v.split(b("\n"))
        if b("\n") not in v or (lines[-1]!=b('')):
            failed.add(p.name)
    assert len(failed)==0, "No final newline for formats: '%s'" % failed

if __name__ == "__main__":

    import sys
    import nose
    if len(sys.argv)==1:
        nose.main(defaultTest=sys.argv[0])
