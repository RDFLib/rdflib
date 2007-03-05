from Util import ListRedirect

class ParsedConditionalAndExpressionList(ListRedirect):
    """
    A list of ConditionalAndExpressions, joined by '||'
    """
    pyBooleanOperator = ' or '
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
    pyBooleanOperator = ' and '
    def __init__(self,relationalExprList):        
        if isinstance(relationalExprList,list):
            self._list = relationalExprList
        else:
            self._list = [relationalExprList]
    def __repr__(self):
        return "<RelationalExpressionList: %s>"%self._list

class ParsedPrefixedMultiplicativeExpressionList(ListRedirect):
    """
    A ParsedMultiplicativeExpressionList lead by a '+' or '-'
    """
    def __init__(self,prefix,mulExprList):
        self.prefix = prefix
        assert prefix != '-',"arithmetic '-' operator not supported"
        if isinstance(mulExprList,list):
            self._list = mulExprList
        else:
            self._list = [mulExprList]
    def __repr__(self):
        return "%s %s"%(self.prefix,self.reduce())

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
    def __init__(self,value=None):
        val = value is None and u"" or value
        super(ParsedString,self).__init__(val)

class ParsedDatatypedLiteral(object):
    """
    Placeholder for Datatyped literals
    This is neccessary (instead of instanciating Literals directly)
    when datatypes IRIRefs are QNames (in which case the prefix needs to be resolved at some point)
    """
    def __init__(self,value,dType):
        self.value = value
        self.dataType = dType

    def __repr__(self):
        return "'%s'^^%s"%(self.value,self.dataType)