from test.data import context1, context2, tarek

import pytest

from rdflib import ConjunctiveGraph, Graph, Literal
from rdflib.namespace import OWL, Namespace
from rdflib.plugins.stores.memory import Memory
from rdflib.term import URIRef

foaf1_uri = URIRef("http://xmlns.com/foaf/0.1/")
foaf2_uri = URIRef("http://xmlns.com/foaf/2.0/")

FOAF1 = Namespace(foaf1_uri)
FOAF2 = Namespace(foaf2_uri)


def test_binding_replace():

    # The confusion here is in the two arguments “override” and “replace” and
    # how they serve two different purposes --- changing a prefix already bound
    # to a namespace versus changing a namespace already bound to a prefix.

    g = Graph(bind_namespaces="none")
    assert len(list(g.namespaces())) == 0

    # 1. Changing the namespace of an existing namespace=>prefix binding:

    # Say they release FOAF 2.0 and you want to change the binding of
    # `http://xmlns.com/foaf/2.0/` to `foaf`.

    # Up to now you had `http://xmlns.com/foaf/0.1/=>foaf` and `http://xmlns.com/foaf/2.0/=>foaf2`

    # We'll just set up those two bindings ...
    g.bind("foaf", FOAF1)
    g.bind("foaf2", FOAF2)
    assert len(list(g.namespaces())) == 2
    assert list(g.namespaces()) == [("foaf", foaf1_uri), ("foaf2", foaf2_uri)]

    # Now you want to "upgrade" to FOAF2=>foaf and try the obvious:
    g.bind("foaf", FOAF2)

    # But that doesn't happen, instead a different prefix, `foaf1` is bound:
    assert list(g.namespaces()) == [("foaf", foaf1_uri), ("foaf1", foaf2_uri)]

    # The rationale behind this behaviour is that the prefix "foaf" was already
    # bound to the FOAF1 namespace, so a different prefix for the FOAF2 namespace
    # was automatically created.

    # You can achieve the intended result by setting `replace` to `True`:
    g.bind("foaf", FOAF2, replace=True)

    # Because the FOAF2 namespace was rebound to a different prefix, the old
    # "foaf2" prefix has gone and because the "foaf" prefix was rebound to a
    # different namespace, the old FOAF1 namespace has gone, leaving just:

    assert list(g.namespaces()) == [("foaf", foaf2_uri)]

    # Now, if you wish, you can re-bind the FOAF1.0 namespace to a prefix
    # of your choice
    g.bind("oldfoaf", FOAF1)

    assert list(g.namespaces()) == [
        ("foaf", foaf2_uri),  # Should be present but has been removed.
        ("oldfoaf", foaf1_uri),
    ]

    # 2. Changing the prefix of an existing namespace=>prefix binding:

    # The namespace manager preserves the existing bindings from any
    # subsequent unwanted programmatic rebindings such as:
    g.bind("foaf", FOAF1)

    # Which, as things stand, results in:

    assert list(g.namespaces()) == [("foaf", foaf2_uri), ("foaf1", foaf1_uri)]

    # In which the attempted change from `oldfoaf` to (the already
    # bound-to-a different-namespace `foaf`) was intercepted and
    # changed to a non-clashing prefix of `foaf1`

    # So, after undoing the above unwanted rebinding ..
    g.bind("oldfoaf", FOAF1, replace=True)

    # The bindings are again as desired
    assert list(g.namespaces()) == [("foaf", foaf2_uri), ("oldfoaf", foaf1_uri)]

    # Next time through, set override to False
    g.bind("foaf", FOAF1, override=False)

    # And the bindings will remain as desired
    assert list(g.namespaces()) == [("foaf", foaf2_uri), ("oldfoaf", foaf1_uri)]

    # 3. Parsing data with prefix=>namespace bindings
    # Let's see the situation regarding namespace bindings
    # in parsed data - it can be a bit confusing ...

    # Starting with a very likely example where `foaf` is a
    # prefix for `FOAF1`

    data = """\
    @prefix foaf: <http://xmlns.com/foaf/0.1/> .

    <urn:example:a> foaf:name "Bob" ."""

    g.parse(data=data, format="n3")

    # The FOAF2 namespace is already bound to `foaf` so a
    # non-clashing prefix of `foaf1` is rebound to FOAF1 in
    # place of the existing `oldfoaf` prefix

    assert list(g.namespaces()) == [("foaf", foaf2_uri), ("foaf1", foaf1_uri)]

    # Yes, namespace bindings in parsed data replace existing
    # bindings (i.e. `oldfoaf` was replaced by `foaf1`), just
    # live with it ...

    # A different example of the same principle where `foaf2`
    # replaces the exsting `foaf`

    data = """\
    @prefix foaf2: <http://xmlns.com/foaf/2.0/> .

    <urn:example:b> foaf2:name "Alice" ."""

    g.parse(data=data, format="n3")

    # The already-bound namespace of `foaf=>FOAF2` is replaced
    # by the `foaf2=>FOAF2` binding specified in the N3 source

    assert list(g.namespaces()) == [
        ("foaf1", foaf1_uri),
        ("foaf2", foaf2_uri),
    ]

    # Where a prefix-namespace binding in the data does
    # not clash with the existing binding ...

    data = """\
    @prefix foaf1: <http://xmlns.com/foaf/0.1/> .

    <urn:example:a> foaf1:name "Bob" ."""

    g.parse(data=data, format="n3")

    # The prefix `foaf1`, already bound to FOAF1 is
    # used

    assert list(g.namespaces()) == [
        ("foaf1", foaf1_uri),
        ("foaf2", foaf2_uri),
    ]

    # Otherwise, the existing prefix binding is replaced

    data = """\
    @prefix foaf: <http://xmlns.com/foaf/0.1/> .

    <urn:example:b> foaf:name "Alice" ."""

    g.parse(data=data, format="n3")

    assert list(g.namespaces()) == [
        ("foaf2", foaf2_uri),
        ("foaf", foaf1_uri),
    ]

    # Prefixes are bound to namespaces which in turn have a URIRef
    # representation - so a different prefix=>namespace binding
    # means a different predicate and thus a different statement:

    expected = """
        @prefix foaf: <http://xmlns.com/foaf/0.1/> .
        @prefix foaf2: <http://xmlns.com/foaf/2.0/> .

        <urn:example:a> foaf:name "Bob" .

        <urn:example:b> foaf:name "Alice" ;
            foaf2:name "Alice" .

        """

    s = g.serialize(format="n3")

    for l in expected.split():
        assert l in s


def test_prefix_alias_disallowed():

    # CANNOT BIND A PREFIX ALIASED TO AN EXISTING BOUND NAMESPACE

    g = Graph(bind_namespaces="none")
    g.bind("owl", OWL)
    assert ("owl", URIRef("http://www.w3.org/2002/07/owl#")) in list(g.namespaces())

    g.bind("wol", OWL, override=False)
    assert ("owl", URIRef("http://www.w3.org/2002/07/owl#")) in list(g.namespaces())
    assert ("wol", URIRef("http://www.w3.org/2002/07/owl#")) not in list(g.namespaces())


def test_rebind_prefix_succeeds():

    # CAN REPLACE A PREFIX-NAMESPACE BINDING

    g = Graph(bind_namespaces="none")
    g.bind("owl", OWL)
    assert ("owl", URIRef("http://www.w3.org/2002/07/owl#")) in list(g.namespaces())

    g.bind("wol", OWL)
    assert ("wol", URIRef("http://www.w3.org/2002/07/owl#")) in list(g.namespaces())
    assert ("owl", URIRef("http://www.w3.org/2002/07/owl#")) not in list(g.namespaces())


def test_parse_rebinds_prefix():

    # PARSED PREFIX-NAMESPACE BINDINGS REPLACE EXISTING BINDINGS

    data = """@prefix friend-of-a-friend: <http://xmlns.com/foaf/0.1/> .

    <urn:example:a> friend-of-a-friend:name "Bob" .

    """

    # Use full set of namespace bindings, including foaf
    g = Graph(bind_namespaces="none")
    g.bind("foaf", FOAF1)
    assert ("foaf", foaf1_uri) in list(g.namespaces())

    g.parse(data=data, format="n3")

    # foaf no longer in set of namespace bindings
    assert ("foaf", foaf1_uri) not in list(g.namespaces())
    assert ("friend-of-a-friend", foaf1_uri) in list(g.namespaces())


@pytest.mark.xfail(
    reason="""
    Automatic handling of unknown predicates not automatically registered with namespace manager

    NOTE: This is not a bug, but more of a feature request.
    """
)
def test_automatic_handling_of_unknown_predicates():

    # AUTOMATIC HANDLING OF UNKNOWN PREDICATES

    """
    Automatic handling of unknown predicates
    -----------------------------------------

    As a programming convenience, a namespace binding is automatically
    created when :class:`rdflib.term.URIRef` predicates are added to the graph.
    """

    g = Graph(bind_namespaces="none")

    g.add((tarek, URIRef("http://xmlns.com/foaf/0.1/name"), Literal("Tarek")))

    assert len(list(g.namespaces())) > 0


def test_automatic_handling_of_unknown_predicates_only_effected_after_serialization():

    g = Graph(bind_namespaces="none")

    g.add((tarek, URIRef("http://xmlns.com/foaf/0.1/name"), Literal("Tarek")))

    assert "@prefix ns1: <http://xmlns.com/foaf/0.1/> ." in g.serialize(format="n3")

    assert len(list(g.namespaces())) > 0
    assert ("ns1", URIRef("http://xmlns.com/foaf/0.1/")) in list(g.namespaces())


def test_multigraph_bindings():
    data = """@prefix friend-of-a-friend: <http://xmlns.com/foaf/0.1/> .

    <urn:example:a> friend-of-a-friend:name "Bob" .

    """

    store = Memory()

    g1 = Graph(store, identifier=context1, bind_namespaces="none")

    g1.bind("foaf", FOAF1)
    assert list(g1.namespaces()) == [("foaf", foaf1_uri)]
    assert list(store.namespaces()) == [("foaf", foaf1_uri)]

    g1.add((tarek, FOAF1.name, Literal("tarek")))

    assert list(store.namespaces()) == [("foaf", foaf1_uri)]

    g2 = Graph(store, identifier=context2, bind_namespaces="none")
    g2.parse(data=data, format="n3")

    # The parser-caused rebind is in the underlying store and all objects
    # that use the store see the changed binding:
    assert list(store.namespaces()) == [("friend-of-a-friend", foaf1_uri)]
    assert list(g1.namespaces()) == [("friend-of-a-friend", foaf1_uri)]

    # Including newly-created objects that use the store
    cg = ConjunctiveGraph(store=store)

    assert ("foaf", foaf1_uri) not in list(cg.namespaces())
    assert ("friend-of-a-friend", foaf1_uri) in list(cg.namespaces())

    assert len(list(g1.namespaces())) == 6
    assert len(list(g2.namespaces())) == 6
    assert len(list(cg.namespaces())) == 6
    assert len(list(store.namespaces())) == 6

    cg.store.add_graph(g1)
    cg.store.add_graph(g2)

    assert "@prefix friend-of-a-friend: <http://xmlns.com/foaf/0.1/>" in cg.serialize(
        format="n3"
    )

    # In the notation3 format, the statement asserting tarek's name
    # now references the changed prefix:
    assert '<urn:example:tarek> friend-of-a-friend:name "tarek" .' in cg.serialize(
        format="n3"
    )

    # Add foaf2 binding if not already bound
    cg.bind("foaf2", FOAF2, override=False)
    assert ("foaf2", foaf2_uri) in list(cg.namespaces())

    # Impose foaf binding ... if not already bound
    cg.bind("foaf", FOAF1, override=False)
    assert ("foaf", foaf1_uri) not in list(cg.namespaces())


def test_new_namespace_new_prefix():
    g = Graph(bind_namespaces="none")
    g.bind("foaf", FOAF1)
    assert list(g.namespaces()) == [("foaf", foaf1_uri)]


def test_change_prefix_override_true():
    g = Graph(bind_namespaces="none")

    g.bind("foaf", FOAF1)
    assert list(g.namespaces()) == [("foaf", foaf1_uri)]

    g.bind("oldfoaf", FOAF1)
    # Changed
    assert list(g.namespaces()) == [("oldfoaf", foaf1_uri)]


def test_change_prefix_override_false():
    g = Graph(bind_namespaces="none")

    g.bind("foaf", FOAF1)
    assert list(g.namespaces()) == [("foaf", foaf1_uri)]

    g.bind("oldfoaf", FOAF1, override=False)
    # No change
    assert list(g.namespaces()) == [("foaf", foaf1_uri)]


def test_change_namespace_override_true():
    g = Graph(bind_namespaces="none")

    g.bind("foaf", FOAF1)
    assert list(g.namespaces()) == [("foaf", foaf1_uri)]

    g.bind("foaf", FOAF2)
    # Different prefix used
    assert list(g.namespaces()) == [("foaf", foaf1_uri), ("foaf1", foaf2_uri)]


def test_change_namespace_override_false():
    g = Graph(bind_namespaces="none")

    g.bind("foaf", FOAF1)
    assert list(g.namespaces()) == [("foaf", foaf1_uri)]

    # Different namespace so override is irrelevant in this case
    g.bind("foaf", FOAF2, override=False)
    # Different prefix used
    assert list(g.namespaces()) == [("foaf", foaf1_uri), ("foaf1", foaf2_uri)]


def test_new_namespace_override_false():
    g = Graph(bind_namespaces="none")

    g.bind("foaf", FOAF2)
    assert list(g.namespaces()) == [("foaf", foaf2_uri)]

    # Namespace not already bound so override is irrelevant in this case
    g.bind("owl", OWL, override=False)
    # Given prefix used
    assert list(g.namespaces()) == [
        ("foaf", foaf2_uri),
        ("owl", URIRef("http://www.w3.org/2002/07/owl#")),
    ]


def test_change_namespace_and_prefix():

    # A more extensive illustration of attempted rebinds of
    # `foaf` being intercepted and changed to a non-clashing
    # prefix of `foafN` (where N is an incrementing integer) ...

    g = Graph(bind_namespaces="none")

    g.bind("foaf", FOAF1)
    assert list(g.namespaces()) == [("foaf", foaf1_uri)]

    g.bind("foaf", FOAF2, replace=True)
    assert list(g.namespaces()) == [("foaf", foaf2_uri)]

    g.bind("foaf1", FOAF1)

    assert list(g.namespaces()) == [("foaf", foaf2_uri), ("foaf1", foaf1_uri)]

    foaf3_uri = URIRef("http://xmlns.com/foaf/3.0/")
    FOAF3 = Namespace("http://xmlns.com/foaf/3.0/")

    g.bind("foaf", FOAF3)

    assert list(g.namespaces()) == [
        ("foaf", foaf2_uri),
        ("foaf1", foaf1_uri),
        ("foaf2", foaf3_uri),
    ]

    foaf4_uri = URIRef("http://xmlns.com/foaf/4.0/")
    FOAF4 = Namespace("http://xmlns.com/foaf/4.0/")

    g.bind("foaf", FOAF4)

    assert list(g.namespaces()) == [
        ("foaf", foaf2_uri),
        ("foaf1", foaf1_uri),
        ("foaf2", foaf3_uri),
        ("foaf3", foaf4_uri),
    ]
