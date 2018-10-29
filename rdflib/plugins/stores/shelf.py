import shelve

from rdflib.store import Store, VALID_STORE, NO_STORE
from rdflib.term import URIRef
from six import b
from six.moves.urllib.request import pathname2url
from six import iteritems

import shelve

from os import mkdir
from os.path import exists, abspath

from rdflib.util import lru, from_n3

import logging
logger = logging.getLogger(__name__)

__all__ = ['Shelf']


class Shelf(Store):
    context_aware = True
    formula_aware = False
    transaction_aware = False
    graph_aware = True
    __prefix = {}
    __namespace = {}

    def __init__(self, configuration=None, identifier=None):
        self.__open = False
        self.__identifier = identifier
        super(Shelf, self).__init__(configuration)

    def __get_identifier(self):
        return self.__identifier
    identifier = property(__get_identifier)

    def _init_db_environment(self, path):
        if not exists(path):
            mkdir(path)
            # TODO: implement create method and refactor this to it
            self.create(path)
        db_env = shelve.open(path+"/contexts.db")
        return db_env

    def is_open(self):
        return self.__open

    def open(self, path, create=True):
        if self.__identifier is None:
            self.__identifier = URIRef(pathname2url(abspath(path)))

        db_env = self._init_db_environment(path)
        if db_env == NO_STORE:
            return NO_STORE
        self.db_env = db_env
        self.__open = True

        return VALID_STORE

    def sync(self):
        if self.__open:
            pass

    def close(self, commit_pending_transaction=False):
        if self.__open:
            self.db_env.close()
            self.__open = False
            self.__get_context.clear()

    @lru
    def __get_context(self, ident):
        return self.db_env.get(ident, {})

    def __set_context(self, ident, g):
        self.db_env[ident] = g
    
    def add(self, triple, context, quoted=False, txn=None):
        """\
        Add a triple to the store of triples.
        """
        (subject, predicate, object) = triple
        assert self.__open, "The Store must be open."
        assert context != self, "Can not add triple directly to store"
        Store.add(self, (subject, predicate, object), context, quoted)

        s = subject.n3()
        p = predicate.n3()
        o = object.n3()
        c = context.identifier.n3()

        ctx = self.__get_context(c.encode('utf-8'))

        if s not in ctx:
            ctx[s] = {}
        if p not in ctx[s]:
            ctx[s][p] = set()
        ctx[s][p].add(o)
        self.__set_context(c.encode('utf-8'),ctx)

    def remove(self, spo, context, txn=None):
        subject, predicate, object = spo
        assert self.__open, "The Store must be open."
        Store.remove(self, (subject, predicate, object), context)

        if context is not None:
            if context == self:
                context = None
        
        if context is None and subject is None and predicate is None and object is None:
            self.db_env.clear()
            self.__get_context.clear() # clear the LRU cache
            return # this is pretty much it, special case.
        for c in [x for x in [context.identifier.n3().encode('utf-8')] if x in self.db_env] if context is not None else self.db_env.keys():
            ctx = self.__get_context(c.encode('utf-8'))
            if subject is None and predicate is None and object is None:
                ctx.clear()
            else:
                for s in [x for x in [subject.n3()] if x in ctx] if subject is not None else ctx.keys():
                    if predicate is None and object is None:
                        del ctx[s]
                    else:
                        subj = ctx[s]
                        for p in [x for x in [predicate.n3()] if x in subj] if predicate is not None else subj.keys():
                            if object is None:
                                del subj[p]
                            else:
                                o = object.n3()
                                if o in subj[p]:
                                    subj[p].remove(object.n3())
                                if len(subj[p]) == 0:
                                    del subj[p]
                        if len(subj) == 0:
                            del ctx[s]
            #if len(ctx) == 0:
            #    del self.db_env[c]
            #    self.__get_context.clear()
            #else:
            self.__set_context(c.encode('utf-8'), ctx)

    def triples(self, spo, context=None, txn=None):
        """A generator over all the triples matching """
        assert self.__open, "The Store must be open."

        subject, predicate, object = spo

        if context is not None:
            if context == self:
                context = None

        for c in [x for x in [context.identifier.n3().encode('utf-8')] if x in self.db_env] if context is not None else self.db_env.keys():
            ctx = self.__get_context(c.encode('utf-8'))
            for s in [x for x in [subject.n3()] if x in ctx] if subject is not None else ctx.keys():
                for p in [x for x in [predicate.n3()] if x in ctx[s]] if predicate is not None else ctx[s].keys():
                    for o in [x for x in [object.n3()] if x in ctx[s][p]] if object is not None else ctx[s][p]:
                        yield (from_n3(s),from_n3(p),from_n3(o)), from_n3(unicode(c,encoding='utf-8'))

    def __len__(self, context=None):
        assert self.__open, "The Store must be open."
        if context is not None:
            if context == self:
                context = None

        i = 0
        for c in [x for x in [context.identifier.n3().encode('utf-8')] if x in self.db_env] if context is not None else self.db_env.keys():
            ctx = self.__get_context(c.encode('utf-8'))
            for s in ctx.keys():
                for p in ctx[s].keys():
                    i += len(ctx[s][p])
        return i

    def bind(self, prefix, namespace):
        self.__prefix[namespace] = prefix
        self.__namespace[prefix] = namespace

    def namespace(self, prefix):
        return self.__namespace.get(prefix, None)

    def prefix(self, namespace):
        return self.__prefix.get(namespace, None)

    def namespaces(self):
        for prefix, namespace in iteritems(self.__namespace):
            yield prefix, namespace

    def contexts(self, triple=None):
        if triple:
            contexts = set()
            for triples, c in self.triples(triple):
                if c not in contexts:
                    contexts.add(c)
                    yield c
        else:
            for c in self.db_env.keys():
                yield from_n3(unicode(c,encoding='utf-8'))

    def add_graph(self, graph):
        if graph.identifier.n3().encode('utf-8') not in self.db_env:
            self.__set_context(graph.identifier.n3().encode('utf-8'), self.__get_context(graph.identifier.n3().encode('utf-8')))

    def remove_graph(self, graph):
        if graph.identifier.n3().encode('utf-8') in self.db_env:
            del self.db_env[graph.identifier.n3().encode('utf-8')]
            self.__get_context.evict(self,graph.identifier.n3().encode('utf-8'))
