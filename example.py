from rdflib import Graph
from rdflib import URIRef, Literal, BNode, Namespace

from rdflib import RDF


# Create a namespace object for the Friend of a friend namespace.
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

store = Graph()

store.prefix_mapping("dc", "http://http://purl.org/dc/elements/1.1/")
store.prefix_mapping("foaf", "http://xmlns.com/foaf/0.1/")
 
# Create an identifier to use as the subject for Donna.
donna = BNode()

from rdflib.constants import DATATYPE

# Add triples using store's add method.
store.add((donna, RDF.type, FOAF["Person"]))
store.add((donna, FOAF["nick"], Literal("donna")))
store.add((donna, FOAF["name"], Literal("Donna Fales")))

# Iterate over triples in store and print them out.
print "--- printing raw triples ---"
for s, p, o in store:
    print s, p, o
    
# For each foaf:Person in the store print out its mbox property.
print "--- printing mboxes ---"
for person in store.subjects(RDF.type, FOAF["Person"]):
    for mbox in store.objects(person, FOAF["mbox"]):
        print mbox

# Serialize the store as RDF/XML to the file foaf.rdf.
store.graphUnloader().save("foaf.rdf")

# Let's show off the serializers

print "RDF Serializations:"

# Serialize as XML
print "--- start: rdf-xml ---"
print store.graphUnloader().serialize(format="pretty-xml")
print "--- end: rdf-xml ---\n"

# Serialize as NTriples
print "--- start: ntriples ---"
print store.graphUnloader().serialize(format="nt")
print "--- end: ntriples ---\n"

