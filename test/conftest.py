import pytest

pytest.register_assert_rewrite("test.utils")

from typing import Generator  # noqa: E402

from rdflib import Graph

from .data import TEST_DATA_DIR
from .utils.earl import EARLReporter  # noqa: E402
from .utils.httpservermock import ServedBaseHTTPServerMock  # noqa: E402

pytest_plugins = [EARLReporter.__module__]

# This is here so that asserts from these modules are formatted for human
# readibility.


@pytest.fixture(scope="session")
def rdfs_graph() -> Graph:
    return Graph().parse(TEST_DATA_DIR / "defined_namespaces/rdfs.ttl", format="turtle")


@pytest.fixture(scope="session")
def session_httpmock() -> Generator[ServedBaseHTTPServerMock, None, None]:
    with ServedBaseHTTPServerMock() as httpmock:
        yield httpmock


@pytest.fixture(scope="function")
def function_httpmock(
    session_httpmock: ServedBaseHTTPServerMock,
) -> Generator[ServedBaseHTTPServerMock, None, None]:
    session_httpmock.reset()
    yield session_httpmock
