import pytest

from rdflib import Dataset


def test_dataset_contexts_method():
    ds = Dataset()
    with pytest.warns(
        DeprecationWarning,
        match="Dataset.contexts is deprecated, use Dataset.graphs instead.",
    ):
        # Call list() to consume the generator to emit the warning.
        list(ds.contexts())
