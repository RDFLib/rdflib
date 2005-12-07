from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.Literal import Literal
from rdflib.Graph import Graph, QuotedGraph

from rdflib.exceptions import SubjectTypeError, PredicateTypeError, ObjectTypeError, ContextTypeError
from rdflib.compat import rsplit
from cPickle import loads

def first(seq):
    for result in seq:
        return result
    return None

def uniq(sequence, strip=0):
    """removes duplicate strings from the sequence."""
    set = {}
    if strip:
        map(lambda val, default: set.__setitem__(val.strip(), default),
            sequence, [])
    else:
        map(set.__setitem__, sequence, [])
    return set.keys()

def more_than(sequence, number):
    "Returns 1 if sequence has more items than number and 0 if not."
    i = 0
    for item in sequence:
        i += 1
        if i > number:
            return 1
    return 0

def term(str, default=None):
    """See also from_n3"""
    if not str:
        return default
    elif str.startswith("<") and str.endswith(">"):
        return URIRef(str[1:-1])
    elif str.startswith('"') and str.endswith('"'):
        return Literal(str[1:-1])
    elif str.startswith("_"):
        return BNode(str)
    else:
        msg = "Unknown Term Syntax: '%s'" % str
        raise Exception(msg)



from time import mktime, time, gmtime, timezone, altzone, daylight

def date_time(t=None):
    """http://www.w3.org/TR/NOTE-datetime ex: 1997-07-16T19:20:30Z"""
    t = t or time()    
    year, month, day, hh, mm, ss, wd, y, z = gmtime(t)
    s = "%0004d-%02d-%02dT%02d:%02d:%02dZ" % ( year, month, day, hh, mm, ss)
    return s

def parse_date_time(val):
    try:
        ymd, hms = val.split("T")
    except:
        ymd = val
        hms = "00:00:00"
    year, month, day = ymd.split("-")
    hour, minute, second = hms[:-1].split(":")
    
    t = mktime((int(year), int(month), int(day), int(hour),
                        int(minute), int(second), 0, 0, -1))

    # Hum...
    if daylight:
        t = t - timezone
    else:
        t = t - altzone

    return t


classes = {
    1: URIRef,
    2: BNode,
    3: Literal,
    4: Graph,
    5: QuotedGraph
}

def from_bits(bits, backend=None):
    which, r = loads(bits)
    return classes[which](*r)


def from_n3(s, default=None, backend=None):
    """ Creates the Identifier corresponding to the given n3 string. WARNING: untested, may contain bugs. TODO: add test cases."""
    if not s:
        return default
    if s.startswith('<'):
        return URIRef(s[1:-1])
    elif s.startswith('"'):
        # TODO: would a regex be faster?
        value, rest = rsplit(s, '"', 1)
        value = value[1:] # strip leading quote
        if rest.startswith("@"):
            if "^^" in rest:
                language, rest = rsplit(rest, '^^', 1)
                language = language[1:] # strip leading at sign                
            else:
                language = rest[1:] # strip leading at sign
                rest = ''
        else:
            language = ''
        if rest.startswith("^^"):
            datatype = rest[3:-1]
        else:
            datatype = ''
        value = value.decode("unicode-escape")
        return Literal(value, language, datatype)
    elif s.startswith('{'):
	identifier = from_n3(s[1:-1])
	return QuotedGraph(backend, identifier)
    elif s.startswith('['):
	identifier = from_n3(s[1:-1])
	return Graph(backend, identifier)
    else:
        if s.startswith("_:"):
            return BNode(s[2:])
        else:
            return BNode(s)

def check_context(c):
    if not (isinstance(c, URIRef) or \
            isinstance(c, BNode)):
        raise ContextTypeError("%s:%s" % (c, type(c)))

def check_subject(s):
    """ Test that s is a valid subject identifier."""
    if not (isinstance(s, URIRef) or isinstance(s, BNode)):
        raise SubjectTypeError(s)

def check_predicate(p):
    """ Test that p is a valid predicate identifier."""
    if not isinstance(p, URIRef):
        raise PredicateTypeError(p)

def check_object(o):
    """ Test that o is a valid object identifier."""
    if not (isinstance(o, URIRef) or \
            isinstance(o, Literal) or \
            isinstance(o, BNode)):
        raise ObjectTypeError(o)

def check_statement((s, p, o)):
    if not (isinstance(s, URIRef) or isinstance(s, BNode)):
        raise SubjectTypeError(s)

    if not isinstance(p, URIRef):
        raise PredicateTypeError(p)

    if not (isinstance(o, URIRef) or \
            isinstance(o, Literal) or \
            isinstance(o, BNode)):
        raise ObjectTypeError(o)

def check_pattern((s, p, o)):
    if s and not (isinstance(s, URIRef) or isinstance(s, BNode)):
        raise SubjectTypeError(s)

    if p and not isinstance(p, URIRef):
        raise PredicateTypeError(p)

    if o and not (isinstance(o, URIRef) or \
                  isinstance(o, Literal) or \
                  isinstance(o, BNode)):
        raise ObjectTypeError(o)

def graph_to_dot(graph, dot):
    """ Turns graph into dot (graphviz graph drawing format) using pydot. """
    import pydot
    nodes = {}
    for s, o in graph.subject_objects():
        for i in s,o:
            if i not in nodes.keys():
                nodes[i] = i
    for s, p, o in graph.triples((None,None,None)):
        dot.add_edge(pydot.Edge(nodes[s], nodes[o], label=p))

