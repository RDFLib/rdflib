import pytest

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

    def test_a(self):
        assert len(self.c1) == 0

    def test_b(self):
        assert len(self.c2) == 4

    def test_c(self):
        self.c2.append(Literal("5"))
        del self.c2[2]
        assert len(self.c2) == 4

    def test_d(self):
        assert self.c2.index(Literal("5")) == 4

    def test_e(self):
        assert self.c2[2] == Literal("3")

    def test_f(self):
        self.c2[2] = Literal("9")
        assert self.c2[2] == Literal("9")

    def test_g(self):
        self.c2.clear()
        assert len(self.c2) == 0

    def test_h(self):
        self.c2.append_multiple([Literal("80"), Literal("90")])
        assert self.c2[1] == Literal("80")

    def test_i(self):
        assert self.c2[2] == Literal("90")

    def test_j(self):
        assert len(self.c2) == 2

    def test_k(self):
        assert self.c2.end() == 2

    def test_l(self):
        assert self.c3.anyone() in [
            Literal("1"),
            Literal("2"),
            Literal("3"),
            Literal("4"),
        ]

    def test_m(self):
        self.c4.add_at_position(3, Literal("60"))
        assert len(self.c4) == 5

    def test_n(self):
        assert self.c4.index(Literal("60")) == 3

    def test_o(self):
        assert self.c4.index(Literal("3")) == 4

    def test_p(self):
        assert self.c4.index(Literal("4")) == 5

    def test_q(self):
        assert self.c2.index(Literal("1000")) != 3

    def test_r(self):
        match = "rdflib.container.Container.type_of_conatiner is deprecated. Use type_of_container method instead."
        with pytest.warns(DeprecationWarning, match=match):
            assert self.c1.type_of_container() == self.c1.type_of_conatiner()
        with pytest.warns(DeprecationWarning, match=match):
            assert self.c3.type_of_container() == self.c3.type_of_conatiner()
        with pytest.warns(DeprecationWarning, match=match):
            assert self.c4.type_of_container() == self.c4.type_of_conatiner()
