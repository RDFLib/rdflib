import os
import hashlib
from rdflib import BNode, Literal, Namespace, RDF, URIRef, logger
from rdflib.graph import ConjunctiveGraph, Graph, Dataset, DATASET_DEFAULT_GRAPH_ID
from rdflib.namespace import OWL, RDFS, SDO, SKOS, DCTERMS, NamespaceManager
from pathlib import Path
from rdflib.compare import isomorphic, to_isomorphic, to_canonical_graph, graph_diff
import rdflib
import pytest
from pprint import pformat
from rdflib.store import VALID_STORE
from test.data import TEST_DATA_DIR, tarek, michel, likes, pizza, context1, context2
from rdflib.extras.infixowl import BooleanClass, Class, Individual


@pytest.mark.skip("WIP")
def test_infixowl_1():
    testGraph = Graph()
    Individual.factoryGraph = testGraph
    EX = Namespace("http://example.com/")
    namespace_manager = NamespaceManager(Graph())
    namespace_manager.bind("ex", EX, override=False)
    testGraph.namespace_manager = namespace_manager
    fire = Class(EX.Fire)
    water = Class(EX.Water)
    testClass = BooleanClass(members=[fire, water])

    # testClass #doctest: +SKIP
    logger.debug(f"testClass {testClass}")

    # ( ex:Fire AND ex:Water )
    testClass.changeOperator(OWL.unionOf)
    # testClass #doctest: +SKIP
    # ( ex:Fire OR ex:Water )
    logger.debug(f"testClass {testClass}")
    try:
        testClass.changeOperator(OWL.unionOf)
    except Exception as e:
        logger.debug(f"EE{e}")
