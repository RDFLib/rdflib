def test_issue1396_store_query_and_update_methods_querygraph_parameter_does_not_support_conjunctivegraph_and_dataset_dataset(
    get_dataset,
):
    """
    1. With `query` and `Dataset`.

    `Dataset(store="MyCustomStore").update("INSERT DATA {}")` will call the
    underlying `MyCustomStore` with the parameter `queryGraph=BNode
    ("abcde")` with `BNode("abcde")` the dataset `identifier` instead of
    `queryGraph=URI("urn:x-rdflib-default")` that identifies the default graph
    and is used by the basic triple insertion and deletion method.

    With this parameter the `Store` query evaluator will query the `_:abcde` graph
    even if the triples are by default added in the default graph identified by
    `<urn:x-rdflib-default>`.

    3. With `update` and `Dataset`.

    Similarly to the `query` method the `queryGraph` parameter is set to the
    Dataset `identifier` and not `URI("urn:x-rdflib-default")` so the update is
    evaluated against the `_:abcde` graph even if triples are by default added to
    the default graph(`<urn:x-rdflib-default>`) by the `add` method.

    """
    ds = get_dataset
    # logger.debug(f"DS contexts {list(ds.contexts())}")
    # logger.debug(f"DS default context {ds.default_context.identifier}")
    # DS contexts [<Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>]
    # DS default context urn:x-rdflib-default

    ds.update("INSERT DATA {<urn:tarek> <urn:likes> <urn:pizza> .}")
    # logger.debug(f"DS contexts {list(ds.contexts())}")
    # logger.debug(f"DS default context {ds.default_context.identifier}")

    ds.query("SELECT * {?s ?p ?o .}")

    """
    Logger output:

    test/test_dataset_graph_ops.py::test_issue1396_store_query_and_update_methods_querygraph_parameter_does_not_support_conjunctivegraph_and_dataset_dataset[default]
    -------------------------------- live log setup --------------------------------
    DEBUG    rdflib:test_dataset_graph_ops.py:113 Using store <rdflib.plugins.stores.memory.Memory object at 0x7fa0407bf640>
    -------------------------------- live log call ---------------------------------
    DEBUG    rdflib:test_dataset_graph_ops.py:440 DS contexts [<Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>]
    DEBUG    rdflib:test_dataset_graph_ops.py:441 DS default context urn:x-rdflib-default
    DEBUG    rdflib.graph:graph.py:1370 store has update True and use_store_provided True
    DEBUG    rdflib.graph:graph.py:1376 Graph: update:: store.update INSERT DATA {<urn:tarek> <urn:likes> <urn:pizza> .} initNs 27 initBindings {} queryGraph urn:x-rdflib-default kwargs {}
    DEBUG    rdflib:memory.py:559 Memory: update:: update INSERT DATA {<urn:tarek> <urn:likes> <urn:pizza> .} initNs 27 initBindings {} queryGraph urn:x-rdflib-default kwargs {}
    DEBUG    rdflib.graph:graph.py:1387 However, NotImplementedError so passing the buck
    DEBUG    rdflib.graph:graph.py:1393 Graph: update:: processor.graph.identifier urn:x-rdflib-default
    DEBUG    rdflib.graph:graph.py:1397 Graph: update:: processor.update <rdflib.plugins.sparql.processor.SPARQLUpdateProcessor object at 0x7fa0407b8df0> INSERT DATA {<urn:tarek> <urn:likes> <urn:pizza> .} initBindings {} initNs 27 kwargs {}
    DEBUG    rdflib:test_dataset_graph_ops.py:444 DS contexts [<Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>]
    DEBUG    rdflib:test_dataset_graph_ops.py:445 DS default context urn:x-rdflib-default
    DEBUG    rdflib.graph:graph.py:1325 store has query True and use_store_provided True
    DEBUG    rdflib.graph:graph.py:1330 Graph: query:: store.query SELECT * {?s ?p ?o .} initNs 27 initBindings {} queryGraph urn:x-rdflib-default kwargs {}
    DEBUG    rdflib:memory.py:553 Memory: query:: update SELECT * {?s ?p ?o .} initNs 27 initBindings {} queryGraph urn:x-rdflib-default kwargs {}
    DEBUG    rdflib.graph:graph.py:1341 However, NotImplementedError so passing the buck
    DEBUG    rdflib.graph:graph.py:1349 Graph: query:: processor.graph.identifier urn:x-rdflib-default
    DEBUG    rdflib.graph:graph.py:1353 Graph: query:: processor.query <rdflib.plugins.sparql.processor.SPARQLProcessor object at 0x7fa040599940> SELECT * {?s ?p ?o .} initBindings {} initNs 27 kwargs {}
    PASSED                                                                   [ 66%]
    """
