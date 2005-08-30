
from pyparsing import CaselessLiteral, Word, Upcase, delimitedList, Optional, \
     Combine, Group, alphas, nums, alphanums, ParseException, Forward, oneOf, \
     ZeroOrMore, restOfLine, Keyword, srange, OneOrMore, sglQuotedString, dblQuotedString, quotedString, \
     TokenConverter, Empty, Suppress, NoMatch, CharsNotIn

from pyparsing import Literal as ppLiteral  # name Literal assigned by grammar

DEBUG = 0

def punctuation(lit):
    o =  ppLiteral(lit).setName(lit).setResultsName(lit)
    if DEBUG: o.setDebug()
    return o

def keyword(lit):
    o = Keyword(lit, caseless=True).setResultsName(lit).setName(lit)
    if DEBUG: o.setDebug()
    return o

def production(lit):
    o = Forward().setResultsName(lit).setName(lit)
    if DEBUG: o.setDebug()
    return o

class SPARQLGrammar(object):

    # All productions are declared Forward().  This is primarily
    # because the SPARQL spec defines the EBNF grammar in this way and
    # I have stuck rigedly to the spec order.  Paul McGuire (author of
    # pyparsing) has recommended that I reverse the grammar
    # definitions for clarity and performance as Forward()s incur an
    # inderection performance hit.
    #
    # For now I want to keep it this way because SPARQL is still in
    # flux, but as the language stabilizes it will make sense to
    # reverse this grammar into something more "pythonic".

    dot = punctuation(".")
    at = punctuation("@")
    dash = punctuation("-")
    qmark = punctuation("?")
    dollar = punctuation("$")    
    colon = punctuation(":")
    semi = punctuation(";")    
    lt = punctuation("<")
    gt = punctuation(">")
    typ = punctuation("^^")
    lparen = punctuation("(")
    rparen = punctuation(")")
    bang = punctuation("!")
    star = punctuation("*")
    slash = punctuation("/")
    plus = punctuation("+")
    minus = punctuation("-")
    lte = punctuation("<=")
    gte = punctuation(">=")
    eq = punctuation("=")
    noteq = punctuation("!=")
    lbrack = punctuation("[")
    rbrack = punctuation("]")
    lcbrack = punctuation("{")
    rcbrack = punctuation("}")
    leq = punctuation('eq')
    lne = punctuation('ne')
    bnode = punctuation('_:')
    comma = punctuation(',')

    # keywords

    _select = keyword('select')
    _distinct = keyword('distinct')
    _construct = keyword('construct')
    _describe = keyword('describe')
    _ask = keyword('ask')
    _from = keyword('from')
    _where = keyword('where')
    _optional = keyword('optional')
    _prefix = keyword('prefix')
    _limit = keyword('limit')
    _base = keyword('base')
    _named = keyword('named')
    _offset = keyword('offset')
    _a = keyword('a')
    _str = keyword('str')
    _true = keyword('true')
    _false = keyword('false')
    _order = keyword('order')
    _by = keyword('by')
    _asc = keyword('asc')
    _desc = keyword('desc')
    _graph = keyword('graph')
    _union = keyword('union')
    _filter = keyword('filter')
    _lang = keyword('lang')
    _datatype = keyword('datatype')
    _bound = keyword('bound')
    _isuri = keyword('isuri')
    _isblank = keyword('isblank')
    _isliteral = keyword('isliteral')
    _regex = keyword('regex')

    # productions

    Query = production('Query')
    Prolog = production('Prolog')
    BaseDecl = production('BaseDecl')
    PrefixDecl = production('PrefixDecl')
    SelectQuery = production('SelectQuery')
    ConstructQuery = production('ConstructQuery')
    DescribeQuery = production('DescribeQuery')
    AskQuery = production('AskQuery')
    DatasetClause = production('DatasetClause')
    DefaultGraphClause = production('DefaultGraphClause')
    NamedGraphClause = production('NamedGraphClause')
    SourceSelector = production('SourceSelector')
    WhereClause = production('WhereClause')
    SolutionModifier = production('SolutionModifier')
    OrderClause = production('OrderClause')
    OrderCondition = production('OrderCondition')
    LimitClause = production('LimitClause')
    OffsetClause = production('OffsetClause')
    GroupGraphPattern = production('GroupGraphPattern')
    GraphPattern = production('GraphPattern')
    GraphPatternNotTriples = production('GraphPatternNotTriples')
    OptionalGraphPattern = production('OptionalGraphPattern')
    GraphGraphPattern = production('GraphGraphPattern')
    GroupOrUnionGraphPattern = production('GroupOrUnionGraphPattern')
    Constraint = production('Constraint')
    ConstructTemplate = production('ConstructTemplate')
    Triples = production('Triples')
    Triples1 = production('Triples1')
    PropertyList = production('PropertyList')
    PropertyListNotEmpty = production('PropertyListNotEmpty')
    ObjectList = production('ObjectList')
    Verb = production('Verb')
    Object = production('Object')
    TriplesNode = production('TriplesNode')
    BlankNodePropertyList = production('BlankNodePropertyList')
    Collection = production('BlankNodePropertyList')
    GraphNode = production('GraphNode')
    VarOrTerm = production('VarOrTerm')
    VarOrIRIref = production('VarOrIRIref')
    VarOrBlankNodeOrIRIref = production('VarOrBlankNodeOrIRIref')
    Var = production('Var')
    GraphTerm = production('GraphTerm')
    Expression = production('Expression')
    ConditionalOrExpression = production('ConditionalOrExpression')
    ConditionalAndExpression = production('ConditionalAndExpression')
    ValueLogical = production('ValueLogical')
    RelationalExpression = production('RelationalExpression')
    NumericExpression = production('NumericExpression')
    AdditiveExpression = production('AdditiveExpression')
    MultiplicativeExpression = production('MultiplicativeExpression')
    UnaryExpression = production('UnaryExpression')
    CallExpression = production('CallExpression')
    RegexExpression = production('RegexExpression')
    FunctionCall = production('FunctionCall')
    ArgList = production('ArgList')
    BrackettedExpression = production('BrackettedExpression')
    PrimaryExpression = production('PrimaryExpression')
    RDFTerm = production('RDFTerm')
    NumericLiteral = production('NumericLiteral')
    RDFLiteral = production('RDFLiteral')
    BooleanLiteral = production('BooleanLiteral')
    String = production('String')
    IRIref = production('IRIref')
    QName = production('QName')
    BlankNode = production('BlankNode')
    QuotedIRIref = production('QuotedIRIref')
    QNAME_NS = production('QNAME_NS')
    QNAME = production('QNAME')
    BNODE_LABEL = production('BNODE_LABEL')
    VAR1 = production('VAR1')
    VAR2 = production('VAR2')
    LANGTAG = production('LANGTAG')
    INTEGER = production('INTEGER')
    DECIMAL = production('DECIMAL')
    FLOATING_POINT = production('FLOATING_POINT')
    EXPONENT = production('EXPONENT')
    STRING_LITERAL1 = production('STRING_LITERAL1')
    STRING_LITERAL2 = production('STRING_LITERAL2')
    STRING_LITERAL_LONG1 = production('STRING_LITERAL_LONG1')
    STRING_LITERAL_LONG2 = production('STRING_LITERAL_LONG2')
    NCCHAR1 = production('NCCHAR1')
    VARNAME = production('VARNAME')
    NCCHAR  = production('NCCHAR')
    NCNAME_PREFIX = production('NCNAME_PREFIX')
    NCNAME = production('NCNAME')

    _comment = '#' + restOfLine
    
    # BEGIN PRODUCTIONS
    
    # Query ::= Prolog
    #      ( SelectQuery | ConstructQuery | DescribeQuery | AskQuery )

    Query << Prolog + (SelectQuery | ConstructQuery | DescribeQuery | AskQuery)
    Query.ignore(_comment)

    # Prolog ::= BaseDecl? PrefixDecl*

    Prolog << Optional(BaseDecl) + ZeroOrMore(PrefixDecl)

    # BaseDecl ::= 'BASE' QuotedIRIref

    BaseDecl << _base + QuotedIRIref

    # PrefixDecl ::= 'PREFIX' QNAME_NS QuotedIRIref

    PrefixDecl << (_prefix + QNAME_NS + QuotedIRIref)

    # SelectQuery ::= 'SELECT' 'DISTINCT'? ( Var+ | '*' ) DatasetClause* WhereClause SolutionModifier

    SelectQuery << (_select + Optional(_distinct) + (OneOrMore(Var) | star) +
                    ZeroOrMore(DatasetClause) + WhereClause + SolutionModifier)

    # ConstructQuery ::= 'CONSTRUCT' ConstructTemplate DatasetClause* WhereClause SolutionModifier

    ConstructQuery << _construct + ConstructTemplate + ZeroOrMore(DatasetClause) + WhereClause + SolutionModifier

    # DescribeQuery ::= 'DESCRIBE' ( VarOrIRIref+ | '*' ) DatasetClause* WhereClause? SolutionModifier

    DescribeQuery << (_describe + (OneOrMore(VarOrIRIref) | star) +
                      ZeroOrMore(DatasetClause) + Optional(WhereClause) + SolutionModifier)

    # AskQuery ::= 'ASK' DatasetClause* WhereClause

    AskQuery << _ask + ZeroOrMore(DatasetClause) + WhereClause

    # DatasetClause ::= 'FROM' ( DefaultGraphClause | NamedGraphClause )

    DatasetClause << _from + (DefaultGraphClause | NamedGraphClause)

    # DefaultGraphClause ::= SourceSelector

    DefaultGraphClause << SourceSelector

    # NamedGraphClause ::= 'NAMED' SourceSelector

    NamedGraphClause << _named + SourceSelector

    # SourceSelector ::= IRIref

    SourceSelector << IRIref

    # WhereClause ::= 'WHERE'? GroupGraphPattern

    WhereClause << (Optional(_where) + GroupGraphPattern)

    # SolutionModifier ::= OrderClause? LimitClause? OffsetClause?

    SolutionModifier << Optional(OrderClause) + Optional(LimitClause) + Optional(OffsetClause)

    # OrderClause ::= 'ORDER' 'BY' OrderCondition+

    OrderClause << _order + _by + OneOrMore(OrderCondition)

    # OrderCondition ::= ( ( 'ASC' | 'DESC' ) BrackettedExpression )
    #      | ( FunctionCall | Var | BrackettedExpression )

    OrderCondition << (((_asc | _desc) + BrackettedExpression) | (FunctionCall | Var | BrackettedExpression))

    # LimitClause ::= 'LIMIT' INTEGER

    LimitClause << _limit + INTEGER

    # OffsetClause ::= 'OFFSET' INTEGER

    OffsetClause << _offset + INTEGER

    # GroupGraphPattern ::= '{' GraphPattern '}'

    GroupGraphPattern << (lcbrack.suppress() + GraphPattern + rcbrack.suppress())

    # GraphPattern ::= ( Triples '.'? )? ( GraphPatternNotTriples '.'? GraphPattern )?

    GraphPattern << Optional(Triples + Optional(dot.suppress())) + Optional(GraphPatternNotTriples + Optional(dot.suppress()) + GraphPattern)

    # GraphPatternNotTriples ::= OptionalGraphPattern | GroupOrUnionGraphPattern | GraphGraphPattern | Constraint

    GraphPatternNotTriples << (OptionalGraphPattern | GroupOrUnionGraphPattern | GraphGraphPattern | Constraint)

    # OptionalGraphPattern ::= 'OPTIONAL' GroupGraphPattern

    OptionalGraphPattern << _optional + GroupGraphPattern

    # GraphGraphPattern ::= 'GRAPH' VarOrBlankNodeOrIRIref GroupGraphPattern

    GraphGraphPattern << _graph + VarOrBlankNodeOrIRIref + GroupGraphPattern

    # GroupOrUnionGraphPattern ::= GroupGraphPattern ( 'UNION' GroupGraphPattern )*

    GroupOrUnionGraphPattern << GroupGraphPattern + ZeroOrMore(_union + GroupGraphPattern)

    # Constraint ::= 'FILTER' ( BrackettedExpression | CallExpression )

    Constraint << _filter + (BrackettedExpression | CallExpression)

    # ConstructTemplate ::= '{' Triples? '.'? '}'

    ConstructTemplate << lcbrack + Optional(Triples) + Optional(dot.suppress()) + rcbrack

    # Triples ::= Triples1 ( '.' Triples )?

    Triples << Triples1 + Optional(dot.suppress() + Triples)

    # Triples1 ::= VarOrTerm PropertyListNotEmpty | TriplesNode PropertyList

    Triples1 << (VarOrTerm + PropertyListNotEmpty | TriplesNode + PropertyList)

    # PropertyList ::= PropertyListNotEmpty?

    PropertyList << Optional(PropertyListNotEmpty)

    # PropertyListNotEmpty ::= Verb ObjectList ( ';' PropertyList )?

    PropertyListNotEmpty << Verb + ObjectList + Optional(semi + PropertyList)

    # ObjectList ::= Object ( ',' ObjectList )?

    ObjectList << Object + Optional(comma + ObjectList)

    # Verb ::= VarOrBlankNodeOrIRIref | 'a'

    Verb << VarOrBlankNodeOrIRIref | _a

    # Object ::= VarOrTerm | TriplesNode

    Object << (VarOrTerm | TriplesNode)

    # TriplesNode ::= Collection | BlankNodePropertyList

    TriplesNode << (Collection | BlankNodePropertyList)

    # BlankNodePropertyList ::= '[' PropertyListNotEmpty ']'

    BlankNodePropertyList << lbrack + PropertyListNotEmpty + rbrack

    # Collection ::= '(' GraphNode+ ')'

    Collection << lparen + OneOrMore(GraphNode) + rparen

    # GraphNode ::= VarOrTerm | TriplesNode

    GraphNode << (VarOrTerm | TriplesNode)

    # VarOrTerm ::= Var | GraphTerm

    VarOrTerm << (Var | GraphTerm)

    # VarOrIRIref ::= Var | IRIref

    VarOrIRIref << (Var | IRIref)

    # VarOrBlankNodeOrIRIref ::= Var | BlankNode | IRIref

    VarOrBlankNodeOrIRIref << (Var | BlankNode | IRIref)

    # Var ::= VAR1 | VAR2

    Var << (VAR1 | VAR2)

    # GraphTerm ::= RDFTerm | '(' ')'

    GraphTerm << (RDFTerm | lparen + rparen)

    # Expression ::= ConditionalOrExpression

    Expression << ConditionalOrExpression

    # ConditionalOrExpression ::= ConditionalAndExpression ( '||' ConditionalAndExpression )*

    ConditionalAndExpression << ConditionalAndExpression + ZeroOrMore( '||' + ConditionalAndExpression)

    # ConditionalAndExpression ::= ValueLogical ( '&&' ValueLogical )*

    ConditionalAndExpression << ValueLogical + ZeroOrMore('&&' + ValueLogical)

    # ValueLogical ::= RelationalExpression

    ValueLogical << RelationalExpression

    # RelationalExpression ::= NumericExpression ( '=' NumericExpression | '!=' NumericExpression | '<' NumericExpression | '>' NumericExpression | '<=' NumericExpression | '>=' NumericExpression )?

    RelationalExpression << (NumericExpression +
                             Optional(eq + NumericExpression | noteq + NumericExpression |
                                      lt + NumericExpression | gt + NumericExpression |
                                      lte + NumericExpression | gte + NumericExpression))

    # NumericExpression ::= AdditiveExpression

    NumericExpression << AdditiveExpression

    # AdditiveExpression ::= MultiplicativeExpression ( '+' MultiplicativeExpression | '-' MultiplicativeExpression )*

    AdditiveExpression << (MultiplicativeExpression + ZeroOrMore(plus + MultiplicativeExpression |
                                                                 minus + MultiplicativeExpression))

    # MultiplicativeExpression ::= UnaryExpression ( '*' UnaryExpression | '/' UnaryExpression )*

    MultiplicativeExpression << UnaryExpression + ZeroOrMore(star + UnaryExpression | slash + UnaryExpression)

    # UnaryExpression ::=   '!' PrimaryExpression
    #      | '+' PrimaryExpression
    #      | '-' PrimaryExpression
    #      | PrimaryExpression

    UnaryExpression << (bang + PrimaryExpression | plus + PrimaryExpression |
                        minus + PrimaryExpression | PrimaryExpression)

    # CallExpression ::=   'STR' '(' Expression ')'
    #      | 'LANG' '(' Expression ')'
    #      | 'DATATYPE' '(' Expression ')'
    #      | 'BOUND' '(' Var ')'
    #      | 'isURI' '(' Expression ')'
    #      | 'isBLANK' '(' Expression ')'
    #      | 'isLITERAL' '(' Expression ')'
    #      | RegexExpression
    #      | FunctionCall

    CallExpression << (_str + lparen + Expression + rparen |
                       _lang + lparen + Expression + rparen |
                       _datatype + lparen + Expression + rparen |
                       _bound + lparen + Var + rparen |
                       _isuri + lparen + Expression + rparen |
                       _isblank + lparen + Expression + rparen |
                       _isliteral + lparen + Expression + rparen |
                       RegexExpression |
                       FunctionCall)

    # RegexExpression ::= 'REGEX' '(' Expression ',' Expression ( ',' Expression )? ')'

    RegexExpression << _regex + lparen + Expression + comma + Expression + Optional(comma + Expression) + rparen

    # FunctionCall ::= IRIref ArgList

    FunctionCall << IRIref + ArgList

    # ArgList ::= ( '(' ')' | '(' Expression ( ',' Expression )* ')' )

    ArgList << ((lparen + rparen) | rparen + Expression + ZeroOrMore(comma + Expression) + rparen)

    # BrackettedExpression ::= '(' Expression ')'

    BrackettedExpression << lparen + Expression + rparen

    # PrimaryExpression ::= BrackettedExpression | CallExpression | Var | RDFTerm

    PrimaryExpression << (BrackettedExpression | CallExpression | Var | RDFTerm)

    # RDFTerm ::= IRIref | RDFLiteral | NumericLiteral | BooleanLiteral | BlankNode

    RDFTerm << (IRIref | RDFLiteral | NumericLiteral | BooleanLiteral | BlankNode)

    # NumericLiteral ::= INTEGER | FLOATING_POINT

    NumericLiteral << (INTEGER | FLOATING_POINT)

    # RDFLiteral ::= String ( LANGTAG | ( '^^' IRIref ) )?

    RDFLiteral << String + Optional( LANGTAG | ( typ + IRIref))

    # BooleanLiteral ::= 'true' | 'false'

    BooleanLiteral << (_true | _false)

    # String ::= STRING_LITERAL1 | STRING_LITERAL2 | STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2

    String << (STRING_LITERAL1 | STRING_LITERAL2 | STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2)

    # IRIref ::= QuotedIRIref | QName

    IRIref << (QuotedIRIref | QName)

    # QName ::= QNAME | QNAME_NS

    QName << (QNAME | QNAME_NS)

    # BlankNode ::= BNODE_LABEL | '[' ']'

    BlankNode << (BNODE_LABEL | rbrack + lbrack)

    # QuotedIRIref ::= '<' ([^> ])* '>' /* An IRI reference : RFC 3987 */

    QuotedIRIref << lt.suppress() + ZeroOrMore(CharsNotIn('> ')) + gt.suppress()

    # QNAME_NS ::= NCNAME_PREFIX? ':'

    QNAME_NS << Optional(NCNAME_PREFIX) + colon.suppress()

    # QNAME ::= NCNAME_PREFIX? ':' NCNAME?

    QNAME << Optional(NCNAME_PREFIX) + colon + Optional(NCNAME_PREFIX)

    # BNODE_LABEL ::= '_:' NCNAME

    BNODE_LABEL << bnode + NCNAME

    # VAR1 ::= '?' VARNAME

    VAR1 << qmark.suppress() + VARNAME

    # VAR2 ::= '$' VARNAME

    VAR2 << dollar.suppress() + VARNAME

    # LANGTAG ::= '@' [a-zA-Z]+ ('-' [a-zA-Z0-9]+)*

    LANGTAG << at + Word(alphas) + ZeroOrMore(dash + Word(alphas + nums))

    # INTEGER ::= [0-9]+

    INTEGER << Word(nums)

    # DECIMAL ::= [0-9]+ '.' [0-9]* | '.' [0-9]+

    DECIMAL << Word(nums) + dot.suppress() + ZeroOrMore(nums)

    # FLOATING_POINT ::= [0-9]+ '.' [0-9]* EXPONENT? | '.' ([0-9])+ EXPONENT? | ([0-9])+ EXPONENT

    FLOATING_POINT << (OneOrMore(nums) + dot + ZeroOrMore(nums) + Optional(EXPONENT) |
                       dot + OneOrMore(nums) + Optional(EXPONENT) | OneOrMore(nums) + EXPONENT)

    # EXPONENT ::= [eE] [+-]? [0-9]+

    EXPONENT << oneOf('e E') + Optional(oneOf('+ -')) + OneOrMore(nums)

    # STRING_LITERAL1 ::= "'" ( ([^#x27#x5C#xA#xD]) | ('\' [^#xD#xA]) )* "'"

    STRING_LITERAL1 << sglQuotedString

    # STRING_LITERAL2 ::= '"' ( ([^#x22#x5C#xA#xD]) | ('\' [^#xD#xA]) )* '"'

    STRING_LITERAL2 << dblQuotedString

    # STRING_LITERAL_LONG1 ::= "'''" ( [^'\] | ('\' [^#xD#xA]) | ("'" [^']) | ("''" [^']) )* "'''" 

    # STRING_LITERAL_LONG2 ::= '"""' ( [^"\] | ('\' [^#xD#xA]) | ('"' [^"]) | ('""' [^"]) )* '"""'

    # NCCHAR1 ::=   [A-Z]
    #      | [a-z]
    #      | [#x00C0-#x00D6]
    #      | [#x00D8-#x00F6]
    #      | [#x00F8-#x02FF]
    #      | [#x0370-#x037D]
    #      | [#x037F-#x1FFF]
    #      | [#x200C-#x200D]
    #      | [#x2070-#x218F]
    #      | [#x2C00-#x2FEF]
    #      | [#x3001-#xD7FF]
    #      | [#xF900-#xFDCF]
    #      | [#xFDF0-#xFFFD]
    #      | [#x10000-#xEFFFF]

    NCCHAR1 << Word(alphas)

    # VARNAME ::= ( NCCHAR1 | [0-9] ) ( NCCHAR1 | "_" | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] )*

    VARNAME << Word(alphas+nums, alphas+nums+"_")

    # NCCHAR ::= NCCHAR1 | '_' | '-' | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040]

    NCCHAR << (NCCHAR1 | "_" | "-" | Word(nums))

    # NCNAME_PREFIX ::= NCCHAR1 ((NCCHAR|".")* NCCHAR)?

    NCNAME_PREFIX << NCCHAR1 + Optional(ZeroOrMore(NCCHAR | ".") + NCCHAR)

    # NCNAME ::= ( "_" | NCCHAR1 ) ((NCCHAR|".")* NCCHAR)?

    NCNAME << ("_" | NCCHAR1)


if __name__ == '__main__':

    ts = ["SELECT ?title ?bob WHERE { }",
          "SELECT ?title WHERE { <http://example.org/book/book1> <http://purl.org/dc/elements/1.1/title> ?title . }",
#          "PREFIX  : <http://example.org/ns#> SELECT  ?a ?c WHERE { ?a :b ?c . OPTIONAL { ?c :d ?e } . FILTER ! bound(?e) }}",
          "",
          "",

          ]

    for t in ts:

        try:
            tokens = SPARQLGrammar.Query.parseString(t)
            print t
            print tokens
            print tokens.asXML()
        except ParseException, err:
            print t
            print " "*err.loc + "^" + err.msg
            print err
