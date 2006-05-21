from Util import ListRedirect

class ParsedConditionalAndExpressionList(ListRedirect):
    """
    A list of ConditionalAndExpressions, joined by '||'
    """
    def __init__(self,conditionalAndExprList):
        if isinstance(conditionalAndExprList,list):
            self._list = conditionalAndExprList
        else:
            self._list = [conditionalAndExprList]
            
    def __repr__(self):
        return "<ConditionalExpressionList: %s>"%self._list
    
class ParsedRelationalExpressionList(ListRedirect):   
    """
    A list of RelationalExpressions, joined by '&&'s
    """
    def __init__(self,relationalExprList):
        if isinstance(relationalExprList,list):            
            self._list = relationalExprList
        else:
            self._list = [relationalExprList]
    def __repr__(self):
        return "<RelationalExpressionList: %s>"%self._list

class ParsedMultiplicativeExpressionList(ListRedirect):   
    """
    A list of UnaryExpressions, joined by '/' or '*' s
    """
    def __init__(self,unaryExprList):
        if isinstance(unaryExprList,list):            
            self._list = unaryExprList
        else:
            self._list = [unaryExprList]
    def __repr__(self):
        return "<MultiplicativeExpressionList: %s>"%self.reduce()
        
class ParsedAdditiveExpressionList(ListRedirect):        
    """
    A list of MultiplicativeExpressions, joined by '+' or '-' s
    """
    def __init__(self,multiplicativeExprList):
        if isinstance(multiplicativeExprList,list):            
            self._list = multiplicativeExprList
        else:
            self._list = [multiplicativeExprList]
    def __repr__(self):
        return "<AdditiveExpressionList: %s>"%self._list
    
class ParsedString(unicode):
    def __init__(self,value):
        super(ParsedString,self).__init__(value)
