import os
from Ft.Lib import Uri
from glob import glob
from rdflib.sparql.QueryResult import SPARQL_XML_NAMESPACE
from rdflib.sparql.bison import Parse, Query
from rdflib.sparql.graphPattern import BasicGraphPattern as BGP
from rdflib.sparql.Algebra import ReduceToAlgebra, RenderSPARQLAlgebra, AlgebraExpression
from rdflib.Collection import Collection
from rdflib import plugin, Namespace,URIRef, RDF, BNode, Variable,Literal, RDFS, util
from rdflib.util import *
from rdflib.store import Store, VALID_STORE, CORRUPTED_STORE, NO_STORE, UNKNOWN
from rdflib.Graph import Graph, ConjunctiveGraph
from rdflib.syntax.NamespaceManager import NamespaceManager
from sets import Set
from cStringIO import StringIO
from pprint import pprint
WRITE_EARL=False
MAIN_MANIFEST=[#'extended-manifest-evaluation.ttl',
               'manifest-evaluation.ttl',
               'manifest-syntax.ttl']

MANIFEST_NS = Namespace('http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#')
MANIFEST_QUERY_NS = Namespace('http://www.w3.org/2001/sw/DataAccess/tests/test-query#')
TEST_BASE     = Namespace('http://www.w3.org/2001/sw/DataAccess/tests/')
RESULT_NS     = Namespace('http://www.w3.org/2001/sw/DataAccess/tests/result-set#')
EARL          = Namespace('http://www.w3.org/ns/earl#')
FOAF          = Namespace("http://xmlns.com/foaf/0.1/")
CHIMEZIE_FOAF = "http://purl.org/net/chimezie/foaf"
DOAP          = Namespace('http://usefulinc.com/ns/doap#') 

REPORT_NS = {
    u"earl":EARL,
    u"foaf":FOAF,
    u"doap":DOAP
}

manifestNS = {
    u"extra" : Namespace('http://jena.hpl.hp.com/2005/05/test-manifest-extra#'),
    u"rdfs"  : RDFS.RDFSNS,
    u"rdf"   : RDF.RDFNS, 
    u"alg"  : Namespace("http://www.w3.org/2001/sw/DataAccess/tests/data-r2/algebra/manifest#"), 
    u"mf"    : Namespace("http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#"),
    u"dawgt" : Namespace("http://www.w3.org/2001/sw/DataAccess/tests/test-dawg#"),
    u"qt"    : Namespace("http://www.w3.org/2001/sw/DataAccess/tests/test-query#"),
}

RDFLIB_DOAP_DATA=\
"""
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix     : <http://usefulinc.com/ns/doap#> .
@prefix  rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#">.
@prefix  xsd: <http://www.w3.org/2001/XMLSchema#>.

<http://rdflib.net>
  foaf:homepage <http://rdflib.net>;
  a         :Project;
  :name     "RDFLib";
  :release _:a .
  
_:a a :Version ;
    :name "2.4.1.dev-r1252" ;
    :created "2007-10-11"^^xsd:date """

MANIFEST_QUERY2 = \
"""
SELECT ?test ?testName ?testComment ?query ?result ?testAction
WHERE {
    { ?test a mf:QueryEvaluationTest }
      UNION
    { ?test a <http://jena.hpl.hp.com/2005/05/test-manifest-extra#TestQuery> }
      UNION 
    { ?test a mf:PositiveSyntaxTest }
    ?test mf:name   ?testName.
    OPTIONAL { ?test rdfs:comment ?testComment }
    ?test mf:action    ?testAction.
    OPTIONAL { ?test mf:result ?result. ?testAction qt:query ?query }
}"""

PARSED_MANIFEST_QUERY2 = Parse(MANIFEST_QUERY2)

sparqlNsBindings = {u'sparql':SPARQL_XML_NAMESPACE}

def bootStrapStore(store,configString):
    rt = store.open(configString,create=False)
    if rt == NO_STORE:
        store.open(configString,create=True)
    else:
        store.destroy(configString)
        store.open(configString,create=True)

def trialAndErrorRTParse(graph,queryLoc,DEBUG,gName=None):
    qstr = StringIO(open(queryLoc).read())
    try:
        graph.parse(qstr,format='n3',publicID=gName)
        return True
    except Exception, e:
#        if DEBUG:
#            print e
#            print "#### Parse Failure (N3) ###"
#            print qstr.getvalue()
#            print "#####"*5
        try:
            graph.parse(qstr)
            assert list(graph.objects(None,RESULT_NS.resultVariable))
            return True
        except Exception, e:
#            if DEBUG:
#                print e
#                print "#### Parse Failure (RDF/XML) ###"
#                print qstr.getvalue()
#                print "#### ######### ###"
            return False
        

def setupReportingRDF(g,foafURI=CHIMEZIE_FOAF):
    g.parse(StringIO(RDFLIB_DOAP_DATA),format="n3")
    try:
        raise
        g.parse(foafURI)
    except:
        createReporterRDF(g)

def createReporterRDF(g,
                      name="Chimezie Ogbuji",
                      homePage=URIRef("http://metacognition.info"),
                      who=None):
    if not who:
        who = URIRef('http://purl.org/net/chimezie/foaf#chime')
    g.add((who, FOAF.name, Literal(name)))
    g.add((who, RDF.type, FOAF.Person))
    g.add((who, FOAF.homepage, homePage))
    g.add((who, RDFS.seeAlso, URIRef(CHIMEZIE_FOAF)))
    return who

def generateTestAlgebra(subDirs=[]):
    subDirs = subDirs and subDirs or []
    for subDir in subDirs:
        testManifest = 'data-r2/%s/manifest.ttl'%subDir
        assert os.path.exists(testManifest)
        manifestG=Graph()
        manifestG.parse(open(testManifest),publicID=TEST_BASE,format='n3')
        manifestData = \
           manifestG.query(
                                  MANIFEST_QUERY2,
                                  initNs=manifestNS,
                                  DEBUG = False)
        for test,testName,testComment,query,result,testAction in \
            manifestData.serialize(format='python'):
            queryFile = query.replace(TEST_BASE,'data-r2/%s/'%subDir)
            query = open(queryFile).read()
            parsedSPARQL = Parse(query)
            algebraExpr=RenderSPARQLAlgebra(parsedSPARQL)
            if not isinstance(algebraExpr,(AlgebraExpression,BGP)):
                raise
            print "## %s (%s) ##"%(testName,queryFile)
            print query
            print algebraExpr
            print "######"+"#"*len(testName)+'\n'
        
skipTests = [
    #('dataset','dataset-08'),# is Join(A,{{}}) = {{}} or A?
    #('dataset','dataset-09'),#same as above
    ('syntax-sparql1','syntax-lit-17.rq'), #problems with quote escaping
    ('syntax-sparql1','syntax-lit-12.rq'), # ''       ''    ''     ''
    ('syntax-sparql1','syntax-lit-14.rq'), # ''       ''    ''     ''
    ('syntax-sparql1','syntax-lit-20.rq'), # ''       ''    ''     ''
    ('syntax-sparql1','syntax-lit-16.rq'), # ''       ''    ''     ''
    ('syntax-sparql1','syntax-lit-15.rq'), # ''       ''    ''     ''
    ('syntax-sparql1','syntax-lit-10.rq'),
    ('syntax-sparql2','syntax-form-describe01.rq'), #No syntactic support for describe
    ('syntax-sparql2','syntax-form-describe02.rq'), #"     "         "     "      "
    ('syntax-sparql2','syntax-esc-05.rq'), #problems with escape characters in prefixed names
    ('syntax-sparql2','syntax-esc-04.rq'), #    "      "     "        "     "     "       "
    ('optional-filter','dawg-optional-filter-005-simplified'),       #Nesting triggering core dump :(
    ('optional-filter','dawg-optional-filter-005-not-simplified'),       #Nesting triggering core dump :(    
    ('basic','Basic - Quotes 3'),
    ('basic','Basic - Quotes 1'),    
    ('open-world',"open-eq-11"),
    ('open-world',"open-eq-12"),
    ('open-world',"open-eq-10"),
    ('open-world',"open-eq-07"),
    ('open-world',"open-eq-09"),
    ('open-world',"open-eq-08"),
    ('algebra',"Join scope - 1"),#Nesting triggering core dump
#    ('algebra',"Join operator with OPTs, BGPs, and UNIONs"),
    ('algebra',"Filter-scope - 1"),#Nesting triggering core dump
    ('algebra',"Optional-filter - scope of variable"),#Nesting triggering core dump
    ('algebra',"Filter-nested - 2"),#Nesting triggering core dump
    ('type-promotion',"tP-double-float"),
    ('type-promotion',"tP-short-long-fail"),
    ('type-promotion',"tP-integer-short"),
    ('type-promotion',"tP-short-short-fail"),
    ('type-promotion',"tP-float-decimal-fail"),
    ('type-promotion',"tP-short-decimal"),
    ('type-promotion',"tP-nonPositiveInteger-short"),
    ('type-promotion',"tP-short-byte-fail"),
    ('type-promotion',"tP-double-decimal-fail"),
    ('type-promotion',"tP-decimal-decimal"),
    ('type-promotion',"tP-nonNegativeInteger-short"),
    ('type-promotion',"tP-positiveInteger-short"),
    ('type-promotion',"tP-unsignedInt-short"),
    ('type-promotion',"tP-short-short"),
    ('type-promotion',"tP-unsignedLong-short"),
    ('type-promotion',"tP-byte-short"),
    ('type-promotion',"tP-negativeInteger-short"),
    ('type-promotion',"tP-byte-short-fail"),
    ('type-promotion',"tP-unsignedShort-short"),
    ('type-promotion',"tP-unsignedByte-short"),
    ('type-promotion',"tP-long-short"),
    ('type-promotion',"tP-float-float"),
    ('type-promotion',"tP-short-float"),
    ('type-promotion',"tP-double-decimal"),
    ('type-promotion',"tP-float-decimal"),
    ('type-promotion',"tP-int-short"),
    ('type-promotion',"tP-short-int-fail"),
    ('type-promotion',"tP-double-float-fail"),
    ('type-promotion',"tP-double-double"),
    ('type-promotion',"tP-short-double"),
    ('expr-builtin',"lang-case-insensitive-ne"),
    ('expr-builtin',"sameTerm-simple"),
    ('expr-builtin',"lang-case-insensitive-eq"),
    ('expr-builtin',"LangMatches-basic"),    
    ('expr-builtin',"LangMatches-4"),
    ('expr-builtin',"LangMatches-3"),
    ('expr-builtin',"LangMatches-2"),
    ('expr-builtin',"LangMatches-1"),
    ('expr-builtin',"sameTerm-eq"),
    ('expr-builtin',"sameTerm-not-eq"),
    ('expr-ops',"Unary Plusn"),
    ('expr-ops',"Addition"),
    ('expr-ops',"Unary Minus"),
    ('expr-ops',"Multiplication"),
    ('expr-ops',"Subtraction"),
    ('regex',"regex-query-004"),
    ('regex',"regex-query-003"),
    ('i18n',"kanji-01"),
    ('i18n',"kanji-02"),
    ('i18n',"normalization-01"),
    #('construct',"*"),
    ('distinct','All: Distinct'),
    ('distinct','Strings: No distinct'),
    ('distinct','All: No distinct'),
    ('distinct','Strings: Distinct'),
    ('sort','sort-10'),
    ('sort','sort-9'),
    ('sort','sort-8'),
    ('sort','sort-7'),
    ('sort','sort-6'),
    ('sort','sort-5'),
    ('sort','sort-4'),
    ('sort','sort-3'),
    ('sort','sort-2'),
    ('sort','sort-1'),
    ('sort','Builtin sort'),
    ('sort','Function sort'),
    ('sort','Expression sort'),
]        

def castToTerm(node):
    if node.localName == 'bnode':
        return BNode(node.firstChild.nodeValue)
    elif node.localName == 'uri':
        return URIRef(node.firstChild.nodeValue)
    elif node.localName == 'literal':
        if node.xpath('string(@datatype)'):
            dT = URIRef(node.xpath('string(@datatype)'))
            if False:#not node.xpath('*'):
                return Literal('',datatype=dT)
            else:                
                return Literal(node.firstChild.nodeValue,
                               datatype=dT)
        else:
            if False:#not node.xpath('*'):
                return Literal('')
            else:
                return Literal(node.firstChild.nodeValue)
    else:
        raise                        

def parseResults(sparqlRT):
    actualRT = []
    from Ft.Xml.Domlette import NonvalidatingReader
    doc = NonvalidatingReader.parseString(sparqlRT)
    vars = [Variable(v.nodeValue) for v in 
             doc.xpath('/sparql:sparql/sparql:head//@name',
             explicitNss=sparqlNsBindings)]
    askAnswer=doc.xpath('string(/sparql:sparql/sparql:boolean)',explicitNss=sparqlNsBindings)
    if askAnswer:
        actualRT=askAnswer==u'true'
    else:
        for result in doc.xpath('//sparql:result',
                                explicitNss=sparqlNsBindings):
            currBind = {}
            for binding in result.xpath('sparql:binding',
                                        explicitNss=sparqlNsBindings):
                varVal = binding.xpath('string(@name)')
                var = Variable(varVal)
                term = castToTerm(binding.xpath('*')[0])
                currBind[var]=term
            if currBind:
                actualRT.append(currBind)
    return actualRT,vars
        
def testSuite(options,skip=None,mainManifest=MAIN_MANIFEST):
    #Extract options
    singleTest=options.singleTest
    skip = skip or []
    SUBDIR=options.testSuite
    cnt = 0
    
    if mainManifest and options.all:
        testManifests=[]
        for mfst in mainManifest:
            manifestG=Graph()
            assert os.path.exists('data-r2/%s'%mfst)
            manifestG.parse(open('data-r2/%s'%mfst),publicID=TEST_BASE,format='n3')
            #print manifestG.serialize(format='n3')         
            testManifests.extend(['data-r2/'+manifest.split(TEST_BASE)[-1] for \
                manifest in Collection(manifestG,
                                       first(manifestG.objects(predicate=manifestNS['mf'].include)))])
    else:    
        testManifests = ['data-r2/%s/manifest.ttl'%SUBDIR]
    reportGraph = Graph()
    setupReportingRDF(reportGraph)
    for testManifest in testManifests:
        store = plugin.get(options.storeKind,Store)()
        bootStrapStore(store,options.config)
        store.commit()
        manifestG=Graph()
        assert os.path.exists(testManifest)
        manifestG.parse(open(testManifest),publicID=TEST_BASE,format='n3')
#        print PARSED_MANIFEST_QUERY2
#        print MANIFEST_QUERY2
#        pprint(list(manifestG))
        manifestData = \
           manifestG.query(
                                  PARSED_MANIFEST_QUERY2,
                                  initNs=manifestNS,
                                  DEBUG = False)
        print testManifest
        pprint(manifestData)
        for rt in manifestData:
            test,testName,testComment,query,result,testAction=rt
            print test,testName, query, result, testAction
            #print test.replace(TEST_BASE+'data-r2/','').split('/')[-1]
            if mainManifest:
                SUBDIR=test.replace(TEST_BASE+'data-r2/','').split('/')[0]            
            if singleTest and testName != singleTest or\
               testName in skip or\
               (SUBDIR,testName) in skipTests or (SUBDIR,'*') in skipTests:
                outcome = EARL.fail
                report(outcome,test,reportGraph)
                print "Skipping ", test                
                continue
            if not query:
                assert testAction
                query=testAction
            query = open(query.replace(TEST_BASE,'data-r2/%s/'%SUBDIR)).read()
            print "##\t%s\t##"%test
            print query
            try:
                parsedSPARQL = Parse(query)
            except:
                parsedSPARQL = Parse(query,True)
                
            algebraExpr=RenderSPARQLAlgebra(parsedSPARQL)
            if isinstance(parsedSPARQL.query,Query.SelectQuery):
                print "SELECT variables: ", parsedSPARQL.query.variables
            print "Algebra expr:", algebraExpr
            print "## Test: %s - %s ##"%(testName,testComment)
            print "## Result: %s ##"%result
            defaultSource = list(manifestG.objects(
                                    subject=testAction,
                                    predicate=MANIFEST_QUERY_NS.data))
            print list(manifestG.triples((testAction,None,None)))
            namedSources  = list(manifestG.objects(
                                    subject=testAction,
                                    predicate=MANIFEST_QUERY_NS.graphData))
            if defaultSource:
                 defaultSource = \
                    defaultSource[0].replace(TEST_BASE,TEST_BASE+'data-r2/%s/'%SUBDIR)
            else:
                defaultSource = None
            namedSources = [s.replace(TEST_BASE,TEST_BASE+'data-r2/%s/'%SUBDIR)\
                              for s in namedSources]
            #Expected results
            if result:
                print result
                resultG=Graph()
                result = result.replace(TEST_BASE,'data-r2/%s/'%SUBDIR)
                sparqlRTFormat = False
                print "Attempting to parse RDF graph of results from ", result
                if not trialAndErrorRTParse(resultG,
                                            result,
                                            options.verbose,
                                            gName=TEST_BASE+'data-r2/%s/'%SUBDIR):
                    #SPARQL result format!
                    sparqlRTFormat = True
                    from Ft.Xml.Domlette import NonvalidatingReader
                    doc = NonvalidatingReader.parseString(open(result).read())
#                    assert doc.xpath('/sparql:sparql/sparql:head//@name',
#                                     explicitNss=sparqlNsBindings)
                print "SPARQL XML result format?: ", sparqlRTFormat
#                if DEBUG:
#                    print "Expected bindings: "
#                    print open(result).read()
                if options.verbose:
                    print "### Source Graph(s): ###"
                    if defaultSource:
                        print "#### Default Graph ####"              
                        print open(defaultSource.replace(TEST_BASE,'')).read()
                    for source in namedSources:
                        if source:          
                            print "#### Named Graph: %s ####"%source              
                            print open(source.replace(TEST_BASE,'')).read()
                    print "########################"
                store = plugin.get(options.storeKind,Store)()
                store.open(options.config,create=False)
                g=ConjunctiveGraph(store)
                if defaultSource:
                    print defaultSource
                    g.default_context.parse(
                            open(defaultSource.replace(TEST_BASE,'')),
                            format='n3')
                for namedSource in namedSources:
                    nG=Graph(store,
                          identifier=URIRef(namedSource)).parse(
                              open(namedSource.replace(TEST_BASE,'')),
                              format='n3'
                          )
                from Ft.Lib import  Uri
                currDir = Uri.OsPathToUri(os.getcwd())
                currDir = currDir[-1]=='/' and currDir or currDir+'/'
                base = Uri.Absolutize('.', Uri.Absolutize(testManifest,currDir))
                queryRT = g.query(parsedSPARQL,
                                  DEBUG = options.verbose,
                                  dataSetBase = Uri.UriToOsPath(base))
                if result and isinstance(parsedSPARQL.query,
                                         Query.ConstructQuery):
                    rtCheckableGraph = IsomorphicTestableGraph(
                                            store=queryRT.result.store,
                                            identifier=queryRT.result.identifier)
                    expectedCheckableGraph=IsomorphicTestableGraph(
                                                   store=resultG.store,
                                                   identifier=resultG.identifier
                                                   )
                    if rtCheckableGraph == expectedCheckableGraph:
                        outcome=EARL['pass']
                    else:
                        outcome=EARL.fail
                        if options.exitOnFailure:
                            raise
                else:
                    rt = queryRT.serialize(format='python')
                if result:
                    outcome=openSelectCompare(
                                    SUBDIR,
                                      queryRT.serialize(format='xml'),
                                      sparqlRTFormat and result or resultG,
                                      testName,
                                      options.exitOnFailure,
                                      base=base)
                    if outcome==EARL.fail and options.exitOnFailure:
                        raise
                else:
                    outcome = EARL["pass"]
                report(outcome,test,reportGraph)
                store.rollback()
            else:
                outcome = EARL["pass"]
                report(outcome,test,reportGraph)
    out=StringIO()
    namespace_manager = NamespaceManager(Graph())
    for prefix,uri in REPORT_NS.items():
        namespace_manager.bind(prefix, uri, override=False)        
    reportGraph.namespace_manager = namespace_manager    
    if WRITE_EARL:
        reportGraph.serialize(destination=out,format='pretty-xml')
        print out.getvalue()

def report(outcome,test,reportGraph):
    assert outcome
    assert test
    result = BNode()
    reportGraph.add((result, RDF.type, EARL.TestResult))
    reportGraph.add((result, EARL.outcome, outcome))
    assertion = BNode()
    reportGraph.add((assertion, RDF.type, EARL.Assertion))
    reportGraph.add((assertion, EARL.result, result))
    reportGraph.add((assertion,
                 EARL.assertedBy,
                 URIRef('http://purl.org/net/chimezie/foaf#chime')))
    reportGraph.add((assertion,
                 EARL.subject,
                 URIRef('http://rdflib.net')))
    reportGraph.add((assertion, EARL.test, URIRef(test)))

def normalizeTerm(term):
    if isinstance(term,BNode):
        return None
    else:
        return term
def normalizeResult(result):
    return [isinstance(i,tuple) and tuple([normalizeTerm(f) for f in i])\
                or normalizeTerm(i) for i in result]
def extractResultG(SUBDIR,rt,allVars,graph,base=None):
    rSetBNode = BNode()
    graph.add((rSetBNode,RDF.type,RESULT_NS.ResultSet))
    for var in allVars:                            
        graph.add((rSetBNode,RESULT_NS.resultVariable,Literal(var)))
    for d in rt:
        sol = BNode()
        graph.add((rSetBNode,RESULT_NS.solution,sol))
        for k,v in d.items():
            binding = BNode()
            if isinstance(v,URIRef):
                #Ugly hack to get base URI's correctly rooted in DAWG webspace
                v=Uri.Absolutize(v,TEST_BASE+'data-r2/%s/'%SUBDIR)
            graph.add((sol,RESULT_NS.binding,binding))
            graph.add((binding,RESULT_NS.variable,Literal(k)))
            graph.add((binding,RESULT_NS.value,v))
def extractExpectedBindings(resultG,base=None):
    bindings = []
    resultSetNode = resultG.value(predicate=RESULT_NS.value,object=RESULT_NS.ResultSet)
    for solutionNode in resultG.objects(resultSetNode,RESULT_NS.solution):
        bindingDict = {}#dict([(key,None) for key in rtVars])
        for bindingNode in resultG.objects(solutionNode,RESULT_NS.binding):
            value = resultG.value(subject=bindingNode,predicate=RESULT_NS.value)
            name  = resultG.value(subject=bindingNode,predicate=RESULT_NS.variable)
            bindingDict[Variable(name)] = base and Uri.Absolutize(value,base) or value
        bindings.append(bindingDict)
    return bindings
    
def openSelectCompare(SUBDIR,sparqlRT,resultG,testName,exitOnFailure,base=None):
    actualRT,vars = parseResults(sparqlRT)                                
    if isinstance(resultG,Graph):
        expectedRT = extractExpectedBindings(resultG)
    else:
        expectedRT,vars = parseResults(open(resultG).read())
    if isinstance(actualRT,bool):
        #ask answer comparison
        if actualRT == expectedRT:
            print "### TEST PASSED!: %s ###"%testName
            return EARL['pass']
        else: 
            print "### Expected Result: %s ###"%expectedRT
            print "### Actual Result: %s ###"%actualRT
            print "### TEST FAILED!: %s ###"%testName
            return EARL.fail
    else:
        a=[ImmutableDict([(k,v) for k,v in d.items()]) for d in actualRT]
        b=[ImmutableDict([(k,v) for k,v in d.items()]) for d in expectedRT]
        a.sort(key=lambda d:hash(d))
        b.sort(key=lambda d:hash(d))
    
        aGraph = IsomorphicTestableGraph()
        eGraph = IsomorphicTestableGraph()
        if isinstance(resultG,Graph):
            eGraph+= resultG
        else:
            extractResultG(SUBDIR,expectedRT,vars,eGraph,base)                         
        extractResultG(SUBDIR,actualRT,vars,aGraph,base)   
        
        if actualRT == expectedRT or set(a) == set(b):# or aGraph == eGraph:
            print "### TEST PASSED!: %s ###"%testName
            return EARL['pass']
        else:
            if aGraph == eGraph:
                print "### TEST PASSED!: %s (via isomorphic check) ###"%testName
                return EARL['pass']
            else: 
                print "### Expected Result (%s items) ###"%len(expectedRT)
                pprint(expectedRT)
                print "### Actual Results (%s items) ###"%len(actualRT)
                pprint(actualRT)
                print "### TEST FAILED!: %s ###"%testName
                if exitOnFailure:
                    raise
                return EARL.fail

class IsomorphicTestableGraph(Graph):
    """
    Ported from http://www.w3.org/2001/sw/DataAccess/proto-tests/tools/rdfdiff.py
     (Sean B Palmer's RDF Graph Isomorphism Tester)
    """
    def __init__(self, **kargs): 
        super(IsomorphicTestableGraph,self).__init__(**kargs)
        self.hash = None
        
    def internal_hash(self):
        """
        This is defined instead of __hash__ to avoid a circular recursion scenario with the Memory
        store for rdflib which requires a hash lookup in order to return a generator of triples
        """ 
        return hash(tuple(sorted(self.hashtriples())))

    def hashtriples(self): 
        for triple in self: 
            g = ((isinstance(t,BNode) and self.vhash(t)) or t for t in triple)
            yield hash(tuple(g))

    def vhash(self, term, done=False): 
        return tuple(sorted(self.vhashtriples(term, done)))

    def vhashtriples(self, term, done): 
        for t in self: 
            if term in t: yield tuple(self.vhashtriple(t, term, done))

    def vhashtriple(self, triple, term, done): 
        for p in xrange(3): 
            if not isinstance(triple[p], BNode): yield triple[p]
            elif done or (triple[p] == term): yield p
            else: yield self.vhash(triple[p], done=True)
      
    def __eq__(self, G): 
        """Graph isomorphism testing."""
        if not isinstance(G, IsomorphicTestableGraph): return False
        elif len(self) != len(G): return False
        elif list.__eq__(list(self),list(G)): return True # @@
        return self.internal_hash() == G.internal_hash()

    def __ne__(self, G): 
       """Negative graph isomorphism testing."""
       return not self.__eq__(G)

class ImmutableDict(dict):
    '''
    A hashable dict.
    
    >>> a=[ImmutableDict([('one',1),('three',3)]),ImmutableDict([('two',2),('four' ,4)])]
    >>> b=[ImmutableDict([('two',2),('four' ,4)]),ImmutableDict([('one',1),('three',3)])]
    >>> a.sort(key=lambda d:hash(d))
    >>> b.sort(key=lambda d:hash(d))
    >>> a == b
    True
    
    '''
    def __init__(self,*args,**kwds):
        dict.__init__(self,*args,**kwds)
        self._items=list(self.iteritems())
        self._items.sort()
        self._items=tuple(self._items)
    def __setitem__(self,key,value):
        raise NotImplementedError, "dict is immutable"
    def __delitem__(self,key):
        raise NotImplementedError, "dict is immutable"
    def clear(self):
        raise NotImplementedError, "dict is immutable"
    def setdefault(self,k,default=None):
        raise NotImplementedError, "dict is immutable"
    def popitem(self):
        raise NotImplementedError, "dict is immutable"
    def update(self,other):
        raise NotImplementedError, "dict is immutable"
    def __hash__(self):
        return hash(self._items)
                                
if __name__ == '__main__':
    import doctest, sys
    from optparse import OptionParser
    usage = '''usage: %prog [options]'''
    op = OptionParser(usage=usage)
    op.add_option('--singleTest',default=None,
      help="The title of the single test (within the test group) to run ")

    op.add_option('--exitOnFailure',action="store_true",
      help="Exit test run upon any single failure? (false by default)")

    op.add_option('-v','--verbose',action="store_true",
      help="Run in verbose, debug mode? (off by default)")

    op.add_option('-s','--storeKind',default="IOMemory",
      help="The (class) name of the store to use for persistence")

    op.add_option('-c','--config',default='',
      help="Configuration string to use for connecting to persistence store")
    
    op.add_option('-t','--testSuite',default='optional',
      help="The name of the test sub-directory to run ")

    op.add_option('--all',action="store_true",
      help="Run all the tests (cannot be used with -t/--testSuite and false by default)")
    (options, args) = op.parse_args()

    if options.all and options.testSuite:
        options.error('Both --all and -t/--testSuite cannot be used at once')

    testSuite(options,
               skip=[
                     #'graph-08',#see proof
                     #'graph-07',#seems incorrect WRT multiset union (disjunction) semantics
                                #Union(A3,B1) where all the solutions in A3 and B1 are distinct
                     #'graph-02',#There should be 2 triples from the named graph matching ?s ?p ?o
                                #different interpretation of 'default dataset'?
                     #'graph-11',#see proof
                     ])    
