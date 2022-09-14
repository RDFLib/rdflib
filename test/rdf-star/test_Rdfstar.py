
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
    "ttls",
    Parser,
    "rdflib.plugins.parsers.turtlestar",
    "TurtleParser",
)

# tests should be past
def test_TurtlePositiveSyntax_subject():
    g = Graph()
    assert isinstance((g.parse(data="turtle-star/turtle-star-syntax-basic-01.ttl", format = "ttls"), Graph))

# def test_TurtlePositiveSyntax_object():
#     g = Graph()
#     assert isinstance((g.parse("turtle-star/turtle-star-syntax-basic-02.ttl"), Graph))

# def test_TurtlePositiveSyntax_quotedtripleinsideblankNodePropertyList():
#     g = Graph()
#     assert isinstance((g.parse("turtle-star/turtle-star-syntax-inside-01.ttl"), Graph))

# def test_TurtlePositiveSyntax_quotedtripleinsidecollection():
#     g = Graph()
#     assert isinstance((g.parse("turtle-star/turtle-star-syntax-inside-02.ttl"), Graph))

# def test_TurtlePositiveSyntax_nestedquotedtriplesubjectposition():
#     g = Graph()
#     assert isinstance((g.parse("turtle-star/turtle-star-syntax-nested-01.ttl"), Graph))

# def test_TurtlePositiveSyntax_nestedquotedtripleobjectposition():
#     g = Graph()
#     assert isinstance((g.parse("turtle-star/turtle-star-syntax-nested-02.ttl"), Graph))

# def test_TurtlePositiveSyntax_compoundforms():
#     g = Graph()
#     assert isinstance((g.parse("turtle-star/turtle-star-syntax-compound.ttl"), Graph))

# def test_TurtlePositiveSyntax_blanknodesubject():
#     g = Graph()
#     assert isinstance((g.parse("turtle-star/turtle-star-syntax-bnode-01.ttl"), Graph))

# def test_TurtlePositiveSyntax_blanknodeobject():
#     g = Graph()
#     assert isinstance((g.parse("turtle-star/turtle-star-syntax-bnode-02.ttl"), Graph))

# def test_TurtlePositiveSyntax_blanknode():
#     g = Graph()
#     assert isinstance((g.parse("turtle-star/turtle-star-syntax-bnode-03.ttl"), Graph))

# def test_TurtlePositiveSyntax_Annotationform():
#     g = Graph()
#     assert isinstance((g.parse("turtle-star/turtle-star-annotation-1.ttl"), Graph))

# def test_TurtlePositiveSyntax_Annotationexample():
#     g = Graph()
#     assert isinstance((g.parse("turtle-star/turtle-star-annotation-2.ttl"), Graph))

# def test_TurtlePositiveSyntax_subjectquotedtriple():
#     g = Graph()
#     assert isinstance((g.parse("turtle-star/nt-ttl-star-syntax-1.ttl"), Graph))

# def test_TurtlePositiveSyntax_objectquotedtriple():
#     g = Graph()
#     assert isinstance((g.parse("turtle-star/nt-ttl-star-syntax-2.ttl"), Graph))

# def test_TurtlePositiveSyntax_subjectandobjectquotedtriples():
#     g = Graph()
#     assert isinstance((g.parse("turtle-star/nt-ttl-star-syntax-3.ttl"), Graph))

# def test_TurtlePositiveSyntax_whitespaceandterms():
#     g = Graph()
#     assert isinstance((g.parse("turtle-star/nt-ttl-star-syntax-4.ttl"), Graph))

# def test_TurtlePositiveSyntax_Nestednowhitespace():
#     g = Graph()
#     assert isinstance((g.parse("turtle-star/nt-ttl-star-syntax-5.ttl"), Graph))

# def test_TurtlePositiveSyntax_Blanknodesubject():
#     g = Graph()
#     assert isinstance((g.parse("turtle-star/nt-ttl-star-bnode-1.ttl"), Graph))

# def test_TurtlePositiveSyntax_Blanknodeobject():
#     g = Graph()
#     assert isinstance((g.parse("turtle-star/nt-ttl-star-bnode-2.ttl"), Graph))

# def test_TurtlePositiveSyntax_Nestedsubjectterm():
#     g = Graph()
#     assert isinstance((g.parse("turtle-star/nt-ttl-star-nested-1.ttl"), Graph))

# def test_TurtlePositiveSyntax_Nestedsubjectterm():
#     g = Graph()
#     assert isinstance((g.parse("turtle-star/nt-ttl-star-nested-2.ttl"), Graph))

# # tests should be broken

# def test_TurtleNegativeSyntax_Badquotedtripleliteralsubject():
#     g = Graph()
#     try:
#         assert isinstance((g.parse("turtle-star/nt-ttl-star-bad-syntax-1.ttl"), Graph))
#     except:
#         assert True

# def test_TurtleNegativeSyntax_Badquotedtripleliteralsubject():
#     g = Graph()
#     try:
#         assert isinstance((g.parse("turtle-star/nt-ttl-star-bad-syntax-2.ttl"), Graph))
#     except:
#         assert True

# def test_TurtleNegativeSyntax_Badquotedtripleliteralpredicate():
#     g = Graph()
#     try:
#         assert isinstance((g.parse("turtle-star/nt-ttl-star-bad-syntax-3.ttl"), Graph))
#     except:
#         assert True

# def test_TurtleNegativeSyntax_Badquotedtripleblanknodepredicate():
#     g = Graph()
#     try:
#         assert isinstance((g.parse("turtle-star/nt-ttl-star-bad-syntax-4.ttl"), Graph))
#     except:
#         assert True

# def test_TurtleNegativeSyntax_badquotedtripleaspredicate():
#     g = Graph()
#     try:
#         assert isinstance((g.parse("turtle-star/turtle-star-syntax-bad-01.ttl"), Graph))
#     except:
#         assert True

# def test_TurtleNegativeSyntax_badquotedtripleoutsidetriple():
#     g = Graph()
#     try:
#         assert isinstance((g.parse("turtle-star/turtle-star-syntax-bad-02.ttl"), Graph))
#     except:
#         assert True

# def test_TurtleNegativeSyntax_collectionlistinquotedtriple():
#     g = Graph()
#     try:
#         assert isinstance((g.parse("turtle-star/turtle-star-syntax-bad-03.ttl"), Graph))
#     except:
#         assert True

# def test_TurtleNegativeSyntax_badliteralinsubjectpositionofquotedtriple():
#     g = Graph()
#     try:
#         assert isinstance((g.parse("turtle-star/turtle-star-syntax-bad-04.ttl"), Graph))
#     except:
#         assert True

# def test_TurtleNegativeSyntax_blanknodeaspredicateinquotedtriple():
#     g = Graph()
#     try:
#         assert isinstance((g.parse("turtle-star/turtle-star-syntax-bad-05.ttl"), Graph))
#     except:
#         assert True

# def test_TurtlePositiveSyntax_compoundblanknodeexpression():
#     g = Graph()
#     try:
#         assert isinstance((g.parse("turtle-star/turtle-star-syntax-bad-06.ttl"), Graph))
#     except:
#         assert True

# def test_TurtlePositiveSyntax_ncompletequotetriple():
#     g = Graph()
#     try:
#         assert isinstance((g.parse("turtle-star/turtle-star-syntax-bad-07.ttl"), Graph))
#     except:
#         assert True

# def test_TurtlePositiveSyntax_overlongquotedtriple():
#     g = Graph()
#     try:
#         assert isinstance((g.parse("turtle-star/turtle-star-syntax-bad-08.ttl"), Graph))
#     except:
#         assert True

# def test_TurtlePositiveSyntax_emptyannotation():
#     g = Graph()
#     try:
#         assert isinstance((g.parse("turtle-star/turtle-star-syntax-bad-ann-1.ttl"), Graph))
#     except:
#         assert True

# def test_TurtlePositiveSyntax_tripleasannotation():
#     g = Graph()
#     try:
#         assert isinstance((g.parse("turtle-star/turtle-star-syntax-bad-ann-2.ttl"), Graph))
#     except:
#         assert True

if __name__ == "__main__":
    pytest.main()
