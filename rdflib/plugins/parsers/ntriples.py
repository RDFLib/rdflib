#!/usr/bin/env python3

__doc__ = """\
N-Triples Parser
License: GPL 2, W3C, BSD, or MIT
Author: Sean B. Palmer, inamidst.com
"""

import re
import codecs

from rdflib.term import URIRef as URI
from rdflib.term import BNode as bNode
from rdflib.term import Literal
from rdflib.compat import decodeUnicodeEscape
from rdflib.exceptions import ParserError as ParseError
from rdflib.parser import Parser

from io import StringIO, TextIOBase, BytesIO

__all__ = ["unquote", "uriquote", "W3CNTriplesParser", "NTGraphSink", "NTParser"]

uriref = r'<([^:]+:[^\s"<>]*)>'
# Consider a possibly faster regex: '(".*[^\\]"')
literal = r'"([^"\\]*(?:\\.[^"\\]*)*)"'
litinfo = r"(?:@([a-zA-Z]+(?:-[a-zA-Z0-9]+)*)|\^\^" + uriref + r")?"
wspace = r"[ \t]*"
wspaces = r"[ \t]+"
tail = r"[ \t]*\.[ \t]*(#.*)?"

r_line = re.compile(r"([^\r\n]*)(?:\r\n|\r|\n)")
r_wspace = re.compile(wspace)
r_wspaces = re.compile(wspaces)
r_tail = re.compile(tail)
r_uriref = re.compile(uriref)
r_nodeid = re.compile(r"_:([A-Za-z0-9_:]([-A-Za-z0-9_:\.]*[-A-Za-z0-9_:])?)")
r_literal = re.compile(literal + litinfo)
# Should use wspace as soon as read in text mode.
r_comment_or_empty = re.compile(r"[ \t\r]*" + "(#.*)?$")

# https://www.w3.org/TR/n-triples/
# The last item is a uriref (terminated by >), or a literal (terminated by ") or a node id (terminated by -A-Za-z0-9_:)
r_uriref_predicate_object = re.compile(wspace + r"([<_][^ ]+)"
                                       + wspaces + r"(<[^ >]+>)"
                                       + wspaces + r"([<_\"].*[-A-Za-z0-9_:\">])" + tail)

bufsiz = 2048

class DummySink(object):
    def __init__(self):
        self.length = 0

    def triple(self, s, p, o):
        self.length += 1
        print(s, p, o)


quot = {"t": "\t", "n": "\n", "r": "\r", '"': '"', "\\": "\\"}
r_safe = re.compile(r"([\x20\x21\x23-\x5B\x5D-\x7E]+)")
r_quot = re.compile(r'\\(t|n|r|"|\\)')
r_uniquot = re.compile(r"\\u([0-9A-F]{4})|\\U([0-9A-F]{8})")


def _unquote_validate(s):
    """Unquote an N-Triples string in validation mode."""
    result = []
    while s:
        m = r_safe.match(s)
        if m:
            s = s[m.end() :]
            result.append(m.group(1))
            continue

        m = r_quot.match(s)
        if m:
            s = s[2:]
            result.append(quot[m.group(1)])
            continue

        m = r_uniquot.match(s)
        if m:
            s = s[m.end() :]
            u, U = m.groups()
            codepoint = int(u or U, 16)
            if codepoint > 0x10FFFF:
                raise ParseError("Disallowed codepoint: %08X" % codepoint)
            result.append(chr(codepoint))
        elif s.startswith("\\"):
            raise ParseError("Illegal escape at: %s..." % s[:10])
        else:
            raise ParseError("Illegal literal character: %r" % s[0])
    return "".join(result)


def _unquote_not_validate(s):
    """Unquote an N-Triples string if no validation is needed."""
    # Maybe there are no escape char, so no need to decode.
    if "\\" in s:
        s = decodeUnicodeEscape(s)

    return s


r_hibyte = re.compile(r"([\x80-\xFF])")


def _uriquote_validate(uri):
    return r_hibyte.sub(lambda m: "%%%02X" % ord(m.group(1)), uri)


# This sets the proper functions to be used,
# and these functions do not need to check the validate flag.
def validate(value):
    global unquote
    global uriquote
    if value:
        unquote = _unquote_validate
        uriquote = _uriquote_validate
    else:
        unquote = _unquote_not_validate
        # uriquote does not do anything when no validation is needed.
        uriquote = lambda x: x

validate(False)


class W3CNTriplesParser(object):
    """An N-Triples Parser.
    This is a legacy-style Triples parser for NTriples provided by W3C
    Usage::
          p = NTriplesParser(sink=MySink())
          sink = p.parse(f) # file; use parsestring for a string

    To define a context in which blank node identifiers refer to the same blank node
    across instances of NTriplesParser, pass the same dict as `bnode_context` to each
    instance. By default, a new blank node context is created for each instance of
    `NTriplesParser`.
    """

    __slots__ = ("_bnode_ids", "sink", "buffer", "file", "line")

    def __init__(self, sink=None, bnode_context=None):
        if bnode_context is not None:
            self._bnode_ids = bnode_context
        else:
            self._bnode_ids = {}

        if sink is not None:
            self.sink = sink
        else:
            self.sink = DummySink()

        self.file = None

    def parse(self, f, bnode_context=None):
        """
        Parse f as an N-Triples file.

        :type f: :term:`file object`
        :param f: the N-Triples source
        :type bnode_context: `dict`, optional
        :param bnode_context: a dict mapping blank node identifiers (e.g., ``a`` in ``_:a``)
                              to `~rdflib.term.BNode` instances. An empty dict can be
                              passed in to define a distinct context for a given call to
                              `parse`.
        """
        if not hasattr(f, "read"):
            raise ParseError("Item to parse must be a file-like object.")

        if not hasattr(f, "encoding") and not hasattr(f, "charbuffer"):
            # someone still using a bytestream here?
            f = codecs.getreader("utf-8")(f)

        self.file = f
        return self.processing_loop(bnode_context)

    def processing_loop(self, bnode_context):
        while True:
            the_line = self.file.readline()
            if not the_line:
                break
            try:
                self.parseline(the_line, bnode_context=bnode_context)
            except ParseError:
                raise ParseError("Invalid line: {}".format(the_line))
        return self.sink

    def parsestring(self, s, **kwargs):
        """Parse s as an N-Triples string."""
        if not isinstance(s, (str, bytes, bytearray)):
            raise ParseError("Item to parse must be a string instance.")
        if isinstance(s, (bytes, bytearray)):
            f = codecs.getreader("utf-8")(BytesIO(s))
        else:
            f = StringIO(s)
        self.parse(f, **kwargs)

    def readline(self):
        """Read an N-Triples line from buffered input."""
        # N-Triples lines end in either CRLF, CR, or LF
        return self.file.readline()

    def parseline(self, the_line, bnode_context=None):
        # This splits the line into three components.
        m = r_uriref_predicate_object.match(the_line)
        if not m:
            # Very rare case, so performances are less important.
            if r_comment_or_empty.match(the_line):
                return  # The line is a comment
            raise ParseError("Not a triple")

        first_token, second_token, third_token, _ = m.groups()

        subject = self.uriref(first_token) or self.nodeid(first_token, bnode_context)
        if not subject:
            raise ParseError("Subject must be uriref or nodeID")

        predicate = self.uriref(second_token)
        if not predicate:
            raise ParseError("Predicate must be uriref")

        object_ = self.uriref(third_token) or self.nodeid(third_token, bnode_context) or self.literal(third_token)
        if object_ is False:
            raise ParseError("Unrecognised object type")

        self.sink.triple(subject, predicate, object_)

    def uriref(self, the_string):
        if the_string[0] == "<":
            # This strips the opening and closing brackets.
            uri = the_string[1:-1]
            uri = unquote(uri)
            uri = uriquote(uri)
            return URI(uri)
        return False

    def nodeid(self, bnode_id, bnode_context=None):
        if bnode_id[0] == "_":
            # Fix for https://github.com/RDFLib/rdflib/issues/204
            if bnode_context is None:
                bnode_context = self._bnode_ids
            new_id = bnode_context.get(bnode_id, None)
            if new_id is not None:
                # Re-map to id specfic to this doc
                return bNode(new_id)
            else:
                # Replace with freshly-generated document-specific BNode id
                bnode = bNode()
                # Store the mapping
                bnode_context[bnode_id] = bnode
                return bnode
        return False

    def literal(self, the_string):
        if the_string[0] == '"':
            lit, lang, dtype = r_literal.match(the_string).groups()
            if not lang:
                lang = None
            if dtype:
                dtype = unquote(dtype)
                dtype = uriquote(dtype)
                dtype = URI(dtype)
                if lang:
                    raise ParseError("Can't have both a language and a datatype")
            else:
                dtype = None
            lit = unquote(lit)
            return Literal(lit, lang, dtype)
        return False


class NTGraphSink(object):
    __slots__ = ("g",)

    def __init__(self, graph):
        self.g = graph

    def triple(self, s, p, o):
        self.g.add((s, p, o))


class NTParser(Parser):
    """parser for the ntriples format, often stored with the .nt extension

    See http://www.w3.org/TR/rdf-testcases/#ntriples"""

    __slots__ = set()

    @classmethod
    def parse(cls, source, sink, **kwargs):
        """
        Parse the NT format

        :type source: `rdflib.parser.InputSource`
        :param source: the source of NT-formatted data
        :type sink: `rdflib.graph.Graph`
        :param sink: where to send parsed triples
        :param kwargs: Additional arguments to pass to `.NTriplesParser.parse`
        """
        f = source.getCharacterStream()
        if not f:
            b = source.getByteStream()
            # TextIOBase includes: StringIO and TextIOWrapper
            if isinstance(b, TextIOBase):
                # f is not really a ByteStream, but a CharacterStream
                f = b
            else:
                # since N-Triples 1.1 files can and should be utf-8 encoded
                f = codecs.getreader("utf-8")(b)
        parser = W3CNTriplesParser(NTGraphSink(sink))
        parser.parse(f, **kwargs)
        f.close()
