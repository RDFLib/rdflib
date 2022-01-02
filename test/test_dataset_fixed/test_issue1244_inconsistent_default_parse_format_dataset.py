from pathlib import Path
from urllib.error import URLError, HTTPError

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


def test_issue1244_inconsistent_default_parse_format_dataset(get_dataset):
    """
    # STATUS: Fixed

    #  ashleysommer commented on 5 Feb

    We recently changed the Graph.parse() method's format parameter to
    default of turtle instead of XML. This is because turtle is now a much
    more popular file format for Graph data.

    However we overlooked that the ConjunctiveGraph and Dataset classes each
    have their own overloaded parse() method, and they still use 'xml' as
    the default format if none is given.

    The simple thing to do would be simply replace "xml" with "turtle" on
    those too, but looking closer that may not be wise. Because
    ConjuctiveGraph and Dataset are both multi-graph containers and Turtle
    is not multi-graph capable. So usually when you are doing
    ConjunctiveGraph.parse() you will not be expecting a turtle file, but
    more likely .trig or .jsonld.

    Should we change the default format on these to something else, or leave
    it on XML?

    # white-gecko commented on 5 Feb

    I think trig would be good
    """

    ds = get_dataset

    # Parse trig data and file
    ds.parse(data=trig_example)

    # Trig default
    ds.parse(Path("./test/consistent_test_data/testdata02.trig").absolute().as_uri())

    # Parse nquads file
    ds.parse(Path("./test/nquads.rdflib/example.nquads").absolute().as_uri())

    # Parse Trix file
    ds.parse(Path("./test/trix/nokia_example.trix").absolute().as_uri())

    # files
    try:
        ds.parse(__file__)  # here we are trying to parse a Python file!!
    except Exception as e:
        # logger.debug(f"Exception {repr(e)}")
        assert repr(e).startswith("""ParserError("Could not guess RDF format""")

    # .nt can be parsed by Turtle Parser
    ds.parse("test/nt/anons-01.nt")

    # RDF/XML
    ds.parse("test/rdf/datatypes/test001.rdf")  # XML

    # bad filename but set format
    ds.parse("test/rdf/datatypes/test001.borked", format="xml")

    # strings
    ds = get_dataset

    try:
        ds.parse(data="rubbish")
    except Exception as e:
        assert repr(e).startswith("""ParserError('Could not guess RDF format""")

    # Turtle - guess format
    ds.parse(
        data="<http://example.com/a> <http://example.com/a> <http://example.com/a> ."
    )

    # Turtle - format given
    ds.parse(
        data="<http://example.com/a> <http://example.com/a> <http://example.com/a> .",
        format="turtle",
    )

    # URI
    ds = get_dataset

    # only getting HTML
    try:
        ds.parse(location="https://www.google.com")
    except Exception as e:
        # logger.debug(f"Exception {repr(e)}")
        assert (
            repr(e)
            == """PluginException("No plugin registered for (text/html, <class 'rdflib.parser.Parser'>)")"""
        )

    try:
        ds.parse(location="http://www.w3.org/ns/adms.ttl")
        ds.parse(location="http://www.w3.org/ns/adms.rdf")
    except (URLError, HTTPError):
        # this endpoint is currently not available, ignore this test.
        pass

    try:
        # persistent Australian Government online RDF resource without a file-like ending
        ds.parse(location="https://linked.data.gov.au/def/agrif?_format=text/turtle")
    except (URLError, HTTPError):
        # this endpoint is currently not available, ignore this test.
        pass
