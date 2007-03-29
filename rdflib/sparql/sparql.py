"""SPARQL implementation on top of RDFLib

Implementation of the <a href="http://www.w3.org/TR/rdf-sparql-query/">W3C SPARQL</a>
language (version April 2005). The basic class here is
supposed to be a superclass of L{rdflib.sparql.sparqlGraph}; it has
been separated only for a better maintainability.

There is a separate
U{description<http://dev.w3.org/cvsweb/%7Echeckout%7E/2004/PythonLib-IH/Doc/sparqlDesc.html>}
for the functionalities.

"""

##########################################################################
from rdflib.Literal     import Literal
from rdflib.BNode       import BNode
from rdflib.URIRef      import URIRef
from rdflib.exceptions  import Error
from rdflib.util        import check_predicate, check_subject, check_object, list2set

import sys, sets
from types import *

Debug = False

##########################################################################
# Utilities

# Note that the SPARQL draft allows the usage of a different query character, but I decided not to be that
# generous, and keep to one only. I put it into a separate variable to avoid problems if the group decides
# to change the syntax on that detail...
_questChar  = "?"

##
# SPARQL Error Exception (subclass of the RDFLib Exceptions)
class SPARQLError(Error) :
    """Am SPARQL error has been detected"""
    def __init__(self,msg):
        Error.__init__(self, ("SPARQL Error: %s." % msg))

class Unbound :
    """A class to encapsulate a query variable. This class should be used in conjunction with L{BasicGraphPattern<graphPattern.BasicGraphPattern>}."""
    def __init__(self,name) :
        """
        @param name: the name of the variable (without the '?' character)
        @type name: unicode or string
        """
        from sparql import _questChar, Debug
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


def _variablesToArray(variables,name='') :
    """Turn an array of Variables or query strings into an array of query strings. If the 'variables'
    is in fact a single string or Variable, then it is also put into an array.

    @param variables: a string, a unicode, or a Variable, or an array of those (can be mixed, actually). As a special case,
    if the value is "*", it returns None (this corresponds to the wildcard in SPARQL)
    @param name: the string to be used in the error message
    """
    if isinstance(variables,basestring) :
        if variables == "*" :
            return None
        else :
            return [variables]
    elif isinstance(variables,Unbound) :
        return [variables.name]
    elif type(variables) == list or type(variables) == tuple :
        retval = []
        for s in variables :
            if isinstance(s,basestring) :
                retval.append(s)
            elif isinstance(s,Unbound) :
                retval.append(s.name)
            else :
                raise SPARQLError("illegal type in '%s'; must be a string, unicode, or a Variable" % name)
    else :
        raise SPARQLError("'%s' argument must be a string, a Variable, or a list of those" % name)
    return retval

