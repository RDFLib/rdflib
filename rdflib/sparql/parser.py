#!/usr/bin/python
""" SPARQL Lexer, Parser and Function-Mapper
By Shawn Brown <http://shawnbrown.com/contact>

TO DO:
  swap current parser functions for Michelp's pyparsing setup
  add mapping for FILTER/constraints
  typed literals
  integer, double or boolean abbreviations
  language tags (e.g., @fr)
  nested OPTIONALs ???
  blank node and RDF collection syntax ???
  GRAPH statements ???

CURRENTLY SUPPORTED:
  Simple SELECT queries
  Predicate-object and object list shorthand
    (e.g., ?x  foaf:name  ?name ; foaf:mbox  ?mbox ; vcard:TITLE  ?title)
  Multi-line/triple-quoted literals
  BASE, PREFIX, SELECT, WHERE, UNION, OPTIONAL, multiple UNIONs and multiple
    OPTIONALs (but not nested OPTIONALs)

USAGE:
    #from sparql_lpm import doSPARQL
    from rdflib.sparql.parser import doSPARQL
    ...load graph...
    ...define SPARQL query as string...
    result = doSPARQL(queryStr, sparqlGr)

"""

import base64
import re
from rdflib.URIRef import URIRef
from rdflib.sparql.graphPattern import GraphPattern

def _escape(text): return base64.encodestring(text).replace("\n", "")
def _unescape(text): return base64.decodestring(text)

def _escapeLiterals(query):
    """ escape all literals with escape() """
    fn = lambda m: "'" + _escape(m.group(2)) + "'" + m.group(3)
    pat = r"(\"\"\"|'''|[\"'])([^\1]*?[^\\]?)\1" # literal
    return re.sub(pat+"(\s*[.,;\}])", fn, query)

def _resolveShorthand(query):
    """ resolve some of the syntactic shorthand (2.8 Other Syntactic Forms) """
    def doList(pat, text):
        pat = re.compile(pat)
        while pat.search(text): text = re.sub(pat, r"\1\2\3 . \2\4", text)
        return text
    # 2.8.1 Predicate-Object Lists
    pat = r"(\{.*?)([^ ]+ )([^ ]+ [^ ]+)\s?; ([^ ]+ [^ ]+\s?[,;\.\}])"
    query = doList(pat, query)
    # 2.8.2 Object Lists
    pat = r"(\{.*?)([^ ]+ [^ ]+ )([^ ]+\s?), ([^ ]+\s?[,\.\}])"
    query = doList(pat, query)
    # TO DO: look at adding all that other crazy stuff!!!
    return query

def _resolvePrefixes(query):
    """ resolve prefixed IRIs, remove PREFIX statements """
    # parse PREFIX statements
    prefixes = re.findall("PREFIX ([\w\d]+:) <([^<>]+)>", query) # get list of prefix tuples
    prefixes.extend([
        ("rdf:", "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
        ("rdfs:", "http://www.w3.org/2000/01/rdf-schema#"),
        ("xsd:", "http://www.w3.org/2001/XMLSchema#"),
        ("fn:", "http://www.w3.org/2004/07/xpath-functions")])
    matches = re.search("PREFIX : <([^<>]+)>", query) # parse colon-only PREFIX
    if matches != None: prefixes.append((":", matches.group(1)))
    query = re.sub("PREFIX [\w\d]*:[ ]?<[^<>]+>[ ]?", "", query) # remove PREFIX statements
    # escape IRIs (unescaped in ??)
    fn = lambda m: "<" + _escape(m.group(1)) + ">"
    query = re.sub("<([^<>]+)>", fn, query)
    # resolve prefixed IRIs
    for pair in prefixes:
        fn = lambda m: "<" + _escape(pair[1]+m.group(1)) + ">" # escaped too
        query = re.sub(pair[0]+"([^ .\}]+)", fn, query)
    return query

def _resolveBase(query):
    """ resolve relative IRIs using BASE IRI, remove BASE statement """
    pat = re.compile("BASE <([^<>]+)>\s?")
    base = pat.search(query)
    if base != None:
        fn = lambda m: "<" + base.group(1) + m.group(1) + ">"
        query = re.sub("<([^<>: ]+)>", fn, query) # resolve relative IRIs
        query = re.sub(pat, "", query) # remove BASE statement
    return query

def _parseSelect(query):
    """ returns tuple of SELECTed variables or None """
    var = "[?$][\\w\\d]+" # SELECT variable pattern
    select = re.search("SELECT(?: " + var + ")+", query)
    if select != None:
        select = re.findall(var, select.group(0))
        select = tuple(select)
    return select

class _StackManager:
    """ manages token stack for _parser() """
    def __tokenGen(self, tokens):
        for token in tokens:
            yield token
    def __init__(self, tokenList):
        self.stack = self.__tokenGen(tokenList)
        self.current = self.stack.next()
    def next(self):
        try:
            self.current = self.stack.next()
            if self.current == "":
                self.next() # if blank, move to next
        except StopIteration:
            self.current = None
    def token(self):
        return self.current

# 
# The following classes, _listTypes dictionary and _makeList() function are
# used to test for recognized keywords and to create "typed" lists for nested
# statements when parsing the SPARQL query's WHERE statement
#
class Where(list): pass
class Union(list): pass
class Optional(list): pass
_listTypes = {
    "OPTIONAL": lambda : Optional([]),
    "UNION": lambda : Union([]),
    "WHERE": lambda : Where([])
}
def _makeList(keyword):
    """ return list of given type or None """
    global _listTypes
    if keyword in _listTypes:
        return _listTypes[keyword]()
    return None

def _parser(stack, listType="WHERE"):
    """ simple recursive descent SPARQL parser """
    typedList = _makeList(listType)
    nestedType = listType
    while stack.token() != None:
        token = stack.token()
        if _makeList(token) != None:
            nestedType = token
        elif token == "{":
            stack.next() # iterate to next token
            typedList.append(_parser(stack, nestedType))
            nestedType = listType # reset nestedType
        elif token == "}":
            return typedList
        elif token != ".":
            statement = ""
            while token != None and token != "." and token != "{" and token != "}":
                statement += " " + token
                stack.next()
                token = stack.token()
            statement = statement.strip()
            typedList.append(statement)
            continue
        stack.next()
    return typedList

def _parseWhere(query):
    """ split query into tokens, return parsed object """
    stackObj = _StackManager(query)
    return _parser(stackObj)

def _findStatements(stmntType, stmntList):
    """ recurse over nested list, compile & return flat list of matching
        statement strings used by _getStatements() """
    statements = []
    typedList = _makeList(stmntType)
    for stmnt in stmntList:
        if type(stmnt) is str:
            statements.append(stmnt)
        if type(stmnt) == type(typedList):
            statements.extend(_findStatements(stmntType, stmnt))
    return statements

def _getStatements(stmntType, stmntList):
    """ gets statements of given type from given list """
    statements = []
    typedList = _makeList(stmntType)
    for item in stmntList:
        if type(item) == type(typedList):
            statements.append(_findStatements(stmntType, item))
    return statements

def _buildGraphPattern(triples):
    # split strings into tuples of strings
    triples = map((lambda x: tuple(re.split(" ", x))), triples)
    # convert tuples of strings into tuples of RDFLib objects
    isIRI = lambda x: x[0]=="<" and x[-1]==">"
    isLit = lambda x: x[0]=="'" and x[-1]=="'" or x[0]=='"' and x[-1]=='"'
    for i in range(len(triples)):
        sub = triples[i][0]
        pred = triples[i][1]
        obj = triples[i][2]
        # unescape and define objects for IRIs and literals
        if isIRI(sub): sub = URIRef(_unescape(sub[1:-1]))
        if isIRI(pred): pred = URIRef(_unescape(pred[1:-1]))
        if isIRI(obj): obj = URIRef(_unescape(obj[1:-1]))
        elif isLit(obj): obj = _unescape(obj[1:-1])
        # build final triple
        triples[i] = (sub, pred, obj)
    return GraphPattern(triples)

def _buildQueryArgs(query):
    """ """
    # query lexer
    query = _escapeLiterals(query) # are unescaped in _buildGraphPattern()
    query = re.sub("\s+", " ", query).strip() # normalize whitespace
    query = _resolveShorthand(query) # resolve pred-obj and obj lists
    query = _resolveBase(query) # resolve relative IRIs
    query = _resolvePrefixes(query) # resolve prefixes
    query = re.sub(r"\s*([.;,\{\}])\s*", r" \1 ", query) # normalize punctuation
    whereObj = query[query.find("{")+1:query.rfind("}")].strip() # strip non-WHERE bits
    whereObj = whereObj.split(" ") # split into token stack
    # query parser
    select = _parseSelect(query) # select is tuple of select variables
    whereObj = _parseWhere(whereObj) # stack parsed into nested list of typed lists
    # map parsed object to arrays of RDFLib graphPattern objects
    where = _getStatements("WHERE", [whereObj]) # pass whereObj as nested list
    where.extend(_getStatements("UNION", whereObj))
    where = map(_buildGraphPattern, where)
    optional = _getStatements("OPTIONAL", whereObj)
    optional = map(_buildGraphPattern, optional)
    # run query
    #return sparqlGr.query(select, where, optional)
    return { "select":select, "where":where, "optional":optional }

def doSPARQL(query, sparqlGr):
    """ Takes SPARQL query & SPARQL graph, returns SPARQL query result object. """
    x = _buildQueryArgs(query)
    return sparqlGr.query(x["select"], x["where"], x["optional"])


if __name__ == "__main__":
    testCases = [
# basic
"""
SELECT ?name
WHERE { ?a <http://xmlns.com/foaf/0.1/name> ?name }
""",
# simple prefix
"""
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?name
WHERE { ?a foaf:name ?name }
""",
# base statement
"""
BASE <http://xmlns.com/foaf/0.1/>
SELECT ?name
WHERE { ?a <name> ?name }
""",
# prefix and colon-only prefix
"""
PREFIX : <http://xmlns.com/foaf/0.1/>
PREFIX vcard: <http://www.w3.org/2001/vcard-rdf/3.0#>
SELECT ?name ?title
WHERE {
    ?a :name ?name .
    ?a vcard:TITLE ?title
}
""",
# predicate-object list notation
"""
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?name ?mbox
WHERE {
    ?x  foaf:name  ?name ;
        foaf:mbox  ?mbox .
}
""",
# object list notation
"""
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?x
WHERE {
    ?x foaf:nick  "Alice" ,
                  "Alice_" .
}
""",
# escaped literals
"""
PREFIX tag: <http://xmlns.com/foaf/0.1/>
PREFIX vcard: <http://www.w3.org/2001/vcard-rdf/3.0#>
SELECT ?name
WHERE {
    ?a tag:name ?name ;
       vcard:TITLE "escape test vcard:TITLE " ;
       <tag://test/escaping> "This is a ''' Test \"\"\"" ;
       <tag://test/escaping> ?d
}
""",
# key word as variable
"""
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?PREFIX ?WHERE
WHERE {
    ?x  foaf:name  ?PREFIX ;
        foaf:mbox  ?WHERE .
}
""",
# key word as prefix
"""
PREFIX WHERE: <http://xmlns.com/foaf/0.1/>
SELECT ?name ?mbox
WHERE {
    ?x  WHERE:name  ?name ;
        WHERE:mbox  ?mbox .
}
""",
# some test cases from grammar.py
"SELECT ?title WHERE { <http://example.org/book/book1> <http://purl.org/dc/elements/1.1/title> ?title . }",

"""PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?name ?mbox
WHERE { ?person foaf:name ?name .
OPTIONAL { ?person foaf:mbox ?mbox}
}""",

"""PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?name ?name2
WHERE { ?person foaf:name ?name .
OPTIONAL { ?person foaf:knows ?p2 . ?p2 foaf:name   ?name2 . }
}""",

"""PREFIX foaf: <http://xmlns.com/foaf/0.1/>
#PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?name ?mbox
WHERE
{
{ ?person rdf:type foaf:Person } .
OPTIONAL { ?person foaf:name  ?name } .
OPTIONAL {?person foaf:mbox  ?mbox} .
}"""
    ]
    
    print "Content-type: text/plain\n\n"
    for query in testCases:
        print "\n-----\n"
        print '>>> query = """' + query.replace("\n", "\n... ") + '"""'
        print ">>> result = doSPARQL(query, sparqlGr)\n"
        result = _buildQueryArgs(query);
        print "select = ", result["select"], "\n"
        print "where = ", result["where"], "\n"
        print "optional = ", result["optional"], "\n"
        print "result = sparqlGr.query(select, where, optional)"
