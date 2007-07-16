from rdflib import QueryResult,URIRef,BNode,Literal, Namespace
from xml.dom import XML_NAMESPACE
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesNSImpl
from cStringIO import StringIO

SPARQL_XML_NAMESPACE = u'http://www.w3.org/2005/sparql-results#'

try:
    from Ft.Xml import MarkupWriter
    class SPARQLXMLWriter:
        """
        4Suite-based SPARQL XML Writer
        """
        def __init__(self,output):
            self.writer = MarkupWriter(output, indent=u"yes")
            self.writer.startDocument()
            self.writer.startElement(u'sparql',namespace=SPARQL_XML_NAMESPACE)

        def write_header(self,allvarsL):
            self.writer.startElement(u'head', namespace=SPARQL_XML_NAMESPACE)
            for i in xrange(0,len(allvarsL)) :
                self.writer.startElement(u'variable',namespace=SPARQL_XML_NAMESPACE,attributes={u'name':unicode(allvarsL[i])})
                self.writer.endElement(u'variable')
            self.writer.endElement( u'head')

        def write_results_header(self,orderBy,distinct):
            self.writer.startElement(u'results',namespace=SPARQL_XML_NAMESPACE,attributes={u'ordered' : unicode(orderBy and 'true' or 'false'),
                                                                                           u'distinct': unicode(distinct and 'true' or 'false')})

        def write_start_result(self):
            self.writer.startElement(u'result',namespace=SPARQL_XML_NAMESPACE)
            self._resultStarted = True

        def write_end_result(self):
            assert self._resultStarted
            self.writer.endElement(u'result',namespace=SPARQL_XML_NAMESPACE)
            self._resultStarted = False

        def write_binding(self,name,val):
            assert self._resultStarted
            if val:
                attrs = {u'name':unicode(name)}
                self.writer.startElement(u'binding', namespace=SPARQL_XML_NAMESPACE, attributes=attrs)
                if isinstance(val,URIRef) :
                    self.writer.startElement(u'uri', namespace=SPARQL_XML_NAMESPACE)
                    self.writer.text(val)
                    self.writer.endElement(u'uri')
                elif isinstance(val,BNode) :
                    self.writer.startElement(u'bnode', namespace=SPARQL_XML_NAMESPACE)
                    self.writer.text(val)
                    self.writer.endElement(u'bnode')
                elif isinstance(val,Literal) :
                    attrs = {}
                    if val.language :
                        attrs[(u'lang', XML_NAMESPACE)] = unicode(val.language)
                    elif val.datatype:
                        attrs[u'datatype'] = unicode(val.datatype)
                    self.writer.startElement(u'literal', namespace=SPARQL_XML_NAMESPACE, attributes=attrs)
                    self.writer.text(val)
                    self.writer.endElement(u'literal')

                else:
                    raise Exception("Unsupported RDF term: %s"%val)

                self.writer.endElement(u'binding')

        def close(self):
            self.writer.endElement(u'results')
            self.writer.endElement(u'sparql')
except:
    class SPARQLXMLWriter:
        """
        Python saxutils-based SPARQL XML Writer
        """
        def __init__(self, output, encoding='utf-8'):
            writer = XMLGenerator(output, encoding)
            writer.startDocument()
            writer.startPrefixMapping(u'sparql',SPARQL_XML_NAMESPACE)
            writer.startPrefixMapping(u'xml', XML_NAMESPACE)
            writer.startElementNS((SPARQL_XML_NAMESPACE, u'sparql'), u'sparql', AttributesNSImpl({}, {}))
            self.writer = writer
            self._output = output
            self._encoding = encoding

        def write_header(self,allvarsL):
            self.writer.startElementNS((SPARQL_XML_NAMESPACE, u'head'), u'head', AttributesNSImpl({}, {}))
            for i in xrange(0,len(allvarsL)) :
                attr_vals = {
                    (None, u'name'): unicode(allvarsL[i]),
                    }
                attr_qnames = {
                    (None, u'name'): u'name',
                    }
                self.writer.startElementNS((SPARQL_XML_NAMESPACE, u'variable'),
                                             u'variable',
                                             AttributesNSImpl(attr_vals, attr_qnames))
                self.writer.endElementNS((SPARQL_XML_NAMESPACE, u'variable'), u'variable')
            self.writer.endElementNS((SPARQL_XML_NAMESPACE, u'head'), u'head')

        def write_results_header(self,orderBy,distinct):
            attr_vals = {
                (None, u'ordered')  : unicode(orderBy and 'true' or 'false'),
                (None, u'distinct') : unicode(distinct and 'true' or 'false'),
                }
            attr_qnames = {
                (None, u'ordered')  : u'ordered',
                (None, u'distinct') : u'distinct'
                }
            self.writer.startElementNS((SPARQL_XML_NAMESPACE, u'results'),
                                         u'results',
                                         AttributesNSImpl(attr_vals, attr_qnames))

        def write_start_result(self):
            self.writer.startElementNS(
                    (SPARQL_XML_NAMESPACE, u'result'), u'result', AttributesNSImpl({}, {}))
            self._resultStarted = True

        def write_end_result(self):
            assert self._resultStarted
            self.writer.endElementNS((SPARQL_XML_NAMESPACE, u'result'), u'result')
            self._resultStarted = False

        def write_binding(self,name,val):
            assert self._resultStarted
            if val:
                attr_vals = {
                    (None, u'name')  : unicode(name),
                    }
                attr_qnames = {
                    (None, u'name')  : u'name',
                    }
                self.writer.startElementNS((SPARQL_XML_NAMESPACE, u'binding'),
                                       u'binding',
                                       AttributesNSImpl(attr_vals, attr_qnames))

                if isinstance(val,URIRef) :
                    self.writer.startElementNS((SPARQL_XML_NAMESPACE, u'uri'),
                                           u'uri',
                                           AttributesNSImpl({}, {}))
                    self.writer.characters(val)
                    self.writer.endElementNS((SPARQL_XML_NAMESPACE, u'uri'),u'uri')
                elif isinstance(val,BNode) :
                    self.writer.startElementNS((SPARQL_XML_NAMESPACE, u'bnode'),
                                           u'bnode',
                                           AttributesNSImpl({}, {}))
                    self.writer.characters(val)
                    self.writer.endElementNS((SPARQL_XML_NAMESPACE, u'bnode'),u'bnode')
                elif isinstance(val,Literal) :
                    attr_vals = {}
                    attr_qnames = {}
                    if val.language :
                        attr_vals[(XML_NAMESPACE, u'lang')] = val.language
                        attr_qnames[(XML_NAMESPACE, u'lang')] = u"xml:lang"
                    elif val.datatype:
                        attr_vals[(None,u'datatype')] = val.datatype
                        attr_qnames[(None,u'datatype')] = u'datatype'

                    self.writer.startElementNS((SPARQL_XML_NAMESPACE, u'literal'),
                                           u'literal',
                                           AttributesNSImpl(attr_vals, attr_qnames))
                    self.writer.characters(val)
                    self.writer.endElementNS((SPARQL_XML_NAMESPACE, u'literal'),u'literal')

                else:
                    raise Exception("Unsupported RDF term: %s"%val)

                self.writer.endElementNS((SPARQL_XML_NAMESPACE, u'binding'),u'binding')

        def close(self):
            self.writer.endElementNS((SPARQL_XML_NAMESPACE, u'results'), u'results')
            self.writer.endElementNS((SPARQL_XML_NAMESPACE, u'sparql'), u'sparql')
            self.writer.endDocument()

def retToJSON(val):
    if isinstance(val,URIRef):
        return '"type": "uri", "value" : "%s"' % val
    elif isinstance(val,BNode) :
        return '"type": "bnode", "value" : "%s"' % val
    elif isinstance(val,Literal):
        if val.language != "":
            return '"type": "literal", "xml:lang" : "%s", "value" : "%s"' % (val.language, val)
            attr += ' xml:lang="%s" ' % val.language
        elif val.datatype != "" and val.datatype != None:
            return '"type": "typed=literal", "datatype" : "%s", "value" : "%s"' % (val.datatype, val)
        else:
            return '"type": "literal", "value" : "%s"' % val
    else:
        return '"type": "literal", "value" : "%s"' % val

def bindingJSON(name, val):
    if val == None:
        return ""
    retval = ''
    retval += '                   "%s" : {' % name
    retval += retToJSON(val)
#    retval += '}\n'
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
        result,selectionF,allVars,orderBy,distinct,topUnion = qResult
        self.topUnion = topUnion
        self.selected = result
        self.selectionF = selectionF
        self.allVariables = allVars
        self.orderBy = orderBy
        self.distinct = distinct

    def __len__(self):
        if isinstance(self.selected,list):
            return len(self.selected)
        else:
            return 1

    def __iter__(self):
        """Iterates over the result entries"""
        if isinstance(self.selected,list):
            for item in self.selected:
                if isinstance(item,basestring):
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
           allvarsL = self.allVariables
           if format == "json" :
               retval += '    "results" : {\n'
               retval += '          "ordered" : %s,\n' % (self.orderBy and 'true' or 'false')
               retval += '          "distinct" : %s,\n' % (self.distinct and 'true' or 'false')
               retval += '          "bindings" : [\n'
               for i in xrange(0,len(self.selected)):
                   hit = self.selected[i]
                   retval += '               {\n'
                   bindings = []
                   if len(self.selectionF) == 0:
                        for j in xrange(0, len(allvarsL)):
                            b = bindingJSON(allvarsL[j],hit[j])
                            if b != "":
                                bindings.append(b)
                   elif len(self.selectionF) == 1:
                       bindings.append(bindingJSON(self.selectionF[0][1:],hit))
                   else:
                        for j in xrange(0, len(self.selectionF)):
                            b = bindingJSON(self.selectionF[j][1:],hit[j])
                            if b != "":
                                bindings.append(b)
                           
                   retval += "},\n".join(bindings)
                   retval += "}\n"
                   retval += '                }'
                   if i != len(self.selected) -1:
                       retval += ',\n'
                   else:
                       retval += '\n'
               retval += '           ]\n'
               retval += '    }\n'
               retval += '}\n'
               
               selected_vars = self.selectionF
               
               if len(selected_vars) == 0:
                   selected_vars = allvarsL
                   
               header = ""
               header += '{\n'
               header += '   "head" : {\n        "vars" : [\n'
               for i in xrange(0,len(selected_vars)) :
                   header += '             "%s"' % selected_vars[i][1:]
                   if i == len(selected_vars) - 1 :
                       header += '\n'
                   else :
                       header += ',\n'
               header += '         ]\n'
               header += '    },\n'
               
               retval = header + retval
               
           elif format == "xml" :
               # xml output
               out = StringIO()
               writer = SPARQLXMLWriter(out)
               writer.write_header(allvarsL)
               writer.write_results_header(self.orderBy,self.distinct)
               if self.topUnion:
                   for binding in self.topUnion:
                       writer.write_start_result()
                       for key,val in binding.items():
                           if not self.selectionF or \
                              key in self.selectionF:                               
                               writer.write_binding(key,val)
                       writer.write_end_result()
               else:
                   for i in xrange(0,len(self.selected)) :
                       hit = self.selected[i]
                       if len(self.selectionF) == 0 :
                           if topUnion:
                               print topUnion
                               #raise
                           writer.write_start_result()
                           if len(allvarsL) == 1:
                               hit = (hit,) # Not an iterable - a parser bug?   
                           for j in xrange(0,len(allvarsL)) :
                               if not len(hit) < j+1:
                                   writer.write_binding(allvarsL[j],hit[j])
                           writer.write_end_result()
                       elif len(self.selectionF) == 1 :
                           writer.write_start_result()
                           writer.write_binding(self.selectionF[0][1:],hit)
                           writer.write_end_result()
                       else:
                           writer.write_start_result()
                           for j in xrange(0,len(self.selectionF)) :
                               writer.write_binding(self.selectionF[j][1:],hit[j])
                           writer.write_end_result()
               writer.close()
               return out.getvalue()

           return retval
        else:
           raise Exception("Result format not implemented: %s"%format)

