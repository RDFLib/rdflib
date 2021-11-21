"""
RDFLib has a :class:`~rdflib.resource.Resource` class, for a resource-centric API.
The :class:`~rdflib.Graph` class also has a ``resource`` function that can be used
to create resources and manipulate them by quickly adding or querying for triples
where this resource is the subject.

This example shows g.resource() in action.
"""

from rdflib import Graph, RDF, RDFS, Literal
from rdflib.namespace import FOAF

if __name__ == "__main__":
    g = Graph()

    # Create a Resource within graph g
    bob = g.resource("http://example.com/bob")
    # .set replaces all other values
    bob.set(RDF.type, FOAF.Person)
    bob.set(FOAF.name, Literal("Bob"))

    bill = g.resource("http://example.com/bill")
    # .add adds to existing values
    bill.add(RDF.type, FOAF.Person)
    bill.add(RDF.type, FOAF.Agent)
    bill.set(RDFS.label, Literal("Bill"))

    bill.add(FOAF.knows, bob)

    # Resources returned when querying are 'auto-boxed' as resources:
    print(f"Bill knows: {bill.value(FOAF.knows).value(FOAF.name)}")

    # Slicing ([] syntax) can also be used:
    for friend in bill[FOAF.knows]:
        print(f"Bill knows: {next(friend[FOAF.name])}")

    # Or even quicker with paths:
    for friend in bill[FOAF.knows / FOAF.name]:
        print(f"Bill knows: {friend}")

    # Setting single properties is also possible:
    bill[RDFS.label] = Literal("William")
