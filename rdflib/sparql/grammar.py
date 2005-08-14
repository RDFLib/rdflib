
from rdflib.lib.pyparsing import Literal, CaselessLiteral, Word, Upcase, delimitedList, Optional, \
    Combine, Group, alphas, nums, alphanums, ParseException, Forward, oneOf, \
    ZeroOrMore, restOfLine, Keyword, srange, OneOrMore, sglQuotedString, dblQuotedString, quotedString

ppLiteral = Literal # name gets assigned by grammar


def punctuation(lit):
    return ppLiteral(lit)

def keyword(lit):
    return Keyword(lit, caseless=True)

def production(lit):
    return Forward().setResultsName(lit)

class SPARQLGrammar(object):

    # punctuation

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

    # productions

    Query = production('Query')
    ReportFormat = production('ReportFormat')
    FromClause = production('FromClause')
    FromSelector = production('FromSelector')
    WhereClause = production('WhereClause')
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
    String = production('String')
    URI = production('URI')
    QName = production('QName')
    QuotedURI = production('QuotedURI')
    CommaOpt = production('CommaOpt') # unused

    # terminals

    _URI_ = Forward()
    _QNAME_ = Forward() 
    _VAR_ = Forward() 
    _LANG_ = Forward()
    _A2Z_ = Forward() 
    _INTEGER_LITERAL_ = Forward() 
    _DECIMAL_LITERAL_ = Forward() 
    _HEX_LITERAL_ = Forward() 
    _FLOATING_POINT_LITERAL_ = Forward() 
    _EXPONENT_ = Forward() 
    _STRING_LITERAL1_ = Forward() 
    _STRING_LITERAL2_ = Forward() 
    _DIGITS_ = Forward() 
    _NCCHAR1_ = Forward()
    _NCNAME_ = Forward() 

    # [1]   Query    ::=   PrefixDecl* ReportFormat  PrefixDecl* FromClause? WhereClause?

    Query << (ZeroOrMore(PrefixDecl) + ReportFormat + ZeroOrMore(PrefixDecl) +
              Optional(FromClause) + Optional(WhereClause))
    
    # [2]  ReportFormat  ::=  'select' 'distinct'? <VAR> ( CommaOpt <VAR> )*
    # | 'select' 'distinct'? '*'
    # | 'construct' TriplePatternList
    # | 'construct' '*'
    # | 'describe' VarOrURI ( CommaOpt VarOrURI )*
    # | 'describe' '*'
    # | 'ask'

    ReportFormat << (select + Optional(distinct) + Group(delimitedList(_VAR_)) |
                     select + Optional(distinct) + star |
                     construct + TriplePatternList |
                     construct + star |
                     describe + delimitedList(VarOrURI) |
                     describe + star |
                     ask)
    
    # [3]  FromClause  ::=  'from' FromSelector ( CommaOpt FromSelector )*

    FromClause << ffrom + delimitedList(FromSelector)
    
    # [4]  FromSelector  ::=  URI

    FromSelector << URI
    
    # [5]  WhereClause  ::=  'where' GraphPattern

    WhereClause << where + GraphPattern
    
    # [6]  SourceGraphPattern  ::=  'source' '*' GraphPattern1
    # | 'source' VarOrURI GraphPattern1

    SourceGraphPattern = source + star + GraphPattern1

    # [7]  OptionalGraphPattern  ::=  'optional' GraphPattern1
    # | '[' GraphPattern ']'

    OptionalGraphPattern << optional + GraphPattern1 | lbrack + GraphPattern + rbrack

    # [8]  GraphPattern  ::=  PatternElement PatternElement*

    GraphPattern << PatternElement + ZeroOrMore(PatternElement)

    # [9]  PatternElement  ::=  TriplePatternList
    # | ExplicitGroup
    # | PatternElementForms

    PatternElement << TriplePatternList | ExplicitGroup | PatternElementForms

    # [10]  GraphPattern1  ::=  PatternElement1

    GraphPattern1 << PatternElement1

    # [11]  PatternElement1  ::=  SingleTriplePatternOrGroup
    # | PatternElementForms

    PatternElement1 << SingleTriplePatternOrGroup | PatternElementForms

    # [12]  PatternElementForms  ::=  SourceGraphPattern
    # | OptionalGraphPattern
    # | 'and' Expression

    PatternElementForms << SourceGraphPattern | OptionalGraphPattern | aand + Expression

    # [13]  SingleTriplePatternOrGroup  ::=  TriplePattern
    # | ExplicitGroup

    SingleTriplePatternOrGroup << TriplePattern | ExplicitGroup

    # [14]  ExplicitGroup  ::=  '(' GraphPattern ')'

    ExplicitGroup << lparen + GraphPattern + rparen

    # [15]  TriplePatternList  ::=  TriplePattern TriplePattern*

    TriplePatternList << TriplePattern + ZeroOrMore(TriplePattern)

    # [16]  TriplePattern  ::=  '(' VarOrURI VarOrURI VarOrLiteral ')'

    TriplePattern << lparen + VarOrURI + VarOrURI + VarOrLiteral + rparen

    # [17]  VarOrURI  ::=  <VAR> | URI

    VarOrURI << (_VAR_ | URI)

    # [18]  VarOrLiteral  ::=  <VAR> | Literal

    VarOrLiteral << (_VAR_ | Literal)

    # [19]  PrefixDecl  ::=  'prefix' <NCNAME> ':' QuotedURI
    # | 'prefix' ':' QuotedURI

    PrefixDecl << prefix + _NCNAME_ + colon + QuotedURI
    
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

    RelationalComparitor << (eqeq + RelationalExpression) | (noteq + RelationalExpression)

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

    AdditiveOperation << (plus + MultiplicativeExpression) | (minus + MultiplicativeExpression)

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

    PrimaryExpression << _VAR_ | Literal | FunctionCall | lparen + Expression + rparen

    # [37]  FunctionCall  ::=  '&' <QNAME> '(' ArgList? ')'

    FunctionCall << amp + _QNAME_ + lparen + Optional(ArgList) + rparen

    # [38]  ArgList  ::=  VarOrLiteral ( ',' VarOrLiteral )*

    ArgList << delimitedList(VarOrLiteral)

    # [39]  Literal  ::=  URI
    # | NumericLiteral
    # | TextLiteral

    Literal << _URI_ | NumericLiteral | TextLiteral

    #[40] NumericLiteral  ::= <INTEGER_LITERAL> | <FLOATING_POINT_LITERAL>

    NumericLiteral << _INTEGER_LITERAL_ + _FLOATING_POINT_LITERAL_

    # [41]  TextLiteral    ::=   String  <LANG>? ( '^^' URI )?

    TextLiteral << String + Optional(_LANG_) + Optional(typ + URI)

    # [42]   String    ::=   <STRING_LITERAL1> | <STRING_LITERAL2>

    String << _STRING_LITERAL1_ | _STRING_LITERAL2_
    
    # [43]  URI  ::=  QuotedURI | QName

    URI << QuotedURI | QName
    
    # [44]  QName  ::=  <QNAME>

    QName << _QNAME_
    
    # [45]  QuotedURI  ::=  <URI>

    QuotedURI << _URI_
    
    # [46]  CommaOpt  ::=  ','?

    # unused

    # [47]   <URI>    ::=   "<" <NCCHAR1> (~[">"," "])* ">"

    _URI_ << lt.suppress() + Word(alphanums+"_-./&?:@~=#") + gt.suppress() # wrong

    # [48]  <QNAME>  ::=  (<NCNAME>)? ":" <NCNAME>

    _QNAME_ << Optional(_NCNAME_ + colon) + _NCNAME_

    # [49]  <VAR>  ::=  "?" <NCNAME>

    #    _VAR_ << qmark + _NCNAME_
    _VAR_ = Word("?", alphanums+'_.-', min=2)

    # [50]  <LANG>  ::=  '@' <A2Z><A2Z> ("-" <A2Z><A2Z>)?

    _LANG_ << at + _A2Z_ + Optional(dash + _A2Z_)

    # [51]  <A2Z>  ::=  ["a"-"z","A"-"Z"]>

    _A2Z_ << Word(alphas)

    # [52]  <INTEGER_LITERAL>  ::=  (["+","-"])? <DECIMAL_LITERAL> (["l","L"])?
    # | <HEX_LITERAL> (["l","L"])?

    _INTEGER_LITERAL_ << (Optional(oneOf("+ -")) + _DECIMAL_LITERAL_ + Optional(oneOf("l L")) |
                          _HEX_LITERAL_ + Optional(oneOf("l L")))
                          
    # [53]  <DECIMAL_LITERAL>  ::=  <DIGITS>

    _DECIMAL_LITERAL_ << _DIGITS_

    # [54]  <HEX_LITERAL>  ::=  "0" ["x","X"] (["0"-"9","a"-"f","A"-"F"])+

    _HEX_LITERAL_ << zero + oneOf("x X") + Word(nums + srange('[a-f]') + srange('[a-f]'))

    # [55]  <FLOATING_POINT_LITERAL>  ::=  (["+","-"])? (["0"-"9"])+ "." (["0"-"9"])* (<EXPONENT>)?
    # | "." (["0"-"9"])+ (<EXPONENT>)?
    # | (["0"-"9"])+ <EXPONENT>

    _FLOATING_POINT_LITERAL_ << (Optional(oneOf("+ -")) + Word(nums) + dot + Word(nums) + Optional(_EXPONENT_) |
                                 dot | OneOrMore(nums) + Optional(_EXPONENT_) |
                                 OneOrMore(nums) + _EXPONENT_)

    # [56]  <EXPONENT>  ::=  ["e","E"] (["+","-"])? (["0"-"9"])+

    _EXPONENT_ << oneOf("e E") + Optional(oneOf("+ -")) + Word(nums)

    # [57]  <STRING_LITERAL1>  ::=  "'" ( (~["'","\\","\n","\r"]) | ("\\" ~["\n","\r"]) )* "'"

    _STRING_LITERAL1_ << sglQuotedString

    # [58]  <STRING_LITERAL2>  ::=  "\"" ( (~["\"","\\","\n","\r"]) | ("\\" ~["\n","\r"]) )* "\""

    _STRING_LITERAL2_ << dblQuotedString

    # [59]  <DIGITS>  ::=  (["0"-"9"])

    _DIGITS_ << Word(nums)

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

    _NCNAME_ = Word(alphas+'_', alphanums+'_.-')

if __name__ == '__main__':

    ts = ["SELECT *",
          "SELECT DISTINCT *",
          "SELECT ?title",
          "SELECT ?title, ?name",          
          "SELECT * FROM <a> WHERE  ( <book1> <title> ?title )",
          ]

    for t in ts:

        try:
            tokens = SPARQLGrammar.Query.parseString(t)
            print "tokens = ",        tokens
        except ParseException, err:
            print t
            print " "*err.loc + "^" + err.msg
            print err
