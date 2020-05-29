import rdflib
g = rdflib.Graph()
g.serialize(format="turtle").decode("utf-8")
# empty

g.update('INSERT DATA { _:a <urn:label> "A bnode" }')
g.serialize(format="turtle").decode("utf-8")
# @prefix ns1: <urn:> .
# [] ns1:label "A bnode" .

g.update('INSERT DATA { _:a <urn:label> "Bnode 2" }')
g.serialize(format="turtle").decode("utf-8")

# @prefix ns1: <urn:> .
# [] ns1:label "A bnode",
#        "Bnode 2" .