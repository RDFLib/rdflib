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
from rdflib import RDF, RDFS
from rdflib import URIRef, BNode, Literal
from rdflib.exceptions import ParserError, Error
from rdflib.syntax.xml_names import is_ncname

from xml.sax.saxutils import handler, quoteattr
from urlparse import urljoin, urldefrag

RDFNS = RDF.RDFNS

# http://www.w3.org/TR/rdf-syntax-grammar/#eventterm-attribute-URI
# A mapping from unqualified terms to there qualified version.
UNQUALIFIED = {"about" : RDF.about,
               "ID" : RDF.ID, 
               "type" : RDF.type,
               "resource": RDF.resource,
               "parseType": RDF.parseType}

# http://www.w3.org/TR/rdf-syntax-grammar/#coreSyntaxTerms
CORE_SYNTAX_TERMS = [RDF.RDF, RDF.ID, RDF.about, RDF.parseType, RDF.resource, RDF.nodeID, RDF.datatype]

# http://www.w3.org/TR/rdf-syntax-grammar/#syntaxTerms
SYNTAX_TERMS = CORE_SYNTAX_TERMS + [RDF.Description, RDF.li]

# http://www.w3.org/TR/rdf-syntax-grammar/#oldTerms
OLD_TERMS = [RDFNS["aboutEach"], RDFNS["aboutEachPrefix"], RDFNS["bagID"]]

NODE_ELEMENT_EXCEPTIONS = CORE_SYNTAX_TERMS + [RDF.li,] + OLD_TERMS
NODE_ELEMENT_ATTRIBUTES = [RDF.ID, RDF.nodeID, RDF.about]

PROPERTY_ELEMENT_EXCEPTIONS = CORE_SYNTAX_TERMS + [RDF.Description,] + OLD_TERMS
PROPERTY_ATTRIBUTE_EXCEPTIONS = CORE_SYNTAX_TERMS + [RDF.Description, RDF.li] + OLD_TERMS
PROPERTY_ELEMENT_ATTRIBUTES = [RDF.ID, RDF.resource, RDF.nodeID]

XMLNS = "http://www.w3.org/XML/1998/namespace"
BASE = (XMLNS, "base")
LANG = (XMLNS, "lang")


class BagID(URIRef):
    __slots__ = ['li']
    def __init__(self, val):
        super(URIRef, self).__init__(val)
        self.li = 0

    def next_li(self):
        self.li += 1
        return URIRef(RDFNS + "_%s" % self.li)        


class ElementHandler(object):
    __slots__ = ['start', 'char', 'end', 'li', 'id',
                 'base', 'subject', 'predicate', 'object',
                 'list', 'language', 'datatype', 'declared']
    def __init__(self):
        self.start = None
        self.char = None
        self.end = None
        self.li = 0
        self.id = None
        self.base = None
        self.subject = None
        self.object = None
        self.list = None
        self.language = ""
        self.datatype = ""
        self.declared = None

    def next_li(self):
        self.li += 1
        return URIRef(RDFNS + "_%s" % self.li)


class RDFXMLHandler(handler.ContentHandler):

    def __init__(self, store):
        self.store = store
        self.reset()
        
    def reset(self):
        document_element = ElementHandler()
        document_element.start = self.document_element_start
        document_element.end = lambda name, qname: None
        self.stack = [None, document_element,]
        self.ids = {} # remember IDs we have already seen
        self.bnode = {}
        self._ns_contexts = [{}] # contains uri -> prefix dicts
        self._current_context = self._ns_contexts[-1]

    # ContentHandler methods

    def setDocumentLocator(self, locator):
        self.locator = locator

    def startDocument(self):
        pass

    def startPrefixMapping(self, prefix, namespace):
        self._ns_contexts.append(self._current_context.copy())
        self._current_context[namespace] = prefix
        self.store.bind(prefix, namespace)

    def endPrefixMapping(self, prefix):
        self._current_context = self._ns_contexts[-1]
        del self._ns_contexts[-1]

    def startElementNS(self, name, qname, attrs):
        stack = self.stack
        stack.append(ElementHandler())
        current = self.current
        parent = self.parent
        base = attrs.get(BASE, None)
        if base is not None:
            base, frag = urldefrag(base)
        else:
            if parent:
                base = parent.base
            if base is None:
                systemId = self.locator.getPublicId() or self.locator.getSystemId()
                if systemId:
                    base, frag = urldefrag(systemId)
        current.base = base
        language = attrs.get(LANG, None)
        if language is None:
            if parent:
                language = parent.language
            else:
                language = ''
        current.language = language
        current.start(name, qname, attrs)        
            
    def endElementNS(self, name, qname):
        self.current.end(name, qname)
        self.stack.pop()
    
    def characters(self, content):
        char = self.current.char
        if char:
            char(content)        

    def ignorableWhitespace(self, content):
        pass

    def processingInstruction(self, target, data):
        pass

    def add_reified(self, sid, (s, p, o)):
        self.store.add((sid, RDF.type, RDF.Statement))
        self.store.add((sid, RDF.subject, s))
        self.store.add((sid, RDF.predicate, p))
        self.store.add((sid, RDF.object, o))

    def error(self, message):
        locator = self.locator
        info = "%s:%s:%s: " % (locator.getSystemId(),
                            locator.getLineNumber(), locator.getColumnNumber())
        raise ParserError(info + message)
    
    def get_current(self):
        return self.stack[-2]
    # Create a read only property called current so that self.current
    # give the current element handler.
    current = property(get_current)

    def get_next(self):
        return self.stack[-1]
    # Create a read only property that gives the element handler to be
    # used for the next element.
    next = property(get_next)

    def get_parent(self):
        return self.stack[-3]
    # Create a read only property that gives the current parent
    # element handler
    parent = property(get_parent)

    def absolutize(self, uri):
        s = urljoin(self.current.base, uri, allow_fragments=1)        
        if uri and uri[-1]=="#":
            return URIRef(''.join((s, "#")))
        else:
            return URIRef(s)

    def convert(self, name, qname, attrs):
        if name[0] is None:
            name = name[1]
        else:
            name = "".join(name)
        atts = {}
        for (n, v) in attrs.items(): #attrs._attrs.iteritems(): #
            if n[0] is None:
                att = n[1]
            else:
                att = "".join(n)
            if att.startswith(XMLNS) or att[0:3].lower()=="xml":
                pass
            elif att in UNQUALIFIED:
                #if not RDFNS[att] in atts:
                atts[RDFNS[att]] = v
            else:
                atts[att] = v
        return name, atts

    def document_element_start(self, name, qname, attrs):
        if name[0] and "".join(name) == RDF.RDF:
            next = self.next
            next.start = self.node_element_start
            next.end = self.node_element_end
        else:
            self.node_element_start(name, qname, attrs)
            #self.current.end = self.node_element_end
            # TODO... set end to something that sets start such that
            # another element will cause error
            

    def node_element_start(self, name, qname, attrs):
        name, atts = self.convert(name, qname, attrs)
        current = self.current
        absolutize = self.absolutize
        next = self.next
        next.start = self.property_element_start
        next.end = self.property_element_end

        if name in NODE_ELEMENT_EXCEPTIONS:
            self.error("Invalid node element URI: %s" % name)

        if RDF.ID in atts:
            if RDF.about in atts or RDF.nodeID in atts:
                self.error("Can have at most one of rdf:ID, rdf:about, and rdf:nodeID")

            id = atts[RDF.ID]
            if not is_ncname(id):
                self.error("rdf:ID value is not a valid NCName: %s" % id)
            subject = absolutize("#%s" % id)
            if subject in self.ids:
                self.error("two elements cannot use the same ID: '%s'" % subject)
            self.ids[subject] = 1 # IDs can only appear once within a document
        elif RDF.nodeID in atts:
            if RDF.ID in atts or RDF.about in atts:
                self.error("Can have at most one of rdf:ID, rdf:about, and rdf:nodeID")
            nodeID = atts[RDF.nodeID]
            if not is_ncname(nodeID):
                self.error("rdf:nodeID value is not a valid NCName: %s" % nodeID)
            if nodeID in self.bnode:
                subject = self.bnode[nodeID]
            else:
                subject = BNode()
                self.bnode[nodeID] = subject
        elif RDF.about in atts:
            if RDF.ID in atts or RDF.nodeID in atts:
                self.error("Can have at most one of rdf:ID, rdf:about, and rdf:nodeID")
            subject = absolutize(atts[RDF.about])
        else:
            subject = BNode()

        if name!=RDF.Description: # S1
            self.store.add((subject, RDF.type, absolutize(name)))

        language = current.language
        for att in atts:
            if not att.startswith(RDFNS):
                predicate = absolutize(att)
                try:
                    object = Literal(atts[att], language)
                except Error, e:
                    self.error(e.msg)                
            elif att==RDF.type: #S2
                predicate = RDF.type
                object = absolutize(atts[RDF.type])
            elif att in NODE_ELEMENT_ATTRIBUTES:
                continue
            elif att in PROPERTY_ATTRIBUTE_EXCEPTIONS: #S3
                self.error("Invalid property attribute URI: %s" % att)
                continue # for when error does not throw an exception
            else:
                predicate = absolutize(att)
                try:
                    object = Literal(atts[att], language)
                except Error, e:
                    self.error(e.msg)                    
            self.store.add((subject, predicate, object))

        current.subject = subject

        
    def node_element_end(self, name, qname):
        self.parent.object = self.current.subject
        
    def property_element_start(self, name, qname, attrs):
        name, atts = self.convert(name, qname, attrs)
        current = self.current
        absolutize = self.absolutize        
        next = self.next
        object = None
        current.list = None

        if not name.startswith(RDFNS):
            current.predicate = absolutize(name)            
        elif name==RDF.li:
            current.predicate = current.next_li()
        elif name in PROPERTY_ELEMENT_EXCEPTIONS:
            self.error("Invalid property element URI: %s" % name)
        else:
            current.predicate = absolutize(name)            

        id = atts.get(RDF.ID, None)
        if id is not None:
            if not is_ncname(id):
                self.error("rdf:ID value is not a value NCName: %s" % id)
            current.id = absolutize("#%s" % id)
        else:
            current.id = None

        resource = atts.get(RDF.resource, None)
        nodeID = atts.get(RDF.nodeID, None)
        parse_type = atts.get(RDF.parseType, None)
        if resource is not None and nodeID is not None:
            self.error("Property element cannot have both rdf:nodeID and rdf:resource")
        if resource is not None:
            object = absolutize(resource)
            next.start = self.node_element_start
            next.end = self.node_element_end
        elif nodeID is not None:
            if not is_ncname(nodeID):
                self.error("rdf:nodeID value is not a valid NCName: %s" % nodeID)
            if nodeID in self.bnode:
                object = self.bnode[nodeID]
            else:
                subject = BNode()
                self.bnode[nodeID] = subject
                object = subject
            next.start = self.node_element_start
            next.end = self.node_element_end                
        else:
            if parse_type is not None:
                for att in atts:
                    if att!=RDF.parseType and att!=RDF.ID:
                        self.error("Property attr '%s' now allowed here" % att)
                if parse_type=="Resource": 
                    current.subject = object = BNode()
                    current.char = self.property_element_char                    
                    next.start = self.property_element_start
                    next.end = self.property_element_end
                elif parse_type=="Collection":
                    current.char = None                    
                    next.start = self.node_element_start
                    next.end = self.list_node_element_end
                else: #if parse_type=="Literal":
                     # All other values are treated as Literal
                     # See: http://www.w3.org/TR/rdf-syntax-grammar/#parseTypeOtherPropertyElt
                    object = Literal("", "", RDF.XMLLiteral)
                    current.char = self.literal_element_char
                    current.declared = {}
                    next.start = self.literal_element_start
                    next.char = self.literal_element_char
                    next.end = self.literal_element_end
                current.object = object
                return
            else:
                object = None
                current.char = self.property_element_char
                next.start = self.node_element_start
                next.end = self.node_element_end                

        datatype = current.datatype = atts.get(RDF.datatype, None)
        language = current.language        
        if datatype is not None:
            # TODO: check that there are no atts other than datatype and id
            pass
        else:
            for att in atts:
                if not att.startswith(RDFNS):
                    predicate = absolutize(att)                        
                elif att in PROPERTY_ELEMENT_ATTRIBUTES:
                    continue
                elif att in PROPERTY_ATTRIBUTE_EXCEPTIONS:
                    self.error("""Invalid property attribute URI: %s""" % att)
                else:
                    predicate = absolutize(att)                    

                if att==RDF.type:
                    o = URIRef(atts[att])
                else:
                    o = Literal(atts[att], language, datatype)

                if object is None:
                    object = BNode()
                self.store.add((object, predicate, o))
        if object is None:
            object = Literal("", language, datatype)                
        current.object = object

    def property_element_char(self, data):
        current = self.current
        if current.object is None:
            try:
                current.object = Literal(data, current.language, current.datatype)
            except Error, e:
                self.error(e.msg)                
        else:
            if isinstance(current.object, Literal):
                try:
                    current.object += data
                except Error, e:
                    self.error(e.msg)
            
    def property_element_end(self, name, qname):
        current = self.current
        if self.next.end==self.list_node_element_end:
            self.store.add((current.list, RDF.rest, RDF.nil))
        if current.object is not None:
            self.store.add((self.parent.subject, current.predicate, current.object))
            if current.id is not None:
                self.add_reified(current.id, (self.parent.subject,
                                 current.predicate, current.object))
        current.subject = None

    def list_node_element_end(self, name, qname):
        current = self.current        
        if not self.parent.list:
            list = BNode()
            # Removed between 20030123 and 20030905
            #self.store.add((list, RDF.type, LIST))
            self.parent.list = list
            self.store.add((self.parent.list, RDF.first, current.subject))
            self.parent.object = list
            self.parent.char = None            
        else:
            list = BNode()
            # Removed between 20030123 and 20030905            
            #self.store.add((list, RDF.type, LIST))
            self.store.add((self.parent.list, RDF.rest, list))
            self.store.add((list, RDF.first, current.subject))
            self.parent.list = list

    def literal_element_start(self, name, qname, attrs):
        current = self.current
        self.next.start = self.literal_element_start
        self.next.char = self.literal_element_char
        self.next.end = self.literal_element_end
        current.declared = self.parent.declared.copy()
        if name[0]:
            prefix = self._current_context[name[0]]
            if prefix:
                current.object = "<%s:%s" % (prefix, name[1])
            else:
                current.object = "<%s" % name[1]
            if not name[0] in current.declared:
                current.declared[name[0]] = prefix
                if prefix:
                    current.object += (' xmlns:%s="%s"' % (prefix, name[0]))
                else:
                    current.object += (' xmlns="%s"' % name[0])
        else:
            current.object = "<%s" % name[1]

        for (name, value) in attrs.items():
            if name[0]:
                if not name[0] in current.declared:
                    current.declared[name[0]] = self._current_context[name[0]]
                name = current.declared[name[0]] + ":" + name[1]
            else:
                name = name[1]
            current.object += (' %s=%s' % (name, quoteattr(value)))
        current.object += ">"

    def literal_element_char(self, data):
        self.current.object += data
        
    def literal_element_end(self, name, qname):
        if name[0]:
            prefix = self._current_context[name[0]]
            if prefix:
                end = u"</%s:%s>" % (prefix, name[1])
            else:
                end = u"</%s>" % name[1]
        else:
            end = u"</%s>" % name[1]
        self.parent.object += self.current.object + end
