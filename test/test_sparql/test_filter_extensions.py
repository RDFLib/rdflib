from rdflib.graph import ConjunctiveGraph
from rdflib.namespace import Namespace, RDF, XSD
from rdflib.term import BNode, Literal


DC = Namespace(u"http://purl.org/dc/elements/1.1/")
FUNC = Namespace(u"http://example.org/functions#")


graph = ConjunctiveGraph()
graph.add((BNode(), RDF.value, Literal(0)))
graph.add((BNode(), RDF.value, Literal(1)))
graph.add((BNode(), RDF.value, Literal(2)))
graph.add((BNode(), RDF.value, Literal(3)))

from rdflib.term import _toPythonMapping
NUMERIC_TYPES = [type_uri for type_uri in _toPythonMapping if \
                 _toPythonMapping[type_uri] in (int, float, long)]

def func_even(a):
    # Should this be required, or be done automatically?
    from rdflib.sparql.sparqlOperators import getValue
    value = getValue(a)

    if isinstance(value, Literal) and value.datatype in NUMERIC_TYPES:
        return Literal(int(value.toPython() % 2 == 0), datatype=XSD.boolean)
    else:
        raise TypeError(a)

def test_even_extension():
    res = list(graph.query("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX func:  <http://example.org/functions#>

    SELECT ?value
    WHERE { ?x rdf:value ?value . FILTER ( func:even(?value) ) }

    """))
    res.sort()
    expected = [Literal(0), Literal(2)]
    assert res == expected, "Expected %s but got %s" % (expected, res)

test_even_extension.sparql = True
test_even_extension.known_issue = True # Extension functions are not
                                       # implemented!  See the
                                       # `mapToOperator` function in
                                       # SPARQLEvaluate.py for details.

if __name__ == '__main__':
    test_even_extension()
