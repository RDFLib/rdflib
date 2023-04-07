import json
import logging
import pprint
from typing import Any, Dict, Union

import pytest

from rdflib import Graph
from rdflib.namespace import Namespace
from rdflib.plugins.shared.jsonld.context import Context

EG = Namespace("http://example.org/")


@pytest.mark.parametrize(
    ["input"],
    [
        (
            Context(
                {
                    "eg": f"{EG}",
                }
            ),
        ),
        ({"eg": f"{EG}"},),
    ],
)
def test_serialize_context(input: Union[Dict[str, Any], Context]) -> None:
    """
    The JSON-LD serializer accepts and correctly serializes the context argument to the output.
    """
    graph = Graph()
    graph.add((EG.subject, EG.predicate, EG.object0))
    graph.add((EG.subject, EG.predicate, EG.object1))
    context = Context(
        {
            "eg": f"{EG}",
        }
    )
    logging.debug("context = %s", pprint.pformat(vars(context)))
    data = graph.serialize(format="json-ld", context=context)
    logging.debug("data = %s", data)
    obj = json.loads(data)
    assert obj["@context"] == {"eg": f"{EG}"}
