
from rdflib.plugins import sparql
from rdflib.namespace import RDFS, OWL, DC, SKOS

def test_issue():



    query = sparql.prepareQuery(
        """
            SELECT DISTINCT ?property ?parent
            WHERE{
                ?property a owl:DeprecatedProperty .
                ?property dc:relation ?relation .
                ?property rdfs:subPropertyOf ?parent .
                ?property rdfs:label | skos:altLabel ?label .
            }
        """,
        initNs = {"rdfs":RDFS, "owl":OWL, "dc":DC, "skos":SKOS})
