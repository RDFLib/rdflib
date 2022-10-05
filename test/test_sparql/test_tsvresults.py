from io import StringIO

from rdflib.plugins.sparql.results.tsvresults import TSVResultParser
from rdflib.query import ResultRow


def test_empty_tsvresults_bindings() -> None:
    # check that optional bindings are ordered properly
    source = """?s\t?p\t?o
    \t<urn:p>\t<urn:o>
    <urn:s>\t\t<urn:o>
    <urn:s>\t<urn:p>\t"""

    parser = TSVResultParser()
    source_io = StringIO(source)
    result = parser.parse(source_io)

    for idx, row in enumerate(result):
        assert isinstance(row, ResultRow)
        assert row[idx] is None
