import unittest
from rdflib import Graph, Namespace


class CbdTestCase(unittest.TestCase):
    """Tests the Graph class' cbd() function"""

    def setUp(self):
        self.g = Graph()
        # adding example data for testing
        self.g.parse(
            data="""PREFIX ex: <http://ex/>
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

        self.EX = Namespace("http://ex/")
        self.g.bind("ex", self.EX)

    def testCbd(self):
        self.assertEqual(
            len(self.g.cbd(self.EX.R1)), 3, "cbd() for R1 should return 3 triples"
        )

        self.assertEqual(
            len(self.g.cbd(self.EX.R2)), 2, "cbd() for R3 should return 2 triples"
        )

        self.assertEqual(
            len(self.g.cbd(self.EX.R3)), 8, "cbd() for R3 should return 8 triples"
        )

        self.assertEqual(
            len(self.g.cbd(self.EX.R4)), 0, "cbd() for R4 should return 0 triples"
        )

    def tearDown(self):
        self.g.close()


if __name__ == "__main__":
    unittest.main()
