import rdflib

html = """<!DOCTYPE html>
<html>
    <head>
        <title>Boom</title>
    </head>
<body vocab="http://schema.org/" typeof="Book" resource="http://example.com/">
    <time property="dateCreated"><em>2016-01-01</em></time>
</body>
</html>
"""


def test_time_child_element():
    """
    Ensure TIME elements that contain child nodes parse cleanly
    """
    g = rdflib.Graph()
    g.parse(data=html, format='rdfa')
    date = g.value(
        rdflib.URIRef("http://example.com/"),
        rdflib.URIRef("http://schema.org/dateCreated")
    )
    assert len(g) == 3
    assert date == rdflib.term.Literal("2016-01-01")
