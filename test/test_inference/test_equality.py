"""
Test for OWL 2 RL/RDF rules from

    Table 4. The Semantics of Equality

https://www.w3.org/TR/owl2-profiles/#Reasoning_in_OWL_2_RL_and_RDF_Graphs_using_Rules
"""

from rdflib import OWL, Graph, Literal
from rdflib.plugins.inference import DeductiveClosure
from rdflib.plugins.inference.namespaces import ERRNS, T
from rdflib.plugins.inference.owlrl import OWLRL_Semantics


def test_eq_diff1():
    """
    Test eq-diff1 rule for OWL 2 RL.

    If::

        T(?x, owl:sameAs, ?y)
        T(?x, owl:differentFrom, ?y)

    then::

        false
    """
    g = Graph()

    x = T.x
    y = T.y

    g.add((x, OWL.sameAs, y))
    g.add((x, OWL.differentFrom, y))

    DeductiveClosure(OWLRL_Semantics).expand(g)

    result = g.objects(predicate=ERRNS.error)
    expected = Literal(
        "'sameAs' and 'differentFrom' cannot be used on the same"
        + " subject-object pair:"
    )

    # expect multiple error messages for pairs (x, y), (x, x) and (y, y)
    # due to contradiction:
    #
    #    x == y and x != y => x != x and y != y and x == x and y == y
    assert all(r.startswith(expected) for r in result)
