import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.absolute()))
import json

from rdflib import ConjunctiveGraph, Dataset, Graph


def test_hext_graph():
    """Tests single-grant (not context-aware) data"""
    g = Graph()
    turtle_data = """
            PREFIX ex: <http://example.com/>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            ex:s1
                ex:p1 ex:o1 , ex:o2 ;
                ex:p2 [
                    a owl:Thing ;
                    rdf:value "thingy" ;
                ] ;
                ex:p3 "Object 3" , "Object 4 - English"@en ;
                ex:p4 "2021-12-03"^^xsd:date ;
                ex:p5 42 ;
                ex:p6 "42" ;
                ex:p7 true ;
                ex:p8 "false"^^xsd:boolean ;
            .
            """

    g.parse(data=turtle_data, format="turtle")
    out = g.serialize(format="hext")
    # note: can't test for BNs in result as they will be different every time
    testing_lines = [
        [
            False,
            '["http://example.com/s1", "http://example.com/p1", "http://example.com/o2", "globalId", "", ""]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p3", "Object 3", "http://www.w3.org/2001/XMLSchema#string", "", ""]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p3", "Object 4 - English", "http://www.w3.org/1999/02/22-rdf-syntax-ns#langString", "en", ""]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p1", "http://example.com/o1", "globalId", "", ""]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p4", "2021-12-03", "http://www.w3.org/2001/XMLSchema#date", "", ""]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p6", "42", "http://www.w3.org/2001/XMLSchema#string", "", ""]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p7", "true", "http://www.w3.org/2001/XMLSchema#boolean", "", ""]',
        ],
        [
            False,
            '"http://www.w3.org/1999/02/22-rdf-syntax-ns#value", "thingy", "http://www.w3.org/2001/XMLSchema#string", "", ""]',
        ],
        [False, '["http://example.com/s1", "http://example.com/p2"'],
        [
            False,
            '["http://example.com/s1", "http://example.com/p5", "42", "http://www.w3.org/2001/XMLSchema#integer", "", ""]',
        ],
        [
            False,
            '"http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "http://www.w3.org/2002/07/owl#Thing", "globalId", "", ""]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p8", "false", "http://www.w3.org/2001/XMLSchema#boolean", "", ""]',
        ],
    ]
    for line in out.splitlines():
        for test in testing_lines:
            if test[1] in line:
                test[0] = True

    assert all([x[0] for x in testing_lines])


def test_hext_cg():
    """Tests ConjunctiveGraph data"""
    d = ConjunctiveGraph()
    trig_data = """
            PREFIX ex: <http://example.com/>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            ex:g1 {
                ex:s1
                    ex:p1 ex:o1 , ex:o2 ;
                    ex:p2 [
                        a owl:Thing ;
                        rdf:value "thingy" ;
                    ] ;
                    ex:p3 "Object 3" , "Object 4 - English"@en ;
                    ex:p4 "2021-12-03"^^xsd:date ;
                    ex:p5 42 ;
                    ex:p6 "42" ;
                .
            }

            ex:g2 {
                ex:s1
                    ex:p1 ex:o1 , ex:o2 ;
                .
                ex:s11 ex:p11 ex:o11 , ex:o12 .
            }

            # default graph triples
            ex:s1 ex:p1 ex:o1 , ex:o2 .
            ex:s21 ex:p21 ex:o21 , ex:o22 .

            # other default graph triples
            {
                ex:s1 ex:p1 ex:o1 , ex:o2 .
            }
           """
    d.parse(data=trig_data, format="trig", publicID=d.default_context.identifier)
    out = d.serialize(format="hext")
    # note: cant' test for BNs in result as they will be different ever time
    testing_lines = [
        [
            False,
            '["http://example.com/s21", "http://example.com/p21", "http://example.com/o21", "globalId", "", ""]',
        ],
        [
            False,
            '["http://example.com/s21", "http://example.com/p21", "http://example.com/o22", "globalId", "", ""]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p1", "http://example.com/o2", "globalId", "", ""]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p1", "http://example.com/o1", "globalId", "", ""]',
        ],
        [
            False,
            '["http://example.com/s11", "http://example.com/p11", "http://example.com/o12", "globalId", "", "http://example.com/g2"]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p1", "http://example.com/o2", "globalId", "", "http://example.com/g2"]',
        ],
        [
            False,
            '["http://example.com/s11", "http://example.com/p11", "http://example.com/o11", "globalId", "", "http://example.com/g2"]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p1", "http://example.com/o1", "globalId", "", "http://example.com/g2"]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p1", "http://example.com/o2", "globalId", "", "http://example.com/g1"]',
        ],
        [False, '["http://example.com/s1", "http://example.com/p2"'],
        [
            False,
            '"http://www.w3.org/1999/02/22-rdf-syntax-ns#value", "thingy", "http://www.w3.org/2001/XMLSchema#string", "", "http://example.com/g1"]',
        ],
        [
            False,
            '"http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "http://www.w3.org/2002/07/owl#Thing", "globalId", "", "http://example.com/g1"]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p3", "Object 4 - English", "http://www.w3.org/1999/02/22-rdf-syntax-ns#langString", "en", "http://example.com/g1"]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p6", "42", "http://www.w3.org/2001/XMLSchema#string", "", "http://example.com/g1"]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p4", "2021-12-03", "http://www.w3.org/2001/XMLSchema#date", "", "http://example.com/g1"]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p1", "http://example.com/o1", "globalId", "", "http://example.com/g1"]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p5", "42", "http://www.w3.org/2001/XMLSchema#integer", "", "http://example.com/g1"]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p3", "Object 3", "http://www.w3.org/2001/XMLSchema#string", "", "http://example.com/g1"]',
        ],
    ]
    for line in out.splitlines():
        for test in testing_lines:
            if test[1] in line:
                test[0] = True

    assert all([x[0] for x in testing_lines])


def test_hext_dataset():
    """Tests context-aware (multigraph) data"""
    d = Dataset()
    trig_data = """
            PREFIX ex: <http://example.com/>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            ex:g1 {
                ex:s1
                    ex:p1 ex:o1 , ex:o2 ;
                    ex:p2 [
                        a owl:Thing ;
                        rdf:value "thingy" ;
                    ] ;
                    ex:p3 "Object 3" , "Object 4 - English"@en ;
                    ex:p4 "2021-12-03"^^xsd:date ;
                    ex:p5 42 ;
                    ex:p6 "42" ;
                .
            }

            ex:g2 {
                ex:s1
                    ex:p1 ex:o1 , ex:o2 ;
                .
                ex:s11 ex:p11 ex:o11 , ex:o12 .
            }

            # default graph triples
            ex:s1 ex:p1 ex:o1 , ex:o2 .
            ex:s21 ex:p21 ex:o21 , ex:o22 .
           """
    d.parse(data=trig_data, format="trig", publicID=d.default_context.identifier)
    out = d.serialize(format="hext")
    # note: cant' test for BNs in result as they will be different ever time
    testing_lines = [
        [
            False,
            '["http://example.com/s21", "http://example.com/p21", "http://example.com/o21", "globalId", "", ""]',
        ],
        [
            False,
            '["http://example.com/s21", "http://example.com/p21", "http://example.com/o22", "globalId", "", ""]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p1", "http://example.com/o2", "globalId", "", ""]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p1", "http://example.com/o1", "globalId", "", ""]',
        ],
        [
            False,
            '["http://example.com/s11", "http://example.com/p11", "http://example.com/o12", "globalId", "", "http://example.com/g2"]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p1", "http://example.com/o2", "globalId", "", "http://example.com/g2"]',
        ],
        [
            False,
            '["http://example.com/s11", "http://example.com/p11", "http://example.com/o11", "globalId", "", "http://example.com/g2"]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p1", "http://example.com/o1", "globalId", "", "http://example.com/g2"]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p1", "http://example.com/o2", "globalId", "", "http://example.com/g1"]',
        ],
        [False, '["http://example.com/s1", "http://example.com/p2"'],
        [
            False,
            '"http://www.w3.org/1999/02/22-rdf-syntax-ns#value", "thingy", "http://www.w3.org/2001/XMLSchema#string", "", "http://example.com/g1"]',
        ],
        [
            False,
            '"http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "http://www.w3.org/2002/07/owl#Thing", "globalId", "", "http://example.com/g1"]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p3", "Object 4 - English", "http://www.w3.org/1999/02/22-rdf-syntax-ns#langString", "en", "http://example.com/g1"]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p6", "42", "http://www.w3.org/2001/XMLSchema#string", "", "http://example.com/g1"]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p4", "2021-12-03", "http://www.w3.org/2001/XMLSchema#date", "", "http://example.com/g1"]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p1", "http://example.com/o1", "globalId", "", "http://example.com/g1"]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p5", "42", "http://www.w3.org/2001/XMLSchema#integer", "", "http://example.com/g1"]',
        ],
        [
            False,
            '["http://example.com/s1", "http://example.com/p3", "Object 3", "http://www.w3.org/2001/XMLSchema#string", "", "http://example.com/g1"]',
        ],
    ]
    for line in out.splitlines():
        for test in testing_lines:
            if test[1] in line:
                test[0] = True

    assert all([x[0] for x in testing_lines])


def test_hext_json_representation():
    """Tests to see if every link in the ND-JSON Hextuple result is, in fact, JSON"""
    d = Dataset()
    trig_data = """
            PREFIX ex: <http://example.com/>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            ex:g1 {
                ex:s1
                    ex:p1 ex:o1 , ex:o2 ;
                    ex:p2 [
                        a owl:Thing ;
                        rdf:value "thingy" ;
                    ] ;
                    ex:p3 "Object 3" , "Object 4 - English"@en ;
                    ex:p4 "2021-12-03"^^xsd:date ;
                    ex:p5 42 ;
                    ex:p6 "42" ;
                .
            }

            ex:g2 {
                ex:s1
                    ex:p1 ex:o1 , ex:o2 ;
                .
                ex:s11 ex:p11 ex:o11 , ex:o12 .
            }

            # default graph triples
            ex:s1 ex:p1 ex:o1 , ex:o2 .
            ex:s21 ex:p21 ex:o21 , ex:o22 .
           """
    d.parse(data=trig_data, format="trig")
    out = d.serialize(format="hext")
    for line in out.splitlines():
        j = json.loads(line)
        assert isinstance(j, list)


def test_hext_dataset_linecount():
    d = Dataset()
    assert len(d) == 0
    d.parse(
        Path(__file__).parent.parent / "data/test_parser_hext_multigraph.ndjson",
        format="hext",
        publicID=d.default_context.identifier,
    )
    total_triples = 0
    # count all the triples in the Dataset
    for context in d.contexts():
        for triple in context.triples((None, None, None)):
            total_triples += 1
    assert total_triples == 18

    # count the number of serialized Hextuples, should be 22, as per the original file
    lc = len(d.serialize(format="hext").splitlines())
    assert lc == 22


def test_roundtrip():
    d = Dataset()
    d.parse(
        Path(__file__).parent.parent / "data/test_parser_hext_multigraph.ndjson",
        format="hext",
        publicID=d.default_context.identifier,
    )
    d.default_union = True
    with open(
        str(Path(__file__).parent.parent / "data/test_parser_hext_multigraph.ndjson")
    ) as i:
        ordered_input = "".join(sorted(i.readlines())).strip()

    ordered_output = "\n".join(sorted(d.serialize(format="hext").split("\n"))).strip()

    assert ordered_output == ordered_input


# def _make_large_graph():
#     import random
#
#     EX = Namespace("http://example.com/")
#     g = Graph()
#
#     for i in range(1000):
#         s = EX["s" + str(random.randint(1, 10000)).zfill(5)]
#         p = EX["p" + str(random.randint(1, 10000)).zfill(5)]
#         o_r = random.randint(1, 10000)
#         if o_r > 5000:
#             o = EX["p" + str(o_r).zfill(5)]
#         else:
#             o = Literal("p" + str(o_r).zfill(5))
#         g.add((s, p, o))
#     return g
#
#
# def test_hext_scaling():
#     g = _make_large_graph()
#     g.serialize(destination="large.ndjson", format="hext")
#
#
if __name__ == "__main__":
    test_roundtrip()
