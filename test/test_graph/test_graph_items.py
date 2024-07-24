from rdflib import RDF, Graph, Namespace

EX = Namespace("http://example.org/")


def test_items():
    g = Graph().parse(
        data="""
        @prefix : <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

        <> :value (
            <http://example.org/thing1>
            <http://example.org/thing2>
        ).

        <> :value (
            <http://example.org/thing3>
        ).

        <> :value ().

        <> :value (
            <http://example.org/thing4>
            <http://example.org/thing5>
            <http://example.org/thing6>
        ).
        """,
        format="turtle",
    )

    values = {tuple(g.items(v)) for v in g.objects(None, RDF.value)}
    assert values == {
        (EX.thing1, EX.thing2),
        (EX.thing3,),
        (),
        (EX.thing4, EX.thing5, EX.thing6),
    }


def test_recursive_list_detection():
    g = Graph().parse(
        data="""
        @prefix : <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

        <> :value _:a .
        _:a :first "turtles"; :rest _:a .

        <> :value [ :first "turtles"; :rest _:b ] .
        _:b :first "all the way down"; :rest _:b .

        <> :value [ :first "turtles"; :rest _:c ] .
        _:c :first "all the way down"; :rest _:a .

        """,
        format="turtle",
    )

    for v in g.objects(None, RDF.value):
        try:
            list(g.items(v))
        except ValueError as e:  # noqa: F841
            pass
        else:
            assert False, "Expected detection of recursive rdf:rest reference"
