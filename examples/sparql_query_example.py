"""
SPARQL Query using :meth:`rdflib.graph.Graph.query`

The method returns a :class:`~rdflib.query.Result`, iterating over
this yields :class:`~rdflib.query.ResultRow` objects

The variable bindings can be accessed as attributes of the row objects
For variable names that are not valid python identifiers, dict access
(i.e. with ``row[var] / __getitem__``) is also possible.

:attr:`~rdflib.query.ResultRow.vars` contains the variables
"""

import rdflib

if __name__ == "__main__":

    g = rdflib.Graph()
    g.load("foaf.n3", format="n3")

    # The QueryProcessor knows the FOAF prefix from the graph
    # which in turn knows it from reading the N3 RDF file
    for row in g.query("SELECT ?s WHERE { [] foaf:knows ?s .}"):
        print(row.s)
        # or row["s"]
        # or row[rdflib.Variable("s")]
