import sys

from rdflib.sparql import parser, components
from rdflib.term import Literal, URIRef, Variable, BNode
from rdflib.namespace import RDF

from nose import tools, with_setup

import pyparsing

match_definitions = [
    (parser.BaseDecl,
      [
        ('BASE <s:ex>', URIRef('s:ex')),
        ('BASE <>', URIRef('')),
      ]),
    (parser.PrefixDecl,
      [
        ('PREFIX s: <s:ex>', components.PrefixDeclaration(
                               's:', 's:ex')),
      ]),
    (parser.Var,
      [
        ('?foo', Variable('foo')),
        ('$bar', Variable('bar')),
      ]),
    (parser.IRIref,
      [
        ('pre:local', components.QName('pre:local')),
        ('<s:ex>', URIRef('s:ex')),
      ]),
    (parser.RDFLiteral,
      [
        ('"foo"', Literal("foo")),
        ('"foo"@en-US', Literal("foo", lang='en-US')),
        ("'bar'^^pre:type", components.ParsedDatatypedLiteral(
          "bar", components.QName('pre:type'))),
        ("'bar'^^<s:type>", components.ParsedDatatypedLiteral(
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
        ('pre:local', components.QName('pre:local')),
        ('a', RDF.type),
      ]),
    (parser.GraphNode,
      [
        ('foaf:Person', components.QName('foaf:Person')),
      ]),
    (parser.ObjectList,
      [
        ('foaf:Person', [components.QName('foaf:Person')]),
      ]),
    (parser.PropertyListNotEmpty,
      [
        ('''foaf:nick "Alice"@en-US, "Alice_" ;
            a foaf:Person, <s:ex:Object>''',
         [components.PropertyValue(
            components.QName('foaf:nick'),
            [Literal('Alice', lang='en-US'), Literal('Alice_')]),
          components.PropertyValue(RDF.type,
            [components.QName('foaf:Person'), URIRef('s:ex:Object')])
         ]),
      ]),
    (parser.TriplesSameSubject,
      [
        ('''<s:ex:Subject> foaf:nick "Alice"@en-US, "Alice_" ;
                           a foaf:Person, <s:ex:Object>''',
         components.Resource(URIRef('s:ex:Subject'),
           [components.PropertyValue(
              components.QName('foaf:nick'),
              [Literal('Alice', lang='en-US'), Literal('Alice_')]),
            components.PropertyValue(RDF.type,
              [components.QName('foaf:Person'), URIRef('s:ex:Object')])
           ])),
      ]),
    (parser.NumericExpression,
      [
        ('1 / 2 + 3 * 4 / 5',
         components.ParsedAdditiveExpressionList(
          [components.ParsedMultiplicativeExpressionList(
            [Literal(1), '/', Literal(2)]), '+',
           components.ParsedMultiplicativeExpressionList(
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

original_Literal_eq = Literal.__eq__

def set_strict_Literal_eq():
  Literal.__eq__ = strict_Literal_eq

def set_original_Literal_eq():
  Literal.__eq__ = original_Literal_eq

def should_match(component, before, after):
  result = component.parseString(before).asList()[0]
  tools.assert_equal(after, result)

@with_setup(set_strict_Literal_eq, set_original_Literal_eq)
def test_components_should_match():
  for def_index, definition in enumerate(match_definitions):
    component, tests = definition
    for test_index, test in enumerate(tests):
      before, after = test
      should_match.description = (
        should_match.__name__ + '.%d.%d' % (def_index, test_index))
      yield should_match, component, before, after
