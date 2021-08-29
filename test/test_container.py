from rdflib.term import BNode
from rdflib.term import Literal
from rdflib import Graph
from rdflib.container import *
import unittest


class TestContainer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = Graph()
        cls.c1 = Bag(cls.g, BNode())
        cls.c2 = Bag(
            cls.g, BNode(), [Literal("1"), Literal("2"), Literal("3"), Literal("4")]
        )
        cls.c3 = Alt(
            cls.g, BNode(), [Literal("1"), Literal("2"), Literal("3"), Literal("4")]
        )
        cls.c4 = Seq(
            cls.g, BNode(), [Literal("1"), Literal("2"), Literal("3"), Literal("4")]
        )

    def testA(self):
        self.assertEqual(len(self.c1) == 0, True)

    def testB(self):
        self.assertEqual(len(self.c2) == 4, True)

    def testC(self):
        self.c2.append(Literal("5"))
        del self.c2[2]
        self.assertEqual(len(self.c2) == 4, True)

    def testD(self):
        self.assertEqual(self.c2.index(Literal("5")) == 4, True)

    def testE(self):
        self.assertEqual(self.c2[2] == Literal("3"), True)

    def testF(self):
        self.c2[2] = Literal("9")
        self.assertEqual(self.c2[2] == Literal("9"), True)

    def testG(self):
        self.c2.clear()
        self.assertEqual(len(self.c2) == 0, True)

    def testH(self):
        self.c2.append_multiple([Literal("80"), Literal("90")])
        self.assertEqual(self.c2[1] == Literal("80"), True)

    def testI(self):
        self.assertEqual(self.c2[2] == Literal("90"), True)

    def testJ(self):
        self.assertEqual(len(self.c2) == 2, True)

    def testK(self):
        self.assertEqual(self.c2.end() == 2, True)

    def testL(self):
        self.assertEqual(
            self.c3.anyone()
            in [Literal("1"), Literal("2"), Literal("3"), Literal("4")],
            True,
        )

    def testM(self):
        self.c4.add_at_position(3, Literal("60"))
        self.assertEqual(len(self.c4) == 5, True)

    def testN(self):
        self.assertEqual(self.c4.index(Literal("60")) == 3, True)

    def testO(self):
        self.assertEqual(self.c4.index(Literal("3")) == 4, True)

    def testP(self):
        self.assertEqual(self.c4.index(Literal("4")) == 5, True)

    def testQ(self):
        self.assertEqual(
            self.c2.index(Literal("1000")) == 3, False
        )  # there is no Literal("1000") in the Bag


if __name__ == "__main__":
    unittest.main()
