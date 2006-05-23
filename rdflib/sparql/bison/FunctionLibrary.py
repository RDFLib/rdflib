"""
[28] FunctionCall ::= IRIref ArgList
http://www.w3.org/TR/rdf-sparql-query/#evaluation
"""

from Util import ListRedirect

STR         = 0
LANG        = 1
LANGMATCHES = 2
DATATYPE    = 3
BOUND       = 4
isIRI       = 5
isURI       = 6
isBLANK     = 7
isLITERAL   = 8

FUNCTION_NAMES = {
    STR : 'STR',
    LANG : 'LANG',
    LANGMATCHES : 'LANGMATCHES',
    DATATYPE : 'DATATYPE',
    BOUND : 'BOUND',
    isIRI : 'isIRI',
    isURI : 'isURI',
    isBLANK : 'isBLANK',
    isLITERAL : 'isLITERAL',
}

class FunctionCall(object):
    def __init__(self,name,arguments=None):
        self.name = name
        self.arguments = arguments is None and [] or arguments
        
    def __repr__(self):
        return "%s(%s)"%(self.name,','.join([i.reduce() for i in self.arguments]))
    
class ParsedArgumentList(ListRedirect):
    def __init__(self,arguments):
        self._list = arguments
        
class ParsedREGEXInvocation(object):
    def __init__(self,arg1,arg2,arg3=None):
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        
    def __repr__(self):
        return "REGEX(%s,%s%s)"%(self.arg1.reduce(),self.arg2.reduce(),self.arg3 and ',%s'%self.arg3.reduce() or '')

class BuiltinFunctionCall(FunctionCall):    
    def __init__(self,name,arg1,arg2=None):
        if arg2:
            arguments = [arg1,arg2]
        else:
            arguments = [arg1]
        super(BuiltinFunctionCall,self).__init__(name,arguments)
    
    def __repr__(self):
        #print self.name
        #print [type(i) for i in self.arguments]
        return "%s(%s)"%(FUNCTION_NAMES[self.name],','.join([isinstance(i,ListRedirect) and str(i.reduce()) or i for i in self.arguments]))