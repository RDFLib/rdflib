from rdflib.URIRef import URIRef
from rdflib.Literal import Literal
from rdflib.BNode import BNode
from rdflib.Namespace import Namespace
from rdflib.constants import TYPE

# Import RDFLib's InformationStore (a Sleepycat BTree backed
# TripleStore with contexts).
from rdflib.InformationStore import InformationStore as TripleStore

# Create a namespace object for the Friend of a friend namespace.
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

store = TripleStore()
# Open a ZODB connection to the FileStore that the TripleStore should
# use for its indices.
store.open("store")

# Create an identifier to use as the subject for Donna.
donna = BNode()

# Add triples using store's add method.
store.add((donna, TYPE, FOAF["Person"]))
store.add((donna, FOAF["nick"], Literal("donna")))
store.add((donna, FOAF["name"], Literal("Donna Fales")))

# Get a Resource object for the resource with the given URIRef.
eikeon = store[URIRef("http://eikeon.com/#eikeon")]

# Modify the resource eikeon and the store such that the follow is
# true.
eikeon[TYPE] = FOAF["Person"]
eikeon[FOAF["name"]] = Literal("Daniel Krech")
eikeon[FOAF["mbox"]] = URIRef("mailto:eikeon@eikeon.com")
eikeon[FOAF["knows"]] = donna

print eikeon[FOAF["name"]]

# Iterate over triples in store and print them out.
for s, p, o in store:
    print s, p, o
    
# For each foaf:Person in the store print out its mbox property.
for person in store.subjects(TYPE, FOAF["Person"]):
    for mbox in store.objects(person, FOAF["mbox"]):
        print mbox

# Close the store
store.close()
