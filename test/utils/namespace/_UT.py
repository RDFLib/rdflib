from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class UT(DefinedNamespace):
    _fail = True
    _NS = Namespace("http://www.w3.org/2009/sparql/tests/test-update#")

    data: URIRef  # Optional: data for the update test (i.e. default graph in the graph store prior or after the update, depending on whether used within mf:action or within mf:result)
    graph: URIRef  # Optional: points to the named graph within the resource described by the :graphData property, if present, the actual name of the named graph is supposed to be given using the rdfs:label property as a plain literal
    graphData: URIRef  # Optional: named-graph only data for the update test (i.e. named graph in the graph store prior or after the update, depending on whether used within mf:action or within mf:result)
    request: URIRef  # The update request (may consist of several update statements\
    UpdateEvaluationTest: URIRef
    result: URIRef
    success: URIRef
    Success: URIRef
