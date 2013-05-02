"""

RDFLib has a Resource class, for a resource-centric API


"""

from rdflib import Graph, RDF, RDFS, Literal
from rdflib.namespace import FOAF

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

print "Bill's friend: ", bill.value(FOAF.knows).value(FOAF.name)

# slicing ([] syntax) can also be used: 

print list(bill[FOAF.knows])  # return triples!

bill[RDFS.label]=Literal("William")

print g.serialize(format='n3')
