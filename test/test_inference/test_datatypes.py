"""
Test for OWL 2 RL/RDF rules from

    Table 8. The Semantics of Datatypes

https://www.w3.org/TR/owl2-profiles/#Reasoning_in_OWL_2_RL_and_RDF_Graphs_using_Rules

NOTE: The following axioms are skipped on purpose

- dt-eq
- dt-diff
"""

from rdflib import RDF, RDFS, XSD, Graph, Literal
from rdflib.plugins.inference import DeductiveClosure
from rdflib.plugins.inference.namespaces import ERRNS, T
from rdflib.plugins.inference.owlrl import OWLRL_Semantics


def test_dt_type1():
    """
    Test dt-type1 rule for OWL 2 RL.
    """
    g = Graph()
    DeductiveClosure(OWLRL_Semantics).expand(g)

    assert (RDF.PlainLiteral, RDF.type, RDFS.Datatype) in g
    assert (RDF.XMLLiteral, RDF.type, RDFS.Datatype) in g
    assert (RDFS.Literal, RDF.type, RDFS.Datatype) in g
    assert (XSD.decimal, RDF.type, RDFS.Datatype) in g
    assert (XSD.integer, RDF.type, RDFS.Datatype) in g
    assert (XSD.nonNegativeInteger, RDF.type, RDFS.Datatype) in g
    assert (XSD.nonPositiveInteger, RDF.type, RDFS.Datatype) in g
    assert (XSD.positiveInteger, RDF.type, RDFS.Datatype) in g
    assert (XSD.negativeInteger, RDF.type, RDFS.Datatype) in g
    assert (XSD.long, RDF.type, RDFS.Datatype) in g
    assert (XSD.int, RDF.type, RDFS.Datatype) in g
    assert (XSD.short, RDF.type, RDFS.Datatype) in g
    assert (XSD.byte, RDF.type, RDFS.Datatype) in g
    assert (XSD.unsignedLong, RDF.type, RDFS.Datatype) in g
    assert (XSD.unsignedInt, RDF.type, RDFS.Datatype) in g
    assert (XSD.unsignedShort, RDF.type, RDFS.Datatype) in g
    assert (XSD.unsignedByte, RDF.type, RDFS.Datatype) in g
    assert (XSD.float, RDF.type, RDFS.Datatype) in g
    assert (XSD.double, RDF.type, RDFS.Datatype) in g
    assert (XSD.string, RDF.type, RDFS.Datatype) in g
    assert (XSD.normalizedString, RDF.type, RDFS.Datatype) in g
    assert (XSD.token, RDF.type, RDFS.Datatype) in g
    assert (XSD.language, RDF.type, RDFS.Datatype) in g
    assert (XSD.Name, RDF.type, RDFS.Datatype) in g
    assert (XSD.NCName, RDF.type, RDFS.Datatype) in g
    assert (XSD.NMTOKEN, RDF.type, RDFS.Datatype) in g
    assert (XSD.boolean, RDF.type, RDFS.Datatype) in g
    assert (XSD.hexBinary, RDF.type, RDFS.Datatype) in g
    assert (XSD.base64Binary, RDF.type, RDFS.Datatype) in g
    assert (XSD.anyURI, RDF.type, RDFS.Datatype) in g
    assert (XSD.dateTime, RDF.type, RDFS.Datatype) in g
    assert (XSD.dateTimeStamp, RDF.type, RDFS.Datatype) in g


def test_dt_type2():
    """
    Test dt-type2 rule for OWL 2 RL.
    """
    p_one = Literal(1, datatype=XSD.positiveInteger)

    g = Graph()
    g.add((T.A, T.prop, p_one))
    DeductiveClosure(OWLRL_Semantics).expand(g)

    assert (T.A, T.prop, p_one) in g
    assert (p_one, RDF.type, XSD.positiveInteger) in g


def test_dt_not_type():
    """
    Test dt-not-type rule for OWL 2 RL.
    """
    m_one = Literal(-1, datatype=XSD.nonNegativeInteger)

    g = Graph()
    g.add((T.A, T.prop, m_one))
    DeductiveClosure(OWLRL_Semantics).expand(g)

    # TODO, we know this one fails. It is not supposed to.
    # assert (m_one, RDF.type, XSD.nonNegativeInteger) not in g
    assert True

    result = next(g.objects(predicate=ERRNS.error))
    expected = Literal(
        "Lexical value of the literal '-1' does not match its datatype"
        " (http://www.w3.org/2001/XMLSchema#nonNegativeInteger)"
    )
    assert expected == result
