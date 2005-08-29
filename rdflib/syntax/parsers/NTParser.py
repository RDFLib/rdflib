ns_separator = ""

from rdflib.syntax.parsers import Parser

from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.Literal import Literal
from rdflib.constants import RDFNS, TYPE

from rdflib.exceptions import ParserError
from rdflib.URLInputSource import URLInputSource
from rdflib.FileInputSource import FileInputSource

from urllib import urlopen


def uriref(v):
    if v[0]=="<" and v[-1]==">":
        return URIRef(v[1:-1])
    else:
        raise ParserError("NTParser error: invalid uriref of '%s'" % v)

bNodes = {}
def node_id(v):
    if v[0:2]=="_:":
        name = v[3:]
        if not name in bNodes:
            bNodes[name] = BNode()
        return bNodes[name]
    else:
        raise ParserError("NTParser error: invalid node_id of '%s'" % v)

import re
_literal = re.compile(r'''"(?P<value>[^@\^]*)"(?:@(?P<lang>[^\^]*))?(?:\^\^<(?P<datatype>.*)>)?''')    
def literal(v):
    m = _literal.match(v)
    try:
        d = m.groupdict()
        v = d["value"].decode('unicode-escape')
        return Literal(v, d["lang"] or '', d["datatype"])        
    except:
        print "could not parse", v
        return Literal(v)


def lang_string(v):
    if v[0]=='"':    
        return Literal(v[1:-1])
    else:
        return Literal("NYI")
        raise NotImplementedError()

class NTParser(Parser):
    
    def __init__(self):
        super(NTParser, self).__init__()

    def parse(self, source, sink, baseURI=None):
        if isinstance(source, URLInputSource):
            location = str(source)
            baseURI = baseURI or location
            file = urlopen(location)
        elif isinstance(source, FileInputSource):
            file = source.file
        else:
            file = source

        for line in iter(file.readline, ""):
            line = line.lstrip()
            if line and not line[0]=="#": 
                s, p, o = line.split(None, 2)
                o = o.rstrip()
                if not o[-1]==".":
                    raise exception.ParserError("""NTParser error: triple is missing "." """)
                o = o[:-1]
                o = o.rstrip()
                
                if s[0]=="<":
                    def c(num):
                        return unichr(int(num.groups()[0], 16))
                    from re import sub
                    pat = re.compile(r"\\u(....)")
                    s = pat.sub(c, s)        
                    
                    s = uriref(s)
                elif s[0]=="_":
                    s = node_id(s)
                else:
                    raise exception.ParserError("NTParser error: unexpected subject of '%s'" % s)
                if p[0]=="<":
                    p = uriref(p)
                else:
                    raise exception.ParserError("NTParser error: unexpected predicate of '%s'" % p)
                if o[0]=="<":
                    o = uriref(o)
                elif o[0]=="_":
                    o = node_id(o)
                else:
                    o = literal(o)
                sink.add((s, p, o))
            
        file.close()

