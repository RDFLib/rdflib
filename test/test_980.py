from rdflib import Graph


def test_980():
    """
    The problem that this test ensures rdflib solves is that, previous to PR #1108, the
    parsing of two triples with the same n-triples Blank Nodes IDs, here _:0, would
    result in triples with the same rdflib internal BN IDs, e.g.
    rdflib.term.BNode('Ne3fd8261b37741fca22d502483d88964'), see the Issue #980. They
    should have different IDs.
    """
    graph1 = """
    _:0 <http://purl.obolibrary.org/obo/RO_0002350> <http://www.gbif.org/species/0000001> .
    """
    graph2 = """
    _:0 <http://purl.obolibrary.org/obo/RO_0002350> <http://www.gbif.org/species/0000002> .
    """

    g = Graph()
    g.parse(data=graph1, format="nt")
    g.parse(data=graph2, format="nt")

    subs = 0
    for s in g.subjects(None, None):
        subs += 1

    # we must see two different BN subjects
    assert subs == 2
