from rdflib import Graph
from rdflib.compare import isomorphic
import json


def test_wrap():
    """
    Example of intercepting a JSON-LD structure and performing some
    in-memory manipulation and then passing that structure to Graph.parse
    lists in the shacl graph.
    """

    _data = """
    {
        "@context" : {
            "ngff" : "http://example.com/ns#"
        },
        "@graph": [{
            "@type": "ngff:ItemList",
            "ngff:collectionType": {"@type": "ngff:Image"},
            "ngff:itemListElement": [
                {
                    "@type": "ngff:Image",
                    "path": "image1",
                    "name": "Image 1"
                },
                {
                    "@type": "ngff:Image",
                    "path": "something-else",
                    "name": "bob"
                }
            ]
        }]
    }
    """

    # Current workaround
    data = json.loads(_data)
    data = walk(data)
    data = json.dumps(data)  # wasteful
    g1 = Graph()
    g1.parse(data=data, format="json-ld")

    # Desired behavior
    data = json.loads(_data)
    data = walk(data)
    g2 = Graph()
    g2.parse(data=data, format="json-ld")

    assert isomorphic(g1, g2)


def walk(data, path=None):
    """
    Some arbitrary operation on a Python data structure.
    """

    if path is None:
        path = []

    if isinstance(data, dict):
        for k, v in data.items():
            data[k] = walk(v, path + [k])

    elif isinstance(data, list):
        replacement = list()
        for idx, item in enumerate(data):
            if path[-1] == "@graph":
                replacement.append(walk(item, path))
            else:
                wrapper = {"@type": "ListItemWrapper", "ngff:position": idx}
                wrapper["ngff:item"] = walk(item, path + [idx])
                replacement.append(wrapper)
        data = replacement

    return data
