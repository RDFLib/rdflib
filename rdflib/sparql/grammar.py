
from rdflib.lib.pyparsing import Literal, CaselessLiteral, Word, Upcase, delimitedList, Optional, \
    Combine, Group, alphas, nums, alphanums, ParseException, Forward, oneOf, \
    ZeroOrMore, restOfLine, Keyword, srange, OneOrMore, sglQuotedString, dblQuotedString, quotedString

ppLiteral = Literal

class SPARQLGrammar(object):

    # punctuation

    dot = ppLiteral(".")
    zero = ppLiteral("0")
    at = ppLiteral("@")
    dash = ppLiteral("-")
    qmark = ppLiteral("?")
    colon = ppLiteral(":")
    lt = ppLiteral("<")
    gt = ppLiteral(">")
    typ = ppLiteral("^^")
    amp = ppLiteral("&")
    lparen = ppLiteral("(")
    rparen = ppLiteral(")")
    tilde = ppLiteral("~")
    bang = ppLiteral("!")
    star = ppLiteral("*")
    slash = ppLiteral("/")
    mod = ppLiteral("%")
    plus = ppLiteral("+")
    minus = ppLiteral("-")
    lte = ppLiteral("<=")
    gte = ppLiteral(">=")
    eqeq = ppLiteral("==")
    noteq = ppLiteral("!=")
    lbrack = ppLiteral("[")
    rbrack = ppLiteral("]")
    leq = ppLiteral('eq')
    lne = ppLiteral('ne')
    eqpat = ppLiteral('=~')
    nepat = ppLiteral('!~')

    # keyword

    select = Keyword('select')
    distinct = Keyword('distinct')
    construct = Keyword('construct')
    describe = Keyword('describe')
    ask = Keyword('ask')
    ffrom = Keyword('from')
    where = Keyword('where')
    source = Keyword('source')
    optional = Keyword('optional')
    aand = Keyword('and')
    prefix = Keyword('prefix')

    # productions

    Query = Forward()
    ReportFormat = Forward()
    FromClause = Forward()
    FromSelector = Forward()
    WhereClause = Forward()
    SourceGraphPattern = Forward()
    OptionalGraphPattern = Forward()
    GraphPattern = Forward()
    PatternElement = Forward()
    GraphPattern1 = Forward()
    PatternElement1 = Forward()
    PatternElementForms = Forward()
    SingleTriplePatternOrGroup = Forward()
    ExplicitGroup = Forward()
    TriplePatternList = Forward()
    TriplePattern = Forward()
    VarOrURI = Forward()
    VarOrLiteral = Forward()
    PrefixDecl = Forward()
    Expression = Forward()
    ConditionalOrExpression = Forward()
    ConditionalAndExpression = Forward()
    ValueLogical = Forward()
    StringEqualityExpression = Forward()
    StringComparitor = Forward()
    EqualityExpression = Forward()
    RelationalComparitor = Forward()
    RelationalExpression = Forward()
    NumericComparitor = Forward()
    AdditiveExpression = Forward()
    AdditiveOperation = Forward()
    MultiplicativeExpression = Forward()
    MultiplicativeOperation = Forward()
    UnaryExpression = Forward()
    UnaryExpressionNotPlusMinus = Forward()
    PrimaryExpression = Forward()
    FunctionCall = Forward()
    ArgList = Forward()
    Literal = Forward()
    NumericLiteral = Forward()
    TextLiteral = Forward()
    String = Forward()
    URI = Forward()
    QName = Forward()
    QuotedURI = Forward()
    CommaOpt = Forward() # unused

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

    ReportFormat << (select + Optional(distinct) + delimitedList(_VAR_) |
                     select + Optional(distinct) + star |
                     construct + TriplePatternList |
                     construct + star |
                     describe + delimitedList(VarOrURI) |
                     describe + star |
                     ask)
    
    # [3]  FromClause  ::=  'from' FromSelector ( CommaOpt FromSelector )*

    FromClause << ffrom + delimitedList(FromSelector)
    
    # [4]  FromSelector  ::=  URI

    FromSelector << _URI_    
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

    VarOrURI << (_VAR_ | _URI_)

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

    _URI_ << lt + _NCCHAR1_ + gt # wrong

    # [48]  <QNAME>  ::=  (<NCNAME>)? ":" <NCNAME>

    _QNAME_ << Optional(_NCNAME_ + colon) + _NCNAME_

    # [49]  <VAR>  ::=  "?" <NCNAME>

    _VAR_ << qmark + _NCNAME_

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

    _NCCHAR1_ << Word(alphas+"_") # wrong

    # [62]  <NCNAME>  ::=  <NCCHAR1> (<NCCHAR1> | "." | "-" | ["0"-"9"] | "\u00B7" )*

    _NCNAME_ << _NCCHAR1_ + ZeroOrMore(_NCCHAR1_ | dot | dash | nums) # wrong
