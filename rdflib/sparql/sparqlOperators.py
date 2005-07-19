#!/d/Bin/Python/python.exe
# -*- coding: utf-8 -*-
#
#
# $Date: 2005/04/01 07:09:04 $, by $Author: ivan $, $Revision: 1.1 $
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

import sys, os, time, datetime

from sparql import _schemaType, _questChar, SPARQLError, JunkResource
from rdflib.Literal     import Literal
from rdflib.BNode       import BNode
from rdflib.URIRef      import URIRef

from sparql import type_string
from sparql import type_integer
from sparql import type_long
from sparql import type_double
from sparql import type_float
from sparql import type_decimal
from sparql import type_dateTime
from sparql import type_date
from sparql import type_time

from sparql import _graphKey, _createResource

from sparql import Debug

def _strToDate(v) :
    tstr = time.strptime(v,"%Y-%m-%d")
    return datetime.date(tstr.tm_year,tstr.tm_mon,tstr.tm_mday)
    
def _strToTime(v) :
    tstr = time.strptime(v,"%H:%M:%S")
    return datetime.time(tstr.tm_hour,tstr.tm_min,tstr.tm_sec)
    
def _strToDateTime(v) :
    tstr = time.strptime(v,"%Y-%m-%dT%H:%M:%S")
    return datetime.datetime(tstr.tm_year,tstr.tm_mon,tstr.tm_mday,tstr.tm_hour,tstr.tm_min,tstr.tm_sec)

_conversions = {
    type_string:   lambda v: v,
    type_integer:  lambda v: int(v),
    type_float:    lambda v: float(v),
    type_long:     lambda v: long(v),
    type_double:   lambda v: float(v),
    type_decimal:  lambda v: int(v),
    type_date:     _strToDate, 
    type_time:     _strToTime,
    type_dateTime: _strToDateTime,
}

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
    if v.datatype == "" or not (v.datatype in _conversions):
        return v
    else :
        return _conversions[v.datatype](v)

##
# Returns a <em>value retrieval function</em>. The return value can be plugged in a query; it would return
# the value of param directly if param is a real value, and the run-time value if param is a query string of the type
# "?xxx". If no binding is defined at the time of call, the return value is None
# @param param query string or real value
# @return a function taking one parameter (the binding directory)
def getValue(param) :
    unBound = queryString(param)
    if not unBound :
        if isinstance(param,Literal) :
            value = getLiteralValue(v)
        else :
            value = param
    def f(bindings) :
        if unBound :
            val = bindings[param]
            if isinstance(val,Literal) :
                return getLiteralValue(val)
            else :
                return val
        else :
            return value
    return f
    
##
# Operator for '&lt;'
# # @param a value or query string
# @param b value or query string
# @return comparison method
def lt(a,b) :
    fa = getValue(a)
    fb = getValue(b)
    def f(bindings) :
        try :
            return fa(bindings) < fb(bindings)
        except :
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
# Is the variable bound
# @param a value or query string
# @return check method
def bound(a) :
    def f(bindings) :
        if queryString(a) and a in bindings :
            val = bindings[a]
            return not (val == None or val == JunkResource)
        else :
            return False
    return f
            
##
# Is the variable bound to a URIRef
# @param a value or query string
# @return check method
def isURI(a) :
    def f(bindings) :
        try :
            val = bindings[a]
            if val == None or val == JunkResource :
                return False
            else :
                return isinstance(val,URIRef)
        except :
            return False
    return f

##
# Is the variable bound to a Blank Node
# @param a value or query string
# @return check method
def isBlank(a) :
    def f(bindings) :
        try :
            val = bindings[a]
            if val == None or val == JunkResource :
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
    def f(bindings) :
        try :
            val = bindings[a]
            if val == None or val == JunkResource :
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
    def f(bindings) :
        try :
            val = bindings[a]
            if val == None or val == JunkResource :
                return ""
            else :
                return `val`
        except :
            return ""
    return f

##
# Return the lang value of a literal
# @param a value or query string
# @return check method
def lang(a) :
    def f(bindings) :
        try :
            val = bindings[a]
            if val == None or val == JunkResource :
                return ""
            else :
                return val.lang
        except :
            return ""
    return f

##
# Return the datatype URI of a literal
# @param a value or query string
# @return check method
def datatype(a) :
    def f(bindings) :
        try :
            val = bindings[a]
            if val == None or val == JunkResource :
                return ""
            else :
                return val.datatype
        except :
            return ""
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
# @exception SPARQLError if the collection or the item parameters are illegal (not valid resources for
# a collection or an object
def isOnCollection(collection,item) :
    """Generate a method that can be used as a global constaint in sparql to check whether
    the 'item' is an element of the 'collection' (a.k.a. list). Both collection and item can
    be a real resource or a query string. Furthermore, item might be a plain string, that is
    then turned into a literal run-time.
    The method returns an adapted method.
    """
    from rdflib.Store import check_predicate, check_subject, check_object
    from sparql import _questChar
    collUnbound = False
    if queryString(collection) :
        # just keep 'collection', no reason to reassign
        collUnbound = True
    else:
        try :
            check_subject(collection) 
            collUnbound = False
            # if we got here, this is a valid collection resource
        except :
            raise SPARQLError("illegal parameter type, %s" % collection)
    if queryString(item) :
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
            triplets = bindings[_graphKey]                
            return it in triplets.unfoldCollection(coll)
        except :
            # this means that the binding is not available. But that also means that
            # the global constraint was used, for example, with the optional triplets;
            # not available binding means that the method is irrelevant for those
            # ie, it should not become a show-stopper, hence it returns True
            return True
    return checkCollection
    

