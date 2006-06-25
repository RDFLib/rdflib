
from pyparsing import CaselessLiteral, Word, Upcase, delimitedList, Optional, \
     Combine, Group, alphas, nums, alphanums, ParseException, Forward, oneOf, \
     ZeroOrMore, restOfLine, Keyword, srange, OneOrMore, sglQuotedString, dblQuotedString, quotedString, \
     TokenConverter, Empty, Suppress, NoMatch

from pyparsing import Literal as ppLiteral

def punctuation(lit):
    return ppLiteral(lit)

def keyword(lit):
    return Keyword(lit, caseless=True).setResultsName(lit).setName(lit)

def production(lit):
    return Forward().setResultsName(lit).setName(lit)

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
    zero = punctuation("0")
    at = punctuation("@")
    dash = punctuation("-")
    qmark = punctuation("?")
    colon = punctuation(":")
    lt = punctuation("<")
    gt = punctuation(">")
    typ = punctuation("^^")
    amp = punctuation("&")
    lparen = punctuation("(")
    rparen = punctuation(")")
    tilde = punctuation("~")
    bang = punctuation("!")
    star = punctuation("*")
    slash = punctuation("/")
    mod = punctuation("%")
    plus = punctuation("+")
    minus = punctuation("-")
    lte = punctuation("<=")
    gte = punctuation(">=")
    eqeq = punctuation("==")
    noteq = punctuation("!=")
    lbrack = punctuation("[")
    rbrack = punctuation("]")
    leq = punctuation('eq')
    lne = punctuation('ne')
    eqpat = punctuation('=~')
    nepat = punctuation('!~')

    # keywords

    select = keyword('select')
    distinct = keyword('distinct')
    construct = keyword('construct')
    describe = keyword('describe')
    ask = keyword('ask')
    ffrom = keyword('from')
    where = keyword('where')
    source = keyword('source')
    optional = keyword('optional')
    aand = keyword('and')
    prefix = keyword('prefix')
    limit = keyword('limit')

    # productions

    Query = production('Query')
    ReportFormat = production('ReportFormat')
    FromClause = production('FromClause')
    FromSelector = production('FromSelector')
    WhereClause = production('WhereClause')
    LimitClause = production('LimitClause')
    SourceGraphPattern = production('SourceGraphPattern')
    OptionalGraphPattern = production('OptionalGraphPattern')
    GraphPattern = production('GraphPattern')
    PatternElement = production('PatternElement')
    GraphPattern1 = production('GraphPattern1')
    PatternElement1 = production('PatternElement1')
    PatternElementForms = production('PatternElementForms')
    SingleTriplePatternOrGroup = production('SingleTriplePatternOrGroup')
    ExplicitGroup = production('ExplicitGroup')
    TriplePatternList = production('TriplePatternList')
    TriplePattern = production('TriplePattern')
    VarOrURI = production('VarOrURI')
    VarOrLiteral = production('VarOrLiteral')
    PrefixDecl = production('PrefixDecl')
    Expression = production('Expression')
    ConditionalOrExpression = production('ConditionalOrExpression')
    ConditionalAndExpression = production('ConditionalAndExpression')
    ValueLogical = production('ValueLogical')
    StringEqualityExpression = production('StringEqualityExpression')
    StringComparitor = production('StringComparitor')
    EqualityExpression = production('EqualityExpression')
    RelationalComparitor = production('RelationalComparitor')
    RelationalExpression = production('RelationalExpression')
    NumericComparitor = production('NumericComparitor')
    AdditiveExpression = production('AdditiveExpression')
    AdditiveOperation = production('AdditiveOperation')
    MultiplicativeExpression = production('MultiplicativeExpression')
    MultiplicativeOperation = production('MultiplicativeOperation')
    UnaryExpression = production('UnaryExpression')
    UnaryExpressionNotPlusMinus = production('UnaryExpressionNotPlusMinus')
    PrimaryExpression = production('PrimaryExpression')
    FunctionCall = production('FunctionCall')
    ArgList = production('ArgList')
    Literal = production('Literal')
    NumericLiteral = production('NumericLiteral')
    TextLiteral = production('TextLiteral')
    URI = production('URI')
    CommaOpt = production('CommaOpt') # unused

    # terminals EBNF definitions are at end of spec

    QuotedURI = (lt.suppress() + Word(alphanums+"_-./&?:@~=#") + gt.suppress()).setResultsName('QuotedURI')

    _NCNAME_ = Word(alphas+'_', alphanums+'_.-')
    _DIGITS_ = Word(nums)
    _VAR_ = Word("?", alphanums+'_.-', min=2).setResultsName('Var')

    QName = Combine(Optional(_NCNAME_ + colon) + _NCNAME_).setResultsName('QName')
    String = quotedString.setResultsName('String')

    _EXPONENT_ = oneOf("e E") + Optional(oneOf("+ -")) + Word(nums)
    _DECIMAL_LITERAL_ = _DIGITS_
    _HEX_LITERAL_ = Combine( zero + oneOf("x X") + Word(srange('[0-9a-fA-F]')) ).setResultsName('HexLiteral')
    _INTEGER_LITERAL_ = (Optional(oneOf("+ -")) + _DECIMAL_LITERAL_ + Optional(oneOf("l L")) ^
                          _HEX_LITERAL_ + Optional(oneOf("l L"))).setResultsName('IntegerLiteral')
    _FLOATING_POINT_LITERAL_ = Combine(Optional(oneOf("+ -")) +
                                       Word(nums) + dot + Word(nums) +
                                       Optional(_EXPONENT_) |
                                       dot | OneOrMore(nums) +
                                       Optional(_EXPONENT_) |
                                       OneOrMore(nums) + _EXPONENT_).setResultsName('FloatingPointLiteral')
    _A2Z_ = Word(alphas)
    _LANG_ = Combine(at.suppress() + _A2Z_ + Optional(dash + _A2Z_)).setResultsName('Lang')


    # [1]   Query    ::=   PrefixDecl* ReportFormat  PrefixDecl* FromClause? WhereClause?

    Query << (ZeroOrMore(PrefixDecl) + ReportFormat + ZeroOrMore(PrefixDecl) +
              Optional(FromClause) + Optional(WhereClause) + Optional(LimitClause))

    # [2]  ReportFormat  ::=  'select' 'distinct'? <VAR> ( CommaGroup(Opt <VAR> )*
    # | 'select' 'distinct'? '*'
    # | 'construct' TriplePatternList
    # | 'construct' '*'
    # | 'describe' VarOrURI ( CommaOpt VarOrURI )*
    # | 'describe' '*'
    # | 'ask'

    ReportFormat << (Group(select + Optional(distinct) + Group(OneOrMore(_VAR_))) |
                     Group(select + Optional(distinct) + star.setResultsName('all')) |
                     Group(construct + TriplePatternList) |
                     Group(construct + star) |
                     Group(describe + delimitedList(VarOrURI)) |
                     Group(describe + star) |
                     ask)

    # [3]  FromClause  ::=  'from' FromSelector ( CommaOpt FromSelector )*

    FromClause << ffrom + delimitedList(FromSelector)

    # [4]  FromSelector  ::=  URI

    FromSelector << URI

    # [5]  WhereClause  ::=  'where' GraphPattern

    WhereClause << where + GraphPattern

    # in spec prose but not in spec grammar, no number

    LimitClause << Group(limit + _INTEGER_LITERAL_  )

    # [6]  SourceGraphPattern  ::=  'source' '*' GraphPattern1
    # | 'source' VarOrURI GraphPattern1

    SourceGraphPattern << ((source + star + GraphPattern1) | (source + VarOrURI + GraphPattern1))

    # [7]  OptionalGraphPattern  ::=  'optional' GraphPattern1
    # | '[' GraphPattern ']'

    OptionalGraphPattern << (optional + GraphPattern1 | lbrack.suppress() + GraphPattern + rbrack.suppress())

    # [8]  GraphPattern  ::=  PatternElement PatternElement*

    GraphPattern << OneOrMore(PatternElement)

    # [9]  PatternElement  ::=  TriplePatternList
    # | ExplicitGroup
    # | PatternElementForms

    PatternElement << (TriplePatternList | ExplicitGroup | PatternElementForms)

    # [10]  GraphPattern1  ::=  PatternElement1

    GraphPattern1 << PatternElement1

    # [11]  PatternElement1  ::=  SingleTriplePatternOrGroup
    # | PatternElementForms

    PatternElement1 << (SingleTriplePatternOrGroup | PatternElementForms)

    # [12]  PatternElementForms  ::=  SourceGraphPattern
    # | OptionalGraphPattern
    # | 'and' Expression

    PatternElementForms << (SourceGraphPattern | OptionalGraphPattern | aand + Expression)

    # [13]  SingleTriplePatternOrGroup  ::=  TriplePattern
    # | ExplicitGroup

    SingleTriplePatternOrGroup << (TriplePattern | ExplicitGroup)

    # [14]  ExplicitGroup  ::=  '(' GraphPattern ')'

    ExplicitGroup << lparen.suppress() + GraphPattern + rparen.suppress()

    # [15]  TriplePatternList  ::=  TriplePattern TriplePattern*

    TriplePatternList << OneOrMore(TriplePattern)

    # [16]  TriplePattern  ::=  '(' VarOrURI VarOrURI VarOrLiteral ')'

    TriplePattern << lparen.suppress() + Group(VarOrURI + VarOrURI + VarOrLiteral) + rparen.suppress()

    # [17]  VarOrURI  ::=  <VAR> | URI

    VarOrURI << (_VAR_ | URI)

    # [18]  VarOrLiteral  ::=  <VAR> | Literal

    VarOrLiteral << (_VAR_ | Literal)

    # [19]  PrefixDecl  ::=  'prefix' <NCNAME> ':' QuotedURI
    # | 'prefix' ':' QuotedURI

    PrefixDecl << prefix + Group(_NCNAME_ + colon.suppress() + QuotedURI)

    # [20]  Expression  ::=  ConditionalOrExpression

    Expression << ConditionalOrExpression

    # [21]  ConditionalOrExpression  ::=  ConditionalAndExpression ( '||' ConditionalAndExpression )*

    ConditionalOrExpression << delimitedList(ConditionalAndExpression, '||')

    # [22]  ConditionalAndExpression  ::=  ValueLogical ( '&&' ValueLogical )*

    ConditionalAndExpression << delimitedList(ValueLogical, '&&')

    # [23]  ValueLogical  ::=  StringEqualityExpression

    ValueLogical << StringEqualityExpression

    # [24]  StringEqualityExpression  ::=  EqualityExpression StringComparitor*

    StringEqualityExpression << EqualityExpression + ZeroOrMore(StringComparitor)

    # [25]  StringComparitor  ::=  'eq' EqualityExpression
    # | 'ne' EqualityExpression
    # | '=~' <PATTERN_LITERAL>
    # | '!~' <PATTERN_LITERAL>

    StringComparitor << ((leq + EqualityExpression) | lne + EqualityExpression) # TODO pat lits

    # [26]  EqualityExpression  ::=  RelationalExpression RelationalComparitor?

    EqualityExpression << RelationalExpression + Optional(RelationalComparitor)

    # [27]  RelationalComparitor  ::=  '==' RelationalExpression
    # | '!=' RelationalExpression

    RelationalComparitor << ((eqeq + RelationalExpression) | (noteq + RelationalExpression))

    # [28]  RelationalExpression  ::=  AdditiveExpression NumericComparitor?

    RelationalExpression << AdditiveExpression + Optional(NumericComparitor)

    # [29]  NumericComparitor  ::=  '<' AdditiveExpression
    # | '>' AdditiveExpression
    # | '<=' AdditiveExpression
    # | '>=' AdditiveExpression

    NumericComparitor << ((lt + AdditiveExpression) | (gt + AdditiveExpression) |
                         (lte + AdditiveExpression) | (gte + AdditiveExpression))

    # [30]  AdditiveExpression  ::=  MultiplicativeExpression AdditiveOperation*

    AdditiveExpression << MultiplicativeExpression + ZeroOrMore(AdditiveOperation)

    # [31]  AdditiveOperation  ::=  '+' MultiplicativeExpression
    # | '-' MultiplicativeExpression

    AdditiveOperation << ((plus + MultiplicativeExpression) | (minus + MultiplicativeExpression))

    # [32]  MultiplicativeExpression  ::=  UnaryExpression MultiplicativeOperation*

    MultiplicativeExpression << UnaryExpression + ZeroOrMore(MultiplicativeOperation)

    # [33]  MultiplicativeOperation  ::=  '*' UnaryExpression
    # | '/' UnaryExpression
    # | '%' UnaryExpression

    MultiplicativeOperation << (star + UnaryExpression) | (slash + UnaryExpression) | (mod + UnaryExpression)

    # [34]  UnaryExpression  ::=  UnaryExpressionNotPlusMinus

    UnaryExpression << UnaryExpressionNotPlusMinus

    # [35]  UnaryExpressionNotPlusMinus  ::=  ( '~' | '!' ) UnaryExpression
    # | PrimaryExpression

    UnaryExpressionNotPlusMinus << (tilde | bang) + UnaryExpression

    # [36]  PrimaryExpression ::= <VAR> | Literal | FunctionCall | '(' Expression ')'

    PrimaryExpression << (_VAR_ | Literal | FunctionCall | lparen.suppress() + Expression + rparen.suppress())

    # [37]  FunctionCall  ::=  '&' <QNAME> '(' ArgList? ')'

    FunctionCall << amp.suppress() + QName + lparen.suppress() + Optional(Group(ArgList)) + rparen.suppress()

    # [38]  ArgList  ::=  VarOrLiteral ( ',' VarOrLiteral )*

    ArgList << (delimitedList(VarOrLiteral))

    # [39]  Literal  ::=  URI
    # | NumericLiteral
    # | TextLiteral

    Literal << (QuotedURI | NumericLiteral | TextLiteral)

    #[40] NumericLiteral  ::= <INTEGER_LITERAL> | <FLOATING_POINT_LITERAL>

    NumericLiteral << (_INTEGER_LITERAL_ | _FLOATING_POINT_LITERAL_)

    # [41]  TextLiteral    ::=   String  <LANG>? ( '^^' URI )?

    TextLiteral << String + Optional(_LANG_) + Optional(typ.suppress() + URI).setResultsName('Type')

    # [42]   String    ::=   <STRING_LITERAL1> | <STRING_LITERAL2>

    # [43]  URI  ::=  QuotedURI | QName

    URI << (QuotedURI | QName)

    # [44]  QName  ::=  <QNAME>

    # [45]  QuotedURI  ::=  <URI>

    # [46]  CommaOpt  ::=  ','?

    # [47]   <URI>    ::=   "<" <NCCHAR1> (~[">"," "])* ">"

    # [48]  <QNAME>  ::=  (<NCNAME>)? ":" <NCNAME>

    # [49]  <VAR>  ::=  "?" <NCNAME>

    #    _VAR_ << qmark + _NCNAME_

    # [50]  <LANG>  ::=  '@' <A2Z><A2Z> ("-" <A2Z><A2Z>)?

    # [51]  <A2Z>  ::=  ["a"-"z","A"-"Z"]>

    # [52]  <INTEGER_LITERAL>  ::=  (["+","-"])? <DECIMAL_LITERAL> (["l","L"])?
    # | <HEX_LITERAL> (["l","L"])?

    # [53]  <DECIMAL_LITERAL>  ::=  <DIGITS>

    # [54]  <HEX_LITERAL>  ::=  "0" ["x","X"] (["0"-"9","a"-"f","A"-"F"])+

    # _HEX_LITERAL_ << zero + oneOf("x X") + Word(nums + srange('[a-f]') + srange('[a-f]'))

    # [55]  <FLOATING_POINT_LITERAL>  ::=  (["+","-"])? (["0"-"9"])+ "." (["0"-"9"])* (<EXPONENT>)?
    # | "." (["0"-"9"])+ (<EXPONENT>)?
    # | (["0"-"9"])+ <EXPONENT>

    # [56]  <EXPONENT>  ::=  ["e","E"] (["+","-"])? (["0"-"9"])+

    # [57]  <STRING_LITERAL1>  ::=  "'" ( (~["'","\\","\n","\r"]) | ("\\" ~["\n","\r"]) )* "'"

    # [58]  <STRING_LITERAL2>  ::=  "\"" ( (~["\"","\\","\n","\r"]) | ("\\" ~["\n","\r"]) )* "\""

    # [59]  <DIGITS>  ::=  (["0"-"9"])

    # [60]  <PATTERN_LITERAL>  ::=  [m]/pattern/[i][m][s][x]

    # PATTERN_LITERAL # TODO

    # [61]  <NCCHAR1>  ::=  ["A"-"Z"]
    # | "_" | ["a"-"z"]
    # | ["\u00C0"-"\u02FF"]
    # | ["\u0370"-"\u037D"]
    # | ["\u037F"-"\u1FFF"]
    # | ["\u200C"-"\u200D"]
    # | ["\u2070"-"\u218F"]
    # | ["\u2C00"-"\u2FEF"]
    # | ["\u3001"-"\uD7FF"]
    # | ["\uF900"-"\uFFFF"]

    #    _NCCHAR1_ = srange('[A-Z]') + "_" + srange([a-z])

    # [62]  <NCNAME>  ::=  <NCCHAR1> (<NCCHAR1> | "." | "-" | ["0"-"9"] | "\u00B7" )*

    #    _NCNAME_ << _NCCHAR1_ + Word(_NCCHAR1_, _NCCHAR1_ + dot + dash + nums + u"\u00B7") # wrong


if __name__ == '__main__':

    ts = ["SELECT *",
          "select DISTINCT *",
          "SELECT ?title",
          "SELECT ?title ?name",
          "SELECT distinct ?title ?name",
          "SELECT * FROM <a> WHERE  ( <book1> <title> ?title )",
          "prefix dc: <http://purl.org/dc/1.1/> SELECT * from <a> WHERE  ( <book1> <title> ?title )",
          "PREFIX bob: <http://is.your.uncle/> prefix dc: <http://purl.org/dc/1.1/> select * FROM <a> where  ( bob:book1 dc:title ?title )",
          'PREFIX foaf:   <http://xmlns.com/foaf/0.1/> SELECT ?mbox WHERE ( ?x foaf:name "Johnny Lee Outlaw" ) ( ?x foaf:mbox ?mbox )',
          "PREFIX  dc:  <http://purl.org/dc/elements/1.1/> PREFIX  ns:  <http://example.org/ns#> SELECT  ?title ?price WHERE   ( ?x dc:title ?title ) ( ?x ns:price ?price ) AND ?price < 30",
          'DESCRIBE ?x WHERE (?x ent:employeeId "1234")',
          "PREFIX vcard:  <http://www.w3.org/2001/vcard-rdf/3.0#> CONSTRUCT * WHERE ( ?x vcard:FN ?name )",
          "PREFIX foaf:    <http://xmlns.com/foaf/0.1/> SELECT ?name WHERE ( ?x foaf:name ?name ) LIMIT 20",
          "PREFIX foaf:  <http://xmlns.com/foaf/0.1/> SELECT ?given ?family WHERE SOURCE ?ppd ( ?whom foaf:given ?family )",
          "PREFIX foaf:  <http://xmlns.com/foaf/0.1/> SELECT ?given ?family WHERE SOURCE * ( ?whom foaf:given ?family )"
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
