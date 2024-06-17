"""
Functionality for interacting with graph variants in `test/data/variants`.
"""

from functools import lru_cache
from importlib import import_module
from typing import Type

from rdflib.graph import Graph, _GraphT


def parse_pyvariant(variant_name: str, target: Graph) -> None:
    """
    Parse the graph variant with the given name into the target graph.

    :param variant_name: the name of the graph variant to parse
    :param target: the graph to parse the variant into
    """
    module_name = f"test.data.variants.{variant_name}"
    module = import_module(module_name)
    module.populate_graph(target)


@lru_cache(maxsize=None)
def load_pyvariant(variant_name: str, graph_type: Type[_GraphT]) -> _GraphT:
    """
    Load the graph variant with the given name.

    :param variant_name: the name of the graph variant to load
    :return: the loaded graph variant
    """
    target = graph_type()
    parse_pyvariant(variant_name, target)
    return target
