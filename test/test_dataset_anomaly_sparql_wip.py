import pytest
import os
from pprint import pformat
from rdflib import (
    logger,
    BNode,
    Dataset,
    URIRef,
)
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID


sportquadsnq = open(
    os.path.join(os.path.dirname(__file__), "consistent_test_data", "sportquads.nq")
).read()


michel = URIRef("urn:michel")
tarek = URIRef("urn:tarek")
bob = URIRef("urn:bob")
likes = URIRef("urn:likes")
hates = URIRef("urn:hates")
pizza = URIRef("urn:pizza")
cheese = URIRef("urn:cheese")

c1 = URIRef("urn:context-1")
c2 = URIRef("urn:context-2")


def render_contexts(ds):
    return (
        "context identifiers / triples\n"
        f"{pformat([(c.identifier.n3(), len(c)) for c in sorted(list(ds.contexts()))], width=200)}"
    )


@pytest.mark.skip
def test_issue319_add_graph_as_dataset_default():

    # STATUS: FIXME remains an issue
    """
    uholzer commented on 1 Aug 2013

    Imagine, you are given a Graph, maybe created with Graph() or maybe
    backed by some arbitrary store. Maybe, for some reason you need a
    Dataset and you want your Graph to be the default graph of this
    Dataset. The Dataset should not and will not need to contain any other
    graphs.

    Is there a straightforward way to achieve this without copying all
    triples? As far as I know, Dataset needs a context_aware and
    graph_aware store, so it is not possible to just create a Dataset
    backed by the same store. Graham Klyne is interested in this because he
    wants to provide a SPARQL endpoint for a given rdflib.Graph, but my
    implementation of a SPARQL endpoint requires a Dataset. I don't really
    like to implement support for plain graphs, so I wonder whether there
    is a simple solution.

    Also, I wonder whether it would be useful to have a true union of
    several graphs backed by different stores.


    gromgull commented on 2 Aug 2013

    There is no way to do it currently, but it would be easy enough to add.

    In most cases, the underlying store WILL be context_aware, since most of our
    stores are, but even if it isn't, we could implement a special "single graph
    dataset" that will throw an exception if you try to get any other graphs?

    And actually, the DataSet is very similar to a graph, how would your endpoint
    implementation break if just handed a graph.

    For the actual SPARQL calls, I made an effort to work with both
    ConjunctiveGraph and DataSet (or rather, with graph_aware and not graph_aware
    stores) for the bits that require graphs, and even with a non context-aware
    graph/store for everything else.

    The true-union of graphs from different stores is easy to do naively and with
    poor performance, and probably impossible to make really scalable (if you
    have 1000 graphs ... ) It's probably another issue though :)

    uholzer commented on 2 Aug 2013

    Thinking about it again, some fixes to my implementation should indeed make
    it compatible with rdflib.Graph.

    uholzer commented on 10 Aug 2013

    There is a discrepancy between Graph and Dataset (note that the parsed triple
    is missing from the serialization):

    ds = rdflib.Dataset()
    ds.parse(data='<a> <b> <c>.', format='turtle')
    print(ds.serialize(format='turtle')) #doctring: +SKIP
    for c in ds.contexts(): print c
    ...
    [a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'IOMemory']].
    <urn:x-rdflib-default> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'IOMemory'].

    It is clear to me why this happens. ConjunctiveGraph parses into a fresh graph
    and Dataset inherits this behaviour. For ConjunctiveGraphs one does not
    observe the above, because the default is the union and hence contains the
    fresh graph.

    Is this behaviour intended? (It doesn't bother me much, I just wanted to note it.)

    iherman commented on 11 Aug 2013

    Well...

    One would have to look at the turtle parser behaviour to understand what is
    going on. But it also a rdflib design decision.

    Formally, a turtle file returns a graph. Not a dataset; a graph.

    Which means that the situation below is unclear at a certain level: what
    happens if one parses a turtle file (ie a graph) into a dataset.

    I guess the obvious answer is that it should be parsed into the default graph,
    but either the turtle parser is modified to do that explicitly in case or a
    Dataset, or an extra trick should be done in the Dataset object.

    And, of course, any modification to the turtle file should be done to all
    other parsers, which is a bit of a pain (though may be a much cleaner
    solution!).


    """
    # logger.debug("test_issue319_add_graph_as_dataset_default: initialising dataset")

    ds = Dataset()

    # There are no triples in any context, so dataset length == 0
    assert len(ds) == 0

    # The default graph is a context so the length of ds.contexts() == 1
    assert len(list(ds.contexts())) == 1

    # Only the default graph exists and is yielded by ds.contexts()
    assert (
        repr(list(ds.contexts()))
        == "[<Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>]"
    )

    # only the default graph exists and is properly identified as DATASET_DEFAULT_GRAPH_ID
    assert set(x.identifier for x in ds.contexts()) == set([DATASET_DEFAULT_GRAPH_ID])

    dataset_default_graph = ds.get_context(DATASET_DEFAULT_GRAPH_ID)

    # logger.debug(f"\n\nDATASET_DEFAULT_GRAPH\n{repr(dataset_default_graph)}")

    assert (
        repr(dataset_default_graph)
        == "<Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>"
    )

    ds.bind("urn", URIRef("urn:"))

    # SPARQL update add triple with specified default context

    ds.update(
        "INSERT DATA { GRAPH <urn:x-rdflib-default> { <urn:tarek> <urn:likes> <urn:cheese> . } }"
    )

    # logger.debug("ds:\n" f"{ds.serialize(format='trig')}")

    """
    @prefix urn: <urn:> .

    {
        urn:tarek urn:likes urn:cheese .
    }
    """

    # SPARQL update add triple to unspecified default context

    ds.update("INSERT DATA { <urn:tarek> <urn:likes> <urn:camembert> . } ")

    # logger.debug("ds:\n" f"{ds.serialize(format='trig')}")

    """
    @prefix urn: <urn:> .

    {
        urn:tarek urn:likes urn:camembert,
                urn:cheese .
    }
    """

    # The default graph is a context so the length of ds.contexts() == 1

    assert len(list(ds.contexts())) == 1
    # logger.debug(render_contexts(ds))

    # Add triple to new, BNODE-named context

    g = ds.graph(BNode())

    g.parse(data="<urn:bob> <urn:likes> <urn:pizza> .", format="ttl")

    # Now there are two contexts
    assert len(list(ds.contexts())) == 2
    # logger.debug(render_contexts(ds))

    # logger.debug("ds:\n" f"{ds.serialize(format='trig')}")

    """
    @prefix urn: <urn:> .

    _:N0795bd33e06d4109819f45ceed2eb0c9 {
        urn:bob urn:likes urn:pizza .
    }

    {
        urn:tarek urn:likes urn:camembert,
                urn:cheese .
    }
    """

    # Add triple into new unspecified context

    g = ds.graph()

    g.parse(data="<urn:michel> <urn:likes> <urn:pizza> .", format="ttl")

    assert len(list(ds.contexts())) == 3
    # logger.debug(render_contexts(ds))

    # logger.debug("ds:\n" f"{ds.serialize(format='trig')}")

    """
    @prefix ns1: <http://rdlib.net/.well-known/genid/rdflib/> .
    @prefix urn: <urn:> .

    {
        urn:tarek urn:likes urn:camembert,
                urn:cheese .
    }

    _:Nde7c6d062fdd4747a92ef906b655f088 {
        urn:bob urn:likes urn:pizza .
    }

    ns1:N8267890aafb4419e87be050c36389e15 {
        urn:michel urn:likes urn:pizza .
    }
    """

    # Add triple with specific context into new, unspecified context

    g = ds.graph()

    g.parse(
        data="<urn:michel> <urn:hates> <urn:pizza> <urn:context-3> .", format="nquads"
    )

    # There are now 5!! contexts, one empty as a consequence of creating
    # a new unspecified context and then adding a triple with a different
    # specified context

    assert len(list(ds.contexts())) == 5
    # logger.debug(render_contexts(ds))

    # logger.debug("ds:\n" f"{ds.serialize(format='trig')}")

    """
    @prefix ns1: <http://rdlib.net/.well-known/genid/rdflib/> .
    @prefix urn: <urn:> .

    urn:context-3 {
        urn:michel urn:hates urn:pizza .
    }

    {
        urn:tarek urn:likes urn:camembert,
                urn:cheese .
    }

    _:Ne984fbcb528c4c4498ea228303d16227 {
        urn:bob urn:likes urn:pizza .
    }

    ns1:Naca6c1ff962b4414a2c0299b1ab18aa4 {
        urn:michel urn:likes urn:pizza .
    }
    """

    # Add triple with specified PUBLICID

    ds.parse(
        data="<urn:tarek> <urn:likes> <urn:michel> .",
        format="ttl",
        publicID="urn:context-4",
    )

    # There are now 6 contexts
    assert len(list(ds.contexts())) == 6
    logger.debug(render_contexts(ds))

    # logger.debug("ds:\n" f"{ds.serialize(format='trig')}")
    """
    @prefix ns1: <http://rdlib.net/.well-known/genid/rdflib/> .
    @prefix urn: <urn:> .

    {
        urn:tarek urn:likes urn:camembert,
                urn:cheese .
    }

    urn:context-3 {
        urn:michel urn:hates urn:pizza .
    }

    _:N56cd78f09aee42258f3d80acdada79e1 {
        urn:bob urn:likes urn:pizza .
    }

    urn:context-4 {
        urn:tarek urn:likes urn:michel .
    }

    ns1:Nfd6f5ae4d71c45df95e0f6b418453f2d {
        urn:michel urn:likes urn:pizza .
    }
    """

    # Add triple to unspecified (default) context

    ds.parse(data="<urn:tarek> <urn:likes> <urn:pizza> .", format="ttl")

    assert len(list(ds.contexts())) == 7
    # logger.debug(render_contexts(ds))

    # logger.debug("ds:\n" f"{ds.serialize(format='trig')}")

    """
    @prefix ns1: <http://rdlib.net/.well-known/genid/rdflib/> .
    @prefix urn: <urn:> .

    urn:context-4 {
        urn:tarek urn:likes urn:michel .
    }

    {
        urn:tarek urn:likes urn:camembert,
                urn:cheese .
    }

    urn:context-3 {
        urn:michel urn:hates urn:pizza .
    }

    _:Nc77847b2575946bdb72c1be4801d3bf7 {
        urn:bob urn:likes urn:pizza .
    }

    _:N3f0c8dda6473404f9d8108527475d3ce {
        urn:tarek urn:likes urn:pizza .
    }

    ns1:N11d519ba1081486e920526e4257356a2 {
        urn:michel urn:likes urn:pizza .
    }
    """

    # SPARQL update add triple in a new, specified context

    ds.update(
        "INSERT DATA { GRAPH <urn:context-1> { <urn:tarek> <urn:hates> <urn:pizza> . } }"
    )

    assert len(list(ds.contexts())) == 8
    # logger.debug(render_contexts(ds))
    # logger.debug("ds:\n" f"{ds.serialize(format='trig')}")

    # SPARQL update of BNODE-NAMED graph"

    ds.update(
        "INSERT DATA { GRAPH <urn:context-1> { <urn:tarek> <urn:hates> <urn:cheese> . } }"
    )

    logger.debug("ds:\n" f"{ds.serialize(format='trig')}")

    # logger.debug("ds:\n" f"{ds.serialize(format='trig')}")

    # # So grab the empty context, use that

    # ctx = [c.identifier for c in list(ds.contexts()) if len(c) == 0]
    # assert len(ctx) == 1
    # logger.debug(f"ctx: {ctx[0].n3()}")

    # q = (
    #     "INSERT DATA { GRAPH "
    #     + ctx[0].n3()
    #     + " { <urn:tarek> <urn:hates> <urn:pizza> . } }"
    # )
    # logger.debug(f"q: {q}")

    # ds.update(q)
