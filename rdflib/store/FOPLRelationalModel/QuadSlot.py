"""
Utility functions associated with RDF terms:
    
- normalizing (to 64 bit integers via half-md5-hashes)
- escaping literal's for SQL persistence
"""
from rdflib import BNode
from rdflib import RDF
from rdflib.Literal import Literal
from rdflib.URIRef import URIRef
import md5
from rdflib.term_utils import *
from rdflib.Graph import QuotedGraph
from rdflib.store.REGEXMatching import REGEXTerm

Any = None

SUBJECT    = 0
PREDICATE  = 1
OBJECT     = 2
CONTEXT    = 3

DATATYPE_INDEX = CONTEXT + 1
LANGUAGE_INDEX = CONTEXT + 2

SlotPrefixes = {
     SUBJECT   : 'subject',
     PREDICATE : 'predicate',
     OBJECT    : 'object',
     CONTEXT   : 'context',
     DATATYPE_INDEX : 'dataType',
     LANGUAGE_INDEX : 'language'
}

POSITION_LIST = [SUBJECT,PREDICATE,OBJECT,CONTEXT]

def EscapeQuotes(qstr):
    """
    Ported from Ft.Lib.DbUtil
    """
    if qstr is None:
        return ''
    tmp = qstr.replace("\\","\\\\")
    tmp = tmp.replace("'", "\\'")
    return tmp

def dereferenceQuad(index,quad):
    assert index <= LANGUAGE_INDEX, "Invalid Quad Index"
    if index == DATATYPE_INDEX:
        return isinstance(quad[OBJECT],Literal) and quad[OBJECT].datatype or None
    elif index == LANGUAGE_INDEX:
        return isinstance(quad[OBJECT],Literal) and quad[OBJECT].language or None
    else:
        return quad[index]

def genQuadSlots(quads):
    return [QuadSlot(index,quads[index])for index in POSITION_LIST]        

def normalizeValue(value,termType):
    if value is None:
        value = u'http://www.w3.org/2002/07/owl#NothingU'
    else:
        value = (isinstance(value,Graph) and value.identifier or value) + termType
    return int(md5.new(isinstance(value,unicode) and value.encode('utf-8') or value).hexdigest()[:16],16)

class QuadSlot:
    def __repr__(self):
        #NOTE: http://docs.python.org/ref/customization.html
        return "QuadSlot(%s,%s,%s)"%(SlotPrefixes[self.position],self.term,self.md5Int)    
    
    def __init__(self,position,term):
        assert position in POSITION_LIST, "Unknown quad position: %s"%position
        self.position = position
        self.term = term
        self.md5Int = normalizeValue(term,term2Letter(term))
        self.termType = term2Letter(term)

    def EscapeQuotes(self,qstr):
        """
        Ported from Ft.Lib.DbUtil
        """
        if qstr is None:
            return ''
        tmp = qstr.replace("\\","\\\\")
        tmp = tmp.replace("'", "\\'")
        return tmp

    def normalizeTerm(self):
        if isinstance(self.term,(QuotedGraph,Graph)):
            return self.term.identifier.encode('utf-8')
        elif isinstance(self.term,Literal):
            return self.EscapeQuotes(self.term).encode('utf-8')
        elif self.term is None or isinstance(self.term,(list,REGEXTerm)):
            return self.term
        else:
            return self.term.encode('utf-8')