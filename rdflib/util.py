"""
Some utility functions.

TODO...

"""

from string import rsplit

from rdflib.term import URIRef
from rdflib.term import BNode
from rdflib.term import Literal
from rdflib.graph import Graph, QuotedGraph

from rdflib.exceptions import SubjectTypeError, PredicateTypeError, ObjectTypeError, ContextTypeError


def list2set(seq):
    seen = set()
    return [ x for x in seq if x not in seen and not seen.add(x)]

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



from time import mktime, time, gmtime, localtime, timezone, altzone, daylight

def date_time(t=None, local_time_zone=False):
    """http://www.w3.org/TR/NOTE-datetime ex: 1997-07-16T19:20:30Z

    >>> date_time(1126482850)
    '2005-09-11T23:54:10Z'

    @@ this will change depending on where it is run
    #>>> date_time(1126482850, local_time_zone=True)
    #'2005-09-11T19:54:10-04:00'

    >>> date_time(1)
    '1970-01-01T00:00:01Z'

    >>> date_time(0)
    '1970-01-01T00:00:00Z'
    """
    if t is None:
        t = time()

    if local_time_zone:
        time_tuple = localtime(t)
        if time_tuple[8]:
            tz_mins = altzone // 60
        else:
            tz_mins = timezone // 60
        tzd = "-%02d:%02d" % (tz_mins // 60, tz_mins % 60)
    else:
        time_tuple = gmtime(t)
        tzd = "Z"

    year, month, day, hh, mm, ss, wd, y, z = time_tuple
    s = "%0004d-%02d-%02dT%02d:%02d:%02d%s" % ( year, month, day, hh, mm, ss, tzd)
    return s

def parse_date_time(val):
    """always returns seconds in UTC

    # tests are written like this to make any errors easier to understand
    >>> parse_date_time('2005-09-11T23:54:10Z') - 1126482850.0
    0.0

    >>> parse_date_time('2005-09-11T16:54:10-07:00') - 1126482850.0
    0.0

    >>> parse_date_time('1970-01-01T00:00:01Z') - 1.0
    0.0

    >>> parse_date_time('1970-01-01T00:00:00Z') - 0.0
    0.0
    >>> parse_date_time("2005-09-05T10:42:00") - 1125916920.0
    0.0
    """

    if "T" not in val:
        val += "T00:00:00Z"

    ymd, time = val.split("T")
    hms, tz_str = time[0:8], time[8:]

    if not tz_str or tz_str=="Z":
        time = time[:-1]
        tz_offset = 0
    else:
        signed_hrs = int(tz_str[:3])
        mins = int(tz_str[4:6])
        secs = (cmp(signed_hrs, 0) * mins + signed_hrs * 60) * 60
        tz_offset = -secs

    year, month, day = ymd.split("-")
    hour, minute, second = hms.split(":")

    t = mktime((int(year), int(month), int(day), int(hour),
                int(minute), int(second), 0, 0, 0))
    t = t - timezone + tz_offset
    return t

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
            language = None
        if rest.startswith("^^"):
            datatype = rest[3:-1]
        else:
            datatype = None
        value = value.replace('\\"', '"').replace('\\\\', '\\').decode("unicode-escape")
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


if __name__ == "__main__":
    # try to make the tests work outside of the time zone they were written in
    #import os, time
    #os.environ['TZ'] = 'US/Pacific'
    #try:
    #    time.tzset()
    #except AttributeError, e:
    #    print e
        #pass
        # tzset missing! see
        # http://mail.python.org/pipermail/python-dev/2003-April/034480.html
    import doctest
    doctest.testmod()
