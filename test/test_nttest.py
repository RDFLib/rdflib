import os
import sys
import unittest
import logging
from rdflib.term import BNode
from rdflib.graph import Graph, ConjunctiveGraph
log = logging.getLogger(__file__)

# TODO: make an introspective version (like this one) of
# rdflib.graphutils.isomorphic and use instead.
def crapCompare(g1, g2):
    """A really crappy way to 'check' if two graphs are equal. It ignores blank
    nodes completely and ignores subgraphs."""
    if len(g1) != len(g2):
        raise Exception("Graphs dont have same length")
    for t in g1:
        s = _no_blank(t[0])
        o = _no_blank(t[2])
        if not (s, t[1] ,o) in g2:
            e = "(%s, %s, %s) is not in both graphs!"%(s, t[1], o)
            raise Exception, e
def _no_blank(node):
    if isinstance(node, BNode): return None
    if isinstance(node, Graph):
        return None #node._Graph__identifier = _SQUASHED_NODE
    return node


def check_nt_serialize(fpath, fmt, verbose=False):
    g = ConjunctiveGraph()
    _parse_or_report(verbose, g, fpath, format=fmt)
    if verbose:
        for t in g:
            print t
        print "========================================"
        print "Parsed OK!"
    s = g.serialize(format='nt')
    if verbose:
        print "Serialized to: ", s
    g2 = ConjunctiveGraph()
    _parse_or_report(verbose, g2, data=s, format='nt')
    if verbose:
        print g2.serialize()
    crapCompare(g,g2)

def _parse_or_report(verbose, graph, *args, **kwargs):
    try:
        graph.parse(*args, **kwargs)
    except:
        if verbose:
            print "========================================"
            print "Error in parsing serialization:"
            print args, kwargs
        raise

def _get_test_files_formats():
    skiptests = [
        'test/nt/anons-02.nt',
        'test/nt/anons-03.nt',
        'test/nt/formulae-01.nt',
        'test/nt/formulae-02.nt',
        'test/nt/formulae-03.nt',
        'test/nt/formulae-05.nt',
        'test/nt/formulae-06.nt',
        'test/nt/formulae-10.nt',
        'test/nt/keywords-08.nt',
        'test/nt/lists-06.nt',
        'test/nt/literals-01.nt',
        'test/nt/literals-02.nt',
        'test/nt/literals-04.nt',
        'test/nt/literals-05.nt',
        'test/nt/numeric-01.nt',
        'test/nt/numeric-02.nt',
        'test/nt/numeric-03.nt',
        'test/nt/numeric-04.nt',
        'test/nt/numeric-05.nt',
        'test/nt/paths-04.nt',
        'test/nt/paths-06.nt',
        'test/nt/qname-01.nt',
        'test/nt/rdflibtest05.nt']
    for f in os.listdir('test/nt'):
        fpath = "test/nt/"+f
        if fpath in skiptests:
            log.debug("Skipping %s" % f)
        else:
            if f.endswith('.rdf'):
                yield fpath, 'xml'
            elif f.endswith('.nt'):
                yield fpath, 'nt'

def test_all_nt_serialize():
    for fpath, fmt in _get_test_files_formats():
        yield check_nt_serialize, fpath, fmt


if __name__ == "__main__":
    class TestNTWriting(unittest.TestCase):
        def testWriting(self):
            for fpath, fmt in _get_test_files_formats():
                check_nt_serialize(fpath, fmt)
    if len(sys.argv) > 1:
        check_nt_serialize(sys.argv[1], "nt", True)
        sys.exit()
    else:
        unittest.main()

