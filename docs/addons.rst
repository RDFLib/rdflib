.. _addons: Additions

=========
Additions
=========

TriXSerializer
==============

John L. Clark jlc6 at po.cwru.edu 

Tue Aug 7 01:55:07 EDT 2007

.. note:: Devs,

    I've taken a first pass at implementing a simple TriX serializer.  I
    should have attached the new file (which goes in
    `.../rdflib/syntax/serializers/TriXSerializer.py`) to this email,
    along with a crazy little test script.  The test script exercises
    round tripping, but it turned out parsing was broken, so I fixed it;
    the patch for that (and adding the new serializer to the plugin list)
    should be attached as well.  Finally, does anyone mind if I clean up
    the TriX parser a bit?

    Take care,

        John L. Clark


TriXSerializer.py
-----------------

.. code-block:: python

    from rdflib.syntax.serializers import Serializer

    from rdflib.URIRef import URIRef
    from rdflib.Literal import Literal
    from rdflib.BNode import BNode

    from rdflib.Graph import Graph, ConjunctiveGraph

    from Ft.Xml import MarkupWriter, XML_NAMESPACE

    TRIX_NS = u"http://www.w3.org/2004/03/trix/trix-1/"

    class TriXSerializer(Serializer):
        def __init__(self, store):
            super(TriXSerializer, self).__init__(store)

        def serialize(self, stream, base=None, encoding=None, **args):
            self.writer = MarkupWriter(stream=stream, encoding=encoding,
                                        indent="yes")
            self.writer.startDocument()
            self.writer.startElement(u"TriX", TRIX_NS)

            if isinstance(self.store, ConjunctiveGraph):
                for subgraph in self.store.contexts():
                    self._writeGraph(subgraph)
            elif isinstance(self.store, Graph):
                self._writeGraph(self.store)
            else:
                pass

            self.writer.endElement(u"TriX", TRIX_NS)
            self.writer.endDocument()

        def _writeGraph(self, graph):
            self.writer.startElement(u"graph", TRIX_NS)
            if isinstance(graph.identifier, URIRef):
                self.writer.simpleElement(u"uri", TRIX_NS,
                                            content=unicode(graph.identifier))
            
            for triple in graph.triples((None,None,None)):
                self._writeTriple(triple)
            self.writer.endElement(u"graph", TRIX_NS)

        def _writeTriple(self, triple):
            self.writer.startElement(u"triple", TRIX_NS)
            for component in triple:
                if isinstance(component, URIRef):
                    self.writer.simpleElement(u"uri", TRIX_NS,
                                            content=unicode(component))
                elif isinstance(component, BNode):
                    self.writer.simpleElement(u"id", TRIX_NS,
                                            content=unicode(component))
                elif isinstance(component, Literal):
                    if component.datatype:
                        self.writer.simpleElement(u"typedLiteral", TRIX_NS,
                            content=unicode(component),
                            attributes={u"datatype": unicode(component.datatype)})
                    elif component.language:
                        self.writer.simpleElement(u"plainLiteral", TRIX_NS,
                            content=unicode(component),
                            attributes={
                                (u"xml:lang", XML_NAMESPACE): unicode(component.language)})
                    else:
                        self.writer.simpleElement(u"plainLiteral", TRIX_NS,
                            content=unicode(component))
            self.writer.endElement(u"triple", TRIX_NS)

trixserializer.diff
-------------------

.. code-block:: text

    Index: rdflib/plugin.py
    ===================================================================
    --- rdflib/plugin.py	(revision 1239)
    +++ rdflib/plugin.py	(working copy)
    @@ -49,6 +49,9 @@
     register('pretty-xml', serializers.Serializer,
              'rdflib.syntax.serializers.PrettyXMLSerializer', 'PrettyXMLSerializer')
 
    +register('TriX', serializers.Serializer,
    +         'rdflib.syntax.serializers.TriXSerializer', 'TriXSerializer')
    +
     register('nt', serializers.Serializer,
              'rdflib.syntax.serializers.NTSerializer', 'NTSerializer')
 
    Index: rdflib/syntax/parsers/TriXHandler.py
    ===================================================================
    --- rdflib/syntax/parsers/TriXHandler.py	(revision 1239)
    +++ rdflib/syntax/parsers/TriXHandler.py	(working copy)
    @@ -33,6 +33,7 @@
     """
     from rdflib import RDF, RDFS, Namespace
     from rdflib import URIRef, BNode, Literal
    +from rdflib.Namespace import Namespace
     from rdflib.Graph import Graph
     from rdflib.exceptions import ParserError, Error
     from rdflib.syntax.xml_names import is_ncname
    @@ -42,7 +43,7 @@
 
     RDFNS = RDF.RDFNS
 
    -TRIXNS=Namespace.Namespace("http://www.w3.org/2004/03/trix/trix-1/")
    +TRIXNS=u"http://www.w3.org/2004/03/trix/trix-1/"
 
 
     class TriXHandler(handler.ContentHandler):
    @@ -200,6 +201,7 @@
                     self.error("This should never happen if the SAX parser ensures XML syntax correctness")
 
             if name[1]=="graph":
    +            self.graph = Graph(store = self.store.store)
                 self.state=1
 
             if name[1]=="TriX":

test_trixserializer.py
----------------------

.. code-block:: python

    from rdflib.Graph import ConjunctiveGraph
    from rdflib import URIRef, Literal
    from rdflib.Graph import Graph

    s1 = URIRef('store:1')
    r1 = URIRef('resource:1')
    r2 = URIRef('resource:2')

    label = URIRef('predicate:label')

    g1 = Graph(identifier = s1)
    g1.add((r1, label, Literal("label 1", lang="en")))
    g1.add((r1, label, Literal("label 2")))

    s2 = URIRef('store:2')
    g2 = Graph(identifier = s2)
    g2.add((r2, label, Literal("label 3")))

    g = ConjunctiveGraph()

    for s,p,o in g1.triples((None, None, None)):
        g.addN([(s,p,o,g1)])

    for s,p,o in g2.triples((None, None, None)):
        g.addN([(s,p,o,g2)])

    r3 = URIRef('resource:3')

    g.add((r3, label, Literal(4)))
    #g.addN([(r1, label, Literal("label 1"), s1),
    #        (r1, label, Literal("label 2"), s1),
    #        (r2, label, Literal("label 3"), s2)])

    for c in g.contexts():
        pass
        #s = Graph(g.store, identifier=c)
        #print c, c.identifier.__class__, c.identifier, len(c)

    r = g.serialize(format='TriX')
    print r

    g3 = ConjunctiveGraph()
    from rdflib.StringInputSource import StringInputSource
    g3.parse(StringInputSource(r, None), format='trix')
    for c in g3.contexts():
        print c, c.identifier.__class__, c.identifier, len(c)


test output
-----------

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <TriX xmlns="http://www.w3.org/2004/03/trix/trix-1/">
      <graph>
        <uri>store:2</uri>
        <triple>
          <uri>resource:2</uri>
          <uri>predicate:label</uri>
          <plainLiteral>label 3</plainLiteral>
        </triple>
      </graph>
      <graph>
        <uri>store:1</uri>
        <triple>
          <uri>resource:1</uri>
          <uri>predicate:label</uri>
          <plainLiteral>label 2</plainLiteral>
        </triple>
        <triple>
          <uri>resource:1</uri>
          <uri>predicate:label</uri>
          <plainLiteral xml:lang="en">label 1</plainLiteral>
        </triple>
      </graph>
      <graph>
        <triple>
          <uri>resource:3</uri>
          <uri>predicate:label</uri>
          <typedLiteral datatype="http://www.w3.org/2001/XMLSchema#integer">4</typedLiteral>
        </triple>
      </graph>
    </TriX>

.. code-block:: n3

    [a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'IOMemory']]. 
    <class 'rdflib.BNode.BNode'> QeDIviuA11 1
    <store:2> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'IOMemory']. 
    <class 'rdflib.URIRef.URIRef'> store:2 1
    <store:1> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'IOMemory']. 
    <class 'rdflib.URIRef.URIRef'> store:1 2

SPARQL-XML Serializer
=====================

.. code-block:: python

    # -*- coding: iso-8859-15 -*-
    # (c) Mikael Högqvist, ZIB, AstroGrid-D
    # This software is licensed under the software license specified at
    # http://www.gac-grid.org/

    # this is a work-around of the SPARQL XML-serialization in rdflib which does
    # not work on all installation due to a bug in the python sax-parser
    # We rely on ElementTree which is only available in Python 2.5

    from cStringIO import StringIO

    try:
        from xml.etree.cElementTree import Element, SubElement, ElementTree, ProcessingInstruction
        import xml.etree.cElementTree as ET
    except ImportError:
        from cElementTree import Element, SubElement, ElementTree
        import cElementTree as ET

    from rdflib import URIRef, BNode, Literal

    SPARQL_XML_NAMESPACE = u'http://www.w3.org/2005/sparql-results#'
    XML_NAMESPACE = "http://www.w3.org/2001/XMLSchema#"

    name = lambda elem: u'{%s}%s' % (SPARQL_XML_NAMESPACE, elem)
    xml_name = lambda elem: u'{%s}%s' % (XML_NAMESPACE, elem)

    def variables(results):
        # don't include any variables which are not part of the
        # result set
        #res_vars = set(results.selectionF).intersection(set(results.allVariables))
    
    
        # this means select *, use all variables from the result-set
        if len(results.selectionF) == 0:
            res_vars = results.allVariables
        else:
            res_vars = [v for v in results.selectionF if v in results.allVariables]
        
        return res_vars
    
    def header(results, root):
        head = SubElement(root, name(u'head'))
    
        res_vars = variables(results)    
        for var in res_vars:
            v = SubElement(head, name(u'variable'))
            # remove the ?
            v.attrib[u'name'] = var[1:]

        
    def binding(val, var, elem):
        bindingElem = SubElement(elem, name(u'binding'))
        bindingElem.attrib[u'name'] = var
    
        if isinstance(val,URIRef):
            varElem = SubElement(bindingElem, name(u'uri'))
        elif isinstance(val,BNode) :
            varElem = SubElement(bindingElem, name(u'bnode'))
        elif isinstance(val,Literal):
            varElem = SubElement(bindingElem, name(u'literal'))
        
            if val.language != "" and val.language != None:
                varElem.attrib[xml_name(u'lang')] = str(val.language)
            elif val.datatype != "" and val.datatype != None:
                varElem.attrib[name(u'datatype')] = str(val.datatype)

        varElem.text = str(val)

    def res_iter(results):
        res_vars = variables(results)
    
        for row in results.selected:
            if len(res_vars) == 1:
                row = (row, )
        
            yield zip(row, res_vars)
              
    def result_list(results, root):
        resultsElem = SubElement(root, name(u'results'))
    
        ordered = results.orderBy
    
        if ordered == None:
            ordered = False
    
        # removed according to the new working draft (2007-06-14)    
        # resultsElem.attrib[u'ordered'] = str(ordered)
        # resultsElem.attrib[u'distinct'] = str(results.distinct)

        for row in res_iter(results):
            resultElem = SubElement(resultsElem, name(u'result'))
            # remove the ? from the variable name
            [binding(val, var[1:], resultElem) for (val, var) in row] 
    
    def serializeXML(results):    
        root = Element(name(u'sparql'))
    
        header(results, root)
        result_list(results, root)
    
        out = StringIO()
        tree = ElementTree(root)

        # xml declaration must be written by hand
        # http://www.nabble.com/Writing-XML-files-with-ElementTree-t3433325.html
        out.write('<?xml version="1.0" encoding="utf-8"?>')
        out.write('<?xml-stylesheet type="text/xsl" href="/static/sparql-xml-to-html.xsl"?>')
        tree.write(out, encoding='utf-8')
    
        return out.getvalue()
