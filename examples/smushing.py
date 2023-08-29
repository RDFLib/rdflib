"""
A FOAF smushing example.

Filter a graph by normalizing all ``foaf:Persons`` into URIs based on
their ``mbox_sha1sum``.

Suppose I get two `FOAF <http://xmlns.com/foaf/0.1>`_ documents each
talking about the same person (according to ``mbox_sha1sum``) but they
each used a :class:`rdflib.term.BNode` for the subject. For this demo
I've combined those two documents into one file:

This filters a graph by changing every subject with a
``foaf:mbox_sha1sum`` into a new subject whose URI is based on the
``sha1sum``. This new graph might be easier to do some operations on.

An advantage of this approach over other methods for collapsing BNodes
is that I can incrementally process new FOAF documents as they come in
without having to access my ever-growing archive. Even if another
``65b983bb397fb71849da910996741752ace8369b`` document comes in next
year, I would still give it the same stable subject URI that merges
with my existing data.
"""

from pathlib import Path

from rdflib import Graph, Namespace
from rdflib.namespace import FOAF

STABLE = Namespace("http://example.com/person/mbox_sha1sum/")

EXAMPLES_DIR = Path(__file__).parent

if __name__ == "__main__":
    g = Graph()
    g.parse(f"{EXAMPLES_DIR / 'smushingdemo.n3'}", format="n3")

    newURI = {}  # old subject : stable uri  # noqa: N816
    for s, p, o in g.triples((None, FOAF["mbox_sha1sum"], None)):
        # For this graph, all objects are Identifiers, which is a subclass of
        # string. `n3` does allow for objects which are not Identifiers, like
        # subgraphs.
        assert isinstance(o, str)
        newURI[s] = STABLE[o]

    out = Graph()
    out.bind("foaf", FOAF)

    for s, p, o in g:
        s = newURI.get(s, s)
        o = newURI.get(o, o)  # might be linked to another person
        out.add((s, p, o))

    print(out.serialize())
