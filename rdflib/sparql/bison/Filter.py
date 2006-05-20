class ParsedFilter(object):
    def __init__(self,filter):
        self.filter = filter
        
    def __repr__(self):
        return "FILTER %s"%self.filter

class ParsedExpressionFilter(ParsedFilter):
    def __repr__(self):
        return "FILTER %s"%self.filter.reduce()

class ParsedFunctionFilter(ParsedFilter):
    def __repr__(self):
        return "FILTER %s"%self.filter
