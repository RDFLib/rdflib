
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
    "ntstar",
    Parser,
    "rdflib.plugins.parsers.ntriples-star",
    "NtriplesStarParser",
)

# tests should be past
def test_NtriplesPositiveSyntax_subject():
    g = Graph()
    assert isinstance(g.parse(data="ntriples-star/ntriples-star-syntax-1.nt", format = "ntstar"), Graph)

def test_NtriplesPositiveSyntax_object():
    g = Graph()
    assert isinstance(g.parse("ntriples-star/ntriples-star-syntax-2.nt", format = "ntstar"), Graph)

def test_NtriplesPositiveSyntax_quotedtripleinsideblankNodePropertyList():
    g = Graph()
    assert isinstance(g.parse("ntriples-star/ntriples-star-syntax-3.nt", format = "ntstar"), Graph)

def test_NtriplesPositiveSyntax_quotedtripleinsidecollection():
    g = Graph()
    assert isinstance(g.parse("ntriples-star/ntriples-star-syntax-4.nt", format = "ntstar"), Graph)

#################################
def test_NtriplesPositiveSyntax_nestedquotedtriplesubjectposition():
    g = Graph()
    assert isinstance(g.parse("ntriples-star/ntriples-star-syntax-5.nt", format = "ntstar"), Graph)

def test_NtriplesPositiveSyntax_nestedquotedtripleobjectposition():
    g = Graph()
    assert isinstance(g.parse("ntriples-star/ntriples-star-bnode-1.nt", format = "ntstar"), Graph)
    print(g.serialize())
    # for s, p, o, g in g.quads((None, RDF.type, None, None)):
    #     print(s)

def test_NtriplesPositiveSyntax_compoundforms():
    g = Graph()
    assert isinstance(g.parse("ntriples-star/ntriples-star-bnode-2.nt", format = "ntstar"), Graph)

def test_NtriplesPositiveSyntax_blanknodesubject():
    g = Graph()
    assert isinstance(g.parse("ntriples-star/ntriples-star-nested-1.nt", format = "ntstar"), Graph)

def test_NtriplesPositiveSyntax_blanknodeobject():
    g = Graph()
    assert isinstance(g.parse("ntriples-star/ntriples-star-nested-2.nt", format = "ntstar"), Graph)

# tests should be broken

def test_NtriplesNegativeSyntax_Badquotedtripleaspredicate():
    g = Graph()
    try:
        assert isinstance(g.parse("ntriples-star/ntriples-star-bad-syntax-1.nt", format = "ntstar"), Graph)
    except:
        pytest.xfail("Bad quoted triple literal subject")

def test_NtriplesNegativeSyntax_Badquotedtripleliteralsubject():
    g = Graph()
    try:
        assert isinstance(g.parse("ntriples-star/ntriples-star-bad-syntax-2.nt", format = "ntstar"), Graph)
    except:
        pytest.xfail("Bad quoted triple literal subject")

def test_NtriplesNegativeSyntax_Badquotedtripleliteralpredicate():
    g = Graph()
    try:
        assert isinstance(g.parse("ntriples-star/ntriples-star-bad-syntax-3.nt", format = "ntstar"), Graph)
    except:
        pytest.xfail("Badquotedtripleliteralpredicate")

def test_NtriplesNegativeSyntax_Badquotedtripleblanknodepredicate():
    g = Graph()
    try:
        assert isinstance(g.parse("ntriples-star/ntriples-star-bad-syntax-4.nt", format = "ntstar"), Graph)
    except:
        pytest.xfail("Badquotedtripleblanknodepredicate")

if __name__ == "__main__":
    pytest.main()
