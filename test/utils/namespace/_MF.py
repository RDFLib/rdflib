from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class MF(DefinedNamespace):
    _fail = True
    _NS = Namespace("http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#")

    IllFormedLiterals: URIRef  # Tests that involve lexical forms which are illegal for the datatype
    KnownTypesDefault2Neq: URIRef  # Values in disjoint value spaces are not equal
    LangTagAwareness: URIRef  # Tests that require langauge tag handling in FILTERs
    LaxCardinality: URIRef  # The given mf:result for a test with an mf:resultCardinality of mf:ReducedCardinalityTest  is the results as if the REDUCED keyword were omitted. To pass such a test, an implementation must produce a result set  with each solution in the expected results appearing at least once and  no more than the number of times it appears in the expected results. Of  course, there must also be no results produced that are not in the  expected results.
    Manifest: URIRef  # The class of manifests
    ManifestEntry: URIRef  # One entry in rdf:type list of entries
    NegativeSyntaxTest: URIRef  # A type of test specifically for syntax testing. Syntax tests are not required to have an associated result, only an action. Negative syntax tests are tests of which the result should be a parser error.
    NegativeSyntaxTest11: URIRef  # A type of test specifically for syntax testing of new features in the SPARQL1.1 Query Language. Syntax tests are not required to have an associated result, only an action. Negative syntax tests are tests of which the result should be a parser error.
    NegativeUpdateSyntaxTest11: URIRef  # A type of test specifically for syntax testing of SPARQL1.1 Update. Syntax tests are not required to have an associated result, only an action. Negative syntax tests are tests of which the result should be a parser error.
    Notable: URIRef  # Requirements for a  particular test
    PositiveSyntaxTest: URIRef  # A type of test specifically for syntax testing. Syntax tests are not required to have an associated result, only an action.
    PositiveSyntaxTest11: URIRef  # A type of test specifically for syntax testing of new features in the SPARQL1.1 Query Language. Syntax tests are not required to have an associated result, only an action.
    PositiveUpdateSyntaxTest11: URIRef  # A type of test specifically for syntax testing of SPARQL1.1 Update. Syntax tests are not required to have an associated result, only an action.
    QueryEvaluationTest: URIRef  # A type of test specifically for query evaluation testing. Query evaluation tests are required to have an associated input dataset, a query, and an expected output dataset.
    Requirement: URIRef  # Requirements for a  particular test
    ResultCardinality: URIRef  # Potential modes of evaluating a test's results with respect to solution cardinality
    StringSimpleLiteralCmp: URIRef  # Tests that require simple literal is the same value as an xsd:string of the same lexicial form
    TestStatus: URIRef  # Statuses a test can have
    UpdateEvaluationTest: URIRef  # The class of all SPARQL 1.1 Update evaluation tests
    XsdDateOperations: URIRef  # Tests that require xsd:date operations
    accepted: URIRef  # None
    action: URIRef  # Action to perform
    entries: URIRef  # Connects the manifest resource to rdf:type list of entries
    include: URIRef  # Connects the manifest resource to rdf:type list of manifests
    name: URIRef  # Optional name of this entry
    notable: URIRef  # Notable feature of this test (advisory)
    proposed: URIRef  # None
    rejected: URIRef  # None
    requires: URIRef  # Required functionality for execution of this test
    result: URIRef  # The expected outcome
    # result: URIRef  # The test status
    resultCardinality: URIRef  # Specifies whether passing the test requires strict or lax cardinality adherence
    CSVResultFormatTest: URIRef
    ServiceDescriptionTest: URIRef
    ProtocolTest: URIRef
