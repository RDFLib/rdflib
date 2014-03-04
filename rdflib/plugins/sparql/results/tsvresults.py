
"""
This implements the Tab Separated SPARQL Result Format

It is implemented with pyparsing, reusing the elements from the SPARQL Parser
"""

import codecs

from pyparsing import (
    Optional, ZeroOrMore, Literal, ParserElement, ParseException, Suppress)

from rdflib.query import Result, ResultParser

from rdflib.plugins.sparql.parser import (
    Var, STRING_LITERAL1, STRING_LITERAL2, IRIREF, BLANK_NODE_LABEL,
    NumericLiteral, BooleanLiteral, LANGTAG)
from rdflib.plugins.sparql.parserutils import Comp, Param, CompValue

from rdflib import Literal as RDFLiteral

from rdflib.py3compat import bytestype

ParserElement.setDefaultWhitespaceChars(" \n")


String = STRING_LITERAL1 | STRING_LITERAL2

RDFLITERAL = Comp('literal', Param('string', String) + Optional(
    Param('lang', LANGTAG.leaveWhitespace()
          ) | Literal('^^').leaveWhitespace(
          ) + Param('datatype', IRIREF).leaveWhitespace()))

TERM = RDFLITERAL | IRIREF | BLANK_NODE_LABEL | NumericLiteral | BooleanLiteral
ROW = TERM + ZeroOrMore(Suppress("\t") + TERM)
ROW.parseWithTabs()

HEADER = Var + ZeroOrMore(Suppress("\t") + Var)
HEADER.parseWithTabs()


class TSVResultParser(ResultParser):
    def parse(self, source):

        if isinstance(source.read(0), bytestype):
            # if reading from source returns bytes do utf-8 decoding
            source = codecs.getreader('utf-8')(source)

        try:
            r = Result('SELECT')

            header = source.readline()

            r.vars = list(HEADER.parseString(header.strip(), parseAll=True))
            r.bindings = []
            while True:
                line = source.readline()
                if not line:
                    break
                line = line.strip()
                if line == "":
                    continue

                row = ROW.parseString(line, parseAll=True)
                r.bindings.append(
                    dict(zip(r.vars, (self.convertTerm(x) for x in row))))

            return r

        except ParseException, err:
            print err.line
            print " " * (err.column - 1) + "^"
            print err

    def convertTerm(self, t):
        if isinstance(t, CompValue):
            if t.name == 'literal':
                return RDFLiteral(t.string, lang=t.lang, datatype=t.datatype)
            else:
                raise Exception("I dont know how to handle this: %s" % (t,))
        else:
            return t

if __name__ == '__main__':
    import sys
    r = Result.parse(file(sys.argv[1]), format='tsv')
    print r.vars
    print r.bindings
    # print r.serialize(format='json')
