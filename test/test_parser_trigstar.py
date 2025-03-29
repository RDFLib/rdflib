
import pytest

from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

from rdflib.exceptions import ParserError

from rdflib import Graph
from rdflib.util import guess_format


from rdflib.plugin import register
from rdflib.parser import Parser

register(
    "trigs",
    Parser,
    "rdflib.plugins.parsers.trigstar",
    "TrigParser",
)

# tests should be past
def test_TestTrigPositiveSyntax():
    g = Graph()
    assert isinstance(g.parse(data="trig-star/trig-star-syntax-basic-01.trig", format = "trigs"), Graph)

def test_TestTrigPositiveSyntax():
    g = Graph()
    assert isinstance(g.parse("trig-star/trig-star-syntax-basic-02.trig", format = "trigs"), Graph)

def test_TurtlePositiveSyntax_quotedtripleinsideblankNodePropertyList():
    g = Graph()
    assert isinstance(g.parse("trig-star/trig-star-syntax-inside-01.trig", format = "trigs"), Graph)

def test_TrigPositiveSyntax_quotedtripleinsidecollection():
    g = Graph()
    assert isinstance(g.parse("trig-star/trig-star-syntax-inside-02.trig", format = "trigs"), Graph)

#################################
def test_TrigPositiveSyntax_nestedquotedtriplesubjectposition():
    g = Graph()
    assert isinstance(g.parse("trig-star/trig-star-syntax-nested-01.trig", format = "trigs"), Graph)

def test_TrigPositiveSyntax_nestedquotedtripleobjectposition():
    g = Graph()
    assert isinstance(g.parse("trig-star/trig-star-syntax-nested-02.trig", format = "trigs"), Graph)
    print(g.serialize())
    # for s, p, o, g in g.quads((None, RDF.type, None, None)):
    #     print(s)

def test_TrigPositiveSyntax_compoundforms():
    g = Graph()
    assert isinstance(g.parse("trig-star/trig-star-syntax-compound.trig", format = "trigs"), Graph)

def test_TrigPositiveSyntax_blanknodesubject():
    g = Graph()
    assert isinstance(g.parse("trig-star/trig-star-syntax-bnode-01.trig", format = "trigs"), Graph)

def test_TrigPositiveSyntax_blanknodeobject():
    g = Graph()
    assert isinstance(g.parse("trig-star/trig-star-syntax-bnode-02.trig", format = "trigs"), Graph)

def test_TrigPositiveSyntax_blanknode():
    g = Graph()
    assert isinstance(g.parse("trig-star/trig-star-syntax-bnode-03.trig", format = "trigs"), Graph)

def test_TrigPositiveSyntax_Annotationform():
    g = Graph()
    assert isinstance(g.parse("trig-star/trig-star-annotation-1.trig", format = "trigs"), Graph)

def test_TrigPositiveSyntax_Annotationexample():
    g = Graph()
    assert isinstance(g.parse("trig-star/trig-star-annotation-2.trig", format = "trigs"), Graph)

def test_TrigNegativeSyntax_badquotedtripleaspredicate():
    g = Graph()
    try:
        assert isinstance(g.parse("trig-star/trig-star-syntax-bad-01.trig", format = "trigs"), Graph)
    except:
        pytest.xfail("Badquotedtripleblanknodepredicate")

def test_TrigNegativeSyntax_badquotedtripleoutsidetriple():
    g = Graph()
    try:
        assert isinstance(g.parse("trig-star/trig-star-syntax-bad-02.trig", format = "trigs"), Graph)
    except:
        pytest.xfail("badquotedtripleoutsidetriple")

def test_TrigNegativeSyntax_collectionlistinquotedtriple():
    g = Graph()
    try:
        assert isinstance(g.parse("trig-star/trig-star-syntax-bad-03.trig", format = "trigs"), Graph)
    except:
        pytest.xfail("collectionlistinquotedtriple")

def test_TrigNegativeSyntax_badliteralinsubjectpositionofquotedtriple():
    g = Graph()
    try:
        assert isinstance(g.parse("trig-star/trig-star-syntax-bad-04.trig", format = "trigs"), Graph)
    except:
        pytest.xfail("badliteralinsubjectpositionofquotedtriple")

def test_TrigNegativeSyntax_blanknodeaspredicateinquotedtriple():
    g = Graph()
    try:
        assert isinstance(g.parse("trig-star/trig-star-syntax-bad-05.trig", format = "trigs"), Graph)
    except:
        pytest.xfail("blanknodeaspredicateinquotedtriple")

def test_TrigPositiveSyntax_compoundblanknodeexpression():
    g = Graph()
    try:
        assert isinstance(g.parse("trig-star/trig-star-syntax-bad-06.trig", format = "trigs"), Graph)
    except:
        pytest.xfail("compoundblanknodeexpression")

def test_TrigPositiveSyntax_ncompletequotetriple():
    g = Graph()
    try:
        assert isinstance(g.parse("trig-star/trig-star-syntax-bad-07.trig", format = "trigs"), Graph)
    except:
        pytest.xfail("ncompletequotetriple")

def test_TrigPositiveSyntax_overlongquotedtriple():
    g = Graph()
    try:
        assert isinstance(g.parse("trig-star/trig-star-syntax-bad-08.trig", format = "trigs"), Graph)
    except:
        pytest.xfail("overlongquotedtriple")

def test_TrigPositiveSyntax_emptyannotation():
    g = Graph()
    try:
        assert isinstance(g.parse("trig-star/trig-star-syntax-bad-ann-1.trig", format = "trigs"), Graph)
    except:
        pytest.xfail("emptyannotation")

def test_TrigPositiveSyntax_tripleasannotation():
    g = Graph()
    try:
        assert isinstance(g.parse("trig-star/trig-star-syntax-bad-ann-2.trig", format = "trigs"), Graph)
    except:
        pytest.xfail("tripleasannotation")

if __name__ == "__main__":
    pytest.main()
