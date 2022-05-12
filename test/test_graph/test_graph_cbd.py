import pytest

from rdflib import Graph, Namespace

"""Tests the Graph class' cbd() function"""

EX = Namespace("http://ex/")


@pytest.fixture
def get_graph():
    g = Graph()
    # adding example data for testing
    g.parse(
        data="""
            PREFIX ex: <http://ex/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            ex:R1
              a rdf:Resource ;
              ex:hasChild ex:R2 , ex:R3 .

            ex:R2
              ex:propOne ex:P1 ;
              ex:propTwo ex:P2 .

            ex:R3
                ex:propOne ex:P3 ;
                ex:propTwo ex:P4 ;
                ex:propThree [
                    a rdf:Resource ;
                    ex:propFour "Some Literal" ;
                    ex:propFive ex:P5 ;
                    ex:propSix [
                        ex:propSeven ex:P7 ;
                    ] ;
                ] .
        """,
        format="turtle",
    )

    g.bind("ex", EX)
    yield g
    g.close()


def testCbd(get_graph):
    g = get_graph
    assert len(g.cbd(EX.R1)) == 3, "cbd() for R1 should return 3 triples"

    assert len(g.cbd(EX.R2)) == 2, "cbd() for R3 should return 2 triples"

    assert len(g.cbd(EX.R3)) == 8, "cbd() for R3 should return 8 triples"

    assert len(g.cbd(EX.R4)) == 0, "cbd() for R4 should return 0 triples"


def testCbdReified(get_graph):
    g = get_graph
    # add some reified triples to the testing graph
    g.parse(
        data="""
            PREFIX ex: <http://ex/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            ex:R5
                ex:propOne ex:P1 ;
                ex:propTwo ex:P2 ;
                ex:propRei ex:Pre1 .

            ex:S
                a rdf:Statement ;
                rdf:subject ex:R5 ;
                rdf:predicate ex:propRei ;
                rdf:object ex:Pre1 ;
                ex:otherReiProp ex:Pre2 .
        """,
        format="turtle",
    )

    # this cbd() call should get the 3 basic triples with ex:R5 as subject as well as 5 more from the reified
    # statement
    assert len(g.cbd(EX.R5)) == (3 + 5), "cbd() for R5 should return 8 triples"

    # add crazy reified triples to the testing graph
    g.parse(
        data="""
            PREFIX ex: <http://ex/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            ex:R6
                ex:propOne ex:P1 ;
                ex:propTwo ex:P2 ;
                ex:propRei ex:Pre1 .
            ex:S1
                a rdf:Statement ;
                rdf:subject ex:R6 ;
                rdf:predicate ex:propRei ;
                rdf:object ex:Pre1 ;
                ex:otherReiProp ex:Pre3 .

            ex:S2
                rdf:subject ex:R6 ;
                rdf:predicate ex:propRei2 ;
                rdf:object ex:Pre2 ;
                ex:otherReiProp ex:Pre4 ;
                ex:otherReiProp ex:Pre5 .
        """,
        format="turtle",
    )

    assert len(g.cbd(EX.R6)) == (3 + 5 + 5), "cbd() for R6 should return 12 triples"

    # add example from Concise Bounded Description definition at https://www.w3.org/Submission/CBD/#example
    g.parse(
        data="""
            PREFIX ex:    <http://ex/>
            PREFIX dct:   <http://purl.org/dc/terms/>
            PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX owl:   <http://www.w3.org/2002/07/owl#>
            PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
            PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
            PREFIX dc:    <http://purl.org/dc/elements/1.1/>

            ex:aBookCritic  ex:dislikes  ex:anotherGreatBook ;
                    ex:likes     ex:aReallyGreatBook .

            [ a                 rdf:Statement ;
            rdf:object        "image/jpeg" ;
            rdf:predicate     dc:format ;
            rdf:subject       foaf:Image ;
            rdfs:isDefinedBy  ex:image-formats.rdf
            ] .

            foaf:mbox  a    owl:InverseFunctionalProperty , rdf:Property .

            [ a                 rdf:Statement ;
            rdf:object        "application/pdf" ;
            rdf:predicate     dc:format ;
            rdf:subject       ex:aReallyGreatBook ;
            rdfs:isDefinedBy  ex:book-formats.rdf
            ] .

            ex:aReallyGreatBook  rdfs:seeAlso  ex:anotherGreatBook ;
                    dc:contributor  [ a          foaf:Person ;
                                    foaf:name  "Jane Doe"
                                    ] ;
                    dc:creator      [ a           foaf:Person ;
                                    foaf:img    ex:john.jpg ;
                                    foaf:mbox   "john@example.com" ;
                                    foaf:name   "John Doe" ;
                                    foaf:phone  <tel:+1-999-555-1234>
                                    ] ;
                    dc:format       "application/pdf" ;
                    dc:language     "en" ;
                    dc:publisher    "Examples-R-Us" ;
                    dc:rights       "Copyright (C) 2004 Examples-R-Us. All rights reserved." ;
                    dc:title        "A Really Great Book" ;
                    dct:issued      "2004-01-19"^^xsd:date .

            ex:anotherGreatBook  rdfs:seeAlso  ex:aReallyGreatBook ;
                    dc:creator    "June Doe (june@example.com)" ;
                    dc:format     "application/pdf" ;
                    dc:language   "en" ;
                    dc:publisher  "Examples-R-Us" ;
                    dc:rights     "Copyright (C) 2004 Examples-R-Us. All rights reserved." ;
                    dc:title      "Another Great Book" ;
                    dct:issued    "2004-05-03"^^xsd:date .

            ex:john.jpg  a     foaf:Image ;
                    dc:extent  "1234" ;
                    dc:format  "image/jpeg" .
        """,
        format="turtle",
    )

    assert len(g.cbd(EX.aReallyGreatBook)) == (
        21
    ), "cbd() for aReallyGreatBook should return 21 triples"
