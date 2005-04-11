from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.Literal import Literal

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
    if not str:
        return default
    elif str.startswith("<") and str.endswith(">"):
        return URIRef(str[1:-1])
    elif str.startswith('"') and str.endswith('"'):
        return Literal(str[1:-1])
    elif str.startswith("_:"):
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
    ymd, hms = val.split("T")
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


def from_n3(s):
    if s.startswith('<'):
        return URIRef(s[1:-1])
    elif s.startswith('"'):
        # TODO: would a regex be faster?
        value, rest = s.rsplit('"', 1)
        value = value[1:] # strip leading quote
        if rest.startswith("@"):
            language, rest = rest.rsplit('^^', 1)
            language = language[1:] # strip leading at sign
        else:
            language = ''
        if rest.startswith("^^"):
            datatype = rest[2:]
        else:
            datatype = ''
        value = value.decode("unicode-escape")
        return Literal(value, language, datatype)
    else:
        return BNode(s)
