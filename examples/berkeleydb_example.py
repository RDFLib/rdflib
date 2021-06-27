"""
A simple example showing how to use a BerkeleyDB store to do on-disk persistence:

* creating a ConjunctiveGraph using the BerkeleyDB Store
* adding triples to it
* counting them
* closing the store, emptying the graph
* re-opening the store using the same DB files
* getting the same count of triples as before

"""

from rdflib import ConjunctiveGraph, Namespace, Literal
from rdflib.store import NO_STORE, VALID_STORE

from tempfile import mktemp


if __name__ == "__main__":
    path = mktemp()

    # Declare we are using a BerkeleyDB Store
    graph = ConjunctiveGraph("BerkeleyDB")

    # Open previously created store, or create it if it doesn't exist yet
    # (always doesn't exist in this example as using temp file location)
    rt = graph.open(path, create=False)

    if rt == NO_STORE:
        # There is no underlying BerkeleyDB infrastructure, so create it
        print("Creating new DB")
        graph.open(path, create=True)
    else:
        print("Using existing DB")
        assert rt == VALID_STORE, "The underlying store is corrupt"

    print("Triples in graph before add:", len(graph))
    print("(will always be 0 when using temp file for DB)")

    # Now we'll add some triples to the graph & commit the changes
    EG = Namespace("http://example.net/test/")
    graph.bind("eg", EG)

    graph.add((EG["pic:1"], EG.name, Literal("Jane & Bob")))
    graph.add((EG["pic:2"], EG.name, Literal("Squirrel in Tree")))

    graph.commit()

    print("Triples in graph after add:", len(graph))
    print("(should be 2)")

    # display the graph in Turtle
    print(graph.serialize())

    # close when done, otherwise BerkeleyDB will leak lock entries.
    graph.close()

    graph = None

    # reopen the graph
    graph = ConjunctiveGraph("BerkeleyDB")

    graph.open(path, create=False)

    print("Triples still in graph:", len(graph))
    print("(should still be 2)")

    graph.close()

    # Clean up the temp folder to remove the BerkeleyDB database files...
    import os

    for f in os.listdir(path):
        os.unlink(path + "/" + f)
    os.rmdir(path)
