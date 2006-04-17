from rdflib import *
from rdflib.Graph import QuotedGraph, Graph, ConjunctiveGraph, BackwardCompatGraph

#Takes an instance of a Graph (Graph, QuotedGraph, ConjunctiveGraph, or BackwardCompatGraph)
#and returns the Graphs identifier and 'type' ('U' for Graphs, 'F' for QuotedGraphs ).
def normalizeGraph(graph):
    if isinstance(graph,QuotedGraph):        
        return graph.identifier, 'F'
    else:
        return graph.identifier , term2Letter(graph.identifier)    

TERM_INSTANCIATION_DICT ={
    'U':URIRef,
    'B':BNode,
    'V':Variable,
    'L':Literal
}

GRAPH_TERM_DICT = {
    'F': (QuotedGraph, URIRef),
    'U': (Graph, URIRef),
    'B': (Graph, BNode)
}

def term2Letter(term):
    if isinstance(term,URIRef):
        return 'U'
    elif isinstance(term,BNode):    
        return 'B'
    elif isinstance(term,Literal):
        return 'L'
    elif isinstance(term,QuotedGraph):
        return 'F'
    elif isinstance(term,Variable):
        return 'V'
    elif isinstance(term,Graph):
        return term2Letter(term.identifier)
    elif term is None:
        return 'L'
    else:        
        raise Exception("The given term (%s) is not an instance of any of the known types (URIRef,BNode,Literal,QuotedGraph, or Variable)"%term)

def constructGraph(term):
    return GRAPH_TERM_DICT[term]

def triplePattern2termCombinations((s,p,o)):
    combinations=[]
    #combinations.update(TERM_COMBINATIONS)
    if isinstance(o,Literal):
        for key,val in TERM_COMBINATIONS.items():
            if key[OBJECT] == 'O':
                combinations.append(val)
    return combinations
    
def type2TermCombination(member,klass,context):
    try:
        rt = TERM_COMBINATIONS['%sU%s%s'%(term2Letter(member),term2Letter(klass),normalizeGraph(context)[-1])]
        return rt
    except:
        raise Exception("Unable to persist classification triple: %s %s %s"%(member,'rdf:type',klass,context))

def statement2TermCombination(subject,predicate,obj,context):
    return TERM_COMBINATIONS['%s%s%s%s'%(term2Letter(subject),term2Letter(predicate),term2Letter(obj),normalizeGraph(context)[-1])]

SUBJECT = 0
PREDICATE = 1
OBJECT = 2
CONTEXT = 3

TERM_COMBINATIONS = {
    'UUUU' : 0,
    'UUUB' : 1,
    'UUUF' : 2,
    'UUVU' : 3,
    'UUVB' : 4,
    'UUVF' : 5,
    'UUBU' : 6,
    'UUBB' : 7,
    'UUBF' : 8,
    'UULU' : 9,
    'UULB' : 10,
    'UULF' : 11,
    'UUFU' : 12,
    'UUFB' : 13,
    'UUFF' : 14,
    
    'UVUU' : 15,
    'UVUB' : 16,
    'UVUF' : 17,
    'UVVU' : 18,
    'UVVB' : 19,
    'UVVF' : 20,
    'UVBU' : 21,
    'UVBB' : 22,
    'UVBF' : 23,
    'UVLU' : 24,
    'UVLB' : 25,
    'UVLF' : 26,    
    'UVFU' : 27,
    'UVFB' : 28,
    'UVFF' : 29,

    'VUUU' : 30,
    'VUUB' : 31,
    'VUUF' : 33,    
    'VUVU' : 34,
    'VUVB' : 35,
    'VUVF' : 36,
    'VUBU' : 37,
    'VUBB' : 38,
    'VUBF' : 39,
    'VULU' : 40,
    'VULB' : 41,
    'VULF' : 42,
    'VUFU' : 43,
    'VUFB' : 44,
    'VUFF' : 45,

    'VVUU' : 46,
    'VVUB' : 47,
    'VVUF' : 48,    
    'VVVU' : 49,
    'VVVB' : 50,
    'VVVF' : 51,    
    'VVBU' : 52,
    'VVBB' : 53,
    'VVBF' : 54,
    'VVLU' : 55,
    'VVLB' : 56,
    'VVLF' : 57,
    'VVFU' : 58,
    'VVFB' : 59,
    'VVFF' : 60,

    'BUUU' : 61,
    'BUUB' : 62,
    'BUUF' : 63,
    'BUVU' : 64,
    'BUVB' : 65,
    'BUVF' : 66,
    'BUBU' : 67,
    'BUBB' : 68,
    'BUBF' : 69,
    'BULU' : 70,
    'BULB' : 71,
    'BULF' : 72,
    'BUFU' : 73,
    'BUFB' : 74,
    'BUFF' : 75,

    'BVUU' : 76,
    'BVUB' : 77,
    'BVUF' : 78,
    'BVVU' : 79,
    'BVVB' : 80,
    'BVVF' : 81,
    'BVBU' : 82,
    'BVBB' : 83,
    'BVBF' : 84,
    'BVLU' : 85,
    'BVLB' : 86,
    'BVLF' : 87,
    'BVFU' : 88,
    'BVFB' : 89,
    'BVFF' : 90,

    'FUUU' : 91,
    'FUUB' : 92,
    'FUUF' : 93,
    'FUVU' : 94,
    'FUVB' : 95,
    'FUVF' : 96,
    'FUBU' : 97,
    'FUBB' : 98,
    'FUBF' : 99,
    'FULU' : 100,
    'FULB' : 101,
    'FULF' : 102,
    'FUFU' : 103,
    'FUFB' : 104,
    'FUFF' : 105,

    'FVUU' : 106,
    'FVUB' : 107,
    'FVUF' : 108,
    'FVVU' : 109,
    'FVVB' : 110,
    'FVVF' : 111,
    'FVBU' : 112,
    'FVBB' : 113,
    'FVBF' : 114,
    'FVLU' : 115,
    'FVLB' : 116,
    'FVLF' : 117,
    'FVFU' : 118,
    'FVFB' : 119,
    'FVFF' : 120,
}

REVERSE_TERM_COMBINATIONS = dict([(value,key) for key,value in TERM_COMBINATIONS.items()])
