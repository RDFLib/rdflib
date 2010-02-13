# Copyright (c) 2002, Daniel Krech, http://eikeon.com/
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided
# with the distribution.
#
#   * Neither the name of Daniel Krech nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
"""
from rdflib.namespace import Namespace
from rdflib.term import URIRef
from rdflib.term import BNode
from rdflib.term import Literal
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib.exceptions import ParserError
from rdflib.parser import Parser

from xml.sax.saxutils import handler
from xml.sax import make_parser
from xml.sax.handler import ErrorHandler


TRIXNS=Namespace("http://www.w3.org/2004/03/trix/trix-1/")
XMLNS=Namespace("http://www.w3.org/XML/1998/namespace")

class TriXHandler(handler.ContentHandler):
    """An Sax Handler for TriX. See http://swdev.nokia.com/trix/TriX.html"""

    def __init__(self, store):
        self.store = store
        self.preserve_bnode_ids = False
        self.reset()

    def reset(self):
        self.bnode = {}
        self.graph=self.store
        self.triple=None
        self.state=0
        self.lang=None
        self.datatype=None

    # ContentHandler methods

    def setDocumentLocator(self, locator):
        self.locator = locator

    def startDocument(self):
        pass

    def startPrefixMapping(self, prefix, namespace):
        pass

    def endPrefixMapping(self, prefix):
        pass

    def startElementNS(self, name, qname, attrs):
    
        if name[0]!=str(TRIXNS):
            self.error("Only elements in the TriX namespace are allowed. %s!=%s"%(name[0],TRIXNS))

        if name[1]=="TriX":
            if self.state==0:
                self.state=1
            else:
                self.error("Unexpected TriX element")

        elif name[1]=="graph":
            if self.state==1:
                self.state=2
            else:
                self.error("Unexpected graph element")

        elif name[1]=="uri":
            if self.state==2:
                # the context uri
                self.state=3
            elif self.state==4:
                # part of a triple
                pass
            else:
                self.error("Unexpected uri element")

        elif name[1]=="triple":
            if self.state==2:
                if self.graph==None: 
                    # anonymous graph, create one with random bnode id
                    self.graph=Graph(store=self.store.store)
                # start of a triple
                self.triple=[]
                self.state=4
            else:
                self.error("Unexpected triple element")

        elif name[1]=="typedLiteral":
            if self.state==4:
                # part of triple
                self.lang=None
                self.datatype=None

                try:
                    self.lang=attrs.getValue((unicode(XMLNS), u"lang"))
                except:
                    # language not required - ignore
                    pass
                try: 
                    self.datatype=attrs.getValueByQName(u"datatype")
                except KeyError:
                    self.error("No required attribute 'datatype'")
            else:
                self.error("Unexpected typedLiteral element")
                
        elif name[1]=="plainLiteral":
            if self.state==4:
                # part of triple
                self.lang=None
                self.datatype=None
                try:
                    self.lang=attrs.getValue((unicode(XMLNS), u"lang"))
                except:
                    # language not required - ignore
                    pass

            else:
                self.error("Unexpected plainLiteral element")

        elif name[1]=="id":
            if self.state==2:
                # the context uri
                self.state=3

            elif self.state==4:
                # part of triple
                pass
            else:
                self.error("Unexpected id element")
        
        else:
            self.error("Unknown element %s in TriX namespace"%name[1])

        self.chars=""

    
    def endElementNS(self, name, qname):
        if name[0]!=str(TRIXNS):
            self.error("Only elements in the TriX namespace are allowed. %s!=%s"%(name[0], TRIXNS))

        if name[1]=="uri":
            if self.state==3:
                self.graph=Graph(store=self.store.store, identifier=URIRef(self.chars.strip()))
                self.state=2
            elif self.state==4:
                self.triple+=[URIRef(self.chars.strip())]
            else:
                self.error("Illegal internal self.state - This should never happen if the SAX parser ensures XML syntax correctness")

        elif name[1]=="id":
            if self.state==3:
                self.graph=Graph(self.store.store,identifier=self.get_bnode(self.chars.strip()))
                self.state=2
            elif self.state==4:
                self.triple+=[self.get_bnode(self.chars.strip())]
            else:
                self.error("Illegal internal self.state - This should never happen if the SAX parser ensures XML syntax correctness")

        elif name[1]=="plainLiteral" or name[1]=="typedLiteral":
            if self.state==4:
                self.triple+=[Literal(self.chars, lang=self.lang, datatype=self.datatype)]
            else:
                self.error("This should never happen if the SAX parser ensures XML syntax correctness")

        elif name[1]=="triple":
            if self.state==4:
                if len(self.triple)!=3:
                    self.error("Triple has wrong length, got %d elements: %s"%(len(self.triple),self.triple))

                self.graph.add(self.triple)
                #self.store.store.add(self.triple,context=self.graph)
                #self.store.addN([self.triple+[self.graph]])
                self.state=2
            else:
                self.error("This should never happen if the SAX parser ensures XML syntax correctness")
                
        elif name[1]=="graph":
            self.graph=None
            self.state=1

        elif name[1]=="TriX":
            self.state=0
        
        else: 
            self.error("Unexpected close element")


    def get_bnode(self,label):
        if self.preserve_bnode_ids:
            bn=BNode(label)
        else:
            if label in self.bnode:
                bn=self.bnode[label]
            else: 
                bn=BNode(label)
                self.bnode[label]=bn
        return bn
                

    def characters(self, content):
        self.chars+=content

    
    def ignorableWhitespace(self, content):
        pass

    def processingInstruction(self, target, data):
        pass

    
    def error(self, message):
        locator = self.locator
        info = "%s:%s:%s: " % (locator.getSystemId(),
                            locator.getLineNumber(), locator.getColumnNumber())
        raise ParserError(info + message)


def create_parser(store):
    parser = make_parser()
    # Workaround for bug in expatreader.py. Needed when
    # expatreader is trying to guess a prefix.
    parser.start_namespace_decl("xml", "http://www.w3.org/XML/1998/namespace")
    parser.setFeature(handler.feature_namespaces, 1)
    trix = TriXHandler(store)
    parser.setContentHandler(trix)
    parser.setErrorHandler(ErrorHandler())
    return parser


class TriXParser(Parser):
    """A parser for TriX. See http://swdev.nokia.com/trix/TriX.html"""

    def __init__(self):
        pass

    def parse(self, source, sink, **args):
        assert sink.store.context_aware
        g=ConjunctiveGraph(store=sink.store)
        
        self._parser = create_parser(g)
        content_handler = self._parser.getContentHandler()
        preserve_bnode_ids = args.get("preserve_bnode_ids", None)
        if preserve_bnode_ids is not None:
            content_handler.preserve_bnode_ids = preserve_bnode_ids
        # We're only using it once now
        #content_handler.reset()
        #self._parser.reset()
        self._parser.parse(source)



