from pathlib import Path
from urllib.error import URLError, HTTPError
from rdflib import ConjunctiveGraph

trig_example = """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
 @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
 @prefix swp: <http://www.w3.org/2004/03/trix/swp-1/> .
 @prefix dc: <http://purl.org/dc/elements/1.1/> .
 @prefix ex: <http://www.example.org/vocabulary#> .
 @prefix : <http://www.example.org/exampleDocument#> .

 :G1 { :Monica ex:name "Monica Murphy" .
       :Monica ex:homepage <http://www.monicamurphy.org> .
       :Monica ex:email <mailto:monica@monicamurphy.org> .
       :Monica ex:hasSkill ex:Management }

 :G2 { :Monica rdf:type ex:Person .
       :Monica ex:hasSkill ex:Programming }

 :G3 { :G1 swp:assertedBy _:w1 .
       _:w1 swp:authority :Chris .
       _:w1 dc:date "2003-10-02"^^xsd:date .
       :G2 swp:quotedBy _:w2 .
       :G3 swp:assertedBy _:w2 .
       _:w2 dc:date "2003-09-03"^^xsd:date .
       _:w2 swp:authority :Chris .
       :Chris rdf:type ex:Person .
       :Chris ex:email <mailto:chris@bizer.de> }
"""


def test_issue1244_inconsistent_default_parse_format_conjunctivegraph():

    cg = ConjunctiveGraph()

    # Parse trig data and file
    cg.parse(data=trig_example, format="trig")

    # Trig default
    cg.parse(Path("./test/consistent_test_data/testdata01.trig").absolute().as_uri())

    # Parse nquads file
    cg.parse(Path("./test/nquads.rdflib/example.nquads").absolute().as_uri())

    # Parse Trix file
    cg.parse(Path("./test/trix/nokia_example.trix").absolute().as_uri())

    # files
    try:
        cg.parse(__file__)  # here we are trying to parse a Python file!!
    except Exception as e:
        # logger.debug(f"Exception {repr(e)}")
        assert repr(e).startswith("""ParserError("Could not guess RDF format""")

    # .nt can be parsed by Turtle Parser
    cg.parse("test/nt/anons-01.nt")
    # RDF/XML
    cg.parse("test/rdf/datatypes/test001.rdf")  # XML
    # bad filename but set format
    cg.parse("test/rdf/datatypes/test001.borked", format="xml")

    # strings
    cg = ConjunctiveGraph()

    try:
        cg.parse(data="rubbish")
    except Exception as e:
        # logger.debug(f"Exception {repr(e)}")
        assert repr(e).startswith("""ParserError('Could not guess RDF format""")

    # Turtle - default
    cg.parse(
        data="<http://example.com/a> <http://example.com/a> <http://example.com/a> ."
    )

    # Turtle - format given
    cg.parse(
        data="<http://example.com/a> <http://example.com/a> <http://example.com/a> .",
        format="turtle",
    )

    # URI
    cg = ConjunctiveGraph()

    # only getting HTML
    try:
        cg.parse(location="https://www.google.com")
    except Exception as e:
        assert (
            repr(e)
            == """PluginException("No plugin registered for (text/html, <class 'rdflib.parser.Parser'>)")"""
        )

    try:
        cg.parse(location="http://www.w3.org/ns/adms.ttl")
        cg.parse(location="http://www.w3.org/ns/adms.rdf")
    except (URLError, HTTPError):
        # this endpoint is currently not available, ignore this test.
        pass

    try:
        # persistent Australian Government online RDF resource without a file-like ending
        cg.parse(location="https://linked.data.gov.au/def/agrif?_format=text/turtle")
    except (URLError, HTTPError):
        # this endpoint is currently not available, ignore this test.
        pass
