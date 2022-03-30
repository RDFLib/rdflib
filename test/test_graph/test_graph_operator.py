from rdflib import Graph


class MyGraph(Graph):
    def my_method(self):
        pass


def test_subclass_add_operator():
    g = MyGraph()

    g = g + g
    assert "my_method" in dir(g)


def test_subclass_sub_operator():
    g = MyGraph()

    g = g - g
    assert "my_method" in dir(g)


def test_subclass_mul_operator():
    g = MyGraph()

    g = g * g
    assert "my_method" in dir(g)
