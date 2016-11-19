"""

RDFLib has a :class:`~rdflib.resource.Resource` class, for a resource-centric API.

A resource acts like a URIRef with an associated graph, and allows
quickly adding or querying for triples where this resource is the
subject.


"""

from rdflib import Graph, RDF, RDFS, Literal
from rdflib.namespace import FOAF

if __name__=='__main__':

    g = Graph()

    bob = g.resource('urn:bob')

    bob.set(RDF.type, FOAF.Person) # .set replaces all other values
    bob.set(FOAF.name, Literal("Bob"))


    bill = g.resource('urn:bill')

    bill.add(RDF.type, FOAF.Person) # add adds to existing values
    bill.add(RDF.type, FOAF.Agent)
    bill.set(RDFS.label, Literal("Bill"))

    bill.add(FOAF.knows, bob)

    # Resources returned when querying are 'auto-boxed' as resources:

    print("Bill's friend: ", bill.value(FOAF.knows).value(FOAF.name))

    # slicing ([] syntax) can also be used:

    print("Bill knows: ")
    for friend in bill[FOAF.knows]:
        print(next(friend[FOAF.name]))

    # or even quicker with paths:
    print("Bill knows: ")
    for friend in bill[FOAF.knows/FOAF.name]:
        print(friend)

    # setting single properties is also possible:
    bill[RDFS.label]=Literal("William")
