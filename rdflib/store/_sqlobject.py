from __future__ import generators

__metaclass__ = type

import re
_literal = re.compile(r'''"(?P<value>[^@&]*)"(?:@(?P<lang>[^&]*))?(?:&<(?P<datatype>.*)>)?''')

from urllib import quote, unquote

from rdflib.store import Store
from rdflib.Literal import Literal
from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.exceptions import ContextTypeError

from rdflib.compat import rsplit

import sqlobject
from sqlobject import *

LITERAL = 0
URI = 1
NO_URI = 'uri://oops/'
Any = None

class BaseObject(sqlobject.SQLObject):

    _lazyUpdate = True
    _cacheValues = False

class Literals(BaseObject):

    hash = IntCol(notNull=1)
    value = StringCol(notNull=1, validator=validators.String(strip_spaces=1))
    hashIndex = DatabaseIndex('hash')

class Namespaces(BaseObject):

    hash = IntCol(notNull=1)
    value = StringCol(length=255, notNull=1,
                      validator=validators.String(strip_spaces=1))
    hashIndex = DatabaseIndex('hash')

class PrefixNamespace(BaseObject):

    prefix = StringCol(length=255, notNull=1,
                       validator=validators.String(strip_spaces=1))
    ns = StringCol(length=255, notNull=1,
                   validator=validators.String(strip_spaces=1))
    prefixIndex = DatabaseIndex('prefix')
    nsIndex = DatabaseIndex('ns')
    prefixNsIndex = DatabaseIndex('ns', 'prefix')

class Resources(BaseObject):

    hash = IntCol(notNull=1)
    ns = IntCol(notNull=1)
    name = StringCol(length=255, notNull=1,
                     validator=validators.String(strip_spaces=1))
    hashIndex = DatabaseIndex('hash')
    nsIndex = DatabaseIndex('ns')
    nameIndex = DatabaseIndex('name')
    nsNameIndex = DatabaseIndex('ns', 'name')
    hashNsNameIndex = DatabaseIndex('hash', 'ns', 'name')

class Triples(BaseObject):

    subject = IntCol(notNull=1)
    predicate = IntCol(notNull=1)
    object = IntCol(notNull=1)
    objtype = IntCol(notNull=1, default=LITERAL)

    subjectIndex = DatabaseIndex('subject')
    predicateIndex = DatabaseIndex('predicate')
    objectIndex = DatabaseIndex('object', 'objtype')
    subjectPredicateIndex = DatabaseIndex('subject', 'predicate')
    subjectObjectIndex = DatabaseIndex('subject', 'object', 'objtype')
    predicateObjectIndex = DatabaseIndex('predicate', 'object', 'objtype')

def splituri(uri):
    if uri.startswith('<') and uri.endswith('>'):
        uri = uri[1:-1]
    if uri.startswith('_'):
        uid = ''.join(uri.split('_'))
        return '_', uid
    if '#' in uri:
        ns, local = rsplit(uri, '#', 1)
        return ns + '#', local
    if '/' in uri:
        ns, local = rsplit(uri, '/', 1)
        return ns + '/', local
    return NO_URI, uri

def _fromkey(key):
    if key.startswith("<") and key.endswith(">"):
        key = key[1:-1].decode("UTF-8")
        if key.startswith("_"):
            key = ''.join(splituri(key))
            return BNode(key)
        return URIRef(key)
    elif key.startswith("_"):
        return BNode(key)
    else:
        m = _literal.match(key)
        if m:
            d = m.groupdict()
            value = d["value"]
            value = unquote(value)
            value = value.decode("UTF-8")
            lang = d["lang"] or ''
            datatype = d["datatype"]
            return Literal(value, lang, datatype)
        else:
            msg = "Unknown Key Syntax: '%s'" % key
            raise Exception(msg)

def _tokey(term):
    if isinstance(term, URIRef):
        term = term.encode("UTF-8")
        if not '#' in term and not '/' in term:
            term = '%s%s' % (NO_URI, term)
        return '<%s>' % term
    elif isinstance(term, BNode):
        return '<%s>' % ''.join(splituri(term.encode("UTF-8")))
    elif isinstance(term, Literal):
        language = term.language
        datatype = term.datatype
        value = quote(term.encode("UTF-8"))
        if language:
            language = language.encode("UTF-8")
            if datatype:
                datatype = datatype.encode("UTF-8")
                n3 = '"%s"@%s&<%s>' % (value, language, datatype)
            else:
                n3 = '"%s"@%s' % (value, language)
        else:
            if datatype:
                datatype = datatype.encode("UTF-8")
                n3 = '"%s"&<%s>' % (value, datatype)
            else:
                n3 = '"%s"' % value
        return n3
    else:
        msg = "Unknown term Type for: %s" % term
        raise Exception(msg)

class SQLObject(Store):

    context_aware = False
    __open = False
    _triples = Triples
    _literals = Literals
    _ns = Namespaces
    _prefix_ns = PrefixNamespace
    _resources = Resources
    tables = ('_triples', '_literals', '_ns',
              '_prefix_ns', '_resources')

    def __init__(self):
        pass

    def open(self, uri, create=True):
        if self.__open:
            return
        self.__open = True
        self.connection = connection = connectionForURI(uri)
        # useful for debugging
        # self.connection.debug = True
        for att in self.tables:
            table = getattr(self, att)
            table._connection = connection
            table.createTable(ifNotExists=True)

        self.transaction = transaction = connection.transaction()
        for att in self.tables:
            table = getattr(self, att)
            table._connection = transaction

    def close(self):
        if not self.__open:
            raise ValueError, 'Not open'
        self.__open = False
        self.transaction.commit()

    def _makeHash(self, value):
        # XXX We will be using python's hash, but it should be a database
        # hash eventually.
        return hash(value)

    def _insertLiteral(self, value):
        v_hash = self._makeHash(value)
        lit = self._literals
        if not lit.select(lit.q.hash == v_hash).count():
            lit(hash=v_hash, value=value)
        return v_hash

    def _makeURIHash(self, value=None, namespace=None, local_name=None):
        if namespace is None and local_name is None:
            namespace, local_name = splituri(value)
        ns_hash = self._makeHash(namespace)
        rsrc_hash = self._makeHash((ns_hash, local_name))
        return ns_hash, rsrc_hash

    def _insertURI(self, value=None, namespace=None, local_name=None):
        if namespace is None and local_name is None:
            namespace, local_name = splituri(value)
        ns_hash, rsrc_hash = self._makeURIHash(value, namespace, local_name)
        ns = self._ns
        if not ns.select(ns.q.hash == ns_hash).count():
            ns(hash=ns_hash, value=namespace)
        rsrc = self._resources
        if not rsrc.select(rsrc.q.hash == rsrc_hash).count():
            rsrc(hash=rsrc_hash, ns=ns_hash, name=local_name)
        return rsrc_hash

    def _insertTriple(self, s_hash, p_hash, o_hash, objtype=URI):
        trip = self._triples
        clause = AND(trip.q.subject == s_hash,
                     trip.q.predicate == p_hash,
                     trip.q.object == o_hash)
        if not trip.select(clause).count():
            trip(subject=s_hash, predicate=p_hash,
                 object=o_hash, objtype=objtype)

    def tokey(self, obj):
        if isinstance(obj, (URIRef, BNode)):
            return URI, self._makeURIHash(_tokey(obj))[1]
        elif isinstance(obj, Literal):
            return LITERAL, self._makeHash(_tokey(obj))
        elif obj is Any:
            return None, Any
        raise ValueError, obj

    def insert(self, obj):
        if isinstance(obj, (URIRef, BNode)):
            return URI, self._insertURI(_tokey(obj))
        elif isinstance(obj, Literal):
            return LITERAL, self._insertLiteral(_tokey(obj))
        raise ValueError, obj

    def add(self, (subject, predicate, object), context=None):
        """\
        Add a triple to the store of triples.
        """
        tokey = self.insert
        ts, s = tokey(subject)
        tp, p = tokey(predicate)
        to, o = tokey(object)

        self._insertTriple(s, p, o, to)

    def remove(self, (subject, predicate, object), context=None):
        tokey = self.tokey
        where_clause = ''

        if subject is not Any:
            ts, s = tokey(subject)
            where_clause += 'subject = %s' % s
        if predicate is not Any:
            if where_clause:
                where_clause += ' AND '
            tp, p = tokey(predicate)
            where_clause += 'predicate = %s' % p
        if object is not Any:
            if where_clause:
                where_clause += ' AND '
            to, o = tokey(object)
            where_clause += 'object = %s AND objtype = %s' % (o, to)

        trip = self._triples
        conn = trip._connection
        query = 'DELETE from %s' % conn.sqlrepr(trip.q)
        if where_clause:
            query += ' WHERE %s' % where_clause
        conn.query(query)

    def triples(self, (subject, predicate, object), context=None):
        conn = self._triples._connection

        tokey = self.tokey
        where_clause = ''
        if subject is not Any:
            ts, s = tokey(subject)
            where_clause += 'r1.hash = %s' % s
        if predicate is not Any:
            if where_clause:
                where_clause += ' AND '
            tp, p = tokey(predicate)
            where_clause += 'r2.hash = %s' % p
        if object is not Any:
            if where_clause:
                where_clause += ' AND '
            to, o = tokey(object)
            if to == URI:
                where_clause += 'r3.hash = %s' % o
            else:
                where_clause += 'l.hash = %s' % o

        query = ("SELECT '<'||n1.value||r1.name||'>' AS subj, "
                 "'<'||n2.value||r2.name||'>' AS pred, "
                 "CASE WHEN t.objtype = %d "
                 "THEN '<'||n3.value||r3.name||'>' "
                 "ELSE l.value END AS obj, "
                 "l.hash, r3.hash "
                 "FROM resources r1, resources r2, "
                 "namespaces n1, namespaces n2, triples t "
                 "LEFT JOIN literals l ON t.object = l.hash "
                 "LEFT JOIN resources r3 ON t.object = r3.hash "
                 "LEFT JOIN namespaces n3 ON r3.ns = n3.hash "
                 "WHERE t.subject = r1.hash AND "
                 "r1.ns = n1.hash AND "
                 "t.predicate = r2.hash AND "
                 "r2.ns = n2.hash" % URI)
        if where_clause:
            query += ' AND %s' % where_clause
        query += ' ORDER BY subj, pred'
        for t in conn.queryAll(query):
            triple = _fromkey(t[0]), _fromkey(t[1]), _fromkey(t[2])
            yield triple

    def namespace(self, prefix):
        prefix = prefix.encode("utf-8")
        pns = self._prefix_ns
        res = pns.select(pns.q.prefix == prefix)
        if not res.count():
            return None
        return iter(res).next().ns

    def prefix(self, namespace):
        namespace = namespace.encode("utf-8")
        pns = self._prefix_ns
        res = pns.select(pns.q.ns == namespace)
        if not res.count():
            return None
        return iter(res).next().prefix

    def bind(self, prefix, namespace):
        if namespace[-1] == "-":
            raise Exception("??")
        pns = self._prefix_ns
        prefix = prefix.encode("utf-8")
        namespace = namespace.encode("utf-8")
        res = pns.select(AND(pns.q.ns == namespace,
                             pns.q.prefix == prefix))
        if not res.count():
            pns(prefix=prefix, ns=namespace)

    def namespaces(self):
        pns = self._prefix_ns
        for p in pns.select():
            yield p.prefix, URIRef(p.ns)

    def __len__(self):
        return self._triples.select().count()
