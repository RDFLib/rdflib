from __future__ import annotations

import json
import logging
import pprint
from typing import Any, Union

import pytest

from rdflib import Graph, Literal
from rdflib.namespace import XSD
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
def test_serialize_context(input: Union[dict[str, Any], Context]) -> None:
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


@pytest.mark.parametrize(
    ["kwargs", "expected"],
    [
        ({}, "007"),
        ({"use_native_types": False}, "007"),
        ({"use_native_types": True}, 7),
    ],
)
def test_serialize_use_native_types(kwargs: dict[str, Any], expected: Any) -> None:
    """
    Without a context, the JSON-LD serializer writes native JSON values only
    when use_native_types is true, and keeps the lexical form otherwise.
    """
    graph = Graph()
    graph.add(
        (
            EGDO.subject,
            EGDO.predicate,
            Literal("007", datatype=XSD.integer, normalize=False),
        )
    )
    obj = json.loads(graph.serialize(format="json-ld", **kwargs))
    assert obj[0][f"{EGDO.predicate}"] == [
        {"@type": f"{XSD.integer}", "@value": expected}
    ]
