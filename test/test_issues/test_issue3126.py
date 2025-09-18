import pytest

from rdflib import Graph


def test_skolem_de_skolem_roundtrip():
    """Test deskolemization should ignore literals.

    Issue: https://github.com/RDFLib/rdflib/issues/3126
    """

    nt = (
        '<http://example.com> <http://example.com> "http://example.com [some remark]" .'
    )

    graph = Graph().parse(data=nt, format="nt").de_skolemize()

    try:
        graph.de_skolemize()
    except BaseException as ex:
        pytest.fail(f"Unexpected error: {ex}")
