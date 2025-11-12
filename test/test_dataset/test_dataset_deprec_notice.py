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


def test_dataset_default_context_property():
    ds = Dataset()
    with pytest.warns(
        DeprecationWarning,
        match="Dataset.default_context is deprecated, use Dataset.default_graph instead.",
    ):
        ds.default_context

    with pytest.warns(
        DeprecationWarning,
        match="Dataset.default_context is deprecated, use Dataset.default_graph instead.",
    ):
        ds.default_context = ds.graph()


def test_dataset_identifier_property():
    ds = Dataset()
    with pytest.warns(
        DeprecationWarning,
        match="Dataset.identifier is deprecated and will be removed in future versions.",
    ):
        ds.identifier
