from __future__ import annotations

import sys
from contextlib import ExitStack

import pytest

# This is here so that asserts from these modules are formatted for human
# readibility.
pytest.register_assert_rewrite("test.utils")

from pathlib import Path
from typing import (
    Collection,
    Dict,
    Generator,
    Iterable,
    Optional,
    Tuple,
    Union,
)

from rdflib import Graph
from test.utils.audit import AuditHookDispatcher
from test.utils.http import ctx_http_server
from test.utils.httpfileserver import HTTPFileServer

from .data import TEST_DATA_DIR
from .utils.earl import EARLReporter
from .utils.httpservermock import ServedBaseHTTPServerMock

pytest_plugins = [EARLReporter.__module__]


@pytest.fixture(scope="session")
def http_file_server() -> Generator[HTTPFileServer, None, None]:
    host = "127.0.0.1"
    server = HTTPFileServer((host, 0))
    with ctx_http_server(server) as served:
        yield served


@pytest.fixture(scope="session")
def rdfs_graph() -> Graph:
    return Graph().parse(TEST_DATA_DIR / "defined_namespaces/rdfs.ttl", format="turtle")


_ServedBaseHTTPServerMocks = Tuple[ServedBaseHTTPServerMock, ServedBaseHTTPServerMock]


@pytest.fixture(scope="session")
def _session_function_httpmocks() -> Generator[_ServedBaseHTTPServerMocks, None, None]:
    """
    This fixture is session scoped, but it is reset for each function in
    :func:`function_httpmock`. This should not be used directly.
    """
    with ServedBaseHTTPServerMock() as httpmock_a, ServedBaseHTTPServerMock() as httpmock_b:
        yield httpmock_a, httpmock_b


@pytest.fixture(scope="function")
def function_httpmock(
    _session_function_httpmocks: _ServedBaseHTTPServerMocks,
) -> Generator[ServedBaseHTTPServerMock, None, None]:
    """
    HTTP server mock that is reset for each test function.
    """
    (mock, _) = _session_function_httpmocks
    mock.reset()
    yield mock


@pytest.fixture(scope="function")
def function_httpmocks(
    _session_function_httpmocks: _ServedBaseHTTPServerMocks,
) -> Generator[Tuple[ServedBaseHTTPServerMock, ServedBaseHTTPServerMock], None, None]:
    """
    Alternative HTTP server mock that is reset for each test function.

    This exists in case a tests needs to work with two different HTTP servers.
    """
    (mock_a, mock_b) = _session_function_httpmocks
    mock_a.reset()
    mock_b.reset()
    yield mock_a, mock_b


@pytest.fixture(scope="session", autouse=True)
def audit_hook_dispatcher() -> Generator[AuditHookDispatcher, None, None]:
    dispatcher = AuditHookDispatcher()
    sys.addaudithook(dispatcher.audit)
    yield dispatcher


@pytest.fixture(scope="function")
def exit_stack() -> Generator[ExitStack, None, None]:
    with ExitStack() as stack:
        yield stack


EXTRA_MARKERS: Dict[
    Tuple[Optional[str], str], Collection[Union[pytest.MarkDecorator, str]]
] = {
    ("rdflib/__init__.py", "rdflib"): [pytest.mark.webtest],
    ("rdflib/term.py", "rdflib.term.Literal.normalize"): [pytest.mark.webtest],
    ("rdflib/extras/infixowl.py", "rdflib.extras.infixowl"): [pytest.mark.webtest],
}


PROJECT_ROOT = Path(__file__).parent.parent


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items: Iterable[pytest.Item]):
    for item in items:
        parent_name = (
            str(Path(item.parent.module.__file__).relative_to(PROJECT_ROOT))
            if item.parent is not None
            and isinstance(item.parent, pytest.Module)
            and item.parent.module is not None
            else None
        )
        if (parent_name, item.name) in EXTRA_MARKERS:
            extra_markers = EXTRA_MARKERS[(parent_name, item.name)]
            for extra_marker in extra_markers:
                item.add_marker(extra_marker)
