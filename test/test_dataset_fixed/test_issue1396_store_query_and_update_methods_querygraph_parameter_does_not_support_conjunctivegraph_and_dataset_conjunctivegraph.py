def test_issue1396_store_query_and_update_methods_querygraph_parameter_does_not_support_conjunctivegraph_and_dataset_conjunctivegraph(
    get_conjunctivegraph,
):
    """
    `ConjunctiveGraph(store="MyCustomStore").update("INSERT DATA {}")` will call
    the underlying `MyCustomStore` with the parameter `queryGraph="__UNION__"`.

    With only this information the underlying store does not know what is the
    identifier of the `ConjunctiveDataset` default graph in which the triples
    should be added if the update contains an `INSERT` or a `LOAD` action.
    """
    cg = get_conjunctivegraph
    # logger.debug(f"CG contexts {list(cg.contexts())}")
    assert list(cg.contexts()) == []
    # logger.debug(f"CG default context {cg.default_context.identifier}")

    cg.update("INSERT DATA {<urn:tarek> <urn:likes> <urn:pizza> .}")
    # logger.debug(f"CG contexts {list(cg.contexts())}")
    # logger.debug(f"CG default context {cg.default_context.identifier}")    assert list(cg.contexts()) != []

    cg.query("SELECT * {?s ?p ?o .}")

    """
    Logger output:
    ============================= test session starts ==============================
    test/test_dataset_graph_ops.py::test_issue1396_store_query_and_update_methods_querygraph_parameter_does_not_support_conjunctivegraph_and_dataset_conjunctivegraph[default]
    -------------------------------- live log call ---------------------------------
    DEBUG    rdflib:test_dataset_graph_ops.py:491 CG contexts []
    DEBUG    rdflib:test_dataset_graph_ops.py:493 CG default context N1bd29e866be8449c8c6fa4ae824b0838
    DEBUG    rdflib.graph:graph.py:1370 store has update True and use_store_provided True
    DEBUG    rdflib.graph:graph.py:1376 Graph: update:: store.update INSERT DATA {<urn:tarek> <urn:likes> <urn:pizza> .} initNs 27 initBindings {} queryGraph __UNION__ kwargs {}
    DEBUG    rdflib:memory.py:559 Memory: update:: update INSERT DATA {<urn:tarek> <urn:likes> <urn:pizza> .} initNs 27 initBindings {} queryGraph __UNION__ kwargs {}
    DEBUG    rdflib.graph:graph.py:1387 However, NotImplementedError so passing the buck
    DEBUG    rdflib.graph:graph.py:1393 Graph: update:: processor.graph.identifier N1bd29e866be8449c8c6fa4ae824b0838
    DEBUG    rdflib.graph:graph.py:1397 Graph: update:: processor.update <rdflib.plugins.sparql.processor.SPARQLUpdateProcessor object at 0x7f2e38b32d60> INSERT DATA {<urn:tarek> <urn:likes> <urn:pizza> .} initBindings {} initNs 27 kwargs {}
    DEBUG    rdflib:test_dataset_graph_ops.py:496 CG contexts [<Graph identifier=N1bd29e866be8449c8c6fa4ae824b0838 (<class 'rdflib.graph.Graph'>)>]
    DEBUG    rdflib:test_dataset_graph_ops.py:497 CG default context N1bd29e866be8449c8c6fa4ae824b0838
    DEBUG    rdflib.graph:graph.py:1325 store has query True and use_store_provided True
    DEBUG    rdflib.graph:graph.py:1330 Graph: query:: store.query SELECT * {?s ?p ?o .} initNs 27 initBindings {} queryGraph __UNION__ kwargs {}
    DEBUG    rdflib:memory.py:553 Memory: query:: update SELECT * {?s ?p ?o .} initNs 27 initBindings {} queryGraph __UNION__ kwargs {}
    DEBUG    rdflib.graph:graph.py:1341 However, NotImplementedError so passing the buck
    DEBUG    rdflib.graph:graph.py:1349 Graph: query:: processor.graph.identifier N1bd29e866be8449c8c6fa4ae824b0838
    DEBUG    rdflib.graph:graph.py:1353 Graph: query:: processor.query <rdflib.plugins.sparql.processor.SPARQLProcessor object at 0x7f2e389139d0> SELECT * {?s ?p ?o .} initBindings {} initNs 27 kwargs {}
    PASSED                                                                   [100%]
    """
