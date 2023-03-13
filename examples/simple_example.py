import os.path
from tempfile import TemporaryDirectory

from rdflib import RDF, BNode, Graph, Literal
from rdflib.namespace import DC, FOAF

if __name__ == "__main__":
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
    print("--- printing raw triples ---")
    for s, p, o in store:
        print(s, p, o)

    # For each foaf:Person in the store print out its mbox property.
    print()
    print("--- printing mboxes ---")
    for person in store.subjects(RDF.type, FOAF["Person"]):
        for mbox in store.objects(person, FOAF["mbox"]):
            print(mbox)

    tmp_dir = TemporaryDirectory()
    output_file = os.path.join(tmp_dir.name, "donna_foaf.rdf")
    print(f"--- saving RDF to a file ({output_file}) ---")
    # Serialize the store as RDF/XML to the file donna_foaf.rdf.
    store.serialize(f"{output_file}", format="pretty-xml", max_depth=3)

    # Let's show off the serializers
    print()
    print("RDF Serializations:")

    # Serialize as Turtle (default)
    print("--- start: turtle ---")
    print(store.serialize())
    print("--- end: turtle ---\n")

    # Serialize as XML
    print("--- start: rdf-xml ---")
    print(store.serialize(format="pretty-xml"))
    print("--- end: rdf-xml ---\n")

    # Serialize as NTriples
    print("--- start: ntriples ---")
    print(store.serialize(format="nt"))
    print("--- end: ntriples ---\n")

    # Serialize as JSON-LD
    # only if you have the JSON-LD plugin installed!
    print("--- start: JSON-LD ---")
    print(store.serialize(format="json-ld"))
    print("--- end: JSON-LD ---\n")
