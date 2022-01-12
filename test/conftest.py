from .earl import EarlReporter
import pytest

pytest_plugins = [EarlReporter.__module__]

pytest.register_assert_rewrite("test.testutils")
