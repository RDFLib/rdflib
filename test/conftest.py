import sys
from contextlib import ExitStack

import pytest

pytest.register_assert_rewrite("test.utils")

from pathlib import Path  # noqa: E402
from test.utils.audit import AuditHookDispatcher  # noqa: E402
from test.utils.http import ctx_http_server  # noqa: E402
from test.utils.httpfileserver import HTTPFileServer  # noqa: E402
from typing import (  # noqa: E402
    Collection,
    Dict,
    Generator,
    Iterable,
    Optional,
    Tuple,
    Union,
)

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
