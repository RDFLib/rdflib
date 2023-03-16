import sys
from contextlib import ExitStack

import pytest

pytest.register_assert_rewrite("test.utils")

from test.utils.audit import AuditHookDispatcher  # noqa: E402
from test.utils.http import ctx_http_server  # noqa: E402
from test.utils.httpfileserver import HTTPFileServer  # noqa: E402
from typing import Generator, Optional  # noqa: E402

from rdflib import Graph

from .data import TEST_DATA_DIR
from .utils.earl import EARLReporter  # noqa: E402
from .utils.httpservermock import ServedBaseHTTPServerMock  # noqa: E402

pytest_plugins = [EARLReporter.__module__]

# This is here so that asserts from these modules are formatted for human
# readibility.


@pytest.fixture(scope="session")
def http_file_server() -> Generator[HTTPFileServer, None, None]:
    host = "127.0.0.1"
    server = HTTPFileServer((host, 0))
    with ctx_http_server(server) as served:
        yield served


@pytest.fixture(scope="session")
def rdfs_graph() -> Graph:
    return Graph().parse(TEST_DATA_DIR / "defined_namespaces/rdfs.ttl", format="turtle")


@pytest.fixture(scope="session")
def _session_function_httpmock() -> Generator[ServedBaseHTTPServerMock, None, None]:
    """
    This fixture is session scoped, but it is reset for each function in
    :func:`function_httpmock`. This should not be used directly.
    """
    with ServedBaseHTTPServerMock() as httpmock:
        yield httpmock


@pytest.fixture(scope="function")
def function_httpmock(
    _session_function_httpmock: ServedBaseHTTPServerMock,
) -> Generator[ServedBaseHTTPServerMock, None, None]:
    _session_function_httpmock.reset()
    yield _session_function_httpmock


@pytest.fixture(scope="session", autouse=True)
def audit_hook_dispatcher() -> Generator[Optional[AuditHookDispatcher], None, None]:
    if sys.version_info >= (3, 8):
        dispatcher = AuditHookDispatcher()
        sys.addaudithook(dispatcher.audit)
        yield dispatcher
    else:
        yield None


@pytest.fixture(scope="function")
def exit_stack() -> Generator[ExitStack, None, None]:
    with ExitStack() as stack:
        yield stack
