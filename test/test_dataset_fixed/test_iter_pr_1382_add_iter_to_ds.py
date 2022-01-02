from rdflib import URIRef


def test_iter_pr_1382_add_iter_to_ds(get_dataset):
    d = get_dataset

    # STATUS: FIXED not an issue

    """
    PR 1382: adds __iter__ to Dataset
    Test assumes PR chnages have been applied
    """

    uri_a = URIRef("https://example.com/a")
    uri_b = URIRef("https://example.com/b")
    uri_c = URIRef("https://example.com/c")
    uri_d = URIRef("https://example.com/d")

    d.add_graph(URIRef("https://example.com/g1"))
    d.add((uri_a, uri_b, uri_c, URIRef("https://example.com/g1")))
    d.add(
        (uri_a, uri_b, uri_c, URIRef("https://example.com/g1"))
    )  # pointless addition: duplicates above

    d.add_graph(URIRef("https://example.com/g2"))
    d.add((uri_a, uri_b, uri_c, URIRef("https://example.com/g2")))
    d.add((uri_a, uri_b, uri_d, URIRef("https://example.com/g1")))  # new, uri_d

    # traditional iterator
    i_trad = 0
    for t in d.quads((None, None, None)):
        i_trad += 1

    # new Dataset.__iter__ iterator
    i_new = 0
    for t in d:
        i_new += 1

    assert i_new == i_trad  # both should be 3
    assert i_new == 3
