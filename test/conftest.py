import pytest

pytest.register_assert_rewrite("test.utils")

from rdflib import Graph

from .data import TEST_DATA_DIR
from .utils.earl import EarlReporter

pytest_plugins = [EarlReporter.__module__]

# This is here so that asserts from these modules are formatted for human
# readibility.


@pytest.fixture(scope="session")
def rdfs_graph() -> Graph:
    return Graph().parse(TEST_DATA_DIR / "rdfs.ttl", format="turtle")
