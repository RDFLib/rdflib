"""
SPARQL Queries be prepared (i.e parsed and translated to SPARQL algebra)
by the :meth:`rdflib.plugins.sparql.prepareQuery` method.

``initNs`` can be used instead of PREFIX values.

When executing, variables can be bound with the
``initBindings`` keyword parameter.
"""

from pathlib import Path

import rdflib
from rdflib.namespace import FOAF
from rdflib.plugins.sparql import prepareQuery

EXAMPLES_DIR = Path(__file__).parent

if __name__ == "__main__":
    q = prepareQuery(
        "SELECT ?name WHERE { ?person foaf:knows/foaf:name ?name . }",
        initNs={"foaf": FOAF},
    )

    g = rdflib.Graph()
    g.parse(f"{EXAMPLES_DIR / 'foaf.n3'}")

    tim = rdflib.URIRef("http://www.w3.org/People/Berners-Lee/card#i")

    for row in g.query(q, initBindings={"person": tim}):
        # For select queries, the Result object is an iterable of ResultRow
        # objects.
        assert isinstance(row, rdflib.query.ResultRow)
        print(row.name)
