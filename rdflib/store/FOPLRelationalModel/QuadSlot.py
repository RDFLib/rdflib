"""
Utility functions associated with RDF terms:

- normalizing (to 64 bit integers via half-md5-hashes)
- escaping literal's for SQL persistence
"""
from rdflib.term import BNode
from rdflib.namespace import RDF
from rdflib.term import Literal
from rdflib.term import URIRef
from hashlib import md5
from rdflib.term_utils import *
from rdflib.graph import QuotedGraph
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
    tmp = tmp.replace('"', '\\"')
    return tmp

def dereferenceQuad(index,quad):
    assert index <= LANGUAGE_INDEX, "Invalid Quad Index"
    if index == DATATYPE_INDEX:
        return isinstance(quad[OBJECT],Literal) and quad[OBJECT].datatype or None
    elif index == LANGUAGE_INDEX:
        return isinstance(quad[OBJECT],Literal) and quad[OBJECT].language or None
    else:
        return quad[index]

def genQuadSlots(quads, useSignedInts=False):
    return [QuadSlot(index, quads[index], useSignedInts)
            for index in POSITION_LIST]

def normalizeValue(value, termType, useSignedInts=False):
    if value is None:
        value = u'http://www.w3.org/2002/07/owl#NothingU'
    else:
        value = (isinstance(value,Graph) and value.identifier or str(value)) + termType
    unsigned_hash = int(md5.new(
                      isinstance(value, unicode) and value.encode('utf-8')
                                                 or value)
                    .hexdigest()[:16], 16)

    if useSignedInts:
        return makeSigned(unsigned_hash)
    else:
        return unsigned_hash

def normalizeNode(node):
    return normalizeValue(node, term2Letter(node))

bigint_signed_max = 2**63
def makeSigned(bigint):
  if bigint > bigint_signed_max:
    return bigint_signed_max - bigint
  else:
    return bigint

def normalizeNode(node, useSignedInts=False):
    return normalizeValue(node, term2Letter(node), useSignedInts)

class QuadSlot(object):
    def __repr__(self):
        #NOTE: http://docs.python.org/ref/customization.html
        return "QuadSlot(%s,%s,%s)"%(SlotPrefixes[self.position],self.term,self.md5Int)

    def __init__(self, position, term, useSignedInts=False):
        assert position in POSITION_LIST, "Unknown quad position: %s"%position
        self.position = position
        self.term = term
        self.termType = term2Letter(term)
        self.useSignedInts = useSignedInts
        self.md5Int = normalizeValue(term, term2Letter(term), useSignedInts)

    def EscapeQuotes(self,qstr):
        """
        Ported from Ft.Lib.DbUtil
        """
        if qstr is None:
            return ''
        tmp = qstr.replace("\\","\\\\")
        tmp = tmp.replace("'", "\\'")
        tmp = tmp.replace('"', '\\"')
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
         
    def denormalizeTerm(self):
        """
        Denormalizes a term by returning a list of columns in a 'collapsed'
        table (created by merging the binary relation tables and 
        consolidating the lexical value, term type, and md5 integer for each
        corresponding term)
        """
        parts=[self.md5Int,self.normalizeTerm(),self.termType]
        if self.termType == 'L':
            dtypeQSlot = (self.term.datatype and
                            self.__class__(SUBJECT, self.term.datatype,
                                           self.useSignedInts)
                            or None)
            parts += [dtypeQSlot and dtypeQSlot.md5Int or None,
                      dtypeQSlot and dtypeQSlot.normalizeTerm() or None,
                      self.term.language]
        return parts 
