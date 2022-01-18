from .earl import EarlReporter
import pytest

pytest_plugins = [EarlReporter.__module__]

# This is here so that asserts from these modules are formatted for human
# readibility.
pytest.register_assert_rewrite("test.testutils")
