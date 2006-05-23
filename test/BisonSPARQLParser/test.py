from rdflib.sparql.bison import Parse

#class TestClassAndType(unittest.TestCase):
#    
#    def setUp(self):
#        
#    def tearDown(self):
#            
#    def testType(self):
#    
#    def testClass1(self):

test = [
    
]

tests2Skip = [
    'data/SyntaxFull/syntax-bnodes-03.rq', #BNode as a predicate (not allowed by grammar)
    'data/SyntaxFull/syntax-qname-04.rq', #Grammar Ambiguity with ':' matching as QNAME & QNAME_NS
    'data/SyntaxFull/syntax-qname-05.rq', #Same as above
    'data/SyntaxFull/syntax-qname-11.rq', #Same as above
    'data/SyntaxFull/syntax-lit-10.rq'  , #BisonGen's Lexer is chopping up STRING_LITERAL_LONG1 tokens
    'data/SyntaxFull/syntax-lit-12.rq'  , #same as above
    'data/SyntaxFull/syntax-lit-14.rq'  , #same as above
    'data/SyntaxFull/syntax-lit-15.rq'  , #same as above
    'data/SyntaxFull/syntax-lit-16.rq'  , #same as above
    'data/SyntaxFull/syntax-lit-17.rq'  , #same as above
    'data/SyntaxFull/syntax-lit-20.rq'  , #same as above
    'data/unsaid-inference/query-01.rq' , #WHERE without '{ }'
    'data/unsaid-inference/query-02.rq' , #same as above
    'data/unsaid-inference/query-03.rq' , #same as above
    'data/part1/dawg-query-001.rq'      , #no space between variable name and }: .. OPTIONAL { ?person foaf:mbox ?mbox}
    'data/part1/dawg-query-003.rq'      , #Same as above
    'data/regex/regex-query-003.rq'     , #BisonGen's Lexer is chopping up STRING_LITERAL_LONG1 tokens     
    'data/regex/regex-query-004.rq'     , #Same as above
    'data/simple2/dawg-tp-01.rq'        , #WHERE without '{ }'
    'data/simple2/dawg-tp-02.rq'        , #same as above
    'data/simple2/dawg-tp-03.rq'        , #same as above
    'data/simple2/dawg-tp-04.rq'        , #same as above
    'data/SourceSimple/source-simple-01.rq', #WHERE without '{ }'
    'data/SourceSimple/source-simple-02.rq', #Illegal syntax 
    'data/SourceSimple/source-simple-03.rq', #Illegal syntax 
    'data/SourceSimple/source-simple-04.rq', #Illegal syntax 
    'data/SourceSimple/source-simple-05.rq', #Illegal syntax 
    'data/source-named/query-8.1.rq', #WHERE without '{ }'
    'data/source-named/query-8.2.rq', #same as above
    'data/source-named/query-8.3.rq', #same as above
    'data/source-named/query-8.4.rq', #same as above
    'data/source-named/query-8.5.rq', #same as above
    'data/source-named/query-9.1.rq', #same as above
    'data/source-named/query-9.2.rq', #same as above
    'data/survey/query-survey-1.rq', #not sure if the VARNAME token includes ']'.  If it does then the test is invalid
    'data/survey/query-survey-9.rq', #same as above
    'data/Sorting/one-of-one-column.rq' #same as above
    'data/ValueTesting/dateTime-tz0.rq', #bad syntax
    'data/Sorting/one-of-one-column.rq',#not sure if the VARNAME token includes ']'.  If it does then the test is invalid
    'data/ValueTesting/dateTime-tz0.rq',#bad syntax
    'data/ValueTesting/dateTime-tz1.rq',#same as above
    'data/ValueTesting/boolean-logical-OR.rq',#boolean literal is lowercase not uppercase
    'data/ValueTesting/boolean-true-canonical.rq',#same as above
    'data/ValueTesting/boolean-EBV-canonical.rq',#samve as above
    'data/ValueTesting/boolean-equiv-TRUE.rq',#same as above
    'data/ValueTesting/boolean-false-canonical.r',#same as above
    'data/ValueTesting/boolean-false-canonical.rq',#
    'data/ValueTesting/boolean-equiv-FALSE.rq',#
    'data/ValueTesting/extendedType-ne-pass.rq',#[27] Constraint ::= 'FILTER' BrackettedExpression <--
]

DEBUG = False
    
def testBasic():    
    from glob import glob     
    from sre import sub
    for testFile in glob('data/*/*.rq'):
        if testFile.startswith('data/NegativeSyntax'):
            try:
                query = open(testFile).read()        
                p = Parse(query,DEBUG)
            except:
                continue
            else:
                raise Exception("Test %s should have failed!"%testFile)
        if testFile in tests2Skip:
            continue
        query = open(testFile).read()        
        print "### %s ###"%testFile        
        print query
        p = Parse(query,DEBUG)
        print p.prolog        
        print p.query
        
if __name__ == '__main__':
    testBasic()
#    suite1 = unittest.makeSuite(TestClassAndType)
#    suite2 = unittest.makeSuite(TestReason)
#    unittest.TextTestRunner(verbosity=3).run(suite1)
#    unittest.TextTestRunner(verbosity=3).run(suite2)
