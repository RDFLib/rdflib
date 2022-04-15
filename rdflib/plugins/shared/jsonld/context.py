# -*- coding: utf-8 -*-
"""
Implementation of the JSON-LD Context structure. See:

    http://json-ld.org/

"""
# https://github.com/RDFLib/rdflib-jsonld/blob/feature/json-ld-1.1/rdflib_jsonld/context.py

from collections import namedtuple
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Tuple, Union

from rdflib.namespace import RDF

from .errors import (
    INVALID_CONTEXT_ENTRY,
    INVALID_REMOTE_CONTEXT,
    RECURSIVE_CONTEXT_INCLUSION,
)
from .keys import (
    BASE,
    CONTAINER,
    CONTEXT,
    GRAPH,
    ID,
    IMPORT,
    INCLUDED,
    INDEX,
    JSON,
    LANG,
    LIST,
    NEST,
    NONE,
    PREFIX,
    PROPAGATE,
    PROTECTED,
    REV,
    SET,
    TYPE,
    VALUE,
    VERSION,
    VOCAB,
)
from .util import norm_url, source_to_json, split_iri, urljoin, urlsplit

NODE_KEYS = {GRAPH, ID, INCLUDED, JSON, LIST, NEST, NONE, REV, SET, TYPE, VALUE, LANG}


class Defined(int):
    pass


UNDEF = Defined(0)

# From <https://tools.ietf.org/html/rfc3986#section-2.2>
URI_GEN_DELIMS = (":", "/", "?", "#", "[", "]", "@")


class Context(object):
    def __init__(
        self,
        source: Optional[Any] = None,
        base: Optional[str] = None,
        version: Optional[float] = None,
    ):
        self.version = version or 1.0
        self.language = None
        self.vocab = None
        self._base: Optional[str]
        self.base = base
        self.doc_base = base
        self.terms: Dict[str, Any] = {}
        # _alias maps NODE_KEY to list of aliases
        self._alias: Dict[str, List[str]] = {}
        self._lookup: Dict[Tuple[str, Any, Union[Defined, str], bool], Any] = {}
        self._prefixes: Dict[str, Any] = {}
        self.active = False
        self.parent = None
        self.propagate = True
        self._context_cache: Dict[str, Any] = {}
        if source:
            self.load(source)

    @property
    def base(self) -> Optional[str]:
        return self._base

    @base.setter
    def base(self, base: Optional[str]):
        if base:
            hash_index = base.find("#")
            if hash_index > -1:
                base = base[0:hash_index]
        self._base = (
            self.resolve_iri(base)
            if (hasattr(self, "_base") and base is not None)
            else base
        )
        self._basedomain = "%s://%s" % urlsplit(base)[0:2] if base else None

    def subcontext(self, source, propagate=True):
        # IMPROVE: to optimize, implement SubContext with parent fallback support
        parent = self.parent if self.propagate is False else self
        return parent._subcontext(source, propagate)

    def _subcontext(self, source, propagate):
        ctx = Context(version=self.version)
        ctx.propagate = propagate
        ctx.parent = self
        ctx.language = self.language
        ctx.vocab = self.vocab
        ctx.base = self.base
        ctx.doc_base = self.doc_base
        ctx._alias = {k: l[:] for k, l in self._alias.items()}
        ctx.terms = self.terms.copy()
        ctx._lookup = self._lookup.copy()
        ctx._prefixes = self._prefixes.copy()
        ctx._context_cache = self._context_cache
        ctx.load(source)
        return ctx

    def _clear(self):
        self.language = None
        self.vocab = None
        self.terms = {}
        self._alias = {}
        self._lookup = {}
        self._prefixes = {}
        self.active = False
        self.propagate = True

    def get_context_for_term(self, term):
        if term and term.context is not UNDEF:
            return self._subcontext(term.context, propagate=True)
        return self

    def get_context_for_type(self, node):
        if self.version >= 1.1:
            rtype = self.get_type(node) if isinstance(node, dict) else None
            if not isinstance(rtype, list):
                rtype = [rtype] if rtype else []

            for rt in rtype:
                typeterm = self.terms.get(rt)
                if typeterm:
                    break
            else:
                typeterm = None

            if typeterm and typeterm.context:
                subcontext = self.subcontext(typeterm.context, propagate=False)
                if subcontext:
                    return subcontext

        return self.parent if self.propagate is False else self

    def get_id(self, obj):
        return self._get(obj, ID)

    def get_type(self, obj):
        return self._get(obj, TYPE)

    def get_language(self, obj):
        return self._get(obj, LANG)

    def get_value(self, obj):
        return self._get(obj, VALUE)

    def get_graph(self, obj):
        return self._get(obj, GRAPH)

    def get_list(self, obj):
        return self._get(obj, LIST)

    def get_set(self, obj):
        return self._get(obj, SET)

    def get_rev(self, obj):
        return self._get(obj, REV)

    def _get(self, obj, key):
        for alias in self._alias.get(key, []):
            if alias in obj:
                return obj.get(alias)
        return obj.get(key)

    def get_key(self, key: str):
        for alias in self.get_keys(key):
            return alias

    def get_keys(self, key: str):
        if key in self._alias:
            for alias in self._alias[key]:
                yield alias
        yield key

    lang_key = property(lambda self: self.get_key(LANG))
    id_key = property(lambda self: self.get_key(ID))
    type_key = property(lambda self: self.get_key(TYPE))
    value_key = property(lambda self: self.get_key(VALUE))
    list_key = property(lambda self: self.get_key(LIST))
    rev_key = property(lambda self: self.get_key(REV))
    graph_key = property(lambda self: self.get_key(GRAPH))

    def add_term(
        self,
        name: str,
        idref: str,
        coercion: Union[Defined, str] = UNDEF,
        container=UNDEF,
        index=None,
        language=UNDEF,
        reverse=False,
        context=UNDEF,
        prefix=None,
        protected=False,
    ):
        if self.version < 1.1 or prefix is None:
            prefix = isinstance(idref, str) and idref.endswith(URI_GEN_DELIMS)

        if not self._accept_term(name):
            return

        if self.version >= 1.1:
            existing = self.terms.get(name)
            if existing and existing.protected:
                return

        if isinstance(container, (list, set, tuple)):
            container = set(container)
        else:
            container = set([container])

        term = Term(
            idref,
            name,
            coercion,
            container,
            index,
            language,
            reverse,
            context,
            prefix,
            protected,
        )

        self.terms[name] = term

        container_key: Union[Defined, str]
        for container_key in (LIST, LANG, SET):  # , INDEX, ID, GRAPH):
            if container_key in container:
                break
        else:
            container_key = UNDEF

        self._lookup[(idref, coercion or language, container_key, reverse)] = term

        if term.prefix is True:
            self._prefixes[idref] = name

    def find_term(
        self,
        idref: str,
        coercion=None,
        container: Union[Defined, str] = UNDEF,
        language: Optional[str] = None,
        reverse: bool = False,
    ):
        lu = self._lookup

        if coercion is None:
            coercion = language

        if coercion is not UNDEF and container:
            found = lu.get((idref, coercion, container, reverse))
            if found:
                return found

        if coercion is not UNDEF:
            found = lu.get((idref, coercion, UNDEF, reverse))
            if found:
                return found

        if container:
            found = lu.get((idref, coercion, container, reverse))
            if found:
                return found
        elif language:
            found = lu.get((idref, UNDEF, LANG, reverse))
            if found:
                return found
        else:
            found = lu.get((idref, coercion or UNDEF, SET, reverse))
            if found:
                return found

        return lu.get((idref, UNDEF, UNDEF, reverse))

    def resolve(self, curie_or_iri):
        iri = self.expand(curie_or_iri, False)
        if self.isblank(iri):
            return iri
        if " " in iri:
            return ""
        return self.resolve_iri(iri)

    def resolve_iri(self, iri):
        return norm_url(self._base, iri)

    def isblank(self, ref):
        return ref.startswith("_:")

    def expand(self, term_curie_or_iri, use_vocab=True):
        if not isinstance(term_curie_or_iri, str):
            return term_curie_or_iri

        if not self._accept_term(term_curie_or_iri):
            return ""

        if use_vocab:
            term = self.terms.get(term_curie_or_iri)
            if term:
                return term.id

        is_term, pfx, local = self._prep_expand(term_curie_or_iri)
        if pfx == "_":
            return term_curie_or_iri

        if pfx is not None:
            ns = self.terms.get(pfx)
            if ns and ns.prefix and ns.id:
                return ns.id + local
        elif is_term and use_vocab:
            if self.vocab:
                return self.vocab + term_curie_or_iri
            return None

        return self.resolve_iri(term_curie_or_iri)

    def shrink_iri(self, iri):
        ns, name = split_iri(str(iri))
        pfx = self._prefixes.get(ns)
        if pfx:
            return ":".join((pfx, name))
        elif self._base:
            if str(iri) == self._base:
                return ""
            elif iri.startswith(self._basedomain):
                return iri[len(self._basedomain) :]
        return iri

    def to_symbol(self, iri):
        iri = str(iri)
        term = self.find_term(iri)
        if term:
            return term.name
        ns, name = split_iri(iri)
        if ns == self.vocab:
            return name
        pfx = self._prefixes.get(ns)
        if pfx:
            return ":".join((pfx, name))
        return iri

    def load(
        self,
        source: Optional[Union[List[Any], Any]],
        base: Optional[str] = None,
        referenced_contexts: Set[Any] = None,
    ):
        self.active = True
        sources: List[Any] = []
        source = source if isinstance(source, list) else [source]
        referenced_contexts = referenced_contexts or set()
        self._prep_sources(base, source, sources, referenced_contexts)
        for source_url, source in sources:
            if source is None:
                self._clear()
            else:
                self._read_source(source, source_url, referenced_contexts)

    def _accept_term(self, key: str) -> bool:
        if self.version < 1.1:
            return True
        if key and len(key) > 1 and key[0] == "@" and key[1].isalnum():
            return key in NODE_KEYS
        else:
            return True

    def _prep_sources(
        self,
        base: Optional[str],
        inputs: List[Any],
        sources,
        referenced_contexts,
        in_source_url=None,
    ):

        for source in inputs:
            source_url = in_source_url
            if isinstance(source, str):
                source_url = source
                source_doc_base = base or self.doc_base
                new_ctx = self._fetch_context(
                    source, source_doc_base, referenced_contexts
                )
                if new_ctx is None:
                    continue
                else:
                    if base:
                        if TYPE_CHECKING:
                            # if base is not None, then source_doc_base won't be
                            # none due to how it is assigned.
                            assert source_doc_base is not None
                        base = urljoin(source_doc_base, source_url)
                    source = new_ctx

            if isinstance(source, dict):
                if CONTEXT in source:
                    source = source[CONTEXT]
                    source = source if isinstance(source, list) else [source]

            if isinstance(source, list):
                self._prep_sources(
                    base, source, sources, referenced_contexts, source_url
                )
            else:
                sources.append((source_url, source))

    def _fetch_context(self, source, base, referenced_contexts):
        source_url = urljoin(base, source)

        if source_url in referenced_contexts:
            raise RECURSIVE_CONTEXT_INCLUSION
        referenced_contexts.add(source_url)

        if source_url in self._context_cache:
            return self._context_cache[source_url]

        source = source_to_json(source_url)
        if source and CONTEXT not in source:
            raise INVALID_REMOTE_CONTEXT
        self._context_cache[source_url] = source

        return source

    def _read_source(self, source, source_url=None, referenced_contexts=None):
        imports = source.get(IMPORT)
        if imports:
            if not isinstance(imports, str):
                raise INVALID_CONTEXT_ENTRY

            imported = self._fetch_context(
                imports, self.base, referenced_contexts or set()
            )
            if not isinstance(imported, dict):
                raise INVALID_CONTEXT_ENTRY

            imported = imported[CONTEXT]
            imported.update(source)
            source = imported

        self.vocab = source.get(VOCAB, self.vocab)
        self.version = source.get(VERSION, self.version)
        protected = source.get(PROTECTED, False)

        for key, value in source.items():
            if key in {VOCAB, VERSION, IMPORT, PROTECTED}:
                continue
            elif key == PROPAGATE and isinstance(value, bool):
                self.propagate = value
            elif key == LANG:
                self.language = value
            elif key == BASE:
                if not source_url and not imports:
                    self.base = value
            else:
                self._read_term(source, key, value, protected)

    def _read_term(self, source, name, dfn, protected=False):
        idref = None
        if isinstance(dfn, dict):
            # term = self._create_term(source, key, value)
            rev = dfn.get(REV)
            protected = dfn.get(PROTECTED, protected)

            coercion = dfn.get(TYPE, UNDEF)
            if coercion and coercion not in (ID, TYPE, VOCAB):
                coercion = self._rec_expand(source, coercion)

            idref = rev or dfn.get(ID, UNDEF)
            if idref == TYPE:
                idref = str(RDF.type)
                coercion = VOCAB
            elif idref is not UNDEF:
                idref = self._rec_expand(source, idref)
            elif ":" in name:
                idref = self._rec_expand(source, name)
            elif self.vocab:
                idref = self.vocab + name

            context = dfn.get(CONTEXT, UNDEF)

            self.add_term(
                name,
                idref,
                coercion,
                dfn.get(CONTAINER, UNDEF),
                dfn.get(INDEX, UNDEF),
                dfn.get(LANG, UNDEF),
                bool(rev),
                context,
                dfn.get(PREFIX),
                protected=protected,
            )
        else:
            if isinstance(dfn, str):
                if not self._accept_term(dfn):
                    return
                idref = self._rec_expand(source, dfn)

            self.add_term(name, idref, protected=protected)

        if idref in NODE_KEYS:
            self._alias.setdefault(idref, []).append(name)

    def _rec_expand(self, source, expr, prev=None):
        if expr == prev or expr in NODE_KEYS:
            return expr

        is_term, pfx, nxt = self._prep_expand(expr)
        if pfx:
            iri = self._get_source_id(source, pfx)
            if iri is None:
                if pfx + ":" == self.vocab:
                    return expr
                else:
                    term = self.terms.get(pfx)
                    if term:
                        iri = term.id

            if iri is None:
                nxt = expr
            else:
                nxt = iri + nxt
        else:
            nxt = self._get_source_id(source, nxt) or nxt
            if ":" not in nxt and self.vocab:
                return self.vocab + nxt

        return self._rec_expand(source, nxt, expr)

    def _prep_expand(self, expr):
        if ":" not in expr:
            return True, None, expr
        pfx, local = expr.split(":", 1)
        if not local.startswith("//"):
            return False, pfx, local
        else:
            return False, None, expr

    def _get_source_id(self, source, key):
        # .. from source dict or if already defined
        term = source.get(key)
        if term is None:
            dfn = self.terms.get(key)
            if dfn:
                term = dfn.id
        elif isinstance(term, dict):
            term = term.get(ID)
        return term


Term = namedtuple(
    "Term",
    "id, name, type, container, index, language, reverse, context," "prefix, protected",
)
Term.__new__.__defaults__ = (UNDEF, UNDEF, UNDEF, UNDEF, False, UNDEF, False, False)
