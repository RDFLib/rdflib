# -*- coding: utf-8 -*-
import os
import shutil
import tempfile
from pathlib import Path
from test.testutils import GraphHelper
from urllib.error import HTTPError, URLError

import pytest

from rdflib import BNode, URIRef, plugin, logger
from rdflib.graph import Graph, Dataset
from rdflib.exceptions import ParserError
from rdflib.namespace import Namespace
from rdflib.plugin import PluginException
from test.pluginstores import (
    HOST,
    root,
    get_plugin_stores,
    set_store_and_path,
    open_store,
    cleanup,
)

from test.data import (
    michel,
    tarek,
    bob,
    likes,
    hates,
    pizza,
    cheese,
    context1,
    context2,
)


@pytest.fixture(
    scope="function",
    params=get_plugin_stores(),
)
def get_dataset(request):
    storename = request.param

    store, path = set_store_and_path(storename)

    d = Dataset(
        store=store, identifier=URIRef("urn:example:testgraph"), default_union=True
    )

    dataset = open_store(d, storename, path)

    yield dataset

    cleanup(dataset, storename, path)


def populate_dataset(dataset):
    triples = [
        (tarek, likes, pizza),
        (tarek, likes, cheese),
        (michel, likes, pizza),
        (michel, likes, cheese),
        (bob, likes, cheese),
        (bob, hates, pizza),
        (bob, hates, michel),
    ]  # gasp!

    graphcontext1 = dataset.graph(context1)
    for triple in triples:
        dataset.add(triple + (dataset.default_graph.identifier,))
        graphcontext1.add(triple)


def populate_dataset_with_multiple_contexts(dataset):
    triple = (pizza, hates, tarek)  # revenge!

    # add to default context
    dataset.add(triple)

    # add to context 1
    graphcontext1 = dataset.graph(context1)
    graphcontext1.add(triple)
    # add to context 2
    graphcontext2 = dataset.graph(context2)
    graphcontext2.add(triple)


def depopulate_dataset(dataset):
    triples = [
        (tarek, likes, pizza),
        (tarek, likes, cheese),
        (michel, likes, pizza),
        (michel, likes, cheese),
        (bob, likes, cheese),
        (bob, hates, pizza),
        (bob, hates, michel),
    ]  # gasp!

    graphcontext1 = dataset.graph(context1)
    for triple in triples:
        dataset.remove(triple)
        graphcontext1.remove(triple)


def test_add(get_dataset):
    dataset = get_dataset

    populate_dataset(dataset)


def test_remove(get_dataset):
    dataset = get_dataset

    populate_dataset(dataset)
    depopulate_dataset(dataset)
    assert len(dataset.store) == 0


def test_default_triples(get_dataset):
    dataset = get_dataset

    triples = dataset.triples
    Any = None

    populate_dataset(dataset)

    # unbound subjects
    assert len(list(triples((Any, likes, pizza)))) == 2
    assert len(list(triples((Any, hates, pizza)))) == 1
    assert len(list(triples((Any, likes, cheese)))) == 3
    assert len(list(triples((Any, hates, cheese)))) == 0

    # unbound objects
    assert len(list(triples((michel, likes, Any)))) == 2
    assert len(list(triples((tarek, likes, Any)))) == 2
    assert len(list(triples((bob, hates, Any)))) == 2
    assert len(list(triples((bob, likes, Any)))) == 1

    # unbound predicates
    assert len(list(triples((michel, Any, cheese)))) == 1
    assert len(list(triples((tarek, Any, cheese)))) == 1
    assert len(list(triples((bob, Any, pizza)))) == 1
    assert len(list(triples((bob, Any, michel)))) == 1

    # unbound subject, objects
    assert len(list(triples((Any, hates, Any)))) == 2
    assert len(list(triples((Any, likes, Any)))) == 5

    # unbound predicates, objects
    assert len(list(triples((michel, Any, Any)))) == 2
    assert len(list(triples((bob, Any, Any)))) == 3
    assert len(list(triples((tarek, Any, Any)))) == 2

    # unbound subjects, predicates
    assert len(list(triples((Any, Any, pizza)))) == 3
    assert len(list(triples((Any, Any, cheese)))) == 3
    assert len(list(triples((Any, Any, michel)))) == 1

    # all unbound
    assert len(list(triples((Any, Any, Any)))) == 7
    depopulate_dataset(dataset)
    assert len(list(triples((Any, Any, Any)))) == 0


def test_connected(get_dataset):
    dataset = get_dataset

    populate_dataset(dataset)
    assert dataset.connected()

    jeroen = URIRef("jeroen")
    unconnected = URIRef("unconnected")

    dataset.add((jeroen, likes, unconnected))

    assert dataset.connected() is False


def test_graph_sub(get_dataset):

    ds = get_dataset

    ds2 = Dataset()

    ds.add((tarek, likes, pizza))
    ds.add((bob, likes, cheese))
    assert len(ds) == 2

    ds2.add((bob, likes, cheese))
    assert len(ds2) == 1

    ds3 = ds - ds2  # removes bob likes cheese

    logger.debug(f"{list(ds3.quads())}")

    assert len(ds3) == 1
    assert (tarek, likes, pizza) in ds3
    assert (tarek, likes, cheese) not in ds3
    assert (bob, likes, cheese) not in ds3

    ds -= ds2

    assert len(ds) == 1
    assert (tarek, likes, pizza) in ds
    assert (tarek, likes, cheese) not in ds
    assert (bob, likes, cheese) not in ds


def test_graph_add(get_dataset):
    ds = get_dataset

    ds2 = Dataset()

    ds.add((tarek, likes, pizza))

    ds2.add((bob, likes, cheese))

    ds3 = ds + ds2

    assert len(ds3) == 2
    assert (tarek, likes, pizza) in ds3
    assert (tarek, likes, cheese) not in ds3
    assert (bob, likes, cheese) in ds3

    ds += ds2

    assert len(ds) == 2
    assert (tarek, likes, pizza) in ds
    assert (tarek, likes, cheese) not in ds
    assert (bob, likes, cheese) in ds


def test_graph_intersection(get_dataset):
    ds = get_dataset

    ds2 = Dataset()

    ds.add((tarek, likes, pizza))
    ds.add((michel, likes, cheese))

    ds2.add((bob, likes, cheese))
    ds2.add((michel, likes, cheese))

    ds3 = ds * ds2

    assert len(ds3) == 1
    assert (tarek, likes, pizza) not in ds3
    assert (tarek, likes, cheese) not in ds3
    assert (bob, likes, cheese) not in ds3
    assert (michel, likes, cheese) in ds3

    ds *= ds2

    assert len(ds) == 1
    assert (tarek, likes, pizza) not in ds
    assert (tarek, likes, cheese) not in ds
    assert (bob, likes, cheese) not in ds
    assert (michel, likes, cheese) in ds


def test_guess_format_for_parse(get_dataset):
    dataset = get_dataset

    # files
    with pytest.raises(ParserError):
        dataset.parse(__file__)  # here we are trying to parse a Python file!!

    # .nt can be parsed by Turtle Parser
    dataset.parse("test/nt/anons-01.nt")
    # RDF/XML
    dataset.parse("test/rdf/datatypes/test001.rdf")  # XML
    # bad filename but set format
    dataset.parse("test/rdf/datatypes/test001.borked", format="xml")

    # strings
    dataset2 = Dataset()

    with pytest.raises(ParserError):
        dataset2.parse(data="rubbish")

    # Turtle - default
    dataset.parse(
        data="<http://example.com/a> <http://example.com/a> <http://example.com/a> ."
    )

    # Turtle - format given
    dataset.parse(
        data="<http://example.com/a> <http://example.com/a> <http://example.com/a> .",
        format="turtle",
    )

    # RDF/XML - format given
    rdf = """<rdf:RDF
  xmlns:ns1="http://example.org/#"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
>
  <rdf:Description rdf:nodeID="ub63bL2C1">
    <ns1:p rdf:resource="http://example.org/q"/>
    <ns1:r rdf:resource="http://example.org/s"/>
  </rdf:Description>
  <rdf:Description rdf:nodeID="ub63bL5C1">
    <ns1:r>
      <rdf:Description rdf:nodeID="ub63bL6C11">
        <ns1:s rdf:resource="http://example.org/#t"/>
      </rdf:Description>
    </ns1:r>
    <ns1:p rdf:resource="http://example.org/q"/>
  </rdf:Description>
</rdf:RDF>
    """
    dataset.parse(data=rdf, format="xml")

    # only getting HTML
    with pytest.raises(PluginException):
        dataset.parse(location="https://www.google.com")

    try:
        dataset.parse(location="http://www.w3.org/ns/adms.ttl")
        dataset.parse(location="http://www.w3.org/ns/adms.rdf")
    except (URLError, HTTPError):
        # this endpoint is currently not available, ignore this test.
        pass

    try:
        # persistent Australian Government online RDF resource without a file-like ending
        dataset.parse(
            location="https://linked.data.gov.au/def/agrif?_format=text/turtle"
        )
    except (URLError, HTTPError):
        # this endpoint is currently not available, ignore this test.
        pass


def test_parse_file_uri(get_dataset):
    dataset = get_dataset

    EG = Namespace("http://example.org/#")
    path = Path("./test/nt/simple-04.nt").absolute().as_uri()
    dataset.parse(path)
    triple_set = set(t for t in dataset.triples((None, None, None, URIRef(path))))
    assert triple_set == {
        (EG["Subject"], EG["predicate"], EG["ObjectP"]),
        (EG["Subject"], EG["predicate"], EG["ObjectQ"]),
        (EG["Subject"], EG["predicate"], EG["ObjectR"]),
    }


def test_transitive(get_dataset):
    dataset = get_dataset

    person = URIRef("ex:person")
    dad = URIRef("ex:dad")
    mom = URIRef("ex:mom")
    mom_of_dad = URIRef("ex:mom_o_dad")
    mom_of_mom = URIRef("ex:mom_o_mom")
    dad_of_dad = URIRef("ex:dad_o_dad")
    dad_of_mom = URIRef("ex:dad_o_mom")

    parent = URIRef("ex:parent")

    dataset.add((person, parent, dad))
    dataset.add((person, parent, mom))
    dataset.add((dad, parent, mom_of_dad))
    dataset.add((dad, parent, dad_of_dad))
    dataset.add((mom, parent, mom_of_mom))
    dataset.add((mom, parent, dad_of_mom))

    # transitive parents of person
    assert set(dataset.transitive_objects(subject=person, predicate=parent)) == {
        person,
        dad,
        mom_of_dad,
        dad_of_dad,
        mom,
        mom_of_mom,
        dad_of_mom,
    }
    # transitive parents of dad
    assert set(dataset.transitive_objects(dad, parent)) == {
        dad,
        mom_of_dad,
        dad_of_dad,
    }
    # transitive parents of dad_of_dad
    assert set(dataset.transitive_objects(dad_of_dad, parent)) == {dad_of_dad}

    # transitive children (inverse of parents) of mom_of_mom
    assert set(dataset.transitive_subjects(predicate=parent, object=mom_of_mom)) == {
        mom_of_mom,
        mom,
        person,
    }

    # transitive children (inverse of parents) of mom
    assert set(dataset.transitive_subjects(parent, mom)) == {mom, person}
    # transitive children (inverse of parents) of person
    assert set(dataset.transitive_subjects(parent, person)) == {person}


def test_conjunction(get_dataset):
    dataset = get_dataset

    populate_dataset_with_multiple_contexts(dataset)

    triple = (pizza, likes, pizza)
    # add to context 1
    graphcontext1 = dataset.graph(context1)

    graphcontext1.add(triple)

    assert len(dataset) == len(graphcontext1)


def test_len_in_one_context(get_dataset):
    dataset = get_dataset
    # make sure context is empty

    dataset.remove_graph(dataset.graph(context1))

    graph = dataset.graph(context1)
    old_len = len(dataset)

    for i in range(0, 10):
        graph.add((BNode(), hates, hates))
    assert len(graph) == old_len + 10
    assert len(dataset.graph(context1)) == old_len + 10
    dataset.remove_graph(dataset.graph(context1))
    assert len(dataset) == old_len
    assert len(dataset) == 0


def test_len_in_multiple_contexts(get_dataset):
    dataset = get_dataset
    old_len = len(dataset)
    populate_dataset_with_multiple_contexts(dataset)

    # addStuffInMultipleContexts is adding the same triple to
    # three different contexts. So it's only + 1

    assert len(dataset) == old_len + 1

    graphcontext1 = dataset.graph(context1)
    assert len(graphcontext1) == old_len + 1


def test_remove_in_multiple_contexts(get_dataset):
    dataset = get_dataset
    triple = (pizza, hates, tarek)  # revenge!

    populate_dataset_with_multiple_contexts(dataset)
    # triple should be still in store after removing it from context1 + context2
    assert triple in dataset

    graphcontext1 = dataset.graph(context1)
    graphcontext1.remove(triple)

    assert triple in dataset

    graphcontext2 = dataset.graph(context2)
    graphcontext2.remove(triple)
    assert triple in dataset

    dataset.remove(triple)
    # now gone!
    assert triple not in dataset

    # add again and see if remove without context removes all triples!
    populate_dataset_with_multiple_contexts(dataset)
    dataset.remove(triple)
    assert triple not in dataset


def test_contexts(get_dataset):
    dataset = get_dataset
    triple = (pizza, hates, tarek)  # revenge!

    populate_dataset_with_multiple_contexts(dataset)

    assert context1 in dataset.contexts()
    assert context2 in dataset.contexts()

    contextList = list(list(dataset.contexts(triple)))
    assert context1 in contextList
    assert context2 in contextList


def test_remove_context(get_dataset):
    dataset = get_dataset

    populate_dataset_with_multiple_contexts(dataset)
    assert len(Graph(dataset.store, context1)) == 1
    assert len(dataset.graph(context1)) == 1

    dataset.remove_graph(dataset.graph(context1))
    assert context1 not in dataset.contexts()


def test_remove_any(get_dataset):
    dataset = get_dataset

    Any = None
    populate_dataset_with_multiple_contexts(dataset)
    assert len(list(dataset.quads())) == 3
    dataset.remove((Any, Any, Any))
    assert len(list(dataset.quads())) == 0


def test_triples(get_dataset):
    dataset = get_dataset
    triples = dataset.triples
    context1graph = dataset.graph(context1)
    context1triples = context1graph.triples
    Any = None

    populate_dataset(dataset)

    # unbound subjects with context
    assert len(list(context1triples((Any, likes, pizza)))) == 2
    assert len(list(context1triples((Any, hates, pizza)))) == 1
    assert len(list(context1triples((Any, likes, cheese)))) == 3
    assert len(list(context1triples((Any, hates, cheese)))) == 0

    # unbound subjects without context, same results!
    assert len(list(triples((Any, likes, pizza)))) == 2
    assert len(list(triples((Any, hates, pizza)))) == 1
    assert len(list(triples((Any, likes, cheese)))) == 3
    assert len(list(triples((Any, hates, cheese)))) == 0

    # unbound objects with context
    assert len(list(context1triples((michel, likes, Any)))) == 2
    assert len(list(context1triples((tarek, likes, Any)))) == 2
    assert len(list(context1triples((bob, hates, Any)))) == 2
    assert len(list(context1triples((bob, likes, Any)))) == 1

    # unbound objects without context, same results!
    assert len(list(triples((michel, likes, Any)))) == 2
    assert len(list(triples((tarek, likes, Any)))) == 2
    assert len(list(triples((bob, hates, Any)))) == 2
    assert len(list(triples((bob, likes, Any)))) == 1

    # unbound predicates with context
    assert len(list(context1triples((michel, Any, cheese)))) == 1
    assert len(list(context1triples((tarek, Any, cheese)))) == 1
    assert len(list(context1triples((bob, Any, pizza)))) == 1
    assert len(list(context1triples((bob, Any, michel)))) == 1

    # unbound predicates without context, same results!
    assert len(list(triples((michel, Any, cheese)))) == 1
    assert len(list(triples((tarek, Any, cheese)))) == 1
    assert len(list(triples((bob, Any, pizza)))) == 1
    assert len(list(triples((bob, Any, michel)))) == 1

    # unbound subject, objects with context
    assert len(list(context1triples((Any, hates, Any)))) == 2
    assert len(list(context1triples((Any, likes, Any)))) == 5

    # unbound subject, objects without context, same results!
    assert len(list(triples((Any, hates, Any)))) == 2
    assert len(list(triples((Any, likes, Any)))) == 5

    # unbound predicates, objects with context
    assert len(list(context1triples((michel, Any, Any)))) == 2
    assert len(list(context1triples((bob, Any, Any)))) == 3
    assert len(list(context1triples((tarek, Any, Any)))) == 2

    # unbound predicates, objects without context, same results!
    assert len(list(triples((michel, Any, Any)))) == 2
    assert len(list(triples((bob, Any, Any)))) == 3
    assert len(list(triples((tarek, Any, Any)))) == 2

    # unbound subjects, predicates with context
    assert len(list(context1triples((Any, Any, pizza)))) == 3
    assert len(list(context1triples((Any, Any, cheese)))) == 3
    assert len(list(context1triples((Any, Any, michel)))) == 1

    # unbound subjects, predicates without context, same results!
    assert len(list(triples((Any, Any, pizza)))) == 3
    assert len(list(triples((Any, Any, cheese)))) == 3
    assert len(list(triples((Any, Any, michel)))) == 1

    # all unbound with context
    assert len(list(context1triples((Any, Any, Any)))) == 7
    # all unbound without context, same result!
    assert len(list(triples((Any, Any, Any)))) == 7

    for c in [context1graph, dataset]:
        # unbound subjects
        assert set(c.subjects(likes, pizza)) == set((michel, tarek))
        assert set(c.subjects(hates, pizza)) == set((bob,))
        assert set(c.subjects(likes, cheese)) == set([tarek, bob, michel])
        assert set(c.subjects(hates, cheese)) == set()

        # unbound objects
        assert set(c.objects(michel, likes)) == set([cheese, pizza])
        assert set(c.objects(tarek, likes)) == set([cheese, pizza])
        assert set(c.objects(bob, hates)) == set([michel, pizza])
        assert set(c.objects(bob, likes)) == set([cheese])

        # unbound predicates
        assert set(c.predicates(michel, cheese)) == set([likes])
        assert set(c.predicates(tarek, cheese)) == set([likes])
        assert set(c.predicates(bob, pizza)) == set([hates])
        assert set(c.predicates(bob, michel)) == set([hates])

        assert set(c.subject_objects(hates)) == set([(bob, pizza), (bob, michel)])

        assert set(c.subject_objects(likes)) == set(
            [
                (tarek, cheese),
                (michel, cheese),
                (michel, pizza),
                (bob, cheese),
                (tarek, pizza),
            ]
        )

        assert set(c.predicate_objects(michel)) == set(
            [(likes, cheese), (likes, pizza)]
        )
        assert set(c.predicate_objects(bob)) == set(
            [(likes, cheese), (hates, pizza), (hates, michel)]
        )
        assert set(c.predicate_objects(tarek)) == set([(likes, cheese), (likes, pizza)])
        assert set(c.subject_predicates(pizza)) == set(
            [(bob, hates), (tarek, likes), (michel, likes)]
        )
        assert set(c.subject_predicates(cheese)) == set(
            [(bob, likes), (tarek, likes), (michel, likes)]
        )
        assert set(c.subject_predicates(michel)) == set([(bob, hates)])

        assert set(
            c.triples((None, None, None)) if isinstance(c, Dataset) else c
        ) == set(
            [
                (bob, hates, michel),
                (bob, likes, cheese),
                (tarek, likes, pizza),
                (michel, likes, pizza),
                (michel, likes, cheese),
                (bob, hates, pizza),
                (tarek, likes, cheese),
            ]
        )
    # remove stuff and make sure the graph is empty again
    depopulate_dataset(dataset)

    assert len(list(context1triples((Any, Any, Any)))) == 0
    assert len(list(triples((Any, Any, Any)))) == 0
