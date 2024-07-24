from __future__ import annotations

import json
import logging
import pprint
from typing import Any, Dict, Union

import pytest

from rdflib import Graph
from rdflib.plugins.shared.jsonld.context import Context
from test.utils.namespace import EGDO


@pytest.mark.parametrize(
    ["input"],
    [
        (
            Context(
                {
                    "eg": f"{EGDO}",
                }
            ),
        ),
        ({"eg": f"{EGDO}"},),
    ],
)
def test_serialize_context(input: Union[Dict[str, Any], Context]) -> None:
    """
    The JSON-LD serializer accepts and correctly serializes the context argument to the output.
    """
    graph = Graph()
    graph.add((EGDO.subject, EGDO.predicate, EGDO.object0))
    graph.add((EGDO.subject, EGDO.predicate, EGDO.object1))
    context = Context(
        {
            "eg": f"{EGDO}",
        }
    )
    logging.debug("context = %s", pprint.pformat(vars(context)))
    data = graph.serialize(format="json-ld", context=context)
    logging.debug("data = %s", data)
    obj = json.loads(data)
    assert obj["@context"] == {"eg": f"{EGDO}"}
