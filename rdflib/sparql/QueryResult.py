from rdflib import QueryResult,URIRef,BNode,Literal
from sparql import _graphKey

def retToXML(val) :
    if isinstance(val,URIRef) :
        return '<uri>%s</uri>' % val
    elif isinstance(val,BNode) :
        return '<bnode>%s</bnode' % val
    elif isinstance(val,Literal) :
        attr = ""
        if val.language != "" :
            attr += ' xml:lang="%s" ' % val.language
        if val.datatype != "" and val.datatype != None :
            attr += ' datatype="%s" ' % val.datatype
        if attr != "" :
            return '<literal %s>%s</literal>' % (attr.strip(),val)
        else :
            return '<literal>%s</literal>' % val
    else :
        return '<literal>%s</literal>' % val

def retToJSON(val) :
    if isinstance(val,URIRef) :
        return '"type": "uri", "value" : "%s"' % val
    elif isinstance(val,BNode) :
        return '"type": "bnode", "value" : "%s"' % val
    elif isinstance(val,Literal) :
        if val.language != "" :
            return '"type": "literal", "xml:lang" : "%s", "value" : "%s"' % (val.language,val)
            attr += ' xml:lang="%s" ' % val.language
        elif val.datatype != "" and val.datatype != None :
            return '"type": "typed=literal", "datatype" : "%s", "value" : "%s"' % (val.datatype,val)
        else :
            return '"type": "literal", "value" : "%s"' % val
    else :
        return '"type": "literal", "value" : "%s"' % val

def bindingXML(name,val) :
    if val == None :
        return ""
    retval = '            <binding name="%s">\n' % name
    retval += '                ' + retToXML(val) + '\n'
    retval += '            </binding>\n'
    return retval

def bindingJSON(name,val,comma) :
    if val == None :
        return ""
    retval = '                   "%s" : {' % name
    retval += retToJSON(val)
    if comma :
        retval += '},\n'
    else :
        retval += '}\n'
    return retval

class SPARQLQueryResult(QueryResult.QueryResult):
    """
    Query result class for SPARQL
        
    xml   : as an XML string conforming to the SPARQL XML result format: http://www.w3.org/TR/rdf-sparql-XMLres/
    python: as Python objects
    json  : as JSON   
    graph : as an RDFLib Graph - for CONSTRUCT and DESCRIBE queries
    """
    def __init__(self,qResult):
        """
        The constructor is the result straight from sparql-p, which is uple of 1) a list of tuples 
        (in select order, each item is the valid binding for the corresponding variable or 'None') for SELECTs
        , a SPARQLGraph for DESCRIBE/CONSTRUCT, and boolean for ASK  2) the variables selected 3) *all*
        the variables in the Graph Patterns 4) the order clause 5) the DISTINCT clause
        """
        result,selectionF,allVars,orderBy,distinct = qResult
        self.selected = result
        self.selectionF = selectionF
        self.allVariables = allVars
        self.orderBy = orderBy
        self.distinct = distinct
        
    def __len__(self):
        return len([i for i in self])
        
    def __iter__(self):
        """Iterates over the result entries"""
        if isinstance(self.selected,list):
            for item in self.selected:
                if not isinstance(item,(tuple,basestring)):
                    yield tuple(item)
                elif isinstance(item,basestring):
                    yield (item,)
                else:
                    yield item        
        else:
            yield self.selected
        
    def serialize(self,format='xml'):
        if format == 'python':
            return self.selected
        elif format in ['json','xml']:
           retval = ""
           try :
               self.allVariables.remove(_graphKey)
           except :
               # the element was not there, all the better...
               pass
           allvarsL = list(self.allVariables)
           if format == "json" :
               retval += '{\n'
               retval += '   "head" : {\n        "vars" : [\n'
               for i in xrange(0,len(allvarsL)) :
                   retval += '             "%s"' % allvarsL[i][1:]
                   if i == len(allvarsL) - 1 :
                       retval += '\n'
                   else :
                       retval += ',\n'
               retval += '         ]\n'
               retval += '    },\n'
               retval += '    "results" : {\n'
               retval += '          "ordered" : %s,\n' % (self.orderBy and 'true' or 'false')
               retval += '          "distinct" : %s,\n' % (self.distinct and 'true' or 'false')
               retval += '          "bindings" : [\n'
               for i in xrange(0,len(self.selected)) :
                   hit = self.selected[i]
                   retval += '               {\n'
                   if len(self.selectionF) == 0 :
                       for j in xrange(0,len(allvarsL)) :
                           retval += bindingJSON(allvarsL[j][1:],hit[j],j != len(allvarsL) - 1)                       
                   elif len(self.selectionF) == 1 :
                       retval += bindingJSON(self.selectionF[0][1:],hit, False)
                   else :
                       for j in xrange(0,len(self.selectionF)) :
                           retval += bindingJSON(self.selectionF[j][1:],hit[j],j != len(self.selectionF) - 1)
                   retval += '                }'
                   if i != len(self.selected) -1 :
                       retval += ',\n'
                   else :
                       retval += '\n'
               retval += '           ]\n'
               retval += '    }\n'
               retval += '}\n'
           elif format == "xml" :
               # xml output
               retval += '<?xml version="1.0"?>\n'
               retval += '<sparql xmlns="http://www.w3.org/2005/sparql-results#">\n'
               retval += '    <head>\n'
               for i in xrange(0,len(allvarsL)) :
                   retval += '        <variable name="%s"/>\n' % allvarsL[i][1:]
               retval += '    </head>\n'
               retval += '    <results ordered="%s" distinct="%s">\n' % (self.orderBy and 'true' or 'false',self.distinct and 'true' or 'false')
               for i in xrange(0,len(self.selected)) :
                   hit = self.selected[i]
                   retval += '        <result>\n'
                   if len(self.selectionF) == 0 :
                       for j in xrange(0,len(allvarsL)) :
                           retval += bindingXML(allvarsL[j][1:],hit[j])
                   elif len(self.selectionF) == 1 :
                       retval += bindingXML(self.selectionF[0][1:],hit)
                   else :
                       for j in xrange(0,len(self.selectionF)) :
                           retval += bindingXML(self.selectionF[j][1:],hit[j])
                   retval += '        </result>\n'
               retval += '    </results>\n'
               retval += '</sparql>\n'
           return retval
        else :
           raise Exception("Result format not implemented: %s"%format)