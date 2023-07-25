from rdflib import Graph
from rdflib.container import Alt, Bag, Seq
from rdflib.term import BNode, Literal


class TestContainer:
    @classmethod
    def setup_class(cls):
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
        assert len(self.c1) == 0

    def testB(self):
        assert len(self.c2) == 4

    def testC(self):
        self.c2.append(Literal("5"))
        del self.c2[2]
        assert len(self.c2) == 4

    def testD(self):
        assert self.c2.index(Literal("5")) == 4

    def testE(self):
        assert self.c2[2] == Literal("3")

    def testF(self):
        self.c2[2] = Literal("9")
        assert self.c2[2] == Literal("9")

    def testG(self):
        self.c2.clear()
        assert len(self.c2) == 0

    def testH(self):
        self.c2.append_multiple([Literal("80"), Literal("90")])
        assert self.c2[1] == Literal("80")

    def testI(self):
        assert self.c2[2] == Literal("90")

    def testJ(self):
        assert len(self.c2) == 2

    def testK(self):
        assert self.c2.end() == 2

    def testL(self):
        assert self.c3.anyone() in [
            Literal("1"),
            Literal("2"),
            Literal("3"),
            Literal("4"),
        ]

    def testM(self):
        self.c4.add_at_position(3, Literal("60"))
        assert len(self.c4) == 5

    def testN(self):
        assert self.c4.index(Literal("60")) == 3

    def testO(self):
        assert self.c4.index(Literal("3")) == 4

    def testP(self):
        assert self.c4.index(Literal("4")) == 5

    def testQ(self):
        assert self.c2.index(Literal("1000")) != 3
