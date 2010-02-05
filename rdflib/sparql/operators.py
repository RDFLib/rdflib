# -*- coding: utf-8 -*-
#
#
# $Date: 2005/11/04 14:06:36 $, by $Author: ivan $, $Revision: 1.1 $
#
##
# API for the SPARQL operators. The operators (eg, 'lt')
# return a <em>function</em> that can be added to the AND clause of a query. The parameters are either regular values
# or query strings. The resulting function has one parameter (the binding directory), it can be combined with others or
# be plugged to into an array of constraints. For example:
# <pre>
#   constraints = [lt("?m",42)]
#</pre>
# <p>for checking whether "?m" is smaller than the (integer) value 42. It can be combined using the lambda function, for
# example:</p>
# <pre>
#    constraints = [lambda(b) : lt("?m",42")(b) or lt("?n",134)(b)]
# </pre>
# <p>is the expression for:</p>
# <pre>
#    AND ?m < 42 || ?n < 134
# </pre>
# <p>(Clearly, the relative complexity is only on the API level; a SPARQL language parser that starts with a SPARQL
# expression can map on this API).</p>
#
##

import sys, os, re
from rdflib.term import Literal, BNode, URIRef, Variable
from rdflib.namespace import Namespace
from rdflib.sparql.graph import _createResource
from rdflib.sparql import _questChar, Debug

_XSD_NS = Namespace('http://www.w3.org/2001/XMLSchema#')

##
# Boolean test whether this is a a query string or not
# @param v the value to be checked
# @return True if it is a query string
def queryString(v) :
    return isinstance(v,basestring) and len(v) != 0 and v[0] == _questChar

##
# Return the value in a literal, making on the fly conversion on datatype (using the datatypes that are implemented)
# @param v the Literal to be converted
# @return the result of the conversion.
def getLiteralValue(v) :
    return v

##
# Returns a <em>value retrieval function</em>. The return value can be plugged in a query; it would return
# the value of param directly if param is a real value, and the run-time value if param is a query string of the type
# "?xxx". If no binding is defined at the time of call, the return value is None
# @param param query string, Unbound instance, or real value
# @return a function taking one parameter (the binding directory)
def getValue(param) :
    if isinstance(param,Variable) :
        unBound = True
    else :
        unBound = queryString(param)
        if not unBound :
            if isinstance(param,Literal) :
                value = getLiteralValue(param)
            elif callable(param):
                return param
            else :
                value = param
            return lambda(bindings): value
    def f(bindings) :
        if unBound :
            #@@note, param must be reassigned to avoid tricky issues of scope
            #see: http://docs.python.org/ref/naming.html
            _param = isinstance(param,Variable) and param or Variable(param[1:]) 
            val = bindings[_param]
            if isinstance(val,Literal) :
                return getLiteralValue(val)
            else :
                return val
        else :
            return value
    return f

##
# Operator for '&lt;'
# @param a value or query string
# @param b value or query string
# @return comparison method
def lt(a,b) :
    fa = getValue(a)
    fb = getValue(b)
    def f(bindings) :
        try :
            return fa(bindings) < fb(bindings)
        except:
#            raise
            # this is the case when the operators are incompatible
            if Debug :
                (typ,val,traceback) = sys.exc_info()
                sys.excepthook(typ,val,traceback)
            return False
    return f

##
# Operator for '&lt;='
# @param a value or query string
# @param b value or query string
# @return comparison method
def le(a,b) :
    fa = getValue(a)
    fb = getValue(b)
    def f(bindings) :
        try :
            return fa(bindings) <= fb(bindings)
        except :
            # this is the case when the operators are incompatible
            if Debug :
                (typ,val,traceback) = sys.exc_info()
                sys.excepthook(typ,val,traceback)
            return False
    return f

##
# Operator for '&gt;'
# @param a value or query string
# @param b value or query string
# @return comparison method
def gt(a,b) :
    fa = getValue(a)
    fb = getValue(b)
    def f(bindings) :
        try :
            return fa(bindings) > fb(bindings)
        except :
            # this is the case when the operators are incompatible
            if Debug :
                (typ,val,traceback) = sys.exc_info()
                sys.excepthook(typ,val,traceback)
            return False
    return f

##
# Operator for '&gt;='
# @param a value or query string
# @param b value or query string
# @return comparison method
def ge(a,b) :
    fa = getValue(a)
    fb = getValue(b)
    def f(bindings) :
        try :
            return fa(bindings) >= fb(bindings)
        except :
            # this is the case when the operators are incompatible
            if Debug :
                (typ,val,traceback) = sys.exc_info()
                sys.excepthook(typ,val,traceback)
            return False
    return f

##
# Operator for '='
# @param a value or query string
# @param b value or query string
# @return comparison method
def eq(a,b) :
    fa = getValue(a)
    fb = getValue(b)
    def f(bindings) :
        try :
            return fa(bindings) == fb(bindings)
        except :
            # this is the case when the operators are incompatible
            if Debug :
                (typ,val,traceback) = sys.exc_info()
                sys.excepthook(typ,val,traceback)
            return False
    return f
##
# Operator for '!='
# @param a value or query string
# @param b value or query string
# @return comparison method
def neq(a,b) :
    fa = getValue(a)
    fb = getValue(b)
    def f(bindings) :
        try :
            return fa(bindings) != fb(bindings)
        except :
            # this is the case when the operators are incompatible
            if Debug :
                (typ,val,traceback) = sys.exc_info()
                sys.excepthook(typ,val,traceback)
            return False
    return f

def __getVariableName(v):
    if isinstance(v, Variable):
        return v
    elif queryString(v):
        return v[1:]
    else:
        return None


##
# Is the variable bound
# @param a value or query string
# @return check method
def bound(a) :
    v = __getVariableName(a)
    def f(bindings) :
        if v == None :
            return False
        if v in bindings :
            val = bindings[v]
            return not (val == None)
        else :
            return False
    return f

##
# Is the variable bound to a URIRef
# @param a value or query string
# @return check method
def isURI(a) :
    v = __getVariableName(a)
    def f(bindings) :
        if v == None :
            return False
        try :
            val = bindings[v]
            if val == None:
                return False
            else :
                return isinstance(val,URIRef)
        except :
            return False
    return f

##
# Is the variable bound to a IRIRef (this is just an alias for URIRef)
# @param a value or query string
# @return check method
def isIRI(a) :
    return isURI(a)

##
# Is the variable bound to a Blank Node
# @param a value or query string
# @return check method
def isBlank(a) :
    v = __getVariableName(a)
    def f(bindings) :
        if v == None :
            return False
        try :
            val = bindings[v]
            if val == None:
                return False
            else :
                return isinstance(val,BNode)
        except :
            return False
    return f

##
# Is the variable bound to a Literal
# @param a value or query string
# @return check method
def isLiteral(a) :
    v = __getVariableName(a)
    def f(bindings) :
        if v == None :
            return False
        try :
            val = bindings[v]
            if val == None:
                return False
            else :
                return isinstance(val,Literal)
        except :
            return False
    return f

##
# Return the string version of a resource
# @param a value or query string
# @return check method
def str(a) :
    v = __getVariableName(a)
    def f(bindings) :
        if v == None :
            return ""
        try :
            val = bindings[v]
            if val == None:
                return ""
            else :
                from __builtin__ import str as _str
                return _str(val)
        except :
            return ""
    return f

##
# Return the lang value of a literal
# @param a value or query string
# @return check method
def lang(a) :
    v = __getVariableName(a)
    def f(bindings) :
        if v == None: return ""
        try :
            val = bindings[v]
            if val == None:
                return ""
            else :
                return val.language
        except :
            return ""
    return f

##
# Return the datatype URI of a literal
# @param a value or query string
# @return check method
def datatype(a) :
    v = __getVariableName(a)
    def f(bindings) :
        if v == None:
            if isinstance(a,Literal):
                return a.datatype
            else:
                raise TypeError(a)

        try :
            val = bindings[v]
            if val == None:
                return TypeError(v)
            elif isinstance(val,Literal) and not val.language:
                return val.datatype
            else:
                raise TypeError(val)
        except :
            raise TypeError(v)
    return f


##
# Is a resource on a collection. The operator can be used to check whether
#    the 'item' is an element of the 'collection' (a.k.a. list). Both collection and item can
#    be a real resource or a query string.
# @param collection is either a query string (that has to be bound by the query) or an RDFLib Resource
# representing the collection
# @param item is either a query string (that has to be bound by the query), an RDFLib Resource, or
# a data type value that is turned into a corresponding Literal (with possible datatype)
# that must be tested to be part of the collection
# @defreturn a function
def isOnCollection(collection,item, triplets) :
    """Generate a method that can be used as a global constaint in sparql to check whether
    the 'item' is an element of the 'collection' (a.k.a. list). Both collection and item can
    be a real resource or a query string. Furthermore, item might be a plain string, that is
    then turned into a literal run-time.
    The method returns an adapted method.
    """
    #check_subject(collection)
    collUnbound = False
    if isinstance(collection,Variable) :
        collUnbound = True
        collection  = collection
    elif queryString(collection) :
        # just keep 'collection', no reason to reassign
        collUnbound = True
    else:
        collUnbound = False
        # if we got here, this is a valid collection resource
    if isinstance(item,Variable) :
        queryItem = item
        itUnbund  = True
    elif queryString(item) :
        queryItem = item
        itUnbound = True
    else :
        # Note that an exception is raised if the 'item' is invalid
        queryItem = _createResource(item)
        itUnbound = False
    def checkCollection(bindings) :
        try :
            if collUnbound == True :
                # the binding should come from the binding
                coll = bindings[collection]
            else :
                coll = collection
            if itUnbound == True :
                it = bindings[queryItem]
            else :
                it = queryItem
            return it in triplets.items(coll)
        except :
            # this means that the binding is not available. But that also means that
            # the global constraint was used, for example, with the optional triplets;
            # not available binding means that the method is irrelevant for those
            # ie, it should not become a show-stopper, hence it returns True
            return True
    return checkCollection


def addOperator(args,combinationArg):
    """
    SPARQL numeric + operator implemented via Python
    """
    return ' + '.join(["sparqlOperators.getValue(%s)%s"%(i,combinationArg and "(%s)"%combinationArg or '') for i in args])

def XSDCast(source,target=None):
    """
    XSD Casting/Construction Support
    For now (this may be an issue since Literal doesn't override comparisons) it simply creates
    a Literal with the target datatype using the 'lexical' value of the source
    """
    sFunc = getValue(source)
    def f(bindings):
        rt = sFunc(bindings)
        if isinstance(rt,Literal) and rt.datatype == target:
            #Literal already has target datatype
            return rt
        else:
            return Literal(rt,datatype=target)
    return f

def regex(item,pattern,flag=None):
    """
    Invokes the XPath fn:matches function to match text against a regular expression pattern.
    The regular expression language is defined in XQuery 1.0 and XPath 2.0 Functions and Operators section 7.6.1 Regular Expression Syntax
    """
    a = getValue(item)
    b = getValue(pattern)
    if flag:
        cFlag = 0
        usedFlags = []
        #Maps XPath REGEX flags (http://www.w3.org/TR/xpath-functions/#flags) to Python's re flags
        for fChar,_flag in [('i',re.IGNORECASE),('s',re.DOTALL),('m',re.MULTILINE)]:
            if fChar in flag and fChar not in usedFlags:
                cFlag |= _flag
                usedFlags.append(fChar)
        def f1(bindings):
            try:
                return bool(re.compile(b(bindings),cFlag).search(a(bindings)))
            except:
                return False
        return f1
    else:
        def f2(bindings):
            try:
                return bool(re.compile(b(bindings)).search(a(bindings)))
            except:
                return False
        return f2

    def f(bindings):
        try:
            return bool(re.compile(a(bindings)).search(b(bindings)))
        except Exception,e:
            print e
            return False
    return f

def EBV(a):
    """
    *  If the argument is a typed literal with a datatype of xsd:boolean, 
       the EBV is the value of that argument.
    * If the argument is a plain literal or a typed literal with a 
      datatype of xsd:string, the EBV is false if the operand value 
      has zero length; otherwise the EBV is true.
    * If the argument is a numeric type or a typed literal with a datatype 
     derived from a numeric type, the EBV is false if the operand value is 
     NaN or is numerically equal to zero; otherwise the EBV is true.
    * All other arguments, including unbound arguments, produce a type error.    
    """
    fa = getValue(a)
    def f(bindings) :
        try :
            rt = fa(bindings)
            if isinstance(rt,Literal):
                if rt.datatype == _XSD_NS.boolean:
                    ebv = rt.toPython()
                elif rt.datatype == _XSD_NS.string or rt.datatype is None:
                    ebv = len(rt) > 0
                else:
                    pyRT = rt.toPython()
                    if isinstance(pyRT,Literal):
                        #Type error, see: http://www.w3.org/TR/rdf-sparql-query/#ebv
                        raise TypeError("http://www.w3.org/TR/rdf-sparql-query/#ebv")
                    else:
                        ebv = pyRT != 0
                return ebv
            else:
                print rt, type(rt)
                raise
        except Exception,e:
            if isinstance(e,KeyError):
                #see: http://www.w3.org/TR/rdf-sparql-query/#ebv
                raise TypeError("http://www.w3.org/TR/rdf-sparql-query/#ebv")
            # this is the case when the operators are incompatible
            raise
            if Debug :
                (typ,val,traceback) = sys.exc_info()
                sys.excepthook(typ,val,traceback)
            return False
    return f
