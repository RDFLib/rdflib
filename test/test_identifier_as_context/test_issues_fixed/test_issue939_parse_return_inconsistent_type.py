import pytest
from rdflib import ConjunctiveGraph


@pytest.mark.xfail
def test_issue939_parse_return_inconsistent_type():

    test_ttl = """@base <http://purl.org/linkedpolitics/MembersOfParliament_background> .
    @prefix lpv: <vocabulary/> .
    <EUmember_1026>
        a lpv:MemberOfParliament ."""

    # Support this idiom ...
    g = ConjunctiveGraph().parse(data=test_ttl, format="turtle")

    # The reported would like x to be the ConjunctiveGraph or that type

    assert type(g) is ConjunctiveGraph
