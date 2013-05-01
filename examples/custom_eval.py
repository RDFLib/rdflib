"""

This example shows how a custom evaluation function can be added to
handle certain SPARQL Algebra elements

A custom function is added that adds subClassOf "inference" when
asking for rdf:type triples.

Here the custom eval function is added manually, normally you would use
setuptools and entry_points to do it:
i.e. in your setup.py:

    entry_points = {
        'rdf.plugins.sparqleval': [
            'myfunc =     mypackage:MyFunction',
            ],
    }

"""

import rdflib.plugins.sparql.paths
import rdflib

from rdflib.plugins.sparql.evaluate import evalBGP

FOAF = rdflib.Namespace("http://xmlns.com/foaf/0.1/")

inferredSubClass = \
    rdflib.RDFS.subClassOf % '*'  # any number of rdfs.subClassOf


def customEval(ctx, part):
    """
    Rewrite triple patterns to get super-classes
    """

    if part.name == 'BGP':

        # rewrite triples
        triples = []
        for t in part.triples:
            if t[1] == rdflib.RDF.type:
                bnode = rdflib.BNode()
                triples.append((t[0], t[1], bnode))
                triples.append((bnode, inferredSubClass, t[2]))
            else:
                triples.append(t)

        # delegate to normal evalBGP
        return evalBGP(ctx, triples)

    raise NotImplementedError()

# add function directly, normally we would use setuptools and entry_points
rdflib.plugins.sparql.CUSTOM_EVALS['exampleEval'] = customEval

g = rdflib.Graph()
g.load("foaf.rdf")

# Add the subClassStmt so that we can query for it!
g.add((FOAF.Person,
       rdflib.RDFS.subClassOf,
       FOAF.Agent))

# Find all FOAF Agents
for x in g.query(
        'PREFIX foaf: <%s> SELECT * WHERE { ?s a foaf:Agent . }' % FOAF):
    print x
