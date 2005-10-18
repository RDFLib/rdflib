from rdflib import *
from rdflib.Graph import QuotedGraph

def term2Letter(term):
    if type(term) == URIRef:
        return 'U'
    elif type(term) == BNode:    
        return 'B'
    elif type(term) == Literal:
        return 'L'
    elif type(term) == QuotedGraph:
        return 'F'
    elif type(term) == Variable:
        return 'V'
    else:
        print term,type(term)
        raise

def triplePattern2termCombinations((s,p,o)):
    combinations=[]
    #combinations.update(TERM_COMBINATIONS)
    if type(o)==Literal:
        for key,val in TERM_COMBINATIONS.items():
            if key[OBJECT] == 'O':
                combinations.append(val)
    return combinations
    
def type2TermCombination(member,klass):
    return TERM_COMBINATIONS['%sU%s'%(term2Letter(member),term2Letter(klass))]

def statement2TermCombination(subject,predicate,obj):
    #print subject,predicate,obj
    rt=TERM_COMBINATIONS['%s%s%s'%(term2Letter(subject),term2Letter(predicate),term2Letter(obj))]
    #print rt
    return rt

SUBJECT = 0
PREDICATE = 1
OBJECT = 2

TERM_COMBINATIONS = {
    'UUU' : 0,
    'UUV' : 1,
    'UUB' : 2,
    'UUL' : 3,
    'UUF' : 4,

    'UVU' : 5,
    'UVV' : 6,
    'UVB' : 7,
    'UVL' : 8,
    'UVF' : 9,

    'VUU' : 10,
    'VUV' : 11,
    'VUB' : 12,
    'VUL' : 13,
    'VUF' : 14,

    'VVU' : 15,
    'VVV' : 16,
    'VVB' : 17,
    'VVL' : 18,
    'VVF' : 19,

    'BUU' : 20,
    'BUV' : 21,
    'BUB' : 22,
    'BUL' : 23,
    'BUF' : 24,

    'BVU' : 25,
    'BVV' : 26,
    'BVB' : 27,
    'BVL' : 28,
    'BVF' : 29,

    'FUU' : 30,
    'FUV' : 31,
    'FUB' : 32,
    'FUL' : 33,
    'FUF' : 34,

    'FVU' : 35,
    'FVV' : 36,
    'FVB' : 37,
    'FVL' : 38,
    'FVF' : 39
}

REVERSE_TERM_COMBINATIONS = dict([(value,key) for key,value in TERM_COMBINATIONS.items()])
