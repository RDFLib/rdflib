#!/usr/bin/env python
"""
n3proc - An N3 Processor using n3.n3
Author: Sean B. Palmer, inamidst.com
Licence: GPL 2; share and enjoy!
License: http://www.w3.org/Consortium/Legal/copyright-software
Documentation: http://inamidst.com/n3p/

usage:
   %prog [options] <URI>
"""

from rdflib.term import URIRef
from rdflib.term import BNode
from rdflib.term import Literal
from rdflib.term import Variable
from rdflib.namespace import Namespace
from rdflib.graph import QuotedGraph

import sys, os.path, re
import n3p

from urlparse import urljoin as urijoin

RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
OWL = Namespace('http://www.w3.org/2002/07/owl#')
LOG = Namespace('http://www.w3.org/2000/10/swap/log#')
XSD = Namespace('http://www.w3.org/2001/XMLSchema#')
N3R = Namespace('http://www.w3.org/2000/10/swap/reify#')

r_unilower = re.compile(r'(?<=\\u)([0-9a-f]{4})|(?<=\\U)([0-9a-f]{8})')
r_hibyte = re.compile(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\xFF]')

def quote(s):
   if not isinstance(s, unicode):
      s = unicode(s, 'utf-8') # @@ not required?
   if not (u'\\'.encode('unicode-escape') == '\\\\'):
      s = s.replace('\\', r'\\')
   s = s.replace('"', r'\"')
   # s = s.replace(r'\\"', r'\"')
   s = r_hibyte.sub(lambda m: '\\u00%02X' % ord(m.group(0)), s)
   s = s.encode('unicode-escape')
   s = r_unilower.sub(lambda m: (m.group(1) or m.group(2)).upper(), s)
   return str(s)


quot = {'t': '\t', 'n': '\n', 'r': '\r', '"': '"', '\\': '\\'}

r_quot = re.compile(r'\\(t|n|r|"|\\)')
r_uniquot = re.compile(r'\\u([0-9A-F]{4})|\\U([0-9A-F]{8})')

class ParseError(Exception):
   pass

def unquote(s, triplequoted=False, r_safe = re.compile(ur'([\x20\x21\x23-\x5B\x5D-\x7E\u00A0-\uFFFF]+)')):
   """Unquote an N-Triples string.
      Derived from: http://inamidst.com/proj/rdf/ntriples.py
   """
   result = []
   while s:
      m = r_safe.match(s)
      if m:
         s = s[m.end():]
         result.append(m.group(1))
         continue

      m = r_quot.match(s)
      if m:
         s = s[2:]
         result.append(quot[m.group(1)])
         continue

      m = r_uniquot.match(s)
      if m:
         s = s[m.end():]
         u, U = m.groups()
         codepoint = int(u or U, 16)
         if codepoint > 0x10FFFF:
            raise ParseError("Disallowed codepoint: %08X" % codepoint)
         result.append(unichr(codepoint))
      elif s.startswith('\\'):
         raise ParseError("Illegal escape at: %s..." % s[:10])
      elif triplequoted and (s[0] in '\n"'):
         result.append(s[0])
         s = s[1:]
      else: raise ParseError("Illegal literal character: %r" % s[0])
   return unicode(''.join(result))

branches = n3p.branches
regexps = n3p.regexps
start = n3p.start

class N3Processor(n3p.N3Parser):
   def __init__(self, uri, sink, baseURI=False):
      super(N3Processor, self).__init__(uri, branches, regexps)
      if baseURI is False:
         self.baseURI = uri
      else: self.baseURI = baseURI
      self.sink = sink
      self.bindings = {'': urijoin(self.baseURI, '#')}
      self.counter = 0
      self.prefix = False
      self.userkeys = False
      self.anonsubj = False
      self.litinfo = False
      self.forAll = False
      self.forSome = False
      self.universals = {}
      self.existentials = {}
      self.formulae = []
      self.labels = []
      self.mode = []
      self.triples = []
      self.pathmode = 'path'
      self.paths = []
      self.lists = []
      self.bnodes = {}

   def parse(self, start=start):
      super(N3Processor, self).parse(start)

   def onStart(self, prod):
      self.productions.append(prod)
      handler = prod + 'Start'
      if hasattr(self, handler):
         getattr(self, handler)(prod)

   def onFinish(self):
      prod = self.productions.pop()
      handler = prod + 'Finish'
      if hasattr(self, handler):
         getattr(self, handler)()

   def onToken(self, prod, tok):
      if self.productions:
         parentProd = self.productions[-1]
         handler = parentProd + 'Token'
         if hasattr(self, handler):
            getattr(self, handler)(prod, tok)
      else: raise Exception("Token has no parent production.")

   def documentStart(self, prod):
      formula = self.sink.graph
      self.formulae.append(formula)
      self.sink.start(formula)

   def declarationToken(self, prod, tok):
      if prod == '@prefix':
         self.prefix = []
      elif prod == '@keywords':
         self.userkeys = True # bah
      elif (self.prefix is not False) and prod == 'qname':
         self.prefix.append(tok[:-1])
      elif prod == 'explicituri':
         self.prefix.append(tok[1:-1])

   def declarationFinish(self):
      if self.prefix:
         self.bindings[self.prefix[0]] = self.prefix[1]
         self.prefix = False

   def universalStart(self, prod):
      self.forAll = []

   def universalFinish(self):
      for term in self.forAll:
         v = self.univar('var')
         self.universals[term] = (self.formulae[-1], v)
         self.sink.quantify(self.formulae[-1], v)
      self.forAll = False

   def existentialStart(self, prod):
      self.forSome = []

   def existentialFinish(self):
      for term in self.forSome:
         b = BNode()
         self.existentials[term] = (self.formulae[-1], b)
         self.sink.quantify(self.formulae[-1], b)
      self.forSome = False

   def simpleStatementStart(self, prod):
      self.triples.append([])

   def simpleStatementFinish(self):
      if self.triples:
         self.triples.pop()

   def pathStart(self, prod):
      # p = self.paths
      # if not (p and p[-1] and (p[-1][-1] in '!^')):
      if (not self.paths) or (self.pathmode == 'path'):
         self.paths.append([])
         self.pathcounter = 1
      else: self.pathcounter += 1
      self.pathmode = 'path'

   def pathtailStart(self, prod):
      self.pathcounter += 1
      self.pathmode = 'pathtail'

   def pathtailToken(self, prod, tok):
      if prod == '!':
         self.paths[-1].append('!')
      elif prod == '^':
         self.paths[-1].append('^')

   def pathtailFinish(self):
      self.pathcounter -= 1

   def pathFinish(self):
      self.pathcounter -= 1
      self.pathmode = 'path'
      if self.paths and (self.pathcounter < 1):
         path = self.paths.pop()
         if not path: pass
         elif len(path) == 1:
            term = path.pop()
            if self.mode and self.mode[-1] == 'list':
               self.lists[-1].append(term)
            else: self.triples[-1].append(term)
         else: # A path traversal
            objt, path = path[0], path[1:]
            for (i, pred) in enumerate(path):
               if (i % 2) != 0:
                  subj = objt
                  objt = BNode()
                  if path[i-1] == '!':
                     self.triple(subj, pred, objt)
                  elif path[i-1] == '^':
                     self.triple(objt, pred, subj)
            # @@ nested paths?
            if self.mode and self.mode[-1] == 'list':
               self.lists[-1].append(objt)
            else: self.triples[-1].append(objt)
      # if self.anonsubj is True:
      #    self.anonsubj = False
      # self.path = False

   def nodeToken(self, prod, tok):
      nodedict = {}

      def ointerp(prod, tok):
         b = BNode()
         # Record here if it's a subject node
         if self.anonsubj:
            self.anonsubj = False
         if ((not self.triples) or
             (False not in map(lambda s: not len(s), self.triples)) or
             (len(self.triples[-1]) == 3) or
             (len(self.triples) > 1 and
              len(self.triples[-2]) == 3 and
              not len(self.triples[-1]))):
            self.anonsubj = True
         if (self.paths and
             self.paths[-1] and
             self.paths[-1][-1] in '!^'):
            self.anonsubj = 'path'

         if self.paths:
            self.paths[-1].append(b)
            self.triples.append([b])
         elif self.mode and self.mode[-1] == 'list':
            self.lists[-1].append(b)
            self.triples.append([b])
         # else: self.triples[-1].append(b)

         elif len(self.triples[-1]) > 1:
            self.triples.append([b])
         self.mode.append('triple')
      nodedict['['] = ointerp

      def cinterp(prod, tok):
         if ((not self.anonsubj) or
             (self.paths and len(self.paths[-1]) == 1)):
            self.triples.pop()
         elif self.anonsubj == 'path':
            self.triples.pop()
            self.triples.append([])
         else: self.anonsubj = False
         self.mode.pop()
      nodedict[']'] = cinterp

      def oparen(prod, tok):
         self.lists.append([])
         self.mode.append('list')
      nodedict['('] = oparen

      def cparen(prod, tok):
         items = self.lists.pop()
         if items:
            first = head = BNode()
            for (i, item) in enumerate(items):
               if i < len(items) - 1:
                  rest = BNode()
               else: rest = RDF.nil
               self.triple(first, RDF.first, item)
               self.triple(first, RDF.rest, rest)
               first = rest
         else: head = RDF.nil
         self.mode.pop()
         if self.paths:
            self.paths[-1].append(head)
         elif self.mode and self.mode[-1] == 'list':
            self.lists[-1].append(head)
         else: self.triples[-1].append(head)
      nodedict[')'] = cparen

      def obrace(prod, tok):
         f = self.formula()
         if self.paths:
            self.paths[-1].append(f)
         elif self.mode and self.mode[-1] == 'list':
            self.lists[-1].append(f)
         else: self.triples[-1].append(f)

         self.formulae.append(f)
         self.labels.append('f' + str(self.counter))
      nodedict['{'] = obrace

      def cbrace(prod, tok):
         self.formulae.pop()
         self.labels.pop()
         if self.triples and (len(self.triples[-1]) == 3):
            self.triple(*self.triples[-1])
            self.triples[-1].pop()
      nodedict['}'] = cbrace

      def numericliteral(prod, tok):
         if '.' in tok:
            tok = str(float(tok))
            lit = Literal(tok, datatype=XSD.double)
         else:
            tok = str(int(tok))
            lit = Literal(tok, datatype=XSD.integer)
         if self.paths:
            self.paths[-1].append(lit)
         elif self.mode and self.mode[-1] == 'list':
            self.lists[-1].append(lit)
         else: self.triples[-1].append(lit)
      nodedict['numericliteral'] = numericliteral

      def variable(prod, tok):
         var = self.univar(tok[1:], sic=True)
         if self.paths:
            self.paths[-1].append(var)
         elif self.mode and self.mode[-1] == 'list':
            self.lists[-1].append(var)
         else: self.triples[-1].append(var)
      nodedict['variable'] = variable

      def this(prod, tok):
         formula = self.formulae[-1]
         if self.paths:
            self.paths[-1].append(formula)
         elif self.mode and self.mode[-1] == 'list':
            self.lists[-1].append(formula)
         else: self.triples[-1].append(formula)
      nodedict['@this'] = this

      try: nodedict[prod](prod, tok)
      except KeyError: pass

   def literalStart(self, prod):
      self.litinfo = {}

   def literalToken(self, prod, tok):
      if prod == 'string':
         self.litinfo['content'] = tok

   def dtlangToken(self, prod, tok):
      if prod == 'langcode':
         self.litinfo['language'] = tok

   def symbolToken(self, prod, tok):
      if prod == 'explicituri':
         term = self.uri(tok[1:-1])
      elif prod == 'qname':
         term = self.qname(tok)

      if self.litinfo:
         self.litinfo['datatype'] = term
      elif self.forAll is not False:
         self.forAll.append(term)
      elif self.forSome is not False:
         self.forSome.append(term)
      elif self.paths:
         self.paths[-1].append(term)
      elif self.mode and self.mode[-1] == 'list':
         self.lists[-1].append(term)
      else: self.triples[-1].append(term)

   def literalFinish(self):
      content = self.litinfo['content']
      language = self.litinfo.get('language')
      datatype = self.litinfo.get('datatype')

      lit = self.literal(content, language, datatype)
      if self.paths:
         self.paths[-1].append(lit)
      elif self.mode and self.mode[-1] == 'list':
         self.lists[-1].append(lit)
      else: self.triples[-1].append(lit)
      self.litinfo = False

   def objectFinish(self):
      if self.triples and (len(self.triples[-1]) == 3):
         self.triple(*self.triples[-1])
         self.triples[-1].pop()

   def propertylisttailToken(self, prod, tok):
      if prod == ';':
         self.triples[-1] = [self.triples[-1][0]]

   def verbToken(self, prod, tok):
      vkwords ={'@a': RDF.type, '=': OWL.sameAs,
                '=>': LOG.implies, '<=': LOG.implies}
      if vkwords.has_key(prod):
         term = vkwords[prod]
         # if self.paths:
         #    self.paths[-1].append(term)
         if self.mode and self.mode[-1] == 'list':
            self.lists[-1].append(term)
         else: self.triples[-1].append(term)

      if prod in ('@of', '<='):
         # @@ test <= in CWM
         verb = (self.triples[-1][1],)
         self.triples[-1][1] = verb

   def triple(self, subj, pred, objt):
      scp = self.formulae[-1]
      if not isinstance(pred, tuple):
         self.sink.statement(subj, pred, objt, scp)
      else: self.sink.statement(objt, pred[0], subj, scp)

   def qname(self, tok):
      if ':' in tok:
         prefix, name = tok.split(':')
      elif self.userkeys:
         prefix, name = '', tok
      else: raise ParseError("Set user @keywords to use barenames.")
      if (prefix == '_') and (not self.bindings.has_key('_')):
         if name in self.bnodes:
            bnode = self.bnodes[name]
         else:
            bnode = BNode()
            self.bnodes[name] = bnode
         return bnode

      elif not self.bindings.has_key(prefix):
         print >> sys.stderr, "Prefix not bound: %s" % prefix
      return self.uri(self.bindings[prefix] + name)

   def uri(self, tok):
      u = URIRef(urijoin(self.baseURI, tok))
      if self.universals.has_key(u):
         formula, var = self.universals[u]
         if formula in self.formulae:
            return var
      if self.existentials.has_key(u): # @@ elif?
         formula, bnode = self.existentials[u]
         if formula in self.formulae:
            return bnode
      return u

   def formula(self):
      formula_id = BNode()
      if formula_id == self.sink.graph.identifier:
         return self.sink.graph
      else:
         return QuotedGraph(store=self.sink.graph.store, identifier=formula_id)
         #return self.sink.graph.get_context(formula_id, quoted=True)

   def literal(self, content, language, datatype):
      if content.startswith('"""'):
         content = unquote(content[3:-3].decode('utf-8'), triplequoted=True)
      else: content = unquote(content[1:-1].decode('utf-8'))
      return Literal(content, language, datatype)

   def univar(self, label, sic=False):
      if not sic:
         self.counter += 1
         label += str(self.counter)
      return Variable(label)


class NTriplesSink(object):
   def __init__(self, out=None):
      self.out = out or sys.stdout
      self.counter = 0

   def start(self, root):
      self.root = root

   def statement(self, s, p, o, f):
      if f == self.root:
         self.out.write("%s %s %s .\n" % (s, p, o))
      else: self.flatten(s, p, o, f)

   def quantify(self, formula, var):
      if formula != self.root:
         if var.startswith('_'): pred = N3R.existential
         elif var.startswith('?'): pred = N3R.universal
         self.out.write("%s %s %s .\n" % (formula, pred, var))

   def makeStatementID(self):
      return BNode()

   def flatten(self, s, p, o, f):
      fs = self.makeStatementID()
      self.out.write("%s %s %s .\n" % (f, N3R.statement, fs))
      self.out.write("%s %s %s .\n" % (fs, N3R.subject, s))
      self.out.write("%s %s %s .\n" % (fs, N3R.predicate, p))
      self.out.write("%s %s %s .\n" % (fs, N3R.object, o))

def parse(uri, options):
   baseURI = options.baseURI
   sink = NTriplesSink()
   if options.root:
      sink.quantify = lambda *args: True
      sink.flatten = lambda *args: True
   if ':' not in uri:
      uri = 'file://' + os.path.join(os.getcwd(), uri)
   if baseURI and (':' not in baseURI):
      baseURI = 'file://' + os.path.join(os.getcwd(), baseURI)
   p = N3Processor(uri, sink, baseURI=baseURI)
   p.parse()

def main(argv=None):
   import optparse

   class MyHelpFormatter(optparse.HelpFormatter):
      def __init__(self):
         kargs = {'indent_increment': 2, 'short_first': 1,
                  'max_help_position': 25, 'width': None}
         optparse.HelpFormatter.__init__(self, **kargs)
      def format_usage(self, usage):
         return optparse._("%s") % usage.lstrip()
      def format_heading(self, heading):
         return "%*s%s:\n" % (self.current_indent, "", heading)
   formatter = MyHelpFormatter()

   parser = optparse.OptionParser(usage=__doc__, formatter=formatter)
   parser.add_option("-b", "--baseURI", dest="baseURI", default=False,
                     help="set the baseURI", metavar="URI")
   parser.add_option("-r", "--root", dest="root",
                     action="store_true", default=False,
                     help="print triples in the root formula only")
   options, args = parser.parse_args(argv)

   if len(args) == 1:
      parse(args[0], options)
   else: parser.print_help()

if __name__=="__main__":
   main()
