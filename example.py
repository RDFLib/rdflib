from rdflib.URIRef import URIRef
from rdflib.Literal import Literal
from rdflib.BNode import BNode
from rdflib.Namespace import Namespace
from rdflib.constants import TYPE

# Import RDFLib's default TripleStore implementation.
from rdflib.TripleStore import TripleStore

# Create a namespace object for the Friend of a friend namespace.
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

store = TripleStore()

store.prefix_mapping("dc", "http://http://purl.org/dc/elements/1.1/")
store.prefix_mapping("foaf", "http://xmlns.com/foaf/0.1/")
 
# Create an identifier to use as the subject for Donna.
donna = BNode()

# Add triples using store's add method.
store.add((donna, TYPE, FOAF["Person"]))
store.add((donna, FOAF["nick"], Literal("donna")))
store.add((donna, FOAF["name"], Literal("Donna Fales")))

# Iterate over triples in store and print them out.
for s, p, o in store:
    print s, p, o
    
# For each foaf:Person in the store print out its mbox property.
for person in store.subjects(TYPE, FOAF["Person"]):
    for mbox in store.objects(person, FOAF["mbox"]):
        print mbox

# Serialize the store as RDF/XML to the file foaf.rdf.
store.save("foaf.rdf")

print store.serialize()
