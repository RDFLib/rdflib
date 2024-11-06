from __future__ import annotations

from typing import Union, cast

import pytest

from rdflib import Graph, URIRef
from rdflib.extras.shacl import SHACLPathError, parse_shacl_path
from rdflib.namespace import SH, Namespace
from rdflib.paths import Path

EX = Namespace("http://example.org/")


# Create a graph that gets loaded only once
@pytest.fixture(scope="module")
def path_source_data():
    data = """
        @prefix ex: <http://example.org/> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix sh: <http://www.w3.org/ns/shacl#> .


        ex:TestPropShape1
            sh:path ex:pred1 ;
        .
        ex:TestPropShape2a
            sh:path (
                ex:pred1
                ex:pred2
                ex:pred3
            ) ;
        .
        ex:TestPropShape2b
            sh:path (
                (
                    ex:pred1
                    ex:pred2
                )
                ex:pred3
            ) ;
        .
        ex:TestPropShape3
            sh:path [
                sh:inversePath ex:pred1 ;
            ] ;
        .
        ex:TestPropShape4a
            sh:path [
                sh:alternativePath (
                    ex:pred1
                    ex:pred2
                    ex:pred3
                ) ;
            ] ;
        .
        ex:TestPropShape4b
            sh:path [
                sh:alternativePath (
                    [
                        sh:alternativePath (
                            ex:pred1
                            ex:pred2
                        ) ;
                    ]
                    ex:pred3
                ) ;
            ] ;
        .
        ex:TestPropShape5
            sh:path [
                sh:zeroOrMorePath ex:pred1 ;
            ] ;
        .
        ex:TestPropShape6
            sh:path [
                sh:oneOrMorePath ex:pred1 ;
            ] ;
        .
        ex:TestPropShape7
            sh:path [
                sh:zeroOrOnePath ex:pred1 ;
            ] ;
        .
        ex:TestPropShape8
            sh:path [
                sh:zeroOrMorePath [
                    sh:inversePath ex:pred1 ;
                ] ;
            ] ;
        .
        ex:TestPropShape9
            sh:path [
                sh:alternativePath (
                    [
                        sh:inversePath ex:pred1 ;
                    ]
                    (
                        ex:pred1
                        ex:pred2
                    )
                    [
                        sh:alternativePath (
                            ex:pred1
                            ex:pred2
                            ex:pred3
                        ) ;
                    ]
                ) ;
            ] ;
        .
        ex:TestPropShape10
            sh:path (
                [
                    sh:zeroOrMorePath [
                        sh:inversePath ex:pred1 ;
                    ] ;
                ]
                [
                    sh:alternativePath (
                        [
                            sh:zeroOrMorePath [
                                sh:inversePath ex:pred1 ;
                            ] ;
                        ]
                        [
                            sh:alternativePath (
                                ex:pred1
                                [
                                    sh:oneOrMorePath ex:pred2 ;
                                ]
                                [
                                    sh:zeroOrMorePath ex:pred3 ;
                                ]
                            ) ;
                        ]
                    ) ;
                ]
            ) ;
        .
        ex:InvalidTestPropShape1
            sh:path () ;
        .
        ex:InvalidTestPropShape2
            sh:path (
                ex:pred1
            ) ;
        .
        ex:InvalidTestPropShape3
            sh:path [
                sh:alternativePath () ;
            ] ;
        .
        ex:InvalidTestPropShape4
            sh:path [
                sh:alternativePath (
                    ex:pred1
                ) ;
            ] ;
        .
        ex:InvalidTestPropShape5
            sh:path [
                ex:invalidShaclPathProperty ex:pred1
            ] ;
        .
        ex:InvalidTestPropShape6
            sh:path "This can't be a literal!";
        .
        """
    g = Graph()
    g.parse(data=data, format="turtle")
    yield g


@pytest.mark.parametrize(
    ("resource", "expected"),
    (
        # Single SHACL Path
        (EX.TestPropShape1, EX.pred1),
        (EX.TestPropShape2a, EX.pred1 / EX.pred2 / EX.pred3),
        (EX.TestPropShape2b, EX.pred1 / EX.pred2 / EX.pred3),
        (EX.TestPropShape3, ~EX.pred1),
        (EX.TestPropShape4a, EX.pred1 | EX.pred2 | EX.pred3),
        (EX.TestPropShape4b, EX.pred1 | EX.pred2 | EX.pred3),
        (EX.TestPropShape5, EX.pred1 * "*"),  # type: ignore[operator]
        (EX.TestPropShape6, EX.pred1 * "+"),  # type: ignore[operator]
        (EX.TestPropShape7, EX.pred1 * "?"),  # type: ignore[operator]
        # SHACL Path Combinations
        (EX.TestPropShape8, ~EX.pred1 * "*"),
        (
            EX.TestPropShape9,
            ~EX.pred1 | EX.pred1 / EX.pred2 | EX.pred1 | EX.pred2 | EX.pred3,
        ),
        (
            EX.TestPropShape10,
            ~EX.pred1
            * "*"
            / (~EX.pred1 * "*" | EX.pred1 | EX.pred2 * "+" | EX.pred3 * "*"),  # type: ignore[operator]
        ),
        # Invalid Operations
        (EX.InvalidTestPropShape1, SHACLPathError),
        (EX.InvalidTestPropShape2, SHACLPathError),
        (EX.InvalidTestPropShape3, SHACLPathError),
        (EX.InvalidTestPropShape4, SHACLPathError),
        (EX.InvalidTestPropShape5, SHACLPathError),
        (EX.InvalidTestPropShape6, TypeError),
    ),
)
def test_parse_shacl_path(
    path_source_data: Graph, resource: URIRef, expected: Union[URIRef, Path]
):
    path_root = path_source_data.value(resource, SH.path)

    if isinstance(expected, type) and issubclass(expected, BaseException):
        exception_type: type[BaseException] = cast(type[BaseException], expected)
        with pytest.raises(exception_type):
            parse_shacl_path(path_source_data, path_root)  # type: ignore[arg-type]
    else:
        assert parse_shacl_path(path_source_data, path_root) == expected  # type: ignore[arg-type]
