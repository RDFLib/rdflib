from rdflib import Graph


def test_issue527_incomplete_serialization_to_n3_when_using_embedded_formulae():

    input_n3 = """
@prefix : <http://www.example.org/n3/rules#> .
@prefix e: <http://eulersharp.sourceforge.net/2003/03swap/log-rules#> .
@prefix log: <http://www.w3.org/2000/10/swap/log#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

{
    ?SCOPE e:findall (?rbc { ?a :getRBConfidenceScore ?rbc } ?list).
    ?list e:max ?maxrbc.
    ?u :believedToDo ?a0;
       :residentIn ?h.
    ?a :getRBConfidenceScore ?maxrbc;
       log:notEqualTo ?a0.
} => {
    ?u :does ?a.
}.
"""

    graph = Graph()
    graph.parse(data=input_n3, format="n3")
    # print(f"\n{graph.serialize(format='n3')}")

    """
    @prefix : <http://www.example.org/n3/rules#> .
    @prefix e: <http://eulersharp.sourceforge.net/2003/03swap/log-rules#> .
    @prefix log: <http://www.w3.org/2000/10/swap/log#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

    {
        ?SCOPE e:findall ( ?rbc {
                    ?a :getRBConfidenceScore ?rbc .

                } ?list ) .

        ?u :believedToDo ?a0 ;
            :residentIn ?h .

        ?list e:max ?maxrbc .

    } => {
            ?u :does ?a .

        } .

    """

    input = """
?Varname ?f { ?b ?g ?r }.
?b ?n ?c.
"""
    graph = Graph()
    graph.parse(data=input, format="n3")
    # print(f"{repr(graph.serialize(format='n3'))}")

    """
    ?Varname ?f {
            ?b ?g ?r .

        } .
    """

    assert repr(graph.serialize(format="n3")) == repr(
        "\n?Varname ?f {\n        ?b ?g ?r .\n\n    } .\n\n"
    )

    input = """
?varname ?f { ?b ?g ?r }.
?b ?n ?c.
"""
    graph = Graph()
    graph.parse(data=input, format="n3")
    # print(f"{repr(graph.serialize(format='n3'))}")

    """
    ?b ?n ?c .

    ?varname ?f {
            ?b ?g ?r .

        } .
    """

    assert repr(graph.serialize(format="n3")) == repr(
        "\n?b ?n ?c .\n\n?varname ?f {\n        ?b ?g ?r .\n\n    } .\n\n"
    )
