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
    'data/Expr1/expr-3.rq'
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
]

DEBUG = True
    
def testBasic():    
    from glob import glob     
    from sre import sub
    for testFile in test:#glob('data/*/*.rq'):
        if testFile in tests2Skip:
            continue
        query = open(testFile).read()        
        print "### %s ###"%testFile        
        print query
        p = Parse(query,DEBUG)
        print p.prolog        
        print p.query
        #print p.query.solutionModifier.orderClause
#        patterns = p.query.whereClause.parsedGraphPattern.graphPatterns
#        patterns.reverse()        
#        for g in patterns:
#            print "### Graph Pattern %s ###"%(patterns.index(g)+1)
#            g.evaluate()
        
if __name__ == '__main__':
    testBasic()
#    suite1 = unittest.makeSuite(TestClassAndType)
#    suite2 = unittest.makeSuite(TestReason)
#    unittest.TextTestRunner(verbosity=3).run(suite1)
#    unittest.TextTestRunner(verbosity=3).run(suite2)
