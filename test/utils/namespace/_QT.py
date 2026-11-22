from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class QT(DefinedNamespace):
    _fail = True
    _NS = Namespace("http://www.w3.org/2001/sw/DataAccess/tests/test-query#")

    QueryForm: URIRef  # Super class of all query forms
    QueryTest: URIRef  # The class of query tests
    data: URIRef  # Optional: data for the query test
    graphData: URIRef  # Optional: named-graph only data for the query test (ie. not loaded into the background graph)
    query: URIRef  # The query to ask
    queryForm: URIRef  # None
