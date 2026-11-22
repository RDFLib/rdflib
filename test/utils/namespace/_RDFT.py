from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class RDFT(DefinedNamespace):
    _fail = True
    _NS = Namespace("http://www.w3.org/ns/rdftest#")

    approval: URIRef  # Approval status of a test.
    Approval: URIRef  # The superclass of all test approval statuses.
    Approved: URIRef  # Indicates that a test is approved.
    Proposed: URIRef  # Indicates that a test is proposed, but not approved.
    Rejected: URIRef  # Indicates that a test is not approved.
    TestEval: URIRef  # Superclass of all RDF Evaluation Tests.
    TestNQuadsNegativeSyntax: URIRef  # A negative N-Quads syntax test.
    TestNQuadsPositiveSyntax: URIRef  # A positive N-Quads syntax test.
    TestNTriplesNegativeSyntax: URIRef  # A negative N-Triples syntax test.
    TestNTriplesPositiveSyntax: URIRef  # A positive N-Triples syntax test.
    TestSyntax: URIRef  # Superclass of all RDF Syntax Tests.
    TestTrigEval: URIRef  # A positive TriG evaluation test.
    TestTrigNegativeEval: URIRef  # A negative TriG evaluation test.
    TestTriGNegativeSyntax: URIRef  # A negative TriG syntax test.
    TestTriGPositiveSyntax: URIRef  # A positive TriG syntax test.
    TestTurtleEval: URIRef  # A positive Turtle evaluation test.
    TestTurtleNegativeEval: URIRef  # A negative Turtle evaluation test.
    TestTurtleNegativeSyntax: URIRef  # A negative Turtle syntax test.
    TestTurtlePositiveSyntax: URIRef  # A positive Turtle syntax test.
    Test: URIRef  # Superclass of all RDF Tests.
    TestXMLNegativeSyntax: URIRef  # A negative RDF/XML syntax test.
    XMLEval: URIRef  # A positive RDF/XML evaluation test.
    TestXMLEval: URIRef

    TestTrigPositiveSyntax: URIRef
    TestTrigNegativeSyntax: URIRef

    TestTrixEval: URIRef  # A positive TriX evaluation test.
    TestTrixNegativeSyntax: URIRef  # A negative TriX syntax test.
    TestTrixPositiveSyntax: URIRef  # A positive TriX syntax test.
