def test_issue319_add_graph_as_dataset_default(get_dataset):

    # STATUS: FIXED no longer an issue

    ds = get_dataset

    assert len(list(ds.contexts())) == 1

    ds.parse(data="<a> <b> <c> .", format="ttl")

    assert len(list(ds.contexts())) == 1
