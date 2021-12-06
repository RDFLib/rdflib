import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.absolute()))
from rdflib import Dataset, Graph, Namespace, Literal
import json


def test_hext_graph():
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
    testing_lines = [
        [False, '["http://example.com/s1", "http://example.com/p1", "http://example.com/o2", "", ""'],
        [False, '["http://example.com/s1", "http://example.com/p3", "Object 3", "http://www.w3.org/2001/XMLSchema#string", ""'],
        [False, '["http://example.com/s1", "http://example.com/p5", 42, "http://www.w3.org/2001/XMLSchema#integer", ""'],
        [False, '"http://www.w3.org/1999/02/22-rdf-syntax-ns#value", "thingy", "http://www.w3.org/2001/XMLSchema#string", ""'],
        [False, '["http://example.com/s1", "http://example.com/p4", "2021-12-03", "http://www.w3.org/2001/XMLSchema#date", ""'],
        [False, '["http://example.com/s1", "http://example.com/p6", "42", "http://www.w3.org/2001/XMLSchema#string", ""'],
        [False, '["http://example.com/s1", "http://example.com/p7", true, "http://www.w3.org/2001/XMLSchema#boolean", ""'],
        [False, '["http://example.com/s1", "http://example.com/p8", false, "http://www.w3.org/2001/XMLSchema#boolean", ""'],
    ]
    for line in out.splitlines():
        for test in testing_lines:
            if test[1] in line:
                test[0] = True

    assert all([x[0] for x in testing_lines])


def test_hext_dataset():
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
    testing_lines = [
        [False, '["http://example.com/s1", "http://example.com/p1", "http://example.com/o2", "", "", "http://example.com/g2"]'],
        [False, '["http://example.com/s1", "http://example.com/p3", "Object 3", "http://www.w3.org/2001/XMLSchema#string", "", "http://example.com/g1"]'],
        [False, '["http://example.com/s1", "http://example.com/p3", "Object 4 - English", "http://www.w3.org/2001/XMLSchema#string", "en", "http://example.com/g1"]'],
        [False, '["http://example.com/s1", "http://example.com/p5", 42, "http://www.w3.org/2001/XMLSchema#integer", "", "http://example.com/g1"]'],
        [False, '"http://www.w3.org/1999/02/22-rdf-syntax-ns#value", "thingy", "http://www.w3.org/2001/XMLSchema#string", "", "http://example.com/g1"]'],
        [False, '["http://example.com/s1", "http://example.com/p4", "2021-12-03", "http://www.w3.org/2001/XMLSchema#date", "", "http://example.com/g1"]']
    ]
    for line in out.splitlines():
        for test in testing_lines:
            if test[1] in line:
                test[0] = True

    assert all([x[0] for x in testing_lines])


def test_hext_json_representation():
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


def test_roundtrip():
    d = Dataset().parse(Path(__file__).parent / "test_parser_hext_01.ndjson", format="hext")
    with open(str(Path(__file__).parent / "test_parser_hext_01.ndjson")) as i:
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

