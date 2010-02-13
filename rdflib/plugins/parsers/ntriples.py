#!/usr/bin/env python
__doc__="""
N-Triples Parser
License: GPL 2, W3C, BSD, or MIT
Author: Sean B. Palmer, inamidst.com
Documentation: http://inamidst.com/proj/rdf/ntriples-doc

Command line usage::

    ./ntriples.py <URI>    - parses URI as N-Triples
    ./ntriples.py --help   - prints out this help message

# @@ fully empty document?
"""

import re

uriref = r'<([^:]+:[^\s"<>]+)>'
literal = r'"([^"\\]*(?:\\.[^"\\]*)*)"'
litinfo = r'(?:@([a-z]+(?:-[a-z0-9]+)*)|\^\^' + uriref + r')?'

r_line = re.compile(r'([^\r\n]*)(?:\r\n|\r|\n)')
r_wspace = re.compile(r'[ \t]*')
r_wspaces = re.compile(r'[ \t]+')
r_tail = re.compile(r'[ \t]*\.[ \t]*')
r_uriref = re.compile(uriref)
r_nodeid = re.compile(r'_:([A-Za-z][A-Za-z0-9]*)')
r_literal = re.compile(literal + litinfo)

bufsiz = 2048
validate = False

class Node(unicode): pass

# class URI(Node): pass
# class bNode(Node): pass
# class Literal(Node):
#    def __new__(cls, lit, lang=None, dtype=None):
#       n = str(lang) + ' ' + str(dtype) + ' ' + lit
#       return unicode.__new__(cls, n)

from rdflib.term import URIRef as URI
from rdflib.term import BNode as bNode
from rdflib.term import Literal

class Sink(object):
   def __init__(self):
      self.length = 0

   def triple(self, s, p, o):
      self.length += 1
      print (s, p, o)

class ParseError(Exception): pass

quot = {'t': '\t', 'n': '\n', 'r': '\r', '"': '"', '\\': '\\'}
r_safe = re.compile(r'([\x20\x21\x23-\x5B\x5D-\x7E]+)')
r_quot = re.compile(r'\\(t|n|r|"|\\)')
r_uniquot = re.compile(r'\\u([0-9A-F]{4})|\\U([0-9A-F]{8})')

def unquote(s):
   """Unquote an N-Triples string."""
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
      else: raise ParseError("Illegal literal character: %r" % s[0])
   return unicode(''.join(result))

if not validate:
   def unquote(s):
      return s.decode('unicode-escape')

r_hibyte = re.compile(r'([\x80-\xFF])')

def uriquote(uri):
   return r_hibyte.sub(lambda m: '%%%02X' % ord(m.group(1)), uri)
if not validate:
   def uriquote(uri):
      return uri

class NTriplesParser(object):
   """An N-Triples Parser.
   
   Usage::

        p = NTriplesParser(sink=MySink())
        sink = p.parse(f) # file; use parsestring for a string
   """

   def __init__(self, sink=None):
      if sink is not None:
         self.sink = sink
      else: self.sink = Sink()

   def parse(self, f):
      """Parse f as an N-Triples file."""
      if not hasattr(f, 'read'):
         raise ParseError("Item to parse must be a file-like object.")

      self.file = f
      self.buffer = ''
      while True:
         self.line = self.readline()
         if self.line is None: break
         try: self.parseline()
         except ParseError:
            raise ParseError("Invalid line: %r" % self.line)
      return self.sink

   def parsestring(self, s):
      """Parse s as an N-Triples string."""
      if not isinstance(s, basestring):
         raise ParseError("Item to parse must be a string instance.")
      from cStringIO import StringIO
      f = StringIO()
      f.write(s)
      f.seek(0)
      self.parse(f)

   def readline(self):
      """Read an N-Triples line from buffered input."""
      # N-Triples lines end in either CRLF, CR, or LF
      # Therefore, we can't just use f.readline()
      if not self.buffer:
         buffer = self.file.read(bufsiz)
         if not buffer: return None
         self.buffer = buffer

      while True:
         m = r_line.match(self.buffer)
         if m: # the more likely prospect
            self.buffer = self.buffer[m.end():]
            return m.group(1)
         else:
            buffer = self.file.read(bufsiz)
            if not buffer and not self.buffer.isspace():
               raise ParseError("EOF in line")
            elif not buffer:
               return None
            self.buffer += buffer

   def parseline(self):
      self.eat(r_wspace)
      if (not self.line) or self.line.startswith('#'):
         return # The line is empty or a comment

      subject = self.subject()
      self.eat(r_wspaces)

      predicate = self.predicate()
      self.eat(r_wspaces)

      object = self.object()
      self.eat(r_tail)

      if self.line:
         raise ParseError("Trailing garbage")
      self.sink.triple(subject, predicate, object)

   def peek(self, token):
      return self.line.startswith(token)

   def eat(self, pattern):
      m = pattern.match(self.line)
      if not m: # @@ Why can't we get the original pattern?
         raise ParseError("Failed to eat %s" % pattern)
      self.line = self.line[m.end():]
      return m

   def subject(self):
      # @@ Consider using dictionary cases
      subj = self.uriref() or self.nodeid()
      if not subj:
        raise ParseError("Subject must be uriref or nodeID")
      return subj

   def predicate(self):
      pred = self.uriref()
      if not pred:
         raise ParseError("Predicate must be uriref")
      return pred

   def object(self):
      objt = self.uriref() or self.nodeid() or self.literal()
      if objt is False:
         raise ParseError("Unrecognised object type")
      return objt

   def uriref(self):
      if self.peek('<'):
         uri = self.eat(r_uriref).group(1)
         uri = unquote(uri)
         uri = uriquote(uri)
         return URI(uri)
      return False

   def nodeid(self):
      if self.peek('_'):
         return bNode(self.eat(r_nodeid).group(1))
      return False

   def literal(self):
      if self.peek('"'):
         lit, lang, dtype = self.eat(r_literal).groups()
         lang = lang or None
         dtype = dtype or None
         if lang and dtype:
            raise ParseError("Can't have both a language and a datatype")
         lit = unquote(lit)
         return Literal(lit, lang, dtype)
      return False

def parseURI(uri):
   import urllib
   parser = NTriplesParser()
   u = urllib.urlopen(uri)
   sink = parser.parse(u)
   u.close()
   # for triple in sink:
   #    print triple
   print 'Length of input:', sink.length

def main():
   import sys
   if len(sys.argv) == 2:
      parseURI(sys.argv[1])
   else: print __doc__

if __name__=="__main__":
   main()
