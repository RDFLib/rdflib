# -*- coding: utf-8 -*-
"""
An adaptation of the BerkeleyDB Store's key-value approach to use the
Python shelve module as a back-end.
"""

import collections
import logging
import os
import shutil
import sqlite3
from functools import lru_cache
from operator import itemgetter
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generator,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
    cast,
)
from urllib.request import pathname2url

from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, Graph
from rdflib.paths import Path
from rdflib.store import NO_STORE, VALID_STORE, Store
from rdflib.term import BNode, Identifier, Literal, Node, URIRef, Variable

if TYPE_CHECKING:
    from rdflib.graph import _ContextType, _TriplePatternType, _TripleType

logger = logging.getLogger(__name__)

__all__ = ["SQLiteDBStore"]


"""
Taken from https://bugs.python.org/file12933/dbsqlite.py, posted to
https://bugs.python.org/issue3783

Dbm based on sqlite -- Needed to support shelves

Key and values are always stored as bytes. This means that when strings are
used they are implicitly converted to the default encoding before being
stored.

Issues:

    # ??? how to coordinate with whichdb
    # ??? Any difference between blobs and text
    # ??? does default encoding affect str-->bytes or PySqlite3 always use UTF-8
    # ??? what is the correct isolation mode

    >>> d = SQLhash()
    >>> list(d)
    []
    >>> print(list(d), "start")
    [] start
    >>> d["abc"] = "lmno"
    >>> print(d["abc"])
    lmno
    >>> d["abc"] = "rsvp"
    >>> d["xyz"] = "pdq"
    >>> print(d.items())  # doctest: +ELLIPSIS
    SQLhashItemsView(<rdflib.plugins.stores.sqlitedb.SQLhash object at 0x...>)
    >>> print(d.values())  # doctest: +ELLIPSIS
    SQLhashValuesView(<rdflib.plugins.stores.sqlitedb.SQLhash object at 0x...>)
    >>> print(d.keys())  # doctest: +ELLIPSIS
    SQLhashKeysView(<rdflib.plugins.stores.sqlitedb.SQLhash object at 0x...>)
    >>> print(list(d), "list")
    ['abc', 'xyz'] list
    >>> d.update(p="x", q="y", r="z")
    >>> print(d.items())  # doctest: +ELLIPSIS
    SQLhashItemsView(<rdflib.plugins.stores.sqlitedb.SQLhash object at 0x...>)
    >>> del d["abc"]
    >>> try:
    ...     print(d["abc"])
    ... except KeyError:
    ...     pass
    ... else:
    ...     raise Exception("oh noooo!")
    >>> try:
    ...     del d["abc"]
    ... except KeyError:
    ...     pass
    ... else:
    ...     raise Exception("drat!")
    >>> print(list(d))
    ['xyz', 'p', 'q', 'r']
    >>> print(bool(d), True)
    True True
    >>> d.clear()
    >>> print(bool(d), False)
    False False
    >>> print(list(d))
    []
    >>> d.update(p="x", q="y", r="z")
    >>> print(list(d))
    ['p', 'q', 'r']
    >>> d["xyz"] = "pdq"
    >>> d.close()

"""

error = sqlite3.DatabaseError


class ListRepr:
    def __repr__(self) -> str:
        return repr(list(self))  # type: ignore[call-overload]  # pragma: no cover


class SQLhashKeysView(collections.abc.KeysView, ListRepr):
    def __iter__(self):
        qstr = "SELECT key FROM shelf ORDER BY ROWID"
        return map(itemgetter(0), self._mapping.conn.cursor().execute(qstr))


class SQLhashValuesView(collections.abc.ValuesView, ListRepr):
    def __iter__(self) -> Iterator[object]:
        qstr = "SELECT value FROM shelf ORDER BY ROWID"
        return map(itemgetter(0), self._mapping.conn.cursor().execute(qstr))  # type: ignore[attr-defined]


class SQLhashItemsView(collections.abc.ValuesView, ListRepr):
    def __iter__(self) -> Iterator[Any]:
        qstr = "SELECT key, value FROM shelf ORDER BY ROWID"
        return iter(self._mapping.conn.cursor().execute(qstr))  # type: ignore[attr-defined]


class SQLhash(collections.abc.MutableMapping):
    def __init__(self, filename: str = ":memory:", flags: str = "r", mode: Any = None):
        # XXX add flag/mode handling
        #   c -- create if it doesn't exist
        #   n -- new empty
        #   w -- open existing
        #   r -- readonly

        qstr = "CREATE TABLE IF NOT EXISTS shelf (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        self.conn = sqlite3.connect(filename, check_same_thread=False)
        self.conn.text_factory = str
        self.conn.execute(qstr)
        self.conn.commit()

    def close(self) -> None:
        try:
            if self.conn is not None:
                self.conn.commit()
                self.conn.close()
                self.conn = None  # type: ignore[assignment]
        except Exception:  # pragma: no cover
            pass  # pragma: no cover

    def __del__(self) -> None:
        self.close()

    def keys(self) -> "SQLhashKeysView":
        return SQLhashKeysView(self)

    def values(self) -> "SQLhashValuesView":
        return SQLhashValuesView(self)

    def items(self) -> "SQLhashItemsView":  # type: ignore[override]
        return SQLhashItemsView(self)
        # self.conn.commit()

    def update(self, items=(), **kwds) -> None:  # type: ignore[override]
        if isinstance(items, collections.abc.Mapping):
            items = items.items()
        qstr = "REPLACE INTO shelf (key, value) VALUES (?, ?)"
        self.conn.executemany(qstr, items)
        self.conn.commit()
        if kwds:
            self.update(kwds)

    def clear(self) -> None:
        qstr = "DELETE FROM shelf;  VACUUM;"
        self.conn.executescript(qstr)
        self.conn.commit()

    def sync(self) -> None:
        if self.conn is not None:
            self.conn.commit()

    def __getitem__(self, key: object) -> Any:
        qstr = "SELECT value FROM shelf WHERE key = ?"
        item = self.conn.execute(qstr, (key,)).fetchone()
        if item is None:
            raise KeyError(key)
        return item[0]

    def __setitem__(self, key: object, value: object) -> None:
        qstr = "REPLACE INTO shelf (key, value) VALUES (?,?)"
        self.conn.execute(qstr, (key, value))
        # self.conn.commit()

    def __delitem__(self, key: object) -> None:
        if key not in self:
            raise KeyError(key)
        qstr = "DELETE FROM shelf WHERE key = ?"
        self.conn.execute(qstr, (key,))

    def __iter__(self) -> Iterator[object]:
        return iter(self.keys())

    def __contains__(self, key: object) -> bool:
        qstr = "SELECT 1 FROM shelf WHERE key = ?"
        return self.conn.execute(qstr, (key,)).fetchone() is not None

    def __len__(self) -> int:
        qstr = "SELECT COUNT(*) FROM shelf"
        return cast(int, self.conn.execute(qstr).fetchone()[0])

    def __bool__(self) -> bool:
        qstr = "SELECT MAX(ROWID) FROM shelf"  # returns None if count is zero
        return self.conn.execute(qstr).fetchone()[0] is not None


"""
Based on an original contribution by Drew Perttula: `TokyoCabinet Store
<http://bigasterisk.com/darcs/?r=tokyo;a=tree>`_.

and then a Kyoto Cabinet version by Graham Higgins <gjh@bel-epa.com>

this one by Graham Higgins

"""


class SQLiteDBStore(Store):
    """
    A store that allows for on-disk persistent using sqite3 as a
    key/value DB.

    This store allows for quads as well as triples. See examples of use
    in both the `examples.sqlitedb_example` and `test.test_stores`
    files.

    """

    context_aware = True
    formula_aware = True
    transaction_aware = False
    graph_aware = True
    db_env = None
    should_create = True

    def __init__(
        self,
        configuration: Optional[str] = None,
        identifier: Optional["Identifier"] = None,
    ) -> None:
        self.__open = False
        self._terms = 0
        self.__identifier = identifier
        super(SQLiteDBStore, self).__init__(configuration)
        self._loads = self.node_pickler.loads
        self._dumps = self.node_pickler.dumps
        self.dbdir = configuration
        self.__indices: List[Any] = [None] * 3
        self.__indices_info: List[Any] = [None] * 3

    def __get_identifier(self) -> Optional["Identifier"]:
        return self.__identifier  # pragma: no cover

    identifier = property(__get_identifier)

    def is_open(self) -> bool:
        return self.__open

    def open(self, path: Union[str, "os.PathLike[Any]"], create: bool = False) -> int:
        self.should_create = create
        self.path = path

        if self.__identifier is None:
            self.__identifier = URIRef(pathname2url(os.path.abspath(path)))

        dbpathname = os.path.abspath(self.path)
        # Help the user to avoid writing over an existing database
        if self.should_create is True:
            if os.path.exists(dbpathname):
                if os.listdir(dbpathname) != []:
                    raise Exception(
                        f"Database {dbpathname} aready exists, please move or delete it. {os.listdir(dbpathname)}"
                    )
                else:
                    self.dbdir = dbpathname  # pragma: no cover
            else:
                os.mkdir(dbpathname)
                self.dbdir = dbpathname
        else:
            if not os.path.exists(dbpathname):
                return NO_STORE
            else:
                self.dbdir = dbpathname

        dbopenflag = "c" if create is True else "w"
        for i in range(0, 3):
            index_name = to_key_func(i)(
                (
                    "s",
                    "p",
                    "o",
                ),
                "c",
            )
            index = SQLhash(os.path.join(self.dbdir, index_name + ".db"), dbopenflag)
            self.__indices[i] = index
            self.__indices_info[i] = (index, to_key_func(i), from_key_func(i))

        lookup = {}
        for i in range(0, 8):
            results = []
            for start in range(0, 3):
                score = 1
                _len = 0
                for j in range(start, start + 3):
                    if i & (1 << (j % 3)):
                        score = score << 1
                        _len += 1
                    else:
                        break
                tie_break = 2 - start
                results.append(((score, tie_break), start, _len))

            results.sort()
            score, start, _len = results[-1]  # type: ignore  # Incompatible types in assignment (expression has type "Tuple[int, int]", variable has type "int")

            def get_prefix_func(
                start: Any, end: Any
            ) -> Callable[[Tuple[Any, Any, Any], Any], Generator[Any, Any, Any]]:
                def get_prefix(
                    triple: Tuple[Any, Any, Any], context: Any
                ) -> Generator[str, None, None]:
                    if context is None:
                        yield ""
                    else:
                        yield context
                    i = start
                    while i < end:
                        yield triple[i % 3]
                        i += 1
                    yield ""

                return get_prefix

            lookup[i] = (
                self.__indices[start],
                get_prefix_func(start, start + _len),
                from_key_func(start),
                results_from_key_func(start, self._from_string),
            )

        self.__lookup_dict = lookup
        self.__contexts = SQLhash(os.path.join(self.dbdir, "contexts.db"), dbopenflag)
        self.__namespace = SQLhash(os.path.join(self.dbdir, "namespace.db"), dbopenflag)
        self.__prefix = SQLhash(os.path.join(self.dbdir, "prefix.db"), dbopenflag)
        self.__k2i = SQLhash(os.path.join(self.dbdir, "k2i.db"), dbopenflag)
        self.__i2k = SQLhash(os.path.join(self.dbdir, "i2k.db"), dbopenflag)

        try:
            self._terms = int(self.__k2i["__terms__"])
            assert isinstance(self._terms, int)  # pragma: no cover
        except KeyError:
            pass  # new store, no problem

        self.__open = True

        return VALID_STORE

    def close(self, commit_pending_transaction: bool = False) -> None:
        if not self.__open:
            return
        self.__open = False
        for i in self.__indices:
            i.close()
        self.__contexts.close()
        self.__namespace.close()
        self.__prefix.close()
        self.__i2k.close()
        self.__k2i.close()

    def dumpdb(self) -> str:
        assert self.__open, "The Store must be open."
        dump = "\n"
        dbs = {
            "self.__contexts": self.__contexts,
            "self.__namespace": self.__namespace,
            "self.__prefix": self.__prefix,
            "self.__k2i": self.__k2i,
            "self.__i2k": self.__i2k,
            "self.__indices": self.__indices,
        }

        for name, entry in dbs.items():
            dump += f"db: {name}\n"
            if isinstance(entry, list):
                for db in entry:
                    for key, value in db.items():
                        dump += f"\t{key}: {value}\n"
            else:
                for key, value in entry.items():  # type: ignore  # "object" has no attribute "keys"
                    dump += f"\t{key}: {value}\n"
        return dump

    def destroy(self, configuration: str = "") -> None:
        assert self.__open is False, "The Store must be closed."

        path = configuration or self.dbdir
        if os.path.exists(path):  # type: ignore  # Argument 1 to "exists" has incompatible type "Union[str, PathLike[Any], None]"; expected "Union[Union[str, bytes, PathLike[str], PathLike[bytes]], int]"
            try:
                shutil.rmtree(path)  # type: ignore  # Argument 1 to "rmtree" has incompatible type "Union[str, PathLike[Any], None]"; expected "Union[bytes, Union[str, PathLike[str]]]"
            except Exception as e:
                logger.warn(f"Failed to destroy datasbse at {path}: {e}")

    def add(
        self, triple: Tuple[Any, Any, Any], context: Any, quoted: bool = False
    ) -> None:
        """
        Add a triple to the store of triples.
        """

        (subject, predicate, object) = triple
        assert self.__open, "The Store must be open."
        assert context != self, "Can not add triple directly to store"

        _to_string = self._to_string

        s = _to_string(subject)
        p = _to_string(predicate)
        o = _to_string(object)
        c = _to_string(context)

        cspo, cpos, cosp = self.__indices

        try:
            value = cspo[f"{c}^{s}^{p}^{o}^"]
        except KeyError:
            value = None

        if value is None:
            self.__contexts[c] = ""

            try:
                contexts_value = cspo[f"{''}^{s}^{p}^{o}^"]
            except KeyError:
                contexts_value = ""
            contexts = set(contexts_value.split("^"))
            contexts.add(c)

            contexts_value = "^".join(contexts)
            assert contexts_value is not None

            cspo[f"{c}^{s}^{p}^{o}^"] = ""
            cpos[f"{c}^{p}^{o}^{s}^"] = ""
            cosp[f"{c}^{o}^{s}^{p}^"] = ""
            if not quoted:
                cspo[f"^{s}^{p}^{o}^"] = contexts_value
                cpos[f"^{p}^{o}^{s}^"] = contexts_value
                cosp[f"^{o}^{s}^{p}^"] = contexts_value

        # Trigger the Store's TripleAdded events
        Store.add(self, (subject, predicate, object), context, quoted)

    def __remove(self, spo: Tuple[Any, Any, Any], c: Any, quoted: bool = False) -> None:
        s, p, o = spo
        cspo, cpos, cosp = self.__indices
        try:
            contexts_value = cspo[f"^{s}^{p}^{o}^"]
        except KeyError:
            contexts_value = ""
        contexts = set(contexts_value.split("^"))
        contexts.discard(c)
        contexts_value = "^".join(contexts)
        for i, _to_key, _from_key in self.__indices_info:
            del i[_to_key((s, p, o), c)]
        if not quoted:
            if contexts_value:
                for i, _to_key, _from_key in self.__indices_info:
                    i[_to_key((s, p, o), "")] = contexts_value

            else:
                for i, _to_key, _from_key in self.__indices_info:
                    try:
                        del i[_to_key((s, p, o), "")]
                    except Exception:  # pragma: no cover
                        pass  # FIXME okay to ignore these?

    def remove(self, spo: Any, context: Any = None) -> Any:
        subject, predicate, object = spo
        assert self.__open, "The Store must be open."
        _to_string = self._to_string

        if context is not None:
            if context == self:
                context = None

        if (
            subject is not None
            and predicate is not None
            and object is not None
            and context is not None
        ):
            s = _to_string(subject)
            p = _to_string(predicate)
            o = _to_string(object)
            c = _to_string(context)
            try:
                value = self.__indices[0][f"{c}^{s}^{p}^{o}^"]
            except KeyError:
                value = None
            if value is not None:
                self.__remove((s, p, o), c)
        else:
            index, prefix, from_key, results_from_key = self.__lookup(
                (subject, predicate, object), context
            )

            for key in index.keys():
                if key.startswith(prefix):
                    c, s, p, o = from_key(key)
                    if context is None:
                        try:
                            contexts_value = index[key]
                        except KeyError:  # pragma: no cover
                            contexts_value = ""  # pragma: no cover
                        # remove triple from all non quoted contexts
                        contexts = set(contexts_value.split("^"))
                        # and from the conjunctive index
                        contexts.add("")
                        for c in contexts:
                            for i, _to_key, _ in self.__indices_info:
                                del i[_to_key((s, p, o), c)]
                    else:
                        self.__remove((s, p, o), c)

            if context is not None:
                ctxkey = _to_string(context)
                if (
                    subject is None
                    and predicate is None
                    and object is None
                    and ctxkey in self.__contexts.keys()
                ):
                    # TODO: also if context becomes empty and not just on
                    try:
                        del self.__contexts[ctxkey]
                    except KeyError as e:  # pragma: no cover
                        raise Exception(f"OOps {e}")
                        # pass  # pragma: no cover
        # Trigger the Store's TripleRemoved event
        Store.remove(self, (subject, predicate, object), context)

    def triples(
        self,
        spo: "_TriplePatternType",
        context: Optional["_ContextType"] = None,
        txn: Optional[Any] = None,
    ) -> Generator[
        Tuple["_TripleType", Generator[Optional["_ContextType"], None, None]],
        None,
        None,
    ]:
        """A generator over all the triples matching"""
        assert self.__open, "The Store must be open."

        subject, predicate, object = spo

        if context is not None:
            if context == self:
                context = None  # pragma: no cover

        index, prefix, from_key, results_from_key = self.__lookup(
            (subject, predicate, object), context
        )

        for key in index.keys():
            if key.startswith(prefix):
                yield results_from_key(key, subject, predicate, object, index[key])

    def __len__(self, context: Any = None) -> int:
        assert self.__open, "The Store must be open."
        if context is not None:
            if context == self:
                context = None

        if context is None:
            prefix = "^"
        else:
            prefix = f"{self._to_string(context)}^"

        # Return the number of keys into the cspo index
        return len([key for key in self.__indices[0].keys() if key.startswith(prefix)])

    def bind(self, prefix: str, namespace: URIRef, override: bool = True) -> None:
        assert self.__open, "The Store must be open."
        try:
            bound_prefix = self.__prefix[namespace]
        except KeyError:
            bound_prefix = None
        try:
            bound_namespace = self.__namespace[prefix]
        except KeyError:
            bound_namespace = None

        if override:
            if bound_prefix:
                del self.__namespace[bound_prefix]
            if bound_namespace:
                del self.__prefix[bound_namespace]
            self.__prefix[namespace] = prefix
            self.__namespace[prefix] = namespace
        else:
            self.__prefix[bound_namespace or namespace] = bound_prefix or prefix
            self.__namespace[bound_prefix or prefix] = bound_namespace or namespace

    def unbind(self, prefix: str) -> None:
        assert self.__open, "The Store must be open."
        try:
            ns = self.__namespace[prefix]
        except KeyError:
            ns = None
        if ns is not None:
            del self.__namespace[prefix]
            del self.__prefix[ns]

    def namespace(self, prefix: str) -> Union[URIRef, None]:
        assert self.__open, "The Store must be open."
        ns = self.__namespace.get(prefix, None)
        if ns is not None:
            return URIRef(ns)
        return None

    def prefix(self, namespace: URIRef) -> Union[str, None]:
        assert self.__open, "The Store must be open."
        try:
            prefix = self.__prefix[namespace]
        except KeyError:
            prefix = None
        if prefix is not None:
            return prefix
        return None

    def namespaces(self) -> Generator[Tuple[str, URIRef], None, None]:
        assert self.__open, "The Store must be open."
        for k in self.__namespace.keys():
            yield k, URIRef(self.__namespace[k])

    def contexts(
        self, triple: Optional["_TripleType"] = None
    ) -> Generator["_ContextType", None, None]:
        assert self.__open, "The Store must be open."
        _from_string = self._from_string
        _to_string = self._to_string

        if triple:
            subj, pred, obj = triple
            if subj and pred and obj:
                s = _to_string(subj)
                p = _to_string(pred)
                o = _to_string(obj)
                for c in self.__contexts.keys():
                    if self.__indices[0].get(f"{c}^{s}^{p}^{o}^") is not None:
                        # Incompatible types in "yield" (actual type "Node", expected type "Graph")
                        yield _from_string(c)  # type: ignore[misc]
            else:
                for k in self.__contexts:
                    index, prefix, from_key, results_from_key = self.__lookup(
                        (subj, pred, obj), _from_string(k)
                    )
                    for key in index.keys():
                        if key.startswith(prefix):
                            # Incompatible types in "yield" (actual type "Node", expected type "Graph")
                            yield _from_string(k)  # type: ignore[misc]

        else:
            for k in self.__contexts.keys():
                # Incompatible types in "yield" (actual type "Node", expected type "Graph")
                yield _from_string(k)  # type: ignore[misc]

    def add_graph(self, graph: "Graph") -> None:
        assert self.__open, "The Store must be open."
        self.__contexts[self._to_string(graph)] = b""
        for t in graph:
            self.add(t, graph)

    def remove_graph(self, graph: "Graph") -> None:
        assert self.__open, "The Store must be open."
        self.remove((None, None, None), graph)

    @lru_cache(maxsize=5000)
    def _from_string(self, i: str) -> Node:
        """
        rdflib term from index number (as a string)
        """
        assert isinstance(i, (bytes, str)) is True
        try:
            k = self.__i2k[str(int(i))]
        except KeyError:
            k = None
        if k is not None:
            return self._loads(k)
        else:
            raise Exception(f"Key for {i} is None")  # pragma: no cover

    @lru_cache(maxsize=5000)
    def _to_string(self, term: Node) -> str:
        """
        index number (as a string) from rdflib term
        if term is not already in the database, add it
        """
        assert isinstance(
            term, (BNode, Graph, Literal, Path, URIRef, Variable, type(None))
        )
        k = self._dumps(term)
        try:
            i = self.__k2i[k]
        except KeyError:  # pragma: no cover
            i = None  # pragma: no cover

        if i is None:  # (from BdbApi)
            # Does not yet exist, increment refcounter and create
            self._terms += 1
            i = str(self._terms)
            self.__i2k[i] = k
            self.__k2i[k] = i
            self.__k2i[b"__terms__"] = str(self._terms)

        return i

    def __lookup(self, spo: Any, context: Any) -> Any:
        subject, predicate, object = spo
        _to_string = self._to_string
        if context is not None:
            context = _to_string(context)
        i = 0
        if subject is not None:
            i += 1
            subject = _to_string(subject)
        if predicate is not None:
            i += 2
            predicate = _to_string(predicate)
        if object is not None:
            i += 4
            object = _to_string(object)
        index, prefix_func, from_key, results_from_key = self.__lookup_dict[i]
        prefix = "^".join(prefix_func((subject, predicate, object), context))

        return index, prefix, from_key, results_from_key


def to_key_func(i: Any) -> Callable[..., str]:
    def to_key(triple: Tuple[Any, Any, Any], context: Any) -> str:
        "Takes a string; returns key"
        return "^".join(
            (
                context,
                triple[i % 3],
                triple[(i + 1) % 3],
                triple[(i + 2) % 3],
                "",
            )
        )  # "" to tac on the trailing ^

    return to_key


def from_key_func(i: Any) -> Callable[[Any], Tuple[Any, Any, Any, Any]]:
    def from_key(key: Any) -> Tuple[Any, Any, Any, Any]:
        "Takes a key; returns string"
        parts = key.split("^")
        return (
            parts[0],
            parts[(3 - i + 0) % 3 + 1],
            parts[(3 - i + 1) % 3 + 1],
            parts[(3 - i + 2) % 3 + 1],
        )

    return from_key


def results_from_key_func(
    i: int, from_string: Callable[[str], Any]
) -> Callable[..., Any]:
    def from_key(
        key: Any, subject: Any, predicate: Any, object: Any, contexts_value: Any
    ) -> Tuple[Tuple[Any, Any, Any], Generator["Graph", None, None]]:
        "Takes a key and subject, predicate, object; returns tuple for yield"
        parts = key.split("^")
        if subject is None:
            # TODO: i & 1: # dis assemble and/or measure to see which is faster
            # subject is None or i & 1
            s = from_string(parts[(3 - i + 0) % 3 + 1])
        else:
            s = subject
        if predicate is None:  # i & 2:
            p = from_string(parts[(3 - i + 1) % 3 + 1])
        else:
            p = predicate
        if object is None:  # i & 4:
            o = from_string(parts[(3 - i + 2) % 3 + 1])
        else:
            o = object
        return (  # pragma: no cover
            (s, p, o),
            (from_string(c) for c in contexts_value.split("^") if c),
        )

    return from_key


def readable_index(i: int) -> str:
    # type error: Unpacking a string is disallowed
    s, p, o = "?" * 3  # type: ignore[misc]
    if i & 1:
        s = "s"
    if i & 2:
        p = "p"
    if i & 4:
        o = "o"

    return f"{s},{p},{o}"
