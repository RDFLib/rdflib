from rdflib import URIRef


def test_issue301_dataset_does_not_parse(get_dataset):

    # STATUS: FIXED, no longer an issue

    d = get_dataset

    g = d.parse(data="<a:a> <b:b> <c:c> .", format="turtle", publicID=URIRef("g:g"))

    assert g == d.get_context(g.identifier)
