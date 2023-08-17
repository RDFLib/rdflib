from contextlib import ExitStack
from test.utils.result import BindingsCollectionType, assert_bindings_collections_equal
from typing import Type, Union

import pytest
from pyparsing import Optional

from rdflib.namespace import XSD
from rdflib.term import BNode, Literal, URIRef, Variable


@pytest.mark.parametrize(
    ["lhs", "rhs", "expected_result"],
    [
        ([], [], True),
        (
            [
                {
                    Variable("a"): Literal("r0c0"),
                    Variable("b"): URIRef("example:r0c1"),
                },
                {
                    Variable("a"): Literal("r1c0"),
                    Variable("b"): URIRef("example:r1c1"),
                },
            ],
            [],
            False,
        ),
        (
            [
                {
                    Variable("a"): Literal("r0c0"),
                    Variable("b"): URIRef("example:r0c1"),
                },
                {
                    Variable("a"): Literal("r1c0"),
                    Variable("b"): URIRef("example:r1c1"),
                },
                {
                    Variable("a"): Literal("r2c0"),
                    Variable("b"): Literal("2", datatype=XSD.decimal),
                },
            ],
            [
                {
                    Variable("a"): Literal("r0c0"),
                    Variable("b"): URIRef("example:r0c1"),
                },
                {
                    Variable("a"): Literal("r1c0"),
                    Variable("b"): URIRef("example:r1c1"),
                },
                {
                    Variable("a"): Literal("r2c0"),
                    Variable("b"): Literal("2.0", datatype=XSD.decimal),
                },
            ],
            True,
        ),
        (
            [],
            [
                {
                    Variable("a"): Literal("r0c0"),
                    Variable("b"): URIRef("example:r0c1"),
                },
                {
                    Variable("a"): Literal("r1c0"),
                    Variable("b"): URIRef("example:r1c1"),
                },
            ],
            False,
        ),
        (
            [
                {
                    Variable("a"): Literal("r1c0"),
                    Variable("b"): URIRef("example:r1c1"),
                },
                {
                    Variable("a"): Literal("r0c0"),
                    Variable("b"): URIRef("example:r0c1"),
                },
            ],
            [
                {
                    Variable("a"): Literal("r0c0x"),
                    Variable("b"): URIRef("example:r0c1x"),
                },
                {
                    Variable("a"): Literal("r1c0"),
                    Variable("b"): URIRef("example:r1c1"),
                },
            ],
            False,
        ),
        (
            [
                {
                    Variable("a"): Literal("r0c0"),
                    Variable("b"): URIRef("example:r0c1"),
                },
            ],
            [
                {
                    Variable("a"): Literal("r0c0"),
                    Variable("b"): URIRef("example:r0c1"),
                },
                {
                    Variable("a"): Literal("r1c0"),
                    Variable("b"): URIRef("example:r1c1"),
                },
            ],
            False,
        ),
        (
            [
                {
                    Variable("a"): Literal("r0c0"),
                    Variable("b"): URIRef("example:r0c1"),
                },
                {
                    Variable("a"): Literal("r1c0"),
                    Variable("b"): URIRef("example:r1c1"),
                },
            ],
            [
                {
                    Variable("a"): Literal("r1c0"),
                    Variable("b"): URIRef("example:r1c1"),
                },
            ],
            False,
        ),
        (
            [
                {
                    Variable("avg"): Literal(
                        "1.6",
                        datatype=URIRef("http://www.w3.org/2001/XMLSchema#decimal"),
                    ),
                    Variable("s"): URIRef("http://www.example.org/mixed1"),
                },
                {
                    Variable("avg"): Literal(
                        "0.2",
                        datatype=URIRef("http://www.w3.org/2001/XMLSchema#double"),
                    ),
                    Variable("s"): URIRef("http://www.example.org/mixed2"),
                },
                {
                    Variable("avg"): Literal(
                        "2.0",
                        datatype=URIRef("http://www.w3.org/2001/XMLSchema#decimal"),
                    ),
                    Variable("s"): URIRef("http://www.example.org/ints"),
                },
            ],
            [
                {
                    Variable("s"): URIRef("http://www.example.org/ints"),
                    Variable("avg"): Literal(
                        "2",
                        datatype=URIRef("http://www.w3.org/2001/XMLSchema#decimal"),
                    ),
                },
                {
                    Variable("s"): URIRef("http://www.example.org/mixed2"),
                    Variable("avg"): Literal(
                        "0.2",
                        datatype=URIRef("http://www.w3.org/2001/XMLSchema#double"),
                    ),
                },
                {
                    Variable("s"): URIRef("http://www.example.org/mixed1"),
                    Variable("avg"): Literal(
                        "1.6",
                        datatype=URIRef("http://www.w3.org/2001/XMLSchema#decimal"),
                    ),
                },
            ],
            True,
        ),
        (
            [
                {
                    Variable("a"): BNode("1"),
                },
            ],
            [
                {
                    Variable("a"): BNode("2"),
                },
            ],
            True,
        ),
        (
            [
                {
                    Variable("a"): Literal("r0c0"),
                    Variable("b"): URIRef("example:r0c1"),
                },
            ],
            [
                {
                    Variable("a"): Literal("r0c0"),
                    Variable("b"): None,
                },
            ],
            False,
        ),
        (
            [
                {
                    Variable("a"): Literal("r0c0"),
                },
            ],
            [
                {
                    Variable("a"): Literal("r0c0"),
                    Variable("b"): None,
                },
            ],
            True,
        ),
    ],
)
def test_bindings_equal(
    lhs: BindingsCollectionType,
    rhs: BindingsCollectionType,
    expected_result: Union[bool, Type[Exception]],
) -> None:
    catcher: Optional[pytest.ExceptionInfo[Exception]] = None

    with ExitStack() as xstack:
        if isinstance(expected_result, type) and issubclass(expected_result, Exception):
            catcher = xstack.enter_context(pytest.raises(expected_result))
        assert_bindings_collections_equal(lhs, rhs, not expected_result)
    if catcher is not None:
        assert isinstance(catcher.value, Exception)
