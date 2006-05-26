import SPARQLParserc as SPARQLParser
from SPARQLEvaluate import Evaluate, NotImplemented

def CreateSPARQLParser():
    return SPARQLParser.new()    

def Parse(query,debug = False):    
    p = CreateSPARQLParser()
    if debug:
        try:
           p.debug_mode(1)
        except:
            p.debug = 1    
    return p.parse(unicode(query,'utf-8'))

