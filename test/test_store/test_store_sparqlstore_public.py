import json

import pytest

from rdflib import Dataset
from rdflib.plugins.sparql.results.jsonresults import JSONResult
from rdflib.plugins.sparql.results.xmlresults import XMLResult
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from rdflib.query import Result

# Mark all tests in this module as public_endpoints
# They will be skipped by default, unless the --public-endpoints flag is passed to pytest
pytestmark = pytest.mark.public_endpoints


# NOTE: dbpedia virtuoso can be unstable, sometimes everything working as expected
# But it has phases where sometimes it sends (405, 'HTTP Error 405: Not Allowed', None), or urllib.error.HTTPError: HTTP Error 502: Bad Gateway
# While accessing the endpoint directly in the browser works fine (so this is not a network issue or the endpoint being down), classic virtuoso
VIRTUOSO_8_DBPEDIA = "https://dbpedia.org/sparql"
BLAZEGRAPH_WIKIDATA = "https://query.wikidata.org/sparql"
GRAPHDB_FF = "http://factforge.net/repositories/ff-news"  # http://factforge.net/
RDF4J_GEOSCIML = "http://vocabs.ands.org.au/repository/api/sparql/csiro_international-chronostratigraphic-chart_2018-revised-corrected"
ALLEGROGRAPH_AGROVOC = "https://agrovoc.fao.org/sparql"
ALLEGROGRAPH_4_MMI = "https://mmisw.org/sparql"  # AllegroServe/1.3.28 http://mmisw.org:10035/doc/release-notes.html
FUSEKI_LOV = "https://lov.linkeddata.es/dataset/lov/sparql"  # Fuseki - version 1.1.1 (Build date: 2014-10-02T16:36:17+0100)
FUSEKI2_STW = "http://zbw.eu/beta/sparql/stw/query"  # Fuseki 3.8.0 (Fuseki2)
STARDOG_LINDAS = (
    "https://lindas.admin.ch/query"  # human UI https://lindas.admin.ch/sparql/
)
STORE4_CHISE = "http://rdf.chise.org/sparql"  # 4store SPARQL server v1.1.4
QLEVER_WIKIDATA = "https://qlever.cs.uni-freiburg.de/api/wikidata"  # https://qlever.cs.uni-freiburg.de/wikidata


@pytest.fixture(
    params=[
        VIRTUOSO_8_DBPEDIA,
        GRAPHDB_FF,
        ALLEGROGRAPH_AGROVOC,
        ALLEGROGRAPH_4_MMI,
        BLAZEGRAPH_WIKIDATA,
        FUSEKI_LOV,
        RDF4J_GEOSCIML,
        STARDOG_LINDAS,
        STORE4_CHISE,
        FUSEKI2_STW,
        QLEVER_WIKIDATA,
    ]
)
def endpoint(request):
    return request.param


def query_sparql(query, endpoint, return_format, method):
    """Generic function to make a SPARQL request and return the result"""
    g = Dataset(
        SPARQLStore(endpoint, returnFormat=return_format, method=method),
        default_union=True,
    )
    return g.query(query)


METHODS_SUPPORTED = ["GET", "POST", "POST_FORM"]

## SELECT and ASK

ROWS_TYPES_MAP = {
    "xml": XMLResult,
    "json": JSONResult,
    "csv": Result,
    "tsv": Result,
}


@pytest.mark.parametrize("return_format", ROWS_TYPES_MAP.keys())
@pytest.mark.parametrize("method", METHODS_SUPPORTED)
def test_select_query(endpoint, return_format, method):
    """Test SELECT queries with various return formats and methods"""
    if endpoint in [STORE4_CHISE, FUSEKI2_STW] and method in ["POST", "POST_FORM"]:
        pytest.skip(f"{endpoint} does not support POST requests")
    if endpoint in [FUSEKI_LOV] and method == "POST":
        pytest.skip("Return type issue with POST requests")
        # NOTE: getting rdflib.plugin.PluginException: No plugin registered for (text/plain, <class 'rdflib.query.ResultParser'>)

    query = "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 5"
    res = query_sparql(query, endpoint, return_format, method)
    assert isinstance(res, ROWS_TYPES_MAP[return_format])
    assert len(res) > 3

    res_json = json.loads(res.serialize(format="json"))
    assert len(res_json["results"]["bindings"]) > 3


# NOTE: an error usually returns a tuple, e.g. (404, 'HTTP Error 404: Not Found', None)
# But sometimes it can also throws it


@pytest.mark.parametrize("return_format", ROWS_TYPES_MAP.keys())
@pytest.mark.parametrize("method", METHODS_SUPPORTED)
def test_ask_query(endpoint, return_format, method):
    """Test ASK queries with various return formats and methods"""
    if endpoint in [STORE4_CHISE, FUSEKI2_STW] and method in ["POST", "POST_FORM"]:
        pytest.skip("POST requests not supported")
    if endpoint in [STORE4_CHISE] and method == "GET" and return_format == "tsv":
        pytest.skip("TSV not supported with GET requests")
    if endpoint in [
        QLEVER_WIKIDATA,
        ALLEGROGRAPH_4_MMI,
        GRAPHDB_FF,
        RDF4J_GEOSCIML,
        STARDOG_LINDAS,
    ] and return_format in ["csv", "tsv"]:
        pytest.skip("CSV/TSV not supported for ASK query type")
    if endpoint in [VIRTUOSO_8_DBPEDIA] and return_format == "tsv":
        pytest.skip("TSV not supported for ASK query type")
    if endpoint in [FUSEKI_LOV] and method == "POST":
        pytest.skip("Return type issue with POST requests")
        # NOTE: getting rdflib.plugin.PluginException: No plugin registered for (text/plain, <class 'rdflib.query.ResultParser'>)

    query = "ASK WHERE { ?s ?p ?o }"
    res = query_sparql(query, endpoint, return_format, method)
    assert isinstance(res, ROWS_TYPES_MAP[return_format])
    for row in res:
        if return_format in ["csv", "tsv"] and not isinstance(row, bool):
            # NOTE: Sometimes CSV/TSV with ASK returns a tuple. But sometimes it returns a boolean (e.g. wikidata)
            assert len(row) == 1
            assert row[0].toPython() in [True, "true", "1"]
            # And yes the content of the tuple can be one of the 3 above
        else:
            # So it is highly recommended to use XML or JSON for consistency
            assert row is True


## CONSTRUCT and DESCRIBE

RDF_TYPES_MAP = {
    "xml": Result,
    "application/rdf+xml": Result,
    # "turtle": Result,
    # NOTE: Turtle not in SPARQLConnector list of _response_mime_types
    # Only XML available for RDF results
}


@pytest.mark.parametrize("return_format", RDF_TYPES_MAP.keys())
@pytest.mark.parametrize("method", METHODS_SUPPORTED)
def test_construct_query(endpoint, return_format, method):
    """Test CONSTRUCT queries with various return formats and methods"""
    if endpoint in [STORE4_CHISE, FUSEKI2_STW] and method in ["POST", "POST_FORM"]:
        pytest.skip(f"{endpoint} does not support POST requests")
    if endpoint in [FUSEKI_LOV] and method == "POST":
        pytest.skip("Return type issue with POST requests")
        # NOTE: getting rdflib.plugin.PluginException: No plugin registered for (text/plain, <class 'rdflib.query.ResultParser'>)
    if endpoint in [QLEVER_WIKIDATA]:
        pytest.skip("Qlever does not support application/rdf+xml")

    query = "CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o } LIMIT 5"
    res = query_sparql(query, endpoint, return_format, method)
    assert isinstance(res, RDF_TYPES_MAP[return_format])
    assert len(res) > 3

    # Test if serialization works
    res_g = Dataset()
    res_g.parse(res.serialize(format="ttl"), format="ttl")
    assert len(res_g) > 3


@pytest.mark.parametrize("return_format", RDF_TYPES_MAP.keys())
@pytest.mark.parametrize("method", METHODS_SUPPORTED)
def test_describe_query(endpoint, return_format, method):
    """Test DESCRIBE queries with various return formats and methods"""
    if endpoint in [STORE4_CHISE, FUSEKI2_STW] and method in ["POST", "POST_FORM"]:
        pytest.skip(f"{endpoint} does not support POST requests")
    if endpoint in [FUSEKI_LOV] and method == "POST":
        pytest.skip("Return type issue with POST requests")
        # NOTE: getting rdflib.plugin.PluginException: No plugin registered for (text/plain, <class 'rdflib.query.ResultParser'>)
    if endpoint in [QLEVER_WIKIDATA] and return_format in [
        "xml",
        "application/rdf+xml",
    ]:
        pytest.skip("Qlever does not support application/rdf+xml")

    query = "DESCRIBE <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"
    res = query_sparql(query, endpoint, return_format, method)
    assert isinstance(res, RDF_TYPES_MAP[return_format])
    # Would need to get a valid URI for each endpoint to properly test this. But is it worth the pain?
    # assert len(res) > 0


@pytest.mark.parametrize("return_format", ROWS_TYPES_MAP.keys())
@pytest.mark.parametrize("method", METHODS_SUPPORTED)
def test_query_invalid(endpoint, return_format, method):
    """Test invalid query with various return formats and methods"""
    if endpoint in [STORE4_CHISE, FUSEKI2_STW] and method in ["POST", "POST_FORM"]:
        pytest.skip(f"{endpoint} does not support POST requests")
    if endpoint in [FUSEKI_LOV]:
        pytest.skip("Unsupported text/plain type returned by LOV Fuseki when error")
        # rdflib.plugin.PluginException: No plugin registered for (text/plain, <class 'rdflib.query.ResultParser'>)

    query = "SELECT ?s ?p ?o WHERE { ?s } LIMIT 5"
    try:
        res = query_sparql(query, endpoint, return_format, method)
        # NOTE: some endpoints return a tuple with error, others will throw an error
        if "HTTP Error 400" in res[1]:
            assert True
        else:
            assert False, f"Unexpected results for invalid query: {res}"
    except ValueError:
        assert True
