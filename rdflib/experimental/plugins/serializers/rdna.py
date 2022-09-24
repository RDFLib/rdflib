"""
Copyright (c) 2022 The RDFLib Team
Python adaptation of the Digital Bazaar Javscript implementation
https://github.com/digitalbazaar/rdf-canonize
for RDFLib by Graham Higgins <gjh@bel-epa.com>
"""
import hashlib
import typing
from collections import OrderedDict
from functools import cmp_to_key
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
)

from rdflib.graph import Dataset, QuotedGraph
from rdflib.plugins.serializers.nt import _quoteLiteral
from rdflib.serializer import Serializer
from rdflib.term import BNode, Literal, URIRef

if TYPE_CHECKING:
    from _hashlib import HASH  # pragma: no cover

Subject = Union[URIRef, BNode, str]
# Predicate = Union[URIRef, Path]
Predicate = URIRef
Object = Union[URIRef, BNode, Literal, str]

ContextNode = Union[BNode, URIRef, str]
DatasetQuad = Tuple[Subject, Predicate, Object, Optional[ContextNode]]

__all__ = ["RDNASerializer", "IdentifierIssuer"]


DATASET_DEFAULT_GRAPH_ID = URIRef("urn:x-rdflib:default")


class RDNASerializer(Serializer):
    def __init__(self, dataset) -> None:
        self.dataset = dataset

        Serializer.__init__(self, dataset)

    def serialize(
        self,
        stream: IO[bytes],
        base: Optional[str] = None,
        encoding: Optional[str] = "utf-8",
        **kwargs,
    ):
        stream.write(RDNA().normalize(self.dataset).encode("utf-8"))


class RDNAGraphCanonicalizer:
    def __init__(self, dataset) -> None:
        self.dataset = dataset

    def canonicalize(
        self,
        base: Optional[str] = None,
        encoding: Optional[str] = "utf-8",
        **kwargs,
    ):
        return RDNA().normalize(self.dataset, return_graph=True)


class IdentifierIssuer:
    """
    Creates a new IdentifierIssuer. A IdentifierIssuer issues unique
    identifiers, keeping track of any previously issued identifiers.

    @param prefix the prefix to use ('<prefix><counter>').
    @param existing an existing Map to use.
    @param counter the counter to use.
    """

    def __init__(
        self,
        prefix: Optional[str] = None,
        existing: Optional["OrderedDict[str, str]"] = None,
        counter: int = 0,
    ):
        self.prefix = prefix or "_:c14n"
        self._existing = existing or OrderedDict()
        self.counter = counter

    """
    Copies self IdentifierIssuer.

    @return a copy of self IdentifierIssuer.
    """

    def clone(self) -> "IdentifierIssuer":
        return IdentifierIssuer(
            self.prefix, OrderedDict(**self._existing), self.counter
        )

    """
    Gets the new identifier for the given old identifier, where if no old
    identifier is given a new identifier will be generated.

    @param [old] the old identifier to get the new identifier for.

    @return the new identifier.
    """

    def get_id(self, old: Optional[str] = None) -> str:

        # return existing old identifier
        existing = old and self._existing.get(old)

        if existing:
            return existing

        # get next identifier
        identifier = self.prefix + str(self.counter)

        self.counter += 1

        # save mapping
        if old:
            self._existing[old] = identifier

        return identifier

    """
    Returns true if the given old identifer has already been assigned a new
    identifier.
     *
    @param old the old identifier to check.
     *
    @return true if the old identifier has been assigned a new identifier,
      false if not.
    """

    def has_id(self, old: str) -> bool:
        return True if self._existing.get(old, False) else False

    """
    Returns all of the IDs that have been issued new IDs in the order in
    which they were issued new IDs.
     *
    @return the list of old IDs that has been issued new IDs in order.
    """

    def get_old_ids(self) -> Iterable[str]:
        return self._existing.keys()


def sjt_permute(items: List[Any]) -> Generator[List[Any], None, None]:
    # https://stackoverflow.com/a/31218476
    num = len(items)
    if num == 1:
        yield items[:1]
        return

    last = items[-1:]
    uprange = range(num)
    dnrange = uprange[::-1]
    descend = True
    for perm in sjt_permute(items[:-1]):
        rng = dnrange if descend else uprange
        for i in rng:
            yield perm[:i] + last + perm[i:]
        descend = not descend


_HashT = Callable[[], "HASH"]


class MessageDigest:
    """
    * Creates a new MessageDigest.
    *
    * @param algorithm the algorithm to use.
    """

    def __init__(self, hashfunc: _HashT = hashlib.sha256) -> None:

        self.md = hashfunc()

    def update(self, msg: str) -> None:
        self.md.update(str(msg).encode("utf8"))

    def digest(self) -> int:
        return int(self.md.hexdigest(), 16)


class RDNA:
    def __init__(self) -> None:
        self.blank_node_info: "OrderedDict[str, typing.Dict[Any, Any]]" = OrderedDict()
        self.canonical_issuer = IdentifierIssuer("_:c14n")
        self.hash_algorithm: _HashT = hashlib.sha256
        self.quads: List[Any] = []
        self.hash_to_blank_nodes: "Dict[str, List[Any]]" = dict()

    def __use_canonical_id(self, x: Any) -> Any:
        return (
            self.canonical_issuer.get_id(x.n3())
            if isinstance(x, BNode)
            and not x.n3().startswith(self.canonical_issuer.prefix)
            else x
        )

    # 4.4) Normalization Algorithm
    def normalize(self, dataset: Dataset, return_graph=False) -> str:
        # Stash the dataset quads
        self.quads = sorted(list(dataset))

        # 1) Create the normalization state.
        # 2) For every quad in input dataset:
        for quad in self.quads:
            # 2.1) For each blank node that occurs in the quad, add a reference
            # to the quad using the blank node identifier in the blank node to
            # quads map, creating a new entry if necessary.
            for term in quad:
                if isinstance(term, BNode):
                    _id = term.n3()
                    info = self.blank_node_info.get(_id, None)
                    if info:
                        info["quads"].append(quad)
                        self.blank_node_info[_id] = info
                    else:
                        self.blank_node_info[_id] = dict(quads=[quad], digest=None)

        # 3) Create a list of non-normalized blank node identifiers
        # non-normalized identifiers and populate it using the keys from the
        # blank node to quads map.
        # Note: We use a map here and it was generated during step 2.

        # 4) `simple` flag is skipped -- loop is optimized away. This optimization
        # is permitted because there was a typo in the hash first degree quads
        # algorithm in the RDNA spec that was implemented widely making it
        # such that it could not be fixed; the result was that the loop only
        # needs to be run once and the first degree quad hashes will never change.
        # 5.1-5.2 are skipped; first degree quad hashes are generated just once
        # for all non-normalized blank nodes.

        # 5.3) For each blank node identifier identifier in non-normalized
        # identifiers:

        for _id in list(self.blank_node_info.keys()):  # non_normalized ids

            # 5.3.1) Create a hash, _hash, according to the Hash First Degree
            # Quads algorithm.
            _hash = self.hash_first_degree_quads(_id)

            # 5.3.2) Add _hash and identifier key to blank nodes map,
            # creating a new entry if necessary.

            if not self.hash_to_blank_nodes.get(_hash):
                self.hash_to_blank_nodes[_hash] = [_id]
            else:
                self.hash_to_blank_nodes[_hash].append(_id)

        # 5.4) For each hash to identifier list mapping in hash to blank
        # nodes map, lexicographically-sorted by hash:
        # optimize away second sort, gather non-unique hashes in order as we go

        non_unique = []
        for hsh in sorted(list(self.hash_to_blank_nodes.keys())):
            # 5.4.1) If the length of identifier list is greater than 1,
            # continue to the next mapping.
            id_list = self.hash_to_blank_nodes[hsh]

            if len(id_list) > 1:
                non_unique.append(id_list)
                continue
            else:
                # 5.4.2) Use the Issue Identifier algorithm, passing canonical
                # issuer and the single blank node identifier in identifier
                # list, identifier, to issue a canonical replacement identifier
                # for identifier.

                _id = id_list[0]
                self.canonical_issuer.get_id(_id)

            # Note: These steps are skipped, optimized away since the loop
            # only needs to be run once.
            # 5.4.3) Remove identifier from non-normalized identifiers.
            # 5.4.4) Remove hash from the hash to blank nodes map.
            # 5.4.5) Set simple to true.

        # 6) For each hash to identifier list mapping in hash to blank nodes map,
        # lexicographically-sorted by hash:
        # Note: sort optimized away, use `non_unique`.
        for id_list in non_unique:
            # 6.1) Create hash path list where each item will be a result of
            # running the Hash N-Degree Quads algorithm.
            hash_path_list: List[Any] = []

            # 6.2) For each blank node identifier identifier in identifier list:
            for _id in id_list:
                # 6.2.1) If a canonical identifier has already been issued for
                # identifier, continue to the next identifier.
                if self.canonical_issuer.has_id(_id):
                    continue

                # 6.2.2) Create temporary issuer, an identifier issuer
                # initialized with the prefix _:b.
                issuer = IdentifierIssuer("_:b")

                # 6.2.3) Use the Issue Identifier algorithm, passing temporary
                # issuer and identifier, to issue a new temporary blank node
                # identifier for identifier.
                issuer.get_id(_id)

                # 6.2.4) Run the Hash N-Degree Quads algorithm, passing
                # temporary issuer, and append the result to the hash path list.
                hashdigest, issuer = self.hash_ndegree_quads(_id, issuer)
                hash_path_list.append({"digest": hashdigest, "issuer": issuer})

            # 6.3) For each result in the hash path list,
            # lexicographically-sorted by the hashdigest in result:

            hash_path_list.sort(key=cmp_to_key(string_hash_compare))
            for result in hash_path_list:
                # 6.3.1) For each blank node identifier, existing identifier,
                # that was issued a temporary identifier by identifier issuer
                # in result, issue a canonical identifier, in the same order,
                # using the Issue Identifier algorithm, passing canonical
                # issuer and existing identifier.
                for old_id in result["issuer"].get_old_ids():
                    self.canonical_issuer.get_id(old_id)

        """
         Note: At this point all blank nodes in the set of RDF quads have been
        assigned canonical identifiers, which have been stored in the canonical
        issuer. Here each quad is updated by assigning each of its blank nodes
        its new identifier.
        """

        # 7) For each quad, quad, in input dataset:
        # 7.1) Create a copy, quad copy, of quad and replace any existing
        # blank node identifiers using the canonical identifiers
        # previously issued by canonical issuer.
        normalized = []

        dsnormalized = Dataset()

        quads = list(self.quads)

        # Empty graph
        if quads == []:
            return ""

        # Model the triples of a context-unaware Graph as quads in a Dataset default graph
        if len(quads[0]) == 3:
            quads = [(s, p, o, DATASET_DEFAULT_GRAPH_ID) for (s, p, o) in quads]

        for (s, p, o, g) in quads:
            # 7.2) Add quad copy to the normalized dataset.

            if any(isinstance(element, QuotedGraph) for element in [s, p, o]):
                raise Exception("RDNA cannot serialize Graphs that contain Formulae")

            normalized.append(
                self.__serialize_nquad(
                    (
                        self.__use_canonical_id(s),
                        p,
                        self.__use_canonical_id(o),
                        self.__use_canonical_id(g),
                    )
                )
            )

            subj = self.__use_canonical_id(s)
            obj = self.__use_canonical_id(o)
            gid = self.__use_canonical_id(g)

            dsnormalized.add(
                (
                    BNode(subj.replace("_:", ""))
                    if isinstance(subj, str) and subj.startswith("_:")
                    else subj,
                    p,
                    BNode(obj.replace("_:", ""))
                    if isinstance(obj, str) and obj.startswith("_:")
                    else obj,
                    BNode(gid.replace("_:", ""))
                    if isinstance(gid, str) and gid.startswith("_:")
                    else gid,
                )
            )

        if return_graph:
            return dsnormalized
        else:
            # 8) Return the sorted normalized dataset.
            return "".join([*sorted(normalized)])

    # 4.6) Hash First Degree Quads
    def hash_first_degree_quads(self, _id: str) -> Any:

        # helper for modifying component during Hash First Degree Quads
        def modify_first_degree_component(
            _id: str, component: Union[URIRef, BNode]
        ) -> str:
            if not isinstance(component, BNode):
                return component
            else:
                return "_:a" if component.n3() == _id else "_:z"

        # 1) Initialize nquads to an empty list. It will be used to store quads in
        # N-Quads format.
        nquads = []

        # 2) Get the list of quads `quads` associated with the reference blank node
        # identifier in the blank node to quads map.
        info = self.blank_node_info[_id]
        assert isinstance(info, Dict)
        quads = info["quads"]

        # 3) For each quad `quad` in `quads`:
        for quad in quads:
            # 3.1) Serialize the quad in N-Quads format with the following special
            # rule:

            # 3.1.1) If any component in quad is an blank node, then serialize it
            # using a special identifier:

            # 3.1.2) If the blank node's existing blank node identifier matches
            # the reference blank node identifier then use the blank node
            # identifier _:a, otherwise, use the blank node identifier _:z.

            nquads.append(
                self.__serialize_nquad(
                    tuple(  # type: ignore[arg-type]
                        [
                            modify_first_degree_component(_id, component)
                            for component in quad
                        ]
                    )
                )
            )

        # 4) Sort nquads in lexicographical order.
        nquads.sort()

        # 5) Return the hash that results from passing the sorted, joined nquads
        # through the hash algorithm.

        md = MessageDigest(self.hash_algorithm)

        for nquad in nquads:
            md.update(nquad)

        info["digest"] = md.digest()
        self.blank_node_info[_id] = info

        return info["digest"]

    # 4.7) Hash Related Blank Node
    def __hash_related_blank_node(
        self, related: str, quad: DatasetQuad, issuer: IdentifierIssuer, position: str
    ) -> int:
        # 1) Set the identifier to use for related, preferring first the canonical
        # identifier for related if issued, second the identifier issued by issuer
        # if issued, and last, if necessary, the result of the Hash First Degree
        # Quads algorithm, passing related.

        if self.canonical_issuer.has_id(related):
            _id = self.canonical_issuer.get_id(related)
        elif issuer.has_id(related):
            _id = issuer.get_id(related)
        else:
            info = self.blank_node_info.get(related)
            assert isinstance(info, Dict)
            _id = str(info["digest"])

        # 2) Initialize a string input to the value of position.
        # Note: We use a hash object instead.
        md = MessageDigest(self.hash_algorithm)
        md.update(position)

        # 3) If position is not g, append <, the value of the predicate in quad,
        # and > to input.
        if position != "g":
            md.update(f"<{quad[1].n3()}>")
        # 4) Append identifier to input.
        md.update(_id)

        # 5) Return the hash that results from passing input through the hash
        # algorithm.
        return md.digest()

    def __add_related_blank_node_hash(
        self,
        quad: Tuple[Any, Any, Any, Any],
        term: Union[URIRef, BNode],
        position: str,
        _id: str,
        issuer: IdentifierIssuer,
        hash_to_related: "OrderedDict[int, Any]",
    ) -> "OrderedDict[int, Any]":
        if (
            (position == "g" and term is None)
            or not isinstance(term, BNode)
            and not term.n3() == _id
        ):
            return hash_to_related

        # 3.1.1) Set hash to the result of the Hash Related Blank Node
        # algorithm, passing the blank node identifier for component as
        # related, quad, path identifier issuer as issuer, and position as
        # either s, o, or g based on whether component is a subject, object,
        # graph name, respectively.
        related = term.n3()
        _hash = self.__hash_related_blank_node(related, quad, issuer, position)

        # 3.1.2) Add a mapping of hash to the blank node identifier for
        # component to hash to related blank nodes map, adding an entry as
        # necessary.
        entries = hash_to_related.get(_hash)

        if entries:
            entries.append(related)
            hash_to_related[_hash] = entries
        else:
            hash_to_related[_hash] = [related]

        return hash_to_related

    # helper for creating hash to related blank nodes map
    def __create_hash_to_related(
        self, _id: str, issuer: IdentifierIssuer
    ) -> "OrderedDict[int, Any]":
        # 1) Create a hash to related blank nodes map for storing hashes that
        # identify related blank nodes.
        hash_to_related: "OrderedDict[int, Any]" = OrderedDict()

        # 2) Get a reference, quads, to the list of quads in the blank node to
        # quads map for the key identifier.
        info = self.blank_node_info[_id]
        assert isinstance(info, (Dict))
        quads = info["quads"]

        # 3) For each quad in quads:
        for quad in quads:
            if len(quad) == 3:
                g = None
                (s, p, o) = quad
            else:
                (s, p, o, g) = quad
            # 3.1) For each component in quad, if component is the subject, object,
            # or graph name and it is a blank node that is not identified by
            # identifier:
            # steps 3.1.1 and 3.1.2 occur in helpers:
            hash_to_related = self.__add_related_blank_node_hash(
                quad, s, "s", _id, issuer, hash_to_related
            )
            hash_to_related = self.__add_related_blank_node_hash(
                quad, o, "o", _id, issuer, hash_to_related
            )
            hash_to_related = self.__add_related_blank_node_hash(
                quad, g, "g", _id, issuer, hash_to_related
            )

        return hash_to_related

    # 4.8) Hash N-Degree Quads
    def hash_ndegree_quads(
        self, _id: str, issuer: IdentifierIssuer
    ) -> Tuple[int, IdentifierIssuer]:
        # 1) Create a hash to related blank nodes map for storing hashes that
        # identify related blank nodes.
        # Note: 2) and 3) handled within `__create_hash_to_related`
        md = MessageDigest(self.hash_algorithm)
        hash_to_related = self.__create_hash_to_related(_id, issuer)

        # 4) Create an empty string, data to hash.
        # Note: We created a hash object `md` above instead.

        # 5) For each related hash to blank node list mapping in hash to related
        # blank nodes map, sorted lexicographically by related hash:
        hashes = sorted(list(hash_to_related.keys()))
        for _hash in hashes:
            # 5.1) Append the related hash to the data to hash.
            md.update(str(_hash))

            # 5.2) Create a string chosen path.
            chosen_path = ""

            # 5.3) Create an unset chosen issuer variable.
            chosen_issuer: IdentifierIssuer = issuer

            # 5.4) For each permutation of blank node list:
            for permutation in sjt_permute(hash_to_related[_hash]):

                # 5.4.1) Create a copy of issuer, issuer copy.
                issuer_copy = issuer.clone()

                # 5.4.2) Create a string path.
                path = ""

                # 5.4.3) Create a recursion list, to store blank node identifiers
                # that must be recursively processed by this algorithm.
                recursion_list: List[str] = []

                # 5.4.4) For each related in permutation:
                next_permutation = False
                for related in permutation:
                    # 5.4.4.1) If a canonical identifier has been issued for
                    # related, append it to path.
                    if self.canonical_issuer.has_id(related):
                        path += self.canonical_issuer.get_id(related)
                    else:
                        # 5.4.4.2) Otherwise:
                        # 5.4.4.2.1) If issuer copy has not issued an identifier for
                        # related, append related to recursion list.
                        if not issuer_copy.has_id(related):
                            recursion_list.append(related)

                        # 5.4.4.2.2) Use the Issue Identifier algorithm, passing
                        # issuer copy and related and append the result to path.
                        path += issuer_copy.get_id(related)

                    # 5.4.4.3) If chosen path is not empty and the length of path
                    # is greater than or equal to the length of chosen path and
                    # path is lexicographically greater than chosen path, then
                    # skip to the next permutation.
                    # Note: Comparing path length to chosen path length can be optimized
                    # away; only compare lexicographically.
                    if len(chosen_path) != 0 and path > chosen_path:
                        next_permutation = True
                        break

                if next_permutation:
                    continue

                # 5.4.5) For each related in recursion list:
                for related in recursion_list:
                    # 5.4.5.1) Set result to the result of recursively executing
                    # the Hash N-Degree Quads algorithm, passing related for
                    # identifier and issuer copy for path identifier issuer.
                    hashdigest, result_issuer = self.hash_ndegree_quads(
                        related, issuer_copy
                    )

                    # 5.4.5.2) Use the Issue Identifier algorithm, passing issuer
                    # copy and related and append the result to path.
                    path += issuer_copy.get_id(related)

                    # 5.4.5.3) Append <, the hash in result, and > to path.
                    path += f"<{hashdigest}>"

                    # 5.4.5.4) Set issuer copy to the identifier issuer in
                    # result.
                    issuer_copy = result_issuer

                    # 5.4.5.5) If chosen path is not empty and the length of path
                    # is greater than or equal to the length of chosen path and
                    # path is lexicographically greater than chosen path, then
                    # skip to the next permutation.
                    # Note: Comparing path length to chosen path length can be optimized
                    # away; only compare lexicographically.
                    if len(chosen_path) != 0 and path > chosen_path:
                        next_permutation = True
                        break

                if next_permutation:
                    continue

                # 5.4.6) If chosen path is empty or path is lexicographically
                # less than chosen path, set chosen path to path and chosen
                # issuer to issuer copy.
                if len(chosen_path) == 0 or path < chosen_path:
                    chosen_path = path
                    chosen_issuer = issuer_copy

            # 5.5) Append chosen path to data to hash.
            md.update(chosen_path)

            # 5.6) Replace issuer, by reference, with chosen issuer.
            issuer = chosen_issuer

        # 6) Return issuer and the hash that results from passing data to hash
        # through the hash algorithm.

        return md.digest(), issuer

    def __serialize_nquad(self, quad: DatasetQuad) -> str:
        """
        * Converts an RDF quad to an N-Quad string (a single quad).
        *
        * @param quad the RDF quad convert.
        *
        * @return the N-Quad string.
        """

        # Model the triples of a context-unaware Graph as quads in a Dataset default graph
        if len(quad) == 3:
            s, p, o = quad
            g = DATASET_DEFAULT_GRAPH_ID
        else:
            s, p, o, g = quad

        # subject can only be NamedNode or BlankNode
        nquad = s.n3() if isinstance(s, (URIRef, BNode)) else s

        # predicate can only be NamedNode
        nquad += f" {p.n3()} "

        # object is NamedNode, BlankNode, or Literal
        if isinstance(o, (URIRef, BNode, Literal)):
            if isinstance(o, Literal) and getattr(o, "language") is not None:
                o = Literal(o.value, o.language.lower())
            nquad += o.n3() if not isinstance(o, Literal) else _quoteLiteral(o)

        else:
            nquad += o

        # graph can only be NamedNode or BlankNode (or DefaultGraph, but that
        # does not add to `nquad`)

        if isinstance(g, URIRef):
            nquad += f" {g.n3()}"

        elif isinstance(g, str) and g.startswith(self.canonical_issuer.prefix):
            nquad += f" {g}"

        nquad += " .\n"
        return nquad


def string_hash_compare(a: Any, b: Any) -> int:
    if a["digest"] < b["digest"]:
        return -1
    elif a["digest"] > b["digest"]:
        return 1
    else:
        return 0
