import pytest

from rdflib import Graph

from .data import CONSISTENT_DATA_DIR
from .earl import EarlReporter

pytest_plugins = [EarlReporter.__module__]

# This is here so that asserts from these modules are formatted for human
# readibility.
pytest.register_assert_rewrite("test.testutils")


@pytest.fixture(scope="session")
def rdfs_graph() -> Graph:
    return Graph().parse(CONSISTENT_DATA_DIR / "rdfs.ttl", format="turtle")
