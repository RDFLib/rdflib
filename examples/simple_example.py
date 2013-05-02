import logging

# Optional: Configure how we want rdflib logger to log messages
_logger = logging.getLogger("rdflib")
_logger.setLevel(logging.DEBUG)
_hdlr = logging.StreamHandler()
_hdlr.setFormatter(logging.Formatter('%(name)s %(levelname)s: %(message)s'))
_logger.addHandler(_hdlr)

from rdflib import Graph, Literal, BNode, RDF
from rdflib.namespace import FOAF, DC

store = Graph()

# Bind a few prefix, namespace pairs for pretty output
store.bind("dc", DC)
store.bind("foaf", FOAF)

# Create an identifier to use as the subject for Donna.
donna = BNode()

# Add triples using store's add method.
store.add((donna, RDF.type, FOAF.Person))
store.add((donna, FOAF.nick, Literal("donna", lang="foo")))
store.add((donna, FOAF.name, Literal("Donna Fales")))

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
store.serialize("foaf.rdf", format="pretty-xml", max_depth=3)

# Let's show off the serializers

print "RDF Serializations:"

# Serialize as XML
print "--- start: rdf-xml ---"
print store.serialize(format="pretty-xml")
print "--- end: rdf-xml ---\n"

# Serialize as Turtle
print "--- start: turtle ---"
print store.serialize(format="turtle")
print "--- end: turtle ---\n"

# Serialize as NTriples
print "--- start: ntriples ---"
print store.serialize(format="nt")
print "--- end: ntriples ---\n"
