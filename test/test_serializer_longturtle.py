# tests for the longturtle Serializer

from rdflib import Graph


def test_longturtle():
    g = Graph()

    g.parse(
        data="""
        @prefix ex: <https://example.org/> .
        @prefix ex2: <https://example2.org/> .
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        <https://something.com/a>
            a ex:Thing , ex:OtherThing ;
            ex:name "Thing", "Other Thing"@en , "もの"@ja , "rzecz"@pl ;
            ex:singleValueProp "propval" ;
            ex:multiValueProp "propval 1" ;
            ex:multiValueProp "propval 2" ;
            ex:multiValueProp "propval 3" ;
            ex:multiValueProp "propval 4" ;
            ex:bnObj [
                ex:singleValueProp "propval" ;
                ex:multiValueProp "propval 1" ;
                ex:multiValueProp "propval 2" ;
                ex:bnObj [
                    ex:singleValueProp "propval" ;
                    ex:multiValueProp "propval 1" ;
                    ex:multiValueProp "propval 2" ;
                    ex:bnObj [
                        ex:singleValueProp "propval" ;
                        ex:multiValueProp "propval 1" ;
                        ex:multiValueProp "propval 2" ;
                    ] ,
                    [
                        ex:singleValueProp "propval" ;
                        ex:multiValueProp "propval 1" ;
                        ex:multiValueProp "propval 2" ;
                    ] ,
                    [
                        ex:singleValueProp "propval" ;
                        ex:multiValueProp "propval 1" ;
                        ex:multiValueProp "propval 2" ;
                    ] ;
                ] ;
            ] ;
        .

        ex:b
            rdf:type ex:Thing ;
            ex:name "B" ;
            ex2:name "B" .

        ex:c
            rdf:type ex:Thing ;
            ex:name "C" ;
            ex:lst2 (
                ex:one
                ex:two
                ex:three
            ) ;
            ex:lst (
                ex:one
                ex:two
                ex:three
            ) ,
            (
                ex:four
                ex:fize
                ex:six
            ) ;
            ex:bnObj [
                ex:lst (
                    ex:one
                    ex:two
                    ex:three
                ) ,
                (
                    ex:four
                    ex:fize
                    ex:six
                ) ;
            ] .
        """,
        format="turtle",
    )
    s = g.serialize(format="longturtle")
    lines = s.split("\n")

    assert "ex:b" in lines
    assert "    a ex:Thing ;" in lines
    assert (
        """    ex2:name "B" ;
."""
        in s
    )
    assert (
        """                (
                    ex:one
                    ex:two
                    ex:three
                ) ,"""
        in s
    )
    assert '    ex:singleValueProp "propval" ;' in lines

    expected_s = """PREFIX ex: <https://example.org/>
PREFIX ex2: <https://example2.org/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

ex:b
    a ex:Thing ;
    ex:name "B" ;
    ex2:name "B" ;
.

ex:c
    a ex:Thing ;
    ex:bnObj [
            ex:lst
                (
                    ex:one
                    ex:two
                    ex:three
                ) ,
                (
                    ex:four
                    ex:fize
                    ex:six
                )
        ] ;
    ex:lst
        (
            ex:four
            ex:fize
            ex:six
        ) ,
        (
            ex:one
            ex:two
            ex:three
        ) ;
    ex:lst2 (
            ex:one
            ex:two
            ex:three
        ) ;
    ex:name "C" ;
.

<https://something.com/a>
    a
        ex:OtherThing ,
        ex:Thing ;
    ex:bnObj [
            ex:bnObj [
                    ex:bnObj
                        [
                            ex:multiValueProp
                                "propval 1" ,
                                "propval 2" ;
                            ex:singleValueProp "propval"
                        ] ,
                        [
                            ex:multiValueProp
                                "propval 1" ,
                                "propval 2" ;
                            ex:singleValueProp "propval"
                        ] ,
                        [
                            ex:multiValueProp
                                "propval 1" ,
                                "propval 2" ;
                            ex:singleValueProp "propval"
                        ] ;
                    ex:multiValueProp
                        "propval 1" ,
                        "propval 2" ;
                    ex:singleValueProp "propval"
                ] ;
            ex:multiValueProp
                "propval 1" ,
                "propval 2" ;
            ex:singleValueProp "propval"
        ] ;
    ex:multiValueProp
        "propval 1" ,
        "propval 2" ,
        "propval 3" ,
        "propval 4" ;
    ex:name
        "Thing" ,
        "Other Thing"@en ,
        "もの"@ja ,
        "rzecz"@pl ;
    ex:singleValueProp "propval" ;
.

"""

    assert s == expected_s

    # re-parse test
    g2 = Graph().parse(data=s)  # turtle
    assert len(g2) == len(g)
