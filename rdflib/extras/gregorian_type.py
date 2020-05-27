class GregorianType:
    def __init__(self, lexical_value : str, datatype : int):
        self.lexical_value = lexical_value
        lvalue = lexical_value.split('-')
        self.gYear = lvalue[0]
        self.gMonth = None
        if datatype == 2:
            self.gMonth = lvalue[1]

    def __str__(self):
        if self.gMonth == None:
            return self.gYear
        return self.gYear + '-' + self.gMonth

