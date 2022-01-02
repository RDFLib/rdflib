def test_issue319_add_graph_as_conjunctivegraph_default(get_conjunctivegraph):

    # STATUS: FIXED no longer an issue

    cg = get_conjunctivegraph
    assert len(list(cg.contexts())) == 0

    cg.parse(data="<a> <b> <c>.", format="turtle")

    assert len(list(cg.contexts())) == 1
