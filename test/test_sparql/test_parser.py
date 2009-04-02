import sys

from rdflib_sparql import parser, bison as components
from rdflib.term import Literal, URIRef, Variable, BNode
from rdflib.RDF import RDFNS

from nose import tools

import pyparsing

match_definitions = [
    (parser.BaseDecl,
      [
        ('BASE <s:ex>', URIRef('s:ex')),
        ('BASE <>', URIRef('')),
      ]),
    (parser.PrefixDecl,
      [
        ('PREFIX s: <s:ex>', components.Bindings.PrefixDeclaration(
                               's:', 's:ex')),
      ]),
    (parser.Var,
      [
        ('?foo', Variable('foo')),
        ('$bar', Variable('bar')),
      ]),
    (parser.IRIref,
      [
        ('pre:local', components.QName.QName('pre:local')),
        ('<s:ex>', URIRef('s:ex')),
      ]),
    (parser.RDFLiteral,
      [
        ('"foo"', Literal("foo")),
        ('"foo"@en-US', Literal("foo", lang='en-US')),
        ("'bar'^^pre:type", components.Expression.ParsedDatatypedLiteral(
          "bar", components.QName.QName('pre:type'))),
        ("'bar'^^<s:type>", components.Expression.ParsedDatatypedLiteral(
          "bar", URIRef('s:type'))),
      ]),
    (parser.NumericLiteral,
      [
        ('0', Literal(0)),
        ('3.1415', Literal(3.1415)),
        ('+901', Literal(901)),
        ('-9.8e-2', Literal(-9.8e-2)),
      ]),
    (parser.BooleanLiteral,
      [
        ('true', Literal(True)),
        ('true splat', Literal(True)),
        ('false', Literal(False)),
      ]),
    (parser.BlankNode,
      [
        ('_:a', BNode('a')),
      ]),
    (parser.Verb,
      [
        ('?foo', Variable('foo')),
        ('<s:ex>', URIRef('s:ex')),
        ('pre:local', components.QName.QName('pre:local')),
        ('a', RDFNS.type),
      ]),
    (parser.GraphNode,
      [
        ('foaf:Person', components.QName.QName('foaf:Person')),
      ]),
    (parser.ObjectList,
      [
        ('foaf:Person', [components.QName.QName('foaf:Person')]),
      ]),
    (parser.PropertyListNotEmpty,
      [
        ('''foaf:nick "Alice"@en-US, "Alice_" ;
            a foaf:Person, <s:ex:Object>''',
         [components.Triples.PropertyValue(
            components.QName.QName('foaf:nick'),
            [Literal('Alice', lang='en-US'), Literal('Alice_')]),
          components.Triples.PropertyValue(RDFNS.type,
            [components.QName.QName('foaf:Person'), URIRef('s:ex:Object')])
         ]),
      ]),
    (parser.TriplesSameSubject,
      [
        ('''<s:ex:Subject> foaf:nick "Alice"@en-US, "Alice_" ;
                           a foaf:Person, <s:ex:Object>''',
         components.Resource.Resource(URIRef('s:ex:Subject'),
           [components.Triples.PropertyValue(
              components.QName.QName('foaf:nick'),
              [Literal('Alice', lang='en-US'), Literal('Alice_')]),
            components.Triples.PropertyValue(RDFNS.type,
              [components.QName.QName('foaf:Person'), URIRef('s:ex:Object')])
           ])),
      ]),
    (parser.NumericExpression,
      [
        ('1 / 2 + 3 * 4 / 5',
         components.Expression.ParsedAdditiveExpressionList(
          [components.Expression.ParsedMultiplicativeExpressionList(
            [Literal(1), '/', Literal(2)]), '+',
           components.Expression.ParsedMultiplicativeExpressionList(
            [Literal(3), '*', Literal(4), '/', Literal(5)])])),
      ]),
  ]

def strict_Literal_eq(l0, l1):
    try:
        return (l0._cmp_value == l1._cmp_value and
                type(l0._cmp_value) is type(l1._cmp_value) and
                l0.language == l1.language and l0.datatype == l1.datatype)
    except:
        return False
Literal.__eq__ = strict_Literal_eq

class test_parser(object):
  def should_match(self, component, before, after):
    result = component.parseString(before).asList()[0]
    tools.assert_equal(after, result)

  def test_components_should_match(self):
    for component, tests in match_definitions:
      for before, after in tests:
        yield self.should_match, component, before, after
