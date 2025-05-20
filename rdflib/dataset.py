from __future__ import annotations

import pathlib
from enum import Enum
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    BinaryIO,
    TextIO, List, Union, Optional, Tuple, Set, Callable, Type,
)

from rdflib import plugin
from rdflib.collection import Collection
from rdflib.namespace import NamespaceManager
from rdflib.parser import InputSource
from rdflib.resource import Resource
from rdflib.store import Store
from rdflib.term import (
    BNode,
    Literal,
    URIRef, IdentifiedNode, Node,
)

if TYPE_CHECKING:
    from collections.abc import Generator

from rdflib.graph import _TripleType, \
    Graph, _TripleSliceType, _QuadSliceType, _QuadType, _PredicateSliceType, \
    _ObjectSliceType, _SubjectSliceType

from rdflib._type_checking import _NamespaceSetString


class GraphType(Enum):
    DEFAULT = "default"
    NAMED = "named"

_GraphSliceType = List[Union[GraphType, IdentifiedNode]] | GraphType | IdentifiedNode


class Dataset():
    """
    #TODO update docstring. For reference see:
    - Temporary writeup in /dataset_api.md, and
    - examples/datasets.py
    """

    def __init__(
        self,
        store: Store | str = "default",
        namespace_manager: NamespaceManager | None = None,
        base: str | None = None,
        bind_namespaces: _NamespaceSetString = "rdflib",
    ):
        super(Dataset, self).__init__(store=store, identifier=None)
        self.base = base
        self.__store: Store
        if not isinstance(store, Store):
            # TODO: error handling
            self.__store = store = plugin.get(store, Store)()
        else:
            self.__store = store
        self.__namespace_manager = namespace_manager
        self._bind_namespaces = bind_namespaces
        self.context_aware = True
        self.formula_aware = False

        if not self.store.graph_aware:
            raise Exception("Dataset must be backed by a graph-aware store!")


    def __str__(self) -> str:
        pattern = (
            "[a rdflib:Dataset;rdflib:storage " "[a rdflib:Store;rdfs:label '%s']]"
        )
        return pattern % self.store.__class__.__name__

    # type error: Return type "tuple[Type[Dataset], tuple[Store, bool]]" of "__reduce__" incompatible with return type "tuple[Type[Graph], tuple[Store, IdentifiedNode]]" in supertype "Graph"
    def __reduce__(self) -> tuple[type[Dataset], tuple[Store, bool]]:  # type: ignore[override]
        return type(self), (self.store, self.default_union)

    def add_named_graph(
        self,
        graph: Graph,
        name: Optional[IdentifiedNode | str] = None,
        base: str | None = None,
    ) -> Dataset:
        if name is None:
            from rdflib.term import _SKOLEM_DEFAULT_AUTHORITY, rdflib_skolem_genid

            self.bind(
                "genid",
                _SKOLEM_DEFAULT_AUTHORITY + rdflib_skolem_genid,
                override=False,
            )
            name = BNode().skolemize()

        graph.base = base

        self.store.add_graph(graph, name)
        return self

    def has_named_graph(self, name: IdentifiedNode) -> bool:
        raise NotImplementedError

    def remove_named_graph(self, name: IdentifiedNode) -> Dataset:
        raise NotImplementedError

    def get_named_graph(self, name: IdentifiedNode) -> Graph:
        raise NotImplementedError

    def replace_named_graph(self, graph: Graph, name: IdentifiedNode) -> Dataset:
        raise NotImplementedError

    def parse(
        self,
        source: (
            IO[bytes] | TextIO | InputSource | str | bytes | pathlib.PurePath | None
        ) = None,
        publicID: str | None = None,  # noqa: N803
        format: str | None = None,
        location: str | None = None,
        file: BinaryIO | TextIO | None = None,
        data: str | bytes | None = None,
        **args: Any,
    ) -> Dataset:
        raise NotImplementedError

    def graphs(
        self, triple: _TripleType | None = None
    ) -> Generator[tuple[IdentifiedNode, Graph], None, None]:
        raise NotImplementedError

    def triples(
        self,
        triple: _TripleSliceType | _QuadSliceType | None = None,
        graph: _GraphSliceType | None = None,
    ) -> Generator[_TripleType, None, None]:
        if graph is None:  # by default, include the default and all named graphs
            graph = [GraphType.DEFAULT, GraphType.NAMED]
        raise NotImplementedError

    # type error: Return type "Generator[tuple[Node, Node, Node, Optional[Node]], None, None]" of "quads" incompatible with return type "Generator[tuple[Node, Node, Node, Optional[Graph]], None, None]" in supertype "ConjunctiveGraph"
    def quads(  # type: ignore[override]
        self,
        quad: _QuadSliceType | None = None,
        graph: _GraphSliceType | None = None,
    ) -> Generator[_QuadType, None, None]:
        if graph is None:  # by default, include the default and all named graphs
            graph = [GraphType.DEFAULT, GraphType.NAMED]
        raise NotImplementedError

    def default_graph(self) -> Graph:
        return self.default_graph

    # type error: Return type "Generator[tuple[Node, URIRef, Node, Optional[IdentifiedNode]], None, None]" of "__iter__" incompatible with return type "Generator[tuple[IdentifiedNode, IdentifiedNode, Union[IdentifiedNode, Literal]], None, None]" in supertype "Graph"
    def __iter__(  # type: ignore[override]
        self,
    ) -> Generator[_QuadType, None, None]:
        """Iterates over all quads in the store"""
        return self.quads()

    def add(self, quad: _QuadType) -> Dataset:
        raise NotImplementedError

    def remove(self, quad: _QuadType) -> Dataset:
        raise NotImplementedError

    def subjects(
        self,
        predicates: _PredicateSliceType | None = None,
        objects: _ObjectSliceType | None = None,
        graphs: _GraphSliceType | None = None,
     ) -> Generator[IdentifiedNode, None, None]:
        raise NotImplementedError

    def predicates(
        self,
        subjects: _SubjectSliceType | None = None,
        objects: _ObjectSliceType | None = None,
        graphs: _GraphSliceType | None = None,
    ) -> Generator[URIRef, None, None]:
        raise NotImplementedError

    def objects(
        self,
        subjects: _SubjectSliceType | None = None,
        predicates: _PredicateSliceType | None = None,
        graphs: _GraphSliceType | None = None,
    ) -> Generator[Node, None, None]:
        raise NotImplementedError

    def subject_objects(
        self,
        predicates: _PredicateSliceType | None = None,
        graphs: _GraphSliceType | None = None,
    ) -> Generator[tuple[IdentifiedNode, Node], None, None]:
        raise NotImplementedError

    def subject_predicates(
        self,
        objects: _ObjectSliceType | None = None,
        graphs: _GraphSliceType | None = None,
    ) -> Generator[tuple[IdentifiedNode, URIRef], None, None]:
        raise NotImplementedError

    def predicate_objects(
        self,
        subjects: _SubjectSliceType | None = None,
        graphs: _GraphSliceType | None = None,
    ) -> Generator[tuple[URIRef, Node], None, None]:
        raise NotImplementedError

    def value(self,
              subject: Optional[IdentifiedNode] = None,
              predicate: Optional[URIRef] = None,
              object: Optional[Node] = None,
              graph: Optional[IdentifiedNode] = None
              ):
        raise NotImplementedError

    def query(self, query):
        raise NotImplementedError

    def update(self, update):
        raise NotImplementedError

    # the following methods are taken from Graph. It would make sense to extract them
    # as shared methods between Dataset and Graph

    def qname(self, uri: str) -> str:
        return self.namespace_manager.qname(uri)

    def compute_qname(self, uri: str, generate: bool = True) -> Tuple[str, URIRef, str]:
        return self.namespace_manager.compute_qname(uri, generate)

    def bind(
        self,
        prefix: Optional[str],
        namespace: Any,  # noqa: F811
        override: bool = True,
        replace: bool = False,
    ) -> None:
        """Bind prefix to namespace

        If override is True will bind namespace to given prefix even
        if namespace was already bound to a different prefix.

        if replace, replace any existing prefix with the new namespace

        for example:  graph.bind("foaf", "http://xmlns.com/foaf/0.1/")

        """
        # TODO FIXME: This method's behaviour should be simplified and made
        # more robust. If the method cannot do what it is asked it should raise
        # an exception, it is also unclear why this method has all the
        # different modes. It seems to just make it more complex to use, maybe
        # it should be clarified when someone will need to use override=False
        # and replace=False. And also why silent failure here is preferred over
        # raising an exception.
        return self.namespace_manager.bind(
            prefix, namespace, override=override, replace=replace
        )

    def namespaces(self) -> Generator[Tuple[str, URIRef], None, None]:
        """Generator over all the prefix, namespace tuples"""
        for prefix, namespace in self.namespace_manager.namespaces():  # noqa: F402
            yield prefix, namespace


    def n3(self, namespace_manager: Optional[NamespaceManager] = None) -> str:
        """Return an n3 identifier for the Dataset."""
        raise NotImplementedError

    def __reduce__(self) -> Tuple[Type[Graph], Tuple[Store, Node]]:
        """Support for pickling the Dataset."""
        raise NotImplementedError

    def isomorphic(self, other: Dataset, compare_graphs: bool = True) -> bool:
        """Check if two Datasets are isomorphic.

        - If `compare_graphs` is True, checks that all named graphs are isomorphic as well.
        - Otherwise, only the default graphs are compared.
        """
        raise NotImplementedError

    def connected(self) -> bool:
        """Check if the Dataset is connected, treating it as undirected."""
        raise NotImplementedError

    def all_nodes(self) -> Set[Node]:
        """Return all nodes in the Dataset."""
        raise NotImplementedError

    def collection(self, identifier: Node) -> Collection:
        """Create a new Collection instance for the given identifier."""
        raise NotImplementedError

    def resource(self, identifier: Union[Node, str]) -> Resource:
        """Create a new Resource instance for the given identifier."""
        raise NotImplementedError

    def _process_skolem_tuples(self, target: Graph, func: Callable[[Tuple[Node, Node, Node]], Tuple[Node, Node, Node]]) -> None:
        """Helper function to apply a transformation to skolemized triples."""
        raise NotImplementedError

    def skolemize(
        self,
        new_dataset: Optional[Dataset] = None,
        bnode: Optional[BNode] = None,
        authority: Optional[str] = None,
        basepath: Optional[str] = None,
    ) -> Dataset:
        """Convert Blank Nodes within the Dataset to skolemized URIs."""
        raise NotImplementedError

    def de_skolemize(
        self, new_dataset: Optional[Dataset] = None, uriref: Optional[URIRef] = None
    ) -> Dataset:
        """Convert skolemized URIs back into blank nodes."""
        raise NotImplementedError

    def cbd(self, resource: Node, graphs: _GraphSliceType = None) -> Graph:
        """Retrieve the Concise Bounded Description (CBD) of a resource.

        If `graphs` is specified, the CBD is computed from those graphs only.
        Otherwise, it is computed from the entire Dataset.
        """
        raise NotImplementedError
