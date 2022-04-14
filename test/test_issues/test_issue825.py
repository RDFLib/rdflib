import os
from rdflib import Dataset, URIRef
from rdflib.compare import to_isomorphic
from test.data import *

# from test.data import (
#     TEST_DIR,
#     CONSISTENT_DATA_DIR,
#     alice_uri,
#     bob_uri,
#     michel,
#     tarek,
#     bob,
#     likes,
#     hates,
#     pizza,
#     cheese,
#     context0,
#     context1,
#     context2
# )

example4_root = os.path.join(
    CONSISTENT_DATA_DIR, "example-4-default-plus-two-named-graphs-and-one-bnode."
)


def test_issue825a():
    ds = Dataset()

    g1 = ds.graph(context1)
    g1.add((tarek, likes, pizza))
    ig1 = to_isomorphic(g1)
    assert (
        repr(ig1)
        == "<Graph identifier=urn:example:context-1 (<class 'rdflib.compare.IsomorphicGraph'>)>"
    )

    stats = {}
    digest = ig1.graph_digest(stats)
    assert (
        digest
        == 57424069107518051668193532818798030477572203077802475604661812692168366111669
    )

    hexdigest = hex(ig1.graph_digest(stats))
    assert (
        hexdigest
        == "0x7ef4df0f4fa14d32dd05fe0017300ff55ce7134dbc17ee64330ec84ce8e83bb5"
    )

    assert (
        stats["graph_digest"]
        == '7ef4df0f4fa14d32dd05fe0017300ff55ce7134dbc17ee64330ec84ce8e83bb5'
    )

    g2 = ds.graph(context2)

    g2 += g1

    ig2 = to_isomorphic(g2)
    assert (
        repr(ig2)
        == "<Graph identifier=urn:example:context-2 (<class 'rdflib.compare.IsomorphicGraph'>)>"
    )

    stats = {}
    digest = ig2.graph_digest(stats)
    assert (
        digest
        == 57424069107518051668193532818798030477572203077802475604661812692168366111669
    )

    hexdigest = hex(ig2.graph_digest(stats))
    assert (
        hexdigest
        == "0x7ef4df0f4fa14d32dd05fe0017300ff55ce7134dbc17ee64330ec84ce8e83bb5"
    )

    assert (
        stats["graph_digest"]
        == '7ef4df0f4fa14d32dd05fe0017300ff55ce7134dbc17ee64330ec84ce8e83bb5'
    )


def test_issue825b():
    ds = Dataset()

    g1 = ds.graph(context1)
    g1.parse(location=example4_root + "trig", format="trig")
    ig1 = to_isomorphic(g1)
    assert (
        repr(ig1)
        == "<Graph identifier=urn:example:context-1 (<class 'rdflib.compare.IsomorphicGraph'>)>"
    )

    stats = {}
    digest = ig1.graph_digest(stats)
    assert (
        digest
        == 119291551772766548300693480928595134234557834059757368194849658322121506282051
    )

    hexdigest = hex(ig1.graph_digest(stats))
    assert (
        hexdigest
        == "0x107bca0279b1dff512f0782ba5a6fb0c1712a40511c26d373b377024e580dda43"
    )
    assert (
        stats["graph_digest"]
        == '107bca0279b1dff512f0782ba5a6fb0c1712a40511c26d373b377024e580dda43'
    )

    g2 = ds.graph(context2)
    g2.parse(location=example4_root + "trig", format="trig")
    ig2 = to_isomorphic(g2)
    assert (
        repr(ig2)
        == "<Graph identifier=urn:example:context-2 (<class 'rdflib.compare.IsomorphicGraph'>)>"
    )

    stats = {}
    digest = ig2.graph_digest(stats)
    assert (
        digest
        == 119291551772766548300693480928595134234557834059757368194849658322121506282051
    )

    hexdigest = hex(ig2.graph_digest(stats))
    assert (
        hexdigest
        == "0x107bca0279b1dff512f0782ba5a6fb0c1712a40511c26d373b377024e580dda43"
    )
    assert (
        stats["graph_digest"]
        == '107bca0279b1dff512f0782ba5a6fb0c1712a40511c26d373b377024e580dda43'
    )


def test_issue825c():
    ds = Dataset()

    g1 = ds.graph(context1)
    g1.parse(location=example4_root + "trig", format="trig")
    ig1 = to_isomorphic(g1)
    assert (
        repr(ig1)
        == "<Graph identifier=urn:example:context-1 (<class 'rdflib.compare.IsomorphicGraph'>)>"
    )

    stats = {}
    digest = ig1.graph_digest(stats)
    assert (
        digest
        == 119291551772766548300693480928595134234557834059757368194849658322121506282051
    )

    from rdflib.compare import _TripleCanonicalizer

    from hashlib import sha3_256

    ig1 = _TripleCanonicalizer(g1, hashfunc=sha3_256)
    stats = {}
    digest = ig1.to_hash(stats)
    assert (
        digest
        == 171932016137345107086720484544930425303085457504153027218032482882243450367696
    )
    assert (
        hex(digest)
        == "0x17c1e1295913a3826af1f87bc9c8eb11e895d17617349534b28a67d1ab0f3eed0"
    )
    assert (
        stats["graph_digest"]
        == "17c1e1295913a3826af1f87bc9c8eb11e895d17617349534b28a67d1ab0f3eed0"
    )

    from hashlib import sha3_512

    ig1 = _TripleCanonicalizer(g1, hashfunc=sha3_512)
    stats = {}
    digest = ig1.to_hash(stats)
    assert (
        digest
        == 22127388725983745963051291753605134752106653268186335151133868475495740432838955790588054135603625566434318944678253820374159855740432000547842915698478549
    )
    assert (
        hex(digest)
        == "0x1a67c6c5169f8a8434990b8563baf014d79b4a62728ea6fc362c9dc2d080a0ccfd2d67724bce6ac0772f91841d7bf2a976dd8157cdac5e7ab9ddcd54c58ec0dd5"
    )
    assert (
        stats["graph_digest"]
        == "1a67c6c5169f8a8434990b8563baf014d79b4a62728ea6fc362c9dc2d080a0ccfd2d67724bce6ac0772f91841d7bf2a976dd8157cdac5e7ab9ddcd54c58ec0dd5"
    )
