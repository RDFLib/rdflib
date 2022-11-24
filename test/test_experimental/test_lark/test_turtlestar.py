from test.data import context0

import pytest

import rdflib
from rdflib.compare import isomorphic

rdflib.plugin.register(
    "larkturtlestar",
    rdflib.parser.Parser,
    "rdflib.experimental.plugins.parsers.larkturtlestar",
    "LarkTurtleStarParser",
)

rdflib.plugin.register(
    "larkntstar",
    rdflib.parser.Parser,
    "rdflib.experimental.plugins.parsers.larkntriplesstar",
    "LarkNTriplesStarParser",
)

rdflib.plugin.register(
    "rdna",
    rdflib.serializer.Serializer,
    "rdflib.plugins.serializers.rdna",
    "RDNASerializer",
)

testdata = """PREFIX : <http://example/>

:s :p :o .
[ :q <<:s :p :o>> ] :b :c ."""

testresult = """<http://example/s> <http://example/p> <http://example/o> .
_:g1220 <http://example/q> <<<http://example/s> <http://example/p> <http://example/o>>> .
_:g1220 <http://example/b> <http://example/c> .
"""


def test_larkturtlestar():
    ds1 = rdflib.ConjunctiveGraph()
    ds1.parse(data=testdata, format="larkturtlestar", preserve_bnode_ids=True)

    ds1ser = ds1.serialize(format="rdna")

    assert ds1ser == (
        "<http://example/s> <http://example/p> <http://example/o> .\n"
        "_:c14n0 <http://example/b> <http://example/c> .\n"
        "_:c14n0 <http://www.w3.org/1999/02/22-rdf-syntax-ns#object> <http://example/o> .\n"
        "_:c14n0 <http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate> <http://example/p> .\n"
        "_:c14n0 <http://www.w3.org/1999/02/22-rdf-syntax-ns#subject> <http://example/s> .\n"
        "_:c14n0 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement> .\n"
    )

    d1res = [
        (
            rdflib.term.URIRef("http://example/s"),
            rdflib.term.URIRef("http://example/p"),
            rdflib.term.URIRef("http://example/o"),
        ),
        (
            rdflib.term.BNode("_:c14n0"),
            rdflib.term.URIRef("http://example/b"),
            rdflib.term.URIRef("http://example/c"),
        ),
        (
            rdflib.term.BNode("_:c14n1"),
            rdflib.term.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate"),
            rdflib.term.URIRef("http://example/p"),
        ),
        (
            rdflib.term.BNode("_:c14n1"),
            rdflib.term.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#subject"),
            rdflib.term.URIRef("http://example/s"),
        ),
        (
            rdflib.term.BNode("_:c14n1"),
            rdflib.term.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#object"),
            rdflib.term.URIRef("http://example/o"),
        ),
        (
            rdflib.term.BNode("_:c14n1"),
            rdflib.term.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            rdflib.term.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement"),
        ),
        (
            rdflib.term.BNode("_:c14n0"),
            rdflib.term.URIRef("http://example/q"),
            rdflib.term.BNode("_:c14n1"),
        ),
    ]


testdata1 = """PREFIX : <http://example/>

<<:s :p :o>> :q :z .
"""

testresult1 = """<< <http://example/s> <http://example/p> <http://example/o> >> <http://example/q> <http://example/z> ."""


def test_turtlestar_eval_01():
    g1 = rdflib.Graph(identifier=context0)
    g1.parse(data=testdata1, format="larkturtlestar", preserve_bnode_ids=True)

    assert len(g1) == 1

    assert list(g1) == [
        (
            rdflib.term.RDFStarTriple("025cf368e1e95366cbb063dfbb3b41af"),
            rdflib.term.URIRef("http://example/q"),
            rdflib.term.URIRef("http://example/z"),
        )
    ]

    rt = list(g1)[0][0]

    assert isinstance(rt, rdflib.term.RDFStarTriple)

    assert rt.subject().n3() == "<http://example/s>"
    assert rt.predicate().n3() == "<http://example/p>"
    assert rt.object().n3() == "<http://example/o>"

    g2 = rdflib.Graph(identifier=context0)
    g2.parse(data=testresult1, format="larkntstar")

    assert len(g2) == 1

    assert isomorphic(g1, g2)

    assert g1 == g2


testdata2 = """PREFIX : <http://example/>

:a :q <<:s :p :o>> .
"""

testresult2 = """<http://example/a> <http://example/q> << <http://example/s> <http://example/p> <http://example/o> >> ."""


def test_turtlestar_eval_02():
    g1 = rdflib.Graph(identifier=context0)
    g1.parse(data=testdata2, format="larkturtlestar", preserve_bnode_ids=True)

    assert len(g1) == 1

    assert list(g1) == [
        (
            rdflib.term.URIRef("http://example/a"),
            rdflib.term.URIRef("http://example/q"),
            rdflib.term.RDFStarTriple("025cf368e1e95366cbb063dfbb3b41af"),
        )
    ]

    rt = list(g1)[0][2]

    assert isinstance(rt, rdflib.term.RDFStarTriple)

    assert rt.subject().n3() == "<http://example/s>"
    assert rt.predicate().n3() == "<http://example/p>"
    assert rt.object().n3() == "<http://example/o>"

    g2 = rdflib.Graph(identifier=context0)
    g2.parse(data=testresult2, format="larkntstar")

    assert len(g2) == 1

    assert isomorphic(g1, g2)

    assert g1 == g2


testdata3 = """PREFIX : <http://example/>

:alice :dept :tech {| :asserted :bob |} .
"""

testresult3 = """<http://example/alice> <http://example/dept> <http://example/tech> .
<< <http://example/alice> <http://example/dept> <http://example/tech> >> <http://example/asserted> <http://example/bob> ."""


def test_turtlestar_eval_03():
    g1 = rdflib.Graph(identifier=context0)
    g1.parse(data=testdata3, format="larkturtlestar", preserve_bnode_ids=True)

    assert len(g1) == 2

    lg = sorted(list(g1))
    assert lg == [
        (
            rdflib.term.RDFStarTriple("31e9d4ecea4ec93d8b656afc0adc080f"),
            rdflib.term.URIRef("http://example/asserted"),
            rdflib.term.URIRef("http://example/bob"),
        ),
        (
            rdflib.term.URIRef("http://example/alice"),
            rdflib.term.URIRef("http://example/dept"),
            rdflib.term.URIRef("http://example/tech"),
        ),
    ]

    rt = lg[0][0]
    assert isinstance(rt, rdflib.term.RDFStarTriple)

    assert rt.subject() == rdflib.term.URIRef("http://example/alice")
    assert rt.predicate().n3() == "<http://example/dept>"
    assert rt.object().n3() == "<http://example/tech>"

    g2 = rdflib.Graph(identifier=context0)
    g2.parse(data=testresult3, format="larkntstar")

    assert len(g2) == 2

    assert isomorphic(g1, g2)


testdata4 = """PREFIX : <http://example/>
:a :name "Alice" {| :statedBy :bob ; :recorded "2021-07-07"^^xsd:date |} .
"""


testdata4a = """PREFIX : <http://example/>
<< :a :name "Alice" >> :statedBy :bob .
<< :a :name "Alice" >> :recorded "2021-07-07"^^xsd:date .
:a :name "Alice" .
"""

testresult4 = """
<< <http://example/a> <http://example/name> "Alice" >> <http://example/statedBy> <http://example/bob> .
<< <http://example/a> <http://example/name> "Alice" >> <http://example/recorded> "2021-07-07"^^<http://www.w3.org/2001/XMLSchema#date> .
<http://example/a> <http://example/name> "Alice" .
"""


def test_turtlestar_eval_04():
    g1 = rdflib.Graph(identifier=context0)
    g1.parse(data=testdata4, format="larkturtlestar", preserve_bnode_ids=True)

    assert len(g1) == 3

    lg = sorted(list(g1))

    assert lg == [
        (
            rdflib.term.RDFStarTriple("4c8191e1f49bc3349602caaf14e1a616"),
            rdflib.term.URIRef("http://example/recorded"),
            rdflib.term.Literal(
                "2021-07-07",
                datatype=rdflib.term.URIRef("http://www.w3.org/2001/XMLSchema#date"),
            ),
        ),
        (
            rdflib.term.RDFStarTriple("4c8191e1f49bc3349602caaf14e1a616"),
            rdflib.term.URIRef("http://example/statedBy"),
            rdflib.term.URIRef("http://example/bob"),
        ),
        (
            rdflib.term.URIRef("http://example/a"),
            rdflib.term.URIRef("http://example/name"),
            rdflib.term.Literal("Alice"),
        ),
    ]

    rt = lg[0][0]
    assert isinstance(rt, rdflib.term.RDFStarTriple)

    assert rt.subject() == rdflib.term.URIRef("http://example/a")
    assert rt.predicate().n3() == "<http://example/name>"
    assert rt.object().n3() == '"Alice"'
    assert isinstance(rt.object(), rdflib.term.Literal)
    assert rt.object() == rdflib.term.Literal("Alice")

    g2 = rdflib.Graph(identifier=context0)
    g2.parse(data=testresult4, format="larkntstar")

    assert len(g2) == 3

    assert isomorphic(g1, g2)


testdata5 = """PREFIX : <http://example/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

:s :p :o {| :source [ :graph <http://host1/> ;
                      :date "2020-01-20"^^xsd:date
                    ] ;
            :source [ :graph <http://host2/> ;
                      :date "2020-12-31"^^xsd:date
                    ]
          |} .
"""

testresult5 = """<http://example/s> <http://example/p> <http://example/o> .
_:b1 <http://example/graph> <http://host1/> .
_:b1 <http://example/date> "2020-01-20"^^<http://www.w3.org/2001/XMLSchema#date> .
<< <http://example/s> <http://example/p> <http://example/o> >> <http://example/source> _:b1 .
_:b2 <http://example/graph> <http://host2/> .
_:b2 <http://example/date> "2020-12-31"^^<http://www.w3.org/2001/XMLSchema#date> .
<< <http://example/s> <http://example/p> <http://example/o> >> <http://example/source> _:b2 .
"""


def test_turtlestar_eval_05():
    g1 = rdflib.Graph(identifier=context0)
    g1.parse(
        data=testdata5,
        format="larkturtlestar",
        preserve_bnode_ids=True,
        bidprefix="c14n",
    )

    assert len(g1) == 7

    lg = sorted(list(g1))

    assert lg == [
        (
            rdflib.term.RDFStarTriple("025cf368e1e95366cbb063dfbb3b41af"),
            rdflib.term.URIRef("http://example/source"),
            rdflib.term.BNode("c14n1"),
        ),
        (
            rdflib.term.RDFStarTriple("025cf368e1e95366cbb063dfbb3b41af"),
            rdflib.term.URIRef("http://example/source"),
            rdflib.term.BNode("c14n2"),
        ),
        (
            rdflib.term.BNode("c14n1"),
            rdflib.term.URIRef("http://example/date"),
            rdflib.term.Literal(
                "2020-01-20",
                datatype=rdflib.term.URIRef("http://www.w3.org/2001/XMLSchema#date"),
            ),
        ),
        (
            rdflib.term.BNode("c14n1"),
            rdflib.term.URIRef("http://example/graph"),
            rdflib.term.URIRef("http://host1/"),
        ),
        (
            rdflib.term.BNode("c14n2"),
            rdflib.term.URIRef("http://example/date"),
            rdflib.term.Literal(
                "2020-12-31",
                datatype=rdflib.term.URIRef("http://www.w3.org/2001/XMLSchema#date"),
            ),
        ),
        (
            rdflib.term.BNode("c14n2"),
            rdflib.term.URIRef("http://example/graph"),
            rdflib.term.URIRef("http://host2/"),
        ),
        (
            rdflib.term.URIRef("http://example/s"),
            rdflib.term.URIRef("http://example/p"),
            rdflib.term.URIRef("http://example/o"),
        ),
    ]

    g2 = rdflib.Graph(identifier=context0)
    g2.parse(data=testresult5, format="larkntstar", bidprefix="c14n")

    assert len(g2) == 7

    assert isomorphic(g1, g2)

    # from rdflib.extras.visualizegraph import visualize_graph

    # visualize_graph(g1, "/tmp/gviz", compact=True, render_format="svg", view=True)


testdata6 = """PREFIX : <http://example/>

<<:s1 :p1 :o1>> :p :o {| :r :z |} .
"""

testresult6 = """<<<http://example/s1> <http://example/p1> <http://example/o1>>> <http://example/p> <http://example/o> .
<<<<<http://example/s1> <http://example/p1> <http://example/o1>>> <http://example/p> <http://example/o>>> <http://example/r> <http://example/z> .
"""


@pytest.mark.xfail(reason="Annotations of quoted statements not yet implemented")
def test_turtlestar_eval_06():
    g1 = rdflib.Graph(identifier=context0)
    g1.parse(
        data=testdata6,
        format="larkturtlestar",
        preserve_bnode_ids=True,
        bidprefix="c14n",
    )

    # assert len(g1) == 0

    # lg = sorted(list(g1))

    # assert lg == []


testdata7 = """PREFIX : <http://example/>

:s :p :o {| :a :b {| :a2 :b2 |} |}.
"""

testresult7 = """<http://example/s> <http://example/p> <http://example/o> .
<< <http://example/s> <http://example/p> <http://example/o> >> <http://example/a> <http://example/b> .
<< << <http://example/s> <http://example/p> <http://example/o> >> <http://example/a> <http://example/b> >> <http://example/a2> <http://example/b2> .
"""


@pytest.mark.xfail(reason="Nested annotations not yet implemented")
def test_turtlestar_eval_07():
    g1 = rdflib.Graph(identifier=context0)
    g1.parse(
        data=testdata7,
        format="larkturtlestar",
        preserve_bnode_ids=True,
        bidprefix="c14n",
    )
