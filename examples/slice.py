"""
RDFLib Graphs (and Resources) can be "sliced" with [] syntax

This is a short-hand for iterating over triples.

Combined with SPARQL paths (see ``foafpaths.py``) - quite complex queries
can be realised.

See :meth:`rdflib.graph.Graph.__getitem__` for details
"""

from pathlib import Path

from rdflib import RDF, Graph
from rdflib.namespace import FOAF

EXAMPLES_DIR = Path(__file__).parent


if __name__ == "__main__":
    graph = Graph()
    graph.parse(f"{EXAMPLES_DIR / 'foaf.n3'}", format="n3")

    for person in graph[: RDF.type : FOAF.Person]:  # type: ignore[misc]
        friends = list(graph[person : FOAF.knows * "+" / FOAF.name])  # type: ignore[operator]
        if friends:
            print(f"{graph.value(person, FOAF.name)}'s circle of friends:")
            for name in friends:
                print(name)
