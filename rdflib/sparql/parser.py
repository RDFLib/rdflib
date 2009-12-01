#!/usr/bin/env python
import base64
import sys, re

from pyparsing import (Regex, Suppress, Combine, Optional, CaselessKeyword,
                       ZeroOrMore, OneOrMore, removeQuotes, quotedString,
                       Empty, Literal, NoMatch, Group, oneOf, Forward,
                       Keyword, ParseExpression, ParseElementEnhance,
                       ParseException, col, lineno, restOfLine)

import rdflib
from rdflib.term import URIRef
from rdflib.sparql import bison as components

XSD_NS = rdflib.namespace.Namespace(u'http://www.w3.org/2001/XMLSchema#')

# Debug utilities:

DEBUG = False

if DEBUG:
    def apply_to_pyparser_tree(parser, f, cache=None):
        if cache is None:
            cache = set()
        if parser in cache:
            return
        else:
            cache.add(parser)

        f(parser)
        if isinstance(parser, ParseElementEnhance):
            apply_to_pyparser_tree(parser.expr, f, cache)
        elif isinstance(parser, ParseExpression):
            for expr in parser.exprs:
                apply_to_pyparser_tree(expr, f, cache)

    from Ft.Xml import MarkupWriter

    class ParseTracer(object):
        def __init__(self):
            pass

        def start_action(self, instring, loc, expr):
            self.writer.startElement(u'attempt', attributes={
              u'class': unicode(expr.__class__.__name__),
              u'loc': unicode(repr(loc)), u'expr': unicode(repr(expr)),
              u'lineno': unicode(lineno(loc, instring)),
              u'col': unicode(col(loc, instring)),})

        def success_action(self, instring, tokensStart, loc, expr, tokens):
            self.writer.simpleElement(u'success')
            self.writer.endElement(u'attempt')

        def exception_action(self, instring, tokensStart, expr, err):
            self.writer.simpleElement(u'fail', attributes={
              u'err': unicode(repr(err))})
            self.writer.endElement(u'attempt')

        def set_debug_actions(self, parser):
            parser.setDebugActions(
              self.start_action, self.success_action, self.exception_action)

        def parse(self, parser, input, stream):
            self.parser = parser
            apply_to_pyparser_tree(self.parser, self.set_debug_actions)
            self.writer = MarkupWriter(indent='yes', stream=stream)
            self.writer.startDocument()
            self.writer.startElement(u'trace')

            try:
                result = self.parser.parseString(input)[0]
            except ParseException, e:
                self.writer.simpleElement(u'fail', attributes={
                  u'err': unicode(repr(e))})
                #self.writer.endElement(u'attempt')
                raise
            finally:
                self.writer.endElement(u'trace')
                self.writer.endDocument()

            return result

    def data_dir(thing):
        return [member for member in dir(thing) if (
          not member.startswith('__') and
          not callable(getattr(thing, member)))]

    def struct_data(thing, depth=None, brief=False):
        if depth == 0:
            return '...'
        elif depth is not None:
            depth -= 1

        if isinstance(thing, list):
            return [struct_data(item, depth, brief) for item in thing]
        if isinstance(thing, tuple):
            return (struct_data(item, depth, brief) for item in thing)
        d = data_dir(thing)
        if len(d) > 0:
            if brief:
                classname = str(thing.__class__).split('.')[-1]
            else:
                classname = repr(thing.__class__)

            result = {'__class__': thing.__class__}
            for key in d:
                result[key] = struct_data(getattr(thing, key), depth, brief)
            return result
        else:
          return thing

    from pprint import pprint

    def debug(results, text=None):
        if text is None:
            text = ''
        print >> sys.stderr, 'DEBUG (parse success):', text
        pprint(struct_data(results.asList(), 3, True), sys.stderr)

    def debug2(s, loc, toks):
        print >> sys.stderr, 'DEBUG (parse success): parse string =', s
        pprint(struct_data(toks.asList(), 3, True), sys.stderr)

    def debug_fail(s, loc, expr, err):
        print >> sys.stderr, 'DEBUG (parse fail): expr =', expr
        print >> sys.stderr, err


def composition(callables):
    def composed(arg):
        result = arg
        for callable in callables:
            result = callable(result)
        return result
    return composed

def composition2(callables):
    def composed(*args):
        result = args
        for callable in callables:
            result = [callable(*result)]
        return result[0]
    return composed

def regex_group(regex):
    return '(?:%s)' % (regex,)

def as_empty(results):
    return [[]]

def setPropertyValueList(results):
    results = results.asList()
    collection = results[0]
    collection.setPropertyValueList(results[1])
    return collection

class ProjectionMismatchException(Exception):
    pass

def refer_component(component, initial_args=None, projection=None, **kwargs):
    '''
    Create a function to forward parsing results to the appropriate
    constructor.

    The pyparsing library allows us to modify the token stream that is
    returned by a particular expression with the `setParseAction()` method.
    This method sets a handler function that should take a single
    `ParseResults` instance as an argument, and then return a new token or
    list of tokens.  Mainly, we want to pass lower level tokens to SPARQL
    parse tree objects; the constructors for these objects take a number of
    positional arguments, so this function builds a new function that will
    forward the pyparsing results to the positional arguments of the
    appropriate constructor.

    This function provides a bit more functionality with its additional
    arguments:

     - `initial_args`: static list of initial arguments to add to the
     	 beginning of the arguments list before additional processing
     - `projection`: list of integers that reorders the initial arguments
     	 based on the indices that it contains.

    Finally, any additional keyword arguments passed to this function are
    passed along to the handler that is constructed.

    Note that we always convert pyparsing results to a list with the
    `asList()` method before using those results; this works, but we may
    only need this for testing.  To be safe, we include it here, but we
    might want to investigate further whether or not it could be moved only
    to testing code.  Also, we might want to investigate whether a list-only
    parsing mode could be added to pyparsing.
    '''

    if initial_args is None and projection is None:
        def apply(results):
            if DEBUG:
                print >> sys.stderr, component
                debug(results)
            return component(*results.asList(), **kwargs)
    else:
        def apply(results):
            if DEBUG:
                print >> sys.stderr, component
                debug(results)
            if initial_args is not None:
                results = initial_args + results.asList()
            if projection is not None:
                if len(results) < len(projection):
                    raise ProjectionMismatchException(
                      'Expected at least %d results to make %s, got %d.' %
                      (len(projection), str(component), len(results)))
                projected = []
                for index in projection:
                    projected.append(results[index])
            else:
                projected = results
            return component(*projected, **kwargs)
    return apply

# Productions for terminals, except for those that are really only
# associated with one higher-level production, in which case they are
# defined closer to that production:
LT = Suppress('<')
GT = Suppress('>')
LP = Suppress('(')
RP = Suppress(')')
LB = Suppress('[')
RB = Suppress(']')
LC = Suppress('{')
RC = Suppress('}')
COLON = Literal(':')
SEMICOLON = Suppress(';')
COMMA = Suppress(',')
PERIOD = Suppress('.')

IRI = Regex(
  r'[^<>"{}|^`\\%s]*' % ''.join('\\x%02X' % i for i in range(33)))
IRI_REF = LT + IRI + GT
if DEBUG:
    IRI_REF.setName('IRI_REF')

#PN_CHARS_BASE = Regex('[a-zA-Z]')
PN_CHARS_BASE_re = '[a-zA-Z]'
PN_CHARS_U_re = PN_CHARS_BASE_re + '|_'
PN_CHARS_re = PN_CHARS_U_re + '|-|[0-9]'
PN_PREFIX_re = (PN_CHARS_BASE_re +
  '(?:(?:' + PN_CHARS_re + '\\.)*' + PN_CHARS_re + ')?')
PN_PREFIX = Regex(PN_PREFIX_re)

PNAME_NS = Combine(Optional(PN_PREFIX, '') + COLON)
PN_LOCAL = Regex(regex_group(PN_CHARS_U_re + '|[0-9]') +
             regex_group(
               regex_group(PN_CHARS_re + '|\\.') + '*' +
               regex_group(PN_CHARS_re)) + '?')
PNAME_LN = Combine(PNAME_NS + PN_LOCAL)

WS_re = r'[ \t\r\n]*'
NIL = Group(Suppress(Regex(r'\(' + WS_re + r'\)')))


# BaseDecl:
BASE = Suppress(CaselessKeyword('BASE'))

BaseDecl = (BASE + IRI_REF).setParseAction(
  refer_component(components.Bindings.BaseDeclaration))
if DEBUG:
    BaseDecl.setName('BaseDecl')

# PrefixDecl:
PREFIX = Suppress(CaselessKeyword('PREFIX'))

PrefixDecl = (PREFIX + PNAME_NS + IRI_REF).setParseAction(
  refer_component(components.Bindings.PrefixDeclaration))
if DEBUG:
    PrefixDecl.setName('PrefixDecl')

# Prologue:
Prologue = (Optional(BaseDecl, None) +
            Group(ZeroOrMore(PrefixDecl))).setParseAction(
  refer_component(components.Query.Prolog))
if DEBUG:
    Prologue.setName('Prologue')

# Var:
QM = Suppress('?')
USD = Suppress('$')

VARNAME = Regex(regex_group(PN_CHARS_U_re + '|[0-9]') +
                regex_group(PN_CHARS_U_re + '|[0-9]') + '*')
Var = ((QM | USD) + VARNAME).setParseAction(
  refer_component(rdflib.term.Variable))
if DEBUG:
    Var.setName('Var')

# PrefixedName:
PrefixedName = PNAME_LN | PNAME_NS
if DEBUG:
    PrefixedName.setName('PrefixedName')

# IRIref:
IRIref = (IRI_REF.setParseAction(refer_component(components.IRIRef.IRIRef)) |
  PrefixedName.setParseAction(refer_component(components.QName.QName)))
if DEBUG:
    IRIref.setName('IRIref')

# DatasetClause:
FROM = Suppress(CaselessKeyword('FROM'))
NAMED = Suppress(CaselessKeyword('NAMED'))

# Question: will this return a list containing a single token, or
# just the single token?  I want the latter.
#
# Also, I think there is a bug in IRIRef.* in that they assume that the
# IRIref will be a URIRef, but it could also be a QName.
DatasetClause = (FROM + (
  IRIref.copy().setParseAction(
    refer_component(components.IRIRef.RemoteGraph)) |
  NAMED + IRIref.copy().setParseAction(
    refer_component(components.IRIRef.NamedGraph))))
if DEBUG:
    DatasetClause.setName('DatasetClause')

# String:
#
# TODO: flesh this out to include multiline strings, and also
# investigate a possible bug with Expression.ParsedString; it
# doesn't look like it is properly expanding escaped characters.
String = quotedString.setParseAction(composition2(
  [removeQuotes, components.Expression.ParsedString]))
if DEBUG:
    String.setName('String')

# RDFLiteral
AT = Suppress('@')
LANGTAG = AT + Regex(PN_CHARS_BASE_re + '+' +
                     regex_group('-[a-zA-Z0-9]+') + '*')

DOUBLE_HAT = Suppress('^^')
RDFLiteral = ((String + DOUBLE_HAT + IRIref).setParseAction(
    refer_component(components.Expression.ParsedDatatypedLiteral)) |
  (String + Optional(LANGTAG, None)).setParseAction(
    refer_component(rdflib.term.Literal)))
if DEBUG:
    RDFLiteral.setName('RDFLiteral')

# NumericLiteral:
#
# TODO: sort this out so that xsd:decimals and xsd:floats are properly
# segregated.
EXPONENT_re = r'(?:[eE][+-]?[0-9]+)'
INT_re = r'[+-]?[0-9]+'
INT = Regex(INT_re).setParseAction(composition(
  [refer_component(int), rdflib.term.Literal]))
INTEGER = Regex(r'[0-9]+').setParseAction(composition(
  [refer_component(int), rdflib.term.Literal]))
FLOAT_re = (r'[+-]?(?:(?:[0-9]+\.[0-9]*%s?)|' +
                    r'(?:\.[0-9]+%s?)|(?:[0-9]+%s))') % (
  (EXPONENT_re,) * 3)
FLOAT = Regex(FLOAT_re).setParseAction(composition(
  [refer_component(float), rdflib.term.Literal]))
NumericLiteral = (FLOAT | INT)
if DEBUG:
    NumericLiteral.setName('NumericLiteral')

# BooleanLiteral:
BooleanLiteral = (Keyword('true') | Keyword('false')).setParseAction(
  refer_component(rdflib.term.Literal, datatype=XSD_NS.boolean))
if DEBUG:
    BooleanLiteral.setName('BooleanLiteral')

# BlankNode:
ANON = Regex(r'\[' + WS_re + r'\]').setParseAction(
  refer_component(rdflib.term.BNode, None, []))
BLANK_NODE_LABEL = (Suppress('_:') + PN_LOCAL).setParseAction(
  refer_component(rdflib.term.BNode))
BlankNode = (BLANK_NODE_LABEL | ANON)
if DEBUG:
    BlankNode.setName('BlankNode')

# GraphTerm:
GraphTerm = (IRIref | RDFLiteral | NumericLiteral | BooleanLiteral |
             BlankNode | NIL)
if DEBUG:
    GraphTerm.setName('GraphTerm')

# VarOrTerm:
VarOrTerm = Var | GraphTerm
if DEBUG:
    VarOrTerm.setName('VarOrTerm')

# VarOrIRIref:
VarOrIRIref = Var | IRIref
if DEBUG:
    VarOrIRIref.setName('VarOrIRIref')

# Verb:
Verb = (VarOrIRIref | Keyword('a').setParseAction(
  refer_component(getattr, [rdflib.namespace.RDF, 'type'], [0, 1])))
if DEBUG:
    Verb.setName('Verb')


# Expression:
Expression = Forward()
if DEBUG:
    Expression.setName('Expression')

# BuiltInCall:
STR = Suppress(CaselessKeyword('STR'))
LANG = Suppress(CaselessKeyword('LANG'))
LANGMATCHES = Suppress(CaselessKeyword('LANGMATCHES'))
DATATYPE = Suppress(CaselessKeyword('DATATYPE'))
BOUND = Suppress(CaselessKeyword('BOUND'))
isIRI = Suppress(CaselessKeyword('isIRI'))
isURI = Suppress(CaselessKeyword('isURI'))
isBLANK = Suppress(CaselessKeyword('isBLANK'))
isLITERAL = Suppress(CaselessKeyword('isLITERAL'))
sameTerm = Suppress(CaselessKeyword('sameTERM'))

# RegexExpression
REGEX = Suppress(CaselessKeyword('REGEX'))
RegexExpression = (REGEX + LP + Expression + COMMA + Expression +
                   Optional(COMMA + Expression) + RP).setParseAction(
  refer_component(components.FunctionLibrary.ParsedREGEXInvocation))
if DEBUG:
    RegexExpression.setName('RegexExpression')

BuiltInCall = (
  (STR + LP + Expression + RP).setParseAction(
    refer_component(components.FunctionLibrary.BuiltinFunctionCall,
                    [components.FunctionLibrary.STR])) |
  (LANG + LP + Expression + RP).setParseAction(
    refer_component(components.FunctionLibrary.BuiltinFunctionCall,
                    [components.FunctionLibrary.LANG])) |
  (LANGMATCHES + LP + Expression + COMMA + Expression + RP).setParseAction(
    refer_component(components.FunctionLibrary.BuiltinFunctionCall,
                    [components.FunctionLibrary.LANGMATCHES])) |
  (DATATYPE + LP + Expression + RP).setParseAction(
    refer_component(components.FunctionLibrary.BuiltinFunctionCall,
                    [components.FunctionLibrary.DATATYPE])) |
  (BOUND + LP + Var + RP).setParseAction(
    refer_component(components.FunctionLibrary.BuiltinFunctionCall,
                    [components.FunctionLibrary.BOUND])) |
  (sameTerm + LP + Expression + COMMA + Expression + RP).setParseAction(
    refer_component(components.FunctionLibrary.BuiltinFunctionCall,
                    [components.FunctionLibrary.sameTERM])) |
  (isIRI + LP + Expression + RP).setParseAction(
    refer_component(components.FunctionLibrary.BuiltinFunctionCall,
                    [components.FunctionLibrary.isIRI])) |
  (isURI + LP + Expression + RP).setParseAction(
    refer_component(components.FunctionLibrary.BuiltinFunctionCall,
                    [components.FunctionLibrary.isURI])) |
  (isBLANK + LP + Expression + RP).setParseAction(
    refer_component(components.FunctionLibrary.BuiltinFunctionCall,
                    [components.FunctionLibrary.isBLANK])) |
  (isLITERAL + LP + Expression + RP).setParseAction(
    refer_component(components.FunctionLibrary.BuiltinFunctionCall,
                    [components.FunctionLibrary.isLITERAL])) |
  RegexExpression)
if DEBUG:
    BuiltInCall.setName('BuiltInCall')

ArgList = NIL | Group(LP + Expression + ZeroOrMore(COMMA + Expression) + RP)
if DEBUG:
    ArgList.setName('ArgList')

# FunctionCall:
FunctionCall = (IRIref + ArgList).setParseAction(
  refer_component(components.FunctionLibrary.FunctionCall))
if DEBUG:
    FunctionCall.setName('FunctionCall')

BrackettedExpression = LP + Expression + RP
if DEBUG:
    BrackettedExpression.setName('BrackettedExpression')
PrimaryExpression = (BrackettedExpression | BuiltInCall | FunctionCall |
                     IRIref | RDFLiteral | NumericLiteral |
                     BooleanLiteral | Var)
if DEBUG:
    PrimaryExpression.setName('PrimaryExpression')
UnaryExpression = (
  (Suppress('!') + PrimaryExpression).setParseAction(
    refer_component(components.Operators.LogicalNegation)) |
  (Suppress('+') + PrimaryExpression).setParseAction(
    refer_component(components.Operators.NumericPositive)) |
  (Suppress('-') + PrimaryExpression).setParseAction(
    refer_component(components.Operators.NumericNegative)) |
  PrimaryExpression)
if DEBUG:
    UnaryExpression.setName('UnaryExpression')
MultiplicativeExpression = Group(UnaryExpression + ZeroOrMore(
  (Literal('*') | Literal('/')) + UnaryExpression)).setParseAction(
    refer_component(components.Expression.ParsedMultiplicativeExpressionList))
if DEBUG:
    MultiplicativeExpression.setName('MultiplicativeExpression')
AdditiveExpression = Group(MultiplicativeExpression + ZeroOrMore(
  (Literal('+') | Literal('-')) + MultiplicativeExpression)).setParseAction(
    refer_component(components.Expression.ParsedAdditiveExpressionList))
if DEBUG:
    AdditiveExpression.setName('AdditiveExpression')
NumericExpression = AdditiveExpression
RelationalExpression = (
  (NumericExpression + Suppress('=') +
   NumericExpression).setParseAction(
    refer_component(components.Operators.EqualityOperator)) |
  (NumericExpression + Suppress('!=') +
   NumericExpression).setParseAction(
    refer_component(components.Operators.NotEqualOperator)) |
  (NumericExpression + Suppress('<') +
   NumericExpression).setParseAction(
    refer_component(components.Operators.LessThanOperator)) |
  (NumericExpression + Suppress('>') +
   NumericExpression).setParseAction(
    refer_component(components.Operators.GreaterThanOperator)) |
  (NumericExpression + Suppress('<=') +
   NumericExpression).setParseAction(
    refer_component(components.Operators.LessThanOrEqualOperator)) |
  (NumericExpression + Suppress('>=') +
   NumericExpression).setParseAction(
    refer_component(components.Operators.GreaterThanOrEqualOperator)) |
  NumericExpression)
if DEBUG:
    RelationalExpression.setName('RelationalExpression')
ValueLogical = RelationalExpression
ConditionalAndExpression = Group(ValueLogical +
  ZeroOrMore(Suppress('&&') + ValueLogical)).setParseAction(
    refer_component(components.Expression.ParsedRelationalExpressionList))
if DEBUG:
    ConditionalAndExpression.setName('ConditionalAndExpression')
ConditionalOrExpression = Group(ConditionalAndExpression +
  ZeroOrMore(Suppress('||') +
  ConditionalAndExpression)).setParseAction(
    refer_component(components.Expression.ParsedConditionalAndExpressionList))
if DEBUG:
    ConditionalOrExpression.setName('ConditionalOrExpression')
Expression << ConditionalOrExpression

# Constraint (used only in Filter):
Constraint = ((BrackettedExpression).setParseAction(
    refer_component(components.Filter.ParsedExpressionFilter)) |
  (BuiltInCall | FunctionCall).setParseAction(
    refer_component(components.Filter.ParsedFunctionFilter)))
if DEBUG:
    Constraint.setName('Constraint')

# Filter:
FILTER = Suppress(CaselessKeyword('FILTER'))
Filter = (FILTER + Constraint).setName('Filter')


# GraphNode is recursively defined in terms of Collection, ObjectList,
# PropertyListNotEmpty, and TriplesNode.
GraphNode = Forward()
if DEBUG:
    GraphNode.setName('GraphNode')

# Collection:
Collection = (LP + Group(OneOrMore(GraphNode)) + RP).setParseAction(
  refer_component(components.Resource.ParsedCollection))
if DEBUG:
    Collection.setName('Collection')

# ObjectList:
ObjectList = Group(GraphNode + ZeroOrMore(COMMA + GraphNode))
if DEBUG:
    ObjectList.setName('ObjectList')

# PropertyListNotEmpty:
PropertyListItem = (Verb + ObjectList).setParseAction(
  refer_component(components.Triples.PropertyValue))
if DEBUG:
    PropertyListItem.setName('PropertyListItem')
PropertyListNotEmpty = Group(PropertyListItem + ZeroOrMore(
  SEMICOLON + Optional(PropertyListItem)))
if DEBUG:
    PropertyListNotEmpty.setName('PropertyListNotEmpty')

# TriplesNode:
TriplesNode = Collection | (LB + PropertyListNotEmpty + RB).setParseAction(
  refer_component(components.Resource.Resource, [None]))
if DEBUG:
    TriplesNode.setName('TriplesNode')

# GraphNode:
GraphNode << (VarOrTerm | TriplesNode)


# TriplesBlock:
TriplesSameSubject = ((VarOrTerm + PropertyListNotEmpty).setParseAction(
    refer_component(components.Resource.Resource)) |
  (LB + PropertyListNotEmpty + RB +
   Optional(PropertyListNotEmpty, [])).setParseAction(
    refer_component(components.Resource.TwiceReferencedBlankNode)) |
  (Collection + Optional(PropertyListNotEmpty, [])).setParseAction(
    setPropertyValueList))
if DEBUG:
    TriplesSameSubject.setName('TriplesSameSubject')

TriplesBlock = Forward()
TriplesBlock << (TriplesSameSubject + Optional(PERIOD +
                 Optional(TriplesBlock)))
if DEBUG:
    TriplesBlock.setName('TriplesBlock')

# GroupGraphPattern:
GroupGraphPattern = Forward()
OPTIONAL = Suppress(CaselessKeyword('OPTIONAL'))
OptionalGraphPattern = (OPTIONAL + GroupGraphPattern).setParseAction(
  refer_component(components.GraphPattern.ParsedOptionalGraphPattern))
if DEBUG:
    OptionalGraphPattern.setName('OptionalGraphPattern')
UNION = Suppress(CaselessKeyword('UNION'))
UnionGraphPattern = Group(GroupGraphPattern + OneOrMore(
  UNION + GroupGraphPattern)).setParseAction(
    refer_component(components.GraphPattern.ParsedAlternativeGraphPattern))
if DEBUG:
    UnionGraphPattern.setName('UnionGraphPattern')
GRAPH = Suppress(CaselessKeyword('GRAPH'))
GraphGraphPattern = (GRAPH + VarOrIRIref + GroupGraphPattern).setParseAction(
  refer_component(components.GraphPattern.ParsedGraphGraphPattern))
if DEBUG:
    GraphGraphPattern.setName('GraphGraphPattern')
GraphPatternNotTriples = (OptionalGraphPattern | UnionGraphPattern |
                          GraphGraphPattern | GroupGraphPattern)
if DEBUG:
    GraphPatternNotTriples.setName('GraphPatternNotTriples')

GraphPattern = ((Filter + Optional(PERIOD) +
                Optional(Group(TriplesBlock))).setParseAction(
    refer_component(components.GraphPattern.GraphPattern, [None])) |
  (GraphPatternNotTriples + Optional(PERIOD) +
   Optional(Group(TriplesBlock), None)).setParseAction(
    refer_component(components.GraphPattern.GraphPattern, [None], [1, 0, 2])))
if DEBUG:
    GraphPattern.setName('GraphPattern')

GroupGraphPattern << (LC + Optional(Group(TriplesBlock), None) +
                      Group(ZeroOrMore(GraphPattern)) + RC).setParseAction(
  refer_component(components.GraphPattern.ParsedGroupGraphPattern))
if DEBUG:
    GroupGraphPattern.setName('GroupGraphPattern')

# WhereClause:
WHERE = Suppress(Optional(CaselessKeyword('WHERE')))
WhereClause = (WHERE + GroupGraphPattern).setParseAction(
  refer_component(components.Query.WhereClause))
if DEBUG:
    WhereClause.setName('WhereClause')

# RecurseClause:
RECURSE = Suppress(CaselessKeyword('RECURSE'))
TO = Suppress(CaselessKeyword('TO'))
RecurseClause = (RECURSE + Group(OneOrMore(Group(Var + TO + Var))) + 
                 Optional(GroupGraphPattern, None)).setParseAction(
  refer_component(components.Query.RecurseClause))
if DEBUG:
    RecurseClause.setName('RecurseClause')

# SolutionModifier:
ASC = Suppress(Optional(CaselessKeyword('ASC')))
DESC = Suppress(Optional(CaselessKeyword('DESC')))
OrderCondition = (
  (ASC + BrackettedExpression).setParseAction(
    refer_component(components.SolutionModifier.ParsedOrderConditionExpression,
                    [components.SolutionModifier.ASCENDING_ORDER], [1, 0])) |
  (DESC + BrackettedExpression).setParseAction(
    refer_component(components.SolutionModifier.ParsedOrderConditionExpression,
                    [components.SolutionModifier.DESCENDING_ORDER], [1, 0])) |
  BrackettedExpression.copy().setParseAction(
    refer_component(components.SolutionModifier.ParsedOrderConditionExpression,
                    [components.SolutionModifier.UNSPECIFIED_ORDER], [1, 0])) |
  BuiltInCall | FunctionCall | Var)
if DEBUG:
    OrderCondition.setName('OrderCondition')
ORDER = Suppress(Optional(CaselessKeyword('ORDER')))
BY = Suppress(Optional(CaselessKeyword('BY')))
OrderClause = ORDER + BY + Group(OneOrMore(OrderCondition))
if DEBUG:
    OrderClause.setName('OrderClause')
LIMIT = Suppress(Optional(CaselessKeyword('LIMIT')))
LimitClause = LIMIT + INTEGER
if DEBUG:
    LimitClause.setName('LimitClause')
OFFSET = Suppress(Optional(CaselessKeyword('OFFSET')))
OffsetClause = OFFSET + INTEGER
if DEBUG:
    OffsetClause.setName('OffsetClause')
SolutionModifier = (
  (Optional(OrderClause, None) + Optional(LimitClause, None) +
   Optional(OffsetClause, None)).setParseAction(
    refer_component(components.SolutionModifier.SolutionModifier)) |
  (Optional(OrderClause, None) + Optional(OffsetClause, None) +
   Optional(LimitClause, None)).setParseAction(
    refer_component(components.SolutionModifier.SolutionModifier,
                    projection=[0, 2, 1])))
if DEBUG:
    SolutionModifier.setName('SolutionModifier')

# SelectQuery:
SELECT = Suppress(CaselessKeyword('SELECT'))
DISTINCT = Optional(CaselessKeyword('DISTINCT'), None)

SelectQuery = (SELECT + DISTINCT + 
  (Group(OneOrMore(Var)) | Literal('*').setParseAction(as_empty)) +
  Group(ZeroOrMore(DatasetClause)) + 
  WhereClause + Optional(RecurseClause, None) +
  SolutionModifier).setParseAction(
    refer_component(components.Query.SelectQuery,
                    projection=[1, 2, 3, 4, 5, 0]))
if DEBUG:
    SelectQuery.setName('SelectQuery')

# ConstructQuery:
CONSTRUCT = Suppress(CaselessKeyword('CONSTRUCT'))

ConstructTemplate = LC + Optional(Group(TriplesBlock), []) + RC

ConstructQuery = (CONSTRUCT + ConstructTemplate +
  Group(ZeroOrMore(DatasetClause)) + WhereClause +
  SolutionModifier).setParseAction(
    refer_component(components.Query.ConstructQuery))
if DEBUG:
    ConstructQuery.setName('ConstructQuery')

# DescribeQuery:
DESCRIBE = Suppress(CaselessKeyword('DESCRIBE'))

DescribeQuery = (DESCRIBE + 
  (Group(OneOrMore(Var)) | Literal('*').setParseAction(as_empty)) +
  Group(ZeroOrMore(DatasetClause)) + Optional(WhereClause, None) +
  SolutionModifier).setParseAction(
    refer_component(components.Query.DescribeQuery))
if DEBUG:
    DescribeQuery.setName('DescribeQuery')

# AskQuery:
ASK = Suppress(CaselessKeyword('ASK'))

AskQuery = (ASK + Group(ZeroOrMore(DatasetClause)) +
            WhereClause).setParseAction(
              refer_component(components.Query.AskQuery))
if DEBUG:
    AskQuery.setName('AskQuery')

# Query:
Query = (Prologue + (SelectQuery | ConstructQuery |
                     DescribeQuery | AskQuery)).setParseAction(
  refer_component(components.Query.Query))
Query.ignore('#' + restOfLine)
if DEBUG:
    Query.setName('Query')

def parse(stuff):
    if DEBUG:
        tracer = ParseTracer()
        resultfile = open('parse-trace.xml', 'w')
        return tracer.parse(Query, stuff, resultfile)
    return Query.parseString(stuff)[0]

if __name__ == "__main__":
    testCases = [
# basic
"""
SELECT ?name
WHERE { ?a <http://xmlns.com/foaf/0.1/name> ?name }
""",
# simple prefix
"""
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?name
WHERE { ?a foaf:name ?name }
""",
# base statement
"""
BASE <http://xmlns.com/foaf/0.1/>
SELECT ?name
WHERE { ?a <name> ?name }
""",
# prefix and colon-only prefix
"""
PREFIX : <http://xmlns.com/foaf/0.1/>
PREFIX vcard: <http://www.w3.org/2001/vcard-rdf/3.0#>
SELECT ?name ?title
WHERE {
    ?a :name ?name .
    ?a vcard:TITLE ?title
}
""",
# predicate-object list notation
"""
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?name ?mbox
WHERE {
    ?x  foaf:name  ?name ;
        foaf:mbox  ?mbox .
}
""",
# object list notation
"""
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?x
WHERE {
    ?x foaf:nick  "Alice" ,
                  "Alice_" .
}
""",
# escaped literals
"""
PREFIX tag: <http://xmlns.com/foaf/0.1/>
PREFIX vcard: <http://www.w3.org/2001/vcard-rdf/3.0#>
SELECT ?name
WHERE {
    ?a tag:name ?name ;
       vcard:TITLE "escape test vcard:TITLE " ;
       <tag://test/escaping> "This is a ''' Test \"\"\"" ;
       <tag://test/escaping> ?d
}
""",
# key word as variable
"""
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?PREFIX ?WHERE
WHERE {
    ?x  foaf:name  ?PREFIX ;
        foaf:mbox  ?WHERE .
}
""",
# key word as prefix
"""
PREFIX WHERE: <http://xmlns.com/foaf/0.1/>
SELECT ?name ?mbox
WHERE {
    ?x  WHERE:name  ?name ;
        WHERE:mbox  ?mbox .
}
""",
# some test cases from grammar.py
"SELECT ?title WHERE { <http://example.org/book/book1> <http://purl.org/dc/elements/1.1/title> ?title . }",

"""PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?name ?mbox
WHERE { ?person foaf:name ?name .
OPTIONAL { ?person foaf:mbox ?mbox}
}""",

"""PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?name ?name2
WHERE { ?person foaf:name ?name .
OPTIONAL { ?person foaf:knows ?p2 . ?p2 foaf:name   ?name2 . }
}""",

"""PREFIX foaf: <http://xmlns.com/foaf/0.1/>
#PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?name ?mbox
WHERE
{
{ ?person rdf:type foaf:Person } .
OPTIONAL { ?person foaf:name  ?name } .
OPTIONAL {?person foaf:mbox  ?mbox} .
}"""
    ]

    print "Content-type: text/plain\n\n"
    for query in testCases:
        print "\n-----\n"
        print '>>> query = """' + query.replace("\n", "\n... ") + '"""'
        print ">>> result = doSPARQL(query, sparqlGr)\n"
        result = _buildQueryArgs(query);
        print "select = ", result["select"], "\n"
        print "where = ", result["where"], "\n"
        print "optional = ", result["optional"], "\n"
        print "result = sparqlGr.query(select, where, optional)"
