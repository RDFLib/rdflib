from rdflib import Graph, RDF

def test_recursive_list_detection():
        g = Graph().parse(data="""
        @prefix : <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

        <> :value _:a .
        _:a :first "turtles"; :rest _:a .

        <> :value [ :first "turtles"; :rest _:b ] .
        _:b :first "all the way down"; :rest _:b .

        <> :value [ :first "turtles"; :rest _:c ] .
        _:c :first "all the way down"; :rest _:a .

        """, format="turtle")

        for v in g.objects(None, RDF.value):
            try:
                list(g.items(v))
            except ValueError as e:
                pass
            else:
                assert False, "Expected detection of recursive rdf:rest reference"
