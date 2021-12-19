"""
BerkeleyDB in use as a persistent Graph store.

Example 1: simple actions

* creating a ConjunctiveGraph using the BerkeleyDB Store
* adding triples to it
* counting them
* closing the store, emptying the graph
* re-opening the store using the same DB files
* getting the same count of triples as before

Example 2: larger data

* loads multiple graphs downloaded from GitHub into a BerkeleyDB-baked graph stored in the folder gsq_vocabs.
* does not delete the DB at the end so you can see it on disk
"""
import os
from rdflib import ConjunctiveGraph, Namespace, Literal
from rdflib.store import NO_STORE, VALID_STORE
from tempfile import mktemp


def example_1():
    """Creates a ConjunctiveGraph and performs some BerkeleyDB tasks with it"""
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
    for f in os.listdir(path):
        os.unlink(path + "/" + f)
    os.rmdir(path)


def example_2():
    """Loads a number of SKOS vocabularies from GitHub into a BerkeleyDB-backed graph stored in the local folder
    'gsq_vocabs'

    Should print out the number of triples after each load, e.g.:
        177
        248
        289
        379
        421
        628
        764
        813
        965
        1381
        9666
        9719
        ...
    """
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
    import json
    import base64

    g = ConjunctiveGraph("BerkeleyDB")
    g.open("gsg_vocabs", create=True)

    # gsq_vocabs = "https://api.github.com/repos/geological-survey-of-queensland/vocabularies/git/trees/master"
    gsq_vocabs = "https://api.github.com/repos/geological-survey-of-queensland/vocabularies/git/trees/cd7244d39337c1f4ef164b1cf1ea1f540a7277db"
    try:
        res = urlopen(Request(gsq_vocabs, headers={"Accept": "application/json"}))
    except HTTPError as e:
        return e.code, str(e), None

    data = res.read()
    encoding = res.info().get_content_charset("utf-8")
    j = json.loads(data.decode(encoding))
    for v in j["tree"]:
        # process the element in GitHub result if it's a Turtle file
        if v["path"].endswith(".ttl"):
            # for each file, call it by URL, decode it and parse it into the graph
            r = urlopen(v["url"])
            content = json.loads(r.read().decode())["content"]
            g.parse(data=base64.b64decode(content).decode(), format="turtle")
            print(len(g))

    print("loading complete")


if __name__ == "__main__":
    example_1()
    example_2()
