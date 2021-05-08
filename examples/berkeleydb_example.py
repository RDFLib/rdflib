"""
A simple example showing how to use a BerkeleyDB store to do on-disk
persistence.
"""

from rdflib import ConjunctiveGraph, Namespace, Literal
from rdflib.store import NO_STORE, VALID_STORE

from tempfile import mktemp

if __name__ == "__main__":
    path = mktemp()

    # Open previously created store, or create it if it doesn't exist yet
    graph = ConjunctiveGraph("BerkeleyDB")

    rt = graph.open(path, create=False)

    if rt == NO_STORE:
        # There is no underlying BerkeleyDB infrastructure, so create it
        graph.open(path, create=True)
    else:
        assert rt == VALID_STORE, "The underlying store is corrupt"

    print("Triples in graph before add:", len(graph))

    # Now we'll add some triples to the graph & commit the changes
    EG = Namespace("http://example.net/test/")
    graph.bind("eg", EG)

    graph.add((EG["pic:1"], EG.name, Literal("Jane & Bob")))
    graph.add((EG["pic:2"], EG.name, Literal("Squirrel in Tree")))

    graph.commit()

    print("Triples in graph after add:", len(graph))

    # display the graph in Turtle
    print(graph.serialize())

    # close when done, otherwise BerkeleyDB will leak lock entries.
    graph.close()

    graph = None

    # reopen the graph
    graph = ConjunctiveGraph("BerkeleyDB")

    graph.open(path, create=False)

    print("Triples still in graph:", len(graph))

    graph.close()

    # Clean up the temp folder to remove the BerkeleyDB database files...
    import os

    for f in os.listdir(path):
        os.unlink(path + "/" + f)
    os.rmdir(path)
