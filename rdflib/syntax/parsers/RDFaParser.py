"""
RDFa parser.

RDFa is a set of attributes used to embed RDF in XHTML. An important goal of
RDFa is to achieve this RDF embedding without repeating existing XHTML content
when that content is the metadata.

REFERENCES:

	http://www.w3.org/2001/sw/BestPractices/HTML/2005-rdfa-syntax

LICENSE:

  BSD

CHANGE HISTORY:

  2006/06/03 - Initial Version
  2006/06/08 - Added support for role (as per primer not syntax spec)
               Added support for plaintext and flattening of XMLLiterals
               ... (Sections 5.1.1.2 and 5.1.2.1)
               Fixed plaintext bug where it was being resolved as CURIE
               Added support to skip reserved @rel keywords from:
                 http://www.w3.org/TR/REC-html40/types.html#h-6.12
  2006/08/12 - Changed reserved @rel resolution to include a '#'
               Fixed subject resolution for LINK/META when inside HEAD
               Fixed blank node extraction [_:address] -> [_:_:address]
               Added support for passing prefix mappings to the Graph
               via RDFaSink
               Added @id support as part of subject resolution

Copyright (c) 2006, Elias Torres <elias@torrez.us>

"""

import sys, re, urllib, urlparse, cStringIO, string
from xml.dom import pulldom
from rdflib.syntax.parsers import Parser
from rdflib.Graph import ConjunctiveGraph
from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.Literal import Literal
from rdflib.Namespace import Namespace

__version__ = "$Id$"

rdfa_attribs = ["about","property","rel","rev","href","content","role","id"]

reserved_links = ['alternate', 'stylesheet', 'start', 'next', 'prev',
                 'contents', 'index', 'glossary', 'copyright', 'chapter',
                 'section', 'subsection', 'appendix', 'help', 'bookmark']

xhtml = Namespace("http://www.w3.org/1999/xhtml")
xml = Namespace("http://www.w3.org/XML/1998/namespace")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

class RDFaSink(object):
  def __init__(self, graph):
    self.graph = graph
  def __str__(self):
    return self.graph.serialize(format="pretty-xml")
  def triple(self, s, p, o):
    self.graph.add((s, p, o))
  def prefix(self, prefix, ns):
    self.graph.bind(prefix, ns, override=False)

_urifixer = re.compile('^([A-Za-z][A-Za-z0-9+-.]*://)(/*)(.*?)')

def _urljoin(base, uri):
  uri = _urifixer.sub(r'\1\3', uri)
  return urlparse.urljoin(base, uri)

class RDFaParser(Parser):
  def __init__(self):
    self.lang = None
    self.abouts = []
    self.xmlbases = []
    self.langs = []
    self.elementStack = [None]
    self.bcounter = {}
    self.bnodes = {}
    self.sink = None

  def parse(self, source, sink, baseURI=None):
    self.sink = RDFaSink(sink)
    self.triple = self.sink.triple
    self.prefix = self.sink.prefix
    self.baseuri = baseURI or source.getPublicId()
    f = source.getByteStream()
    events = pulldom.parse(f)
    self.handler = events.pulldom
    for (event, node) in events:

      if event == pulldom.START_DOCUMENT:
        self.abouts += [(URIRef(""), node)]

      if event == pulldom.END_DOCUMENT:
        assert len(self.elementStack) == 0

      if event == pulldom.START_ELEMENT:

        # keep track of parent node
        self.elementStack += [node]

        #if __debug__: print [e.tagName for e in self.elementStack if e]

        found = filter(lambda x:x in node.attributes.keys(),rdfa_attribs)

        # keep track of xml:lang xml:base
        baseuri = node.getAttributeNS(xml,"base") or node.getAttribute("xml:base") or self.baseuri
        self.baseuri = _urljoin(self.baseuri, baseuri)
        self.xmlbases.append(self.baseuri)

        if node.hasAttributeNS(xml,"lang") or node.hasAttribute("xml:lang"):
          lang = node.getAttributeNS(xml, 'lang') or node.getAttribute('xml:lang')

          if lang == '':
            # xml:lang could be explicitly set to '', we need to capture that
            lang = None
        else:
          # if no xml:lang is specified, use parent lang
          lang = self.lang

        self.lang = lang
        self.langs.append(lang)

        # node is not an RDFa element.
        if len(found) == 0: continue

        parentNode = self.elementStack[-2]

        if "about" in found:
          self.abouts += [(self.extractCURIEorURI(node.getAttribute("about")),node)]
        elif "id" in found:
          self.abouts += [(self.extractCURIEorURI("#" + node.getAttribute("id")),node)]

        subject = self.abouts[-1][0]

        # meta/link subject processing
        if(node.tagName == "meta" or node.tagName == "link"):
          if not("about" in found) and parentNode:
            if parentNode and parentNode.tagName == "head":
              subject = URIRef("")
            elif(parentNode.hasAttribute("about")):
              subject = self.extractCURIEorURI(parentNode.getAttribute("about"))
            elif parentNode.hasAttributeNS(xml,"id") or parentNode.hasAttribute("id"):
              # TODO: is this the right way to process xml:id by adding a '#'
              id = parentNode.getAttributeNS(xml,"id") or parentNode.getAttribute("id")
              subject = self.extractCURIEorURI("#" + id)
            else:
              subject = self.generateBlankNode(parentNode)

        if 'property' in found:
          predicate = self.extractCURIEorURI(node.getAttribute('property'))
          literal = None
          datatype = None
          plaintext = False

          if node.hasAttribute('datatype'):
            sdt = node.getAttribute('datatype')
            if sdt <> 'plaintext':
              datatype = self.extractCURIEorURI(sdt)
            else:
              plaintext = True

          if node.hasAttribute("content"):
            literal = Literal(node.getAttribute("content"), lang=lang, datatype=datatype)
          else:
            events.expandNode(node)

            # because I expanded, I won't get an END_ELEMENT
            self._popStacks(event, node)

            content = ""
            for child in node.childNodes:
              if datatype or plaintext:
                  content += self._getNodeText(child)
              else:
                content += child.toxml()
            content = content.strip()
            literal = Literal(content,datatype=datatype or rdf.XMLLiteral)

          if literal:
            self.triple(subject, predicate, literal)

        if "rel" in found:
          rel = node.getAttribute("rel").strip()
          if string.lower(rel) in reserved_links:
            rel = xhtml["#" + string.lower(rel)]

          predicate = self.extractCURIEorURI(rel)
          if node.hasAttribute("href"):
            object = self.extractCURIEorURI(node.getAttribute("href"))
            self.triple(subject, predicate, object)

        if "rev" in found:
          predicate = self.extractCURIEorURI(node.getAttribute("rev"))
          if node.hasAttribute("href"):
            object = self.extractCURIEorURI(node.getAttribute("href"))
            self.triple(object, predicate, subject)

        # role is in the primer, but not in the syntax.
        # could be deprecated.
        # Assumptions:
        # - Subject resolution as always (including meta/link)
        # - Attribute Value is a CURIE or URI
        # - It adds another triple, besides prop, rel, rev.
        if "role" in found:
          type = self.extractCURIEorURI(node.getAttribute('role'))
          self.triple(subject, rdf.type, type)

      if event == pulldom.END_ELEMENT:
        self._popStacks(event, node)
     
    # share with sink any prefix mappings
    for nsc in self.handler._ns_contexts:
      for ns, prefix in nsc.items():
        self.prefix(prefix, ns)

    f.close()

  def _getNodeText(self, node):
    if node.nodeType in (3,4): return node.nodeValue
    text = ''
    for child in node.childNodes:
      if child.nodeType in (3,4):
        text = text + child.nodeValue
    return text

  def generateBlankNode(self, parentNode):
    name = parentNode.tagName
    if self.bnodes.has_key(parentNode):
      return self.bnodes[parentNode]

    if self.bcounter.has_key(name):
      self.bcounter[name] = self.bcounter[name] + 1
    else:
      self.bcounter[name] = 0

    self.bnodes[parentNode] = BNode("%s%d" % (name, self.bcounter[name]))

    return self.bnodes[parentNode]

  def extractCURIEorURI(self, resource):
    if(len(resource) > 0 and resource[0] == "[" and resource[-1] == "]"):
      resource = resource[1:-1]

    # resolve prefixes
    # TODO: check whether I need to reverse the ns_contexts
    if(resource.find(":") > -1):
      rpre,rsuf = resource.split(":", 1)
      for nsc in self.handler._ns_contexts:
        for ns, prefix in nsc.items():
          if prefix == rpre:
            resource = ns + rsuf

    # TODO: is this enough to check for bnodes?
    if(len(resource) > 0 and resource[0:2] == "_:"):
      return BNode(resource[2:])

    return URIRef(self.resolveURI(resource))

  def resolveURI(self, uri):
    return _urljoin(self.baseuri or '', uri)

  def _popStacks(self, event, node):
    # check abouts
    if len(self.abouts) <> 0:
      about, aboutnode = self.abouts[-1]
      if aboutnode == node:
        self.abouts.pop()

    # keep track of nodes going out of scope
    self.elementStack.pop()

    # track xml:base and xml:lang going out of scope
    if self.xmlbases:
      self.xmlbases.pop()
      if self.xmlbases and self.xmlbases[-1]:
        self.baseuri = self.xmlbases[-1]

    if self.langs:
      self.langs.pop()
      if self.langs and self.langs[-1]:
        self.lang = self.langs[-1]

if __name__ == "__main__":
    store = ConjunctiveGraph()
    store.load(sys.argv[1], format="rdfa") 
    print store.serialize(format="pretty-xml")

