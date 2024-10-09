from __future__ import annotations

import enum
import http.client
import itertools
import logging
from contextlib import ExitStack
from pathlib import Path
from textwrap import dedent
from typing import Any, Iterable, Tuple
from urllib.request import HTTPHandler, OpenerDirector, Request

import pytest
from _pytest.mark.structures import ParameterSet

from rdflib import Graph
from test.utils.audit import AuditHookDispatcher
from test.utils.httpfileserver import HTTPFileServer, ProtoFileResource
from test.utils.namespace import EGDO
from test.utils.urlopen import context_urlopener

from ..utils import GraphHelper
from ..utils.path import ctx_chdir

JSONLD_CONTEXT = """
{
    "@context": {
        "ex": "http://example.org/"
    }
}
"""

EXPECTED_GRAPH = Graph().add((EGDO.subject, EGDO.predicate, EGDO.object))


def test_default(tmp_path: Path) -> None:
    context_file = tmp_path / "context.jsonld"
    context_file.write_text(dedent(JSONLD_CONTEXT))

    data = f"""
    {{
        "@context": "{context_file.as_uri()}",
        "@id": "ex:subject",
        "ex:predicate": {{ "@id": "ex:object" }}
    }}
    """

    graph = Graph()
    graph.parse(format="json-ld", data=data)
    logging.debug("graph = %s", GraphHelper.triple_set(graph))
    GraphHelper.assert_sets_equals(EXPECTED_GRAPH, graph)


class Defence(enum.Enum):
    NONE = enum.auto()
    AUDIT_HOOK = enum.auto()
    URL_OPENER = enum.auto()


class URIKind(enum.Enum):
    FILE = enum.auto()
    HTTP = enum.auto()
    RELATIVE = enum.auto()


def generate_make_block_file_cases() -> Iterable[ParameterSet]:
    for defence, uri_kind in itertools.product(Defence, URIKind):
        if defence == Defence.URL_OPENER and uri_kind != URIKind.HTTP:
            # URL opener only works for not file URIs
            continue
        yield pytest.param(defence, uri_kind)


@pytest.mark.parametrize(["defence", "uri_kind"], generate_make_block_file_cases())
def test_block_file(
    tmp_path: Path,
    audit_hook_dispatcher: AuditHookDispatcher,
    http_file_server: HTTPFileServer,
    exit_stack: ExitStack,
    defence: Defence,
    uri_kind: URIKind,
) -> None:
    context_file = tmp_path / "context.jsonld"
    context_file.write_text(dedent(JSONLD_CONTEXT))
    context_file_served = http_file_server.add_file_with_caching(
        ProtoFileResource((), context_file)
    )

    context_uri: str
    if uri_kind == URIKind.FILE:
        context_uri = context_file.as_uri()
    elif uri_kind == URIKind.HTTP:
        context_uri = context_file_served.request_url
    elif uri_kind == URIKind.RELATIVE:
        context_uri = context_file.name
        exit_stack.enter_context(ctx_chdir(tmp_path))
    else:
        raise ValueError(f"unknown URI kind: {uri_kind}")

    data = f"""
    {{
        "@context": "{context_uri}",
        "@id": "ex:subject",
        "ex:predicate": {{ "@id": "ex:object" }}
    }}
    """

    data_file = tmp_path / "data.jsonld"
    data_file.write_text(dedent(data))

    if defence == Defence.AUDIT_HOOK and uri_kind == URIKind.FILE:

        def audit_hook(name: str, args: Tuple[Any, ...]) -> None:
            logging.info("block_file_access: name = %s, args = %s", name, args)
            if name == "open" and args[0] == f"{context_file.absolute()}":
                raise PermissionError("access blocked")

        exit_stack.enter_context(audit_hook_dispatcher.ctx_hook("open", audit_hook))

    elif defence == Defence.AUDIT_HOOK and uri_kind == URIKind.RELATIVE:

        def audit_hook(name: str, args: Tuple[Any, ...]) -> None:
            logging.info("block_file_access: name = %s, args = %s", name, args)
            if name == "open" and args[0] == f"{Path.cwd() / context_file.name}":
                raise PermissionError("access blocked")

        exit_stack.enter_context(audit_hook_dispatcher.ctx_hook("open", audit_hook))

    elif defence == Defence.AUDIT_HOOK and uri_kind == URIKind.HTTP:

        def audit_hook(name: str, args: Tuple[Any, ...]) -> None:
            logging.info("block_file_access: name = %s, args = %s", name, args)
            if name == "urllib.Request" and args[0] == context_file_served.request_url:
                raise PermissionError("access blocked")

        exit_stack.enter_context(
            audit_hook_dispatcher.ctx_hook("urllib.Request", audit_hook)
        )

    elif defence == Defence.URL_OPENER and uri_kind == URIKind.HTTP:
        opener = OpenerDirector()

        class SecuredHTTPHandler(HTTPHandler):
            def http_open(self, req: Request) -> http.client.HTTPResponse:
                if req.get_full_url() == context_file_served.request_url:
                    raise PermissionError("access blocked")
                return super().http_open(req)

        opener.add_handler(SecuredHTTPHandler())

        exit_stack.enter_context(context_urlopener(opener))

    elif defence == Defence.NONE:
        pass
    else:
        raise ValueError(
            f"unsupported defence {defence} and uri_kind {uri_kind} combination"
        )

    graph = Graph()
    if defence != Defence.NONE:
        with pytest.raises(PermissionError):
            graph.parse(format="json-ld", data=data)
        assert len(graph) == 0
    else:
        graph.parse(format="json-ld", data=data)
        GraphHelper.assert_sets_equals(EXPECTED_GRAPH, graph)
