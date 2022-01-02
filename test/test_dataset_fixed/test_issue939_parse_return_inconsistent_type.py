from rdflib import ConjunctiveGraph


def test_issue939_parse_return_inconsistent_type():

    # STATUS: FIXED Not an issue (probably)

    # The parse function of ConjunctiveGraph modify in place the
    # ConjunctiveGraph but return a Graph object. This is a minor issue but
    # it can create issues down the road if the parse methode is called like
    # so g = g.parse(source="test.ttl", format='turtle')

    # Demonstration:

    # from rdflib import Graph, ConjunctiveGraph

    # g = ConjunctiveGraph()
    # g.parse(source="test.ttl", format='turtle')
    # print(type(g)) # <class 'rdflib.graph.ConjunctiveGraph'>

    # g = ConjunctiveGraph()
    # g = g.parse(source="test.ttl", format='turtle')
    # print(type(g)) # <class 'rdflib.graph.Graph'>

    test_ttl = """@base <http://purl.org/linkedpolitics/MembersOfParliament_background> .
    @prefix lpv: <vocabulary/> .
    <EUmember_1026>
        a lpv:MemberOfParliament ."""

    # Support this idiom ...
    g = ConjunctiveGraph().parse(data=test_ttl, format="turtle")
    assert type(g) is ConjunctiveGraph

    # The reported would like x to be the ConjunctiveGraph or that type

    assert type(g) is ConjunctiveGraph
