from rdflib.sparql.bison import Parse
from rdflib.sparql.bison.SPARQLEvaluate import Evaluate
from rdflib import plugin, Namespace,URIRef, RDF
from rdflib.store import Store
from rdflib.Graph import Graph, ConjunctiveGraph
from sets import Set
import os
from cStringIO import StringIO
from pprint import pprint

EVALUATE = True
DEBUG_PARSE = False
STORE='MySQL'
configString = ''

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
    'data/examples/ex11.2.3.2_1.rq',
    #'data/TypePromotion/tP-unsignedByte-short.rq'
    #'data/examples/ex11.2.3.1_0.rq',
    #'data/ValueTesting/typePromotion-decimal-decimal-pass.rq',
#    'data/examples/ex11.2.3.2_0.rq',
#    'data/SyntaxFull/syntax-union-02.rq',
    #'data/part1/dawg-query-004.rq',
    
]

tests2Skip = [
    'data/examples/ex11.2.3.1_1.rq',#Compares dateTime with same time, different time-zones
    'data/examples/ex11_1.rq', #Compares with literal BNode labels!
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
    'data/examples/ex11_0.rq', #TimeZone info on xsd:dateTime
]


MANIFEST_NS = Namespace('http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#')
MANIFEST_QUERY_NS = Namespace('http://www.w3.org/2001/sw/DataAccess/tests/test-query#')
TEST_BASE = Namespace('http://www.w3.org/2001/sw/DataAccess/tests/')
RESULT_NS = Namespace('http://www.w3.org/2001/sw/DataAccess/tests/result-set#')

MANIFEST_QUERY = \
"""
PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX mf:     <http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#> 
PREFIX qt:     <http://www.w3.org/2001/sw/DataAccess/tests/test-query#> 

SELECT ?source ?testName ?testComment ?result
WHERE {
  ?testCase mf:action    ?testAction;            
            mf:name      ?testName;
            mf:result    ?result.
  ?testAction qt:query ?query;
              qt:data  ?source.
  
  OPTIONAL { ?testCase rdfs:comment ?testComment }
            
}"""

PARSED_MANIFEST_QUERY = Parse(MANIFEST_QUERY)

def bootStrapStore(store):
    rt = store.open(configString,create=False)
    if rt == -1:
        store.open(configString)
    else:
        store.destroy(configString)
        store.open(configString)    
        
def trialAndErrorRTParse(graph,queryLoc,DEBUG):
    qstr = StringIO(open(queryLoc).read())
    try:
        graph.parse(qstr,format='n3')                            
        return True
    except Exception, e:
        if DEBUG:
            print e
            print "#### Parse Failure (N3) ###"
            print qstr.getvalue()
            print "#####"*5
        try:
            graph.parse(qstr)
            assert list(graph.objects(None,RESULT_NS.resultVariable))
            return True
        except Exception, e:
            if DEBUG:
                print e
                print "#### Parse Failure (RDF/XML) ###"
                print qstr.getvalue()
                print "#### ######### ###"
            return False
    
def testBasic(DEBUG = False):    
    from glob import glob     
    from sre import sub
    for testFile in glob('data/examples/*.rq'):#glob('data/*/*.rq'):
        store = plugin.get(STORE,Store)()
        bootStrapStore(store)
        store.commit()
        
        prefix = testFile.split('.rq')[-1]        
        manifestPath = '/'.join(testFile.split('/')[:-1]+['manifest.n3'])
        manifestPath2 = '/'.join(testFile.split('/')[:-1]+['manifest.ttl'])
        queryFileName = testFile.split('/')[-1]
        store = plugin.get(STORE,Store)()
        store.open(configString,create=False)
        assert len(store) == 0
        manifestG=ConjunctiveGraph(store).default_context        
        if not os.path.exists(manifestPath):
            assert os.path.exists(manifestPath2)
            manifestPath = manifestPath2
        manifestG.parse(open(manifestPath),publicID=TEST_BASE,format='n3')                
        manifestData = Evaluate(store,PARSED_MANIFEST_QUERY,{'?query' : TEST_BASE[queryFileName]})
        store.rollback()
        store.close()
        for source,testCaseName,testCaseComment,expectedRT in manifestData:
            
            if expectedRT:
                expectedRT = '/'.join(testFile.split('/')[:-1]+[expectedRT.replace(TEST_BASE,'')])
            if source:
                source = '/'.join(testFile.split('/')[:-1]+[source.replace(TEST_BASE,'')])
            
            testCaseName = testCaseComment and testCaseComment or testCaseName
            print "## Source: %s ##"%source
            print "## Test: %s ##"%testCaseName
            print "## Result: %s ##"%expectedRT
    
            #Expected results
            if expectedRT:
                store = plugin.get(STORE,Store)()
                store.open(configString,create=False)            
                resultG=ConjunctiveGraph(store).default_context
#                if DEBUG:
#                    print "###"*10
#                    print "parsing: ", open(expectedRT).read()
#                    print "###"*10
                assert len(store) == 0
                print "## Parsing (%s) ##"%(expectedRT)
                if not trialAndErrorRTParse(resultG,expectedRT,DEBUG):
                    if DEBUG:
                        print "Unexpected result format (for %s), skipping"%(expectedRT)                    
                    store.rollback()
                    store.close()
                    continue
                if DEBUG:
                    print "## Done .. ##"
                    
                rtVars = [rtVar for rtVar in resultG.objects(None,RESULT_NS.resultVariable)]                
                bindings = []
                resultSetNode = resultG.value(predicate=RESULT_NS.value,object=RESULT_NS.ResultSet)
                for solutionNode in resultG.objects(resultSetNode,RESULT_NS.solution):         
                    bindingDict = dict([(key,None) for key in rtVars])
                    for bindingNode in resultG.objects(solutionNode,RESULT_NS.binding):
                        value = resultG.value(subject=bindingNode,predicate=RESULT_NS.value)
                        name  = resultG.value(subject=bindingNode,predicate=RESULT_NS.variable)
                        bindingDict[name] = value
                    bindings.append(tuple([bindingDict[vName] for vName in rtVars]))
                if DEBUG:
                    print "Expected bindings: ", bindings
                    print open(expectedRT).read()
                store.rollback()
                store.close()
                           
            if testFile.startswith('data/NegativeSyntax'):
                try:
                    query = open(testFile).read()        
                    p = Parse(query,DEBUG)
                except:
                    continue
                else:
                    raise Exception("Test %s should have failed!"%testFile)
            if testFile in tests2Skip:
                print "Skipping test (%s)"%testCaseName
                continue
            query = open(testFile).read()        
            print "### %s (%s) ###"%(testCaseName,testFile)
            print query
            p = Parse(query,DEBUG_PARSE)
            if DEBUG:
                print p
            if EVALUATE and source:
                if DEBUG:
                    print "### Source Graph: ###"
                    print open(source).read()
                store = plugin.get(STORE,Store)()                
                store.open(configString,create=False)
                g=ConjunctiveGraph(store)
                try:                    
                    g.parse(open(source),format='n3')
                except:
                    print "Unexpected data format (for %s), skipping"%(source)
                    store.rollback()
                    store.close()
                    continue
                #print store
                rt = Evaluate(store,p,DEBUG=DEBUG)
                if expectedRT:
                    nrt = []
                    for i in rt:
                        if not isinstance(i,(tuple,basestring)):
                            nrt.append(tuple(i))
                        elif isinstance(i,basestring):
                            nrt.append((i,))
                        else:
                            nrt.append(i)
                    rt = nrt
                    if rt != bindings and Set([Set(i) for i in rt]) != Set([Set(i) for i in bindings]):#unorderedComparison(rt,bindings):
                        print "### Expected Result (%s) ###"%expectedRT
                        pprint(bindings)
                        print "### Actual Results ###"
                        pprint(rt)
                        raise Exception("### TEST FAILED!: %s ###"%testCaseName)
                    else:
                        print "### TEST PASSED!: %s ###"%testCaseName
                store.rollback()
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        testBasic(bool(int(sys.argv[1])))
    else:
        testBasic()
#    suite1 = unittest.makeSuite(TestClassAndType)
#    suite2 = unittest.makeSuite(TestReason)
#    unittest.TextTestRunner(verbosity=3).run(suite1)
#    unittest.TextTestRunner(verbosity=3).run(suite2)
