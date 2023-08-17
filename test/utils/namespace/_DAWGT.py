from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class DAWGT(DefinedNamespace):
    _fail = True
    _NS = Namespace("http://www.w3.org/2001/sw/DataAccess/tests/test-dawg#")

    ResultForm: URIRef  # Super class of all result forms
    Status: URIRef  # Super class of all test status classes
    approval: URIRef  # The approval status of the test with respect to the working group.
    approvedBy: URIRef  # Contains a reference to the minutes of the RDF Data Access Working Group where the test case status was last changed.
    description: URIRef  # A human-readable summary of the test case.
    issue: URIRef  # Contains a pointer to the associated issue on the RDF Data Access Working Group Tracking document.
    resultForm: URIRef  # None
    warning: URIRef  # Indicates that while the test should pass, it may generate a warning.
    NotClassified: URIRef  # Class of tests that have not been classified
    Approved: URIRef  # Class of tests that are Approved
    Rejected: URIRef  # Class of tests that are Rejected
    Obsoleted: URIRef  # Class of tests that are Obsolete
    Withdrawn: URIRef  # Class of tests that have been Withdrawn
    ResultSet: URIRef  # Class of result expected to be from a SELECT query
    ResultGraph: URIRef  # Class of result expected to be a graph
    ResultBoolean: URIRef  # Class of result expected to be a boolean
