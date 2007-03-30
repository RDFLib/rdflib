from rdflib.sparql import _questChar


class Unbound :
    """A class to encapsulate a query variable. This class should be used in conjunction with L{BasicGraphPattern<graphPattern.BasicGraphPattern>}."""
    def __init__(self,name) :
        """
        @param name: the name of the variable (without the '?' character)
        @type name: unicode or string
        """
        if isinstance(name,basestring) :
            self.name     = _questChar + name
            self.origName = name
        else :
            raise SPARQLError("illegal argument, variable name must be a string or unicode")

    def __repr__(self) :
        retval  = "?%s" % self.origName
        return retval

    def __str__(self) :
        return self.__repr__()


