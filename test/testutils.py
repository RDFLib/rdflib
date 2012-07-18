
from rdflib import BNode, Graph, ConjunctiveGraph

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

def check_serialize_parse(fpath, infmt, testfmt, verbose=False):
    g = ConjunctiveGraph()
    _parse_or_report(verbose, g, fpath, format=infmt)
    if verbose:
        for t in g:
            print t
        print "========================================"
        print "Parsed OK!"
    s = g.serialize(format=testfmt)
    if verbose:
        print s
    g2 = ConjunctiveGraph()
    _parse_or_report(verbose, g2, data=s, format=testfmt)
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
