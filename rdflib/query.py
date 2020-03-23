from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import itertools
import shutil
import tempfile
import warnings
import types

from six import BytesIO
from six import PY2
from six import text_type
from six.moves.urllib.parse import urlparse

__all__ = ['Processor', 'Result', 'ResultParser', 'ResultSerializer',
           'ResultException']


class Processor(object):
    """
    Query plugin interface.

    This module is useful for those wanting to write a query processor
    that can plugin to rdf. If you are wanting to execute a query you
    likely want to do so through the Graph class query method.

    """

    def __init__(self, graph):
        pass

    def query(self, strOrQuery, initBindings={}, initNs={}, DEBUG=False):
        pass


class UpdateProcessor(object):
    """
    Update plugin interface.

    This module is useful for those wanting to write an update
    processor that can plugin to rdflib. If you are wanting to execute
    an update statement you likely want to do so through the Graph
    class update method.

    .. versionadded:: 4.0

    """

    def __init__(self, graph):
        pass

    def update(self, strOrQuery, initBindings={}, initNs={}):
        pass


class ResultException(Exception):
    pass


class EncodeOnlyUnicode(object):
    """
    This is a crappy work-around for
    http://bugs.python.org/issue11649


    """

    def __init__(self, stream):
        self.__stream = stream

    def write(self, arg):
        if isinstance(arg, text_type):
            self.__stream.write(arg.encode("utf-8"))
        else:
            self.__stream.write(arg)

    def __getattr__(self, name):
        return getattr(self.__stream, name)


class ResultRow(tuple):
    """
    a single result row
    allows accessing bindings as attributes or with []

    >>> from rdflib import URIRef, Variable
    >>> rr=ResultRow({ Variable('a'): URIRef('urn:cake') }, [Variable('a')])

    >>> rr[0]
    rdflib.term.URIRef(u'urn:cake')
    >>> rr[1]
    Traceback (most recent call last):
        ...
    IndexError: tuple index out of range

    >>> rr.a
    rdflib.term.URIRef(u'urn:cake')
    >>> rr.b
    Traceback (most recent call last):
        ...
    AttributeError: b

    >>> rr['a']
    rdflib.term.URIRef(u'urn:cake')
    >>> rr['b']
    Traceback (most recent call last):
        ...
    KeyError: 'b'

    >>> rr[Variable('a')]
    rdflib.term.URIRef(u'urn:cake')

    .. versionadded:: 4.0

    """

    def __new__(cls, values, labels):

        instance = super(ResultRow, cls).__new__(
            cls, (values.get(v) for v in labels))
        instance.labels = dict((text_type(x[1]), x[0])
                               for x in enumerate(labels))
        return instance

    def __getattr__(self, name):
        if name not in self.labels:
            raise AttributeError(name)
        return tuple.__getitem__(self, self.labels[name])

    def __getitem__(self, name):
        try:
            return tuple.__getitem__(self, name)
        except TypeError:
            if name in self.labels:
                return tuple.__getitem__(self, self.labels[name])
            if text_type(name) in self.labels:  # passing in variable object
                return tuple.__getitem__(self, self.labels[text_type(name)])
            raise KeyError(name)

    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default

    def asdict(self):
        return dict((v, self[v]) for v in self.labels if self[v] is not None)


class Result(object):
    """
    A common class for representing query result.

    There is a bit of magic here that makes this appear like different
    Python objects, depending on the type of result.

    If the type is "SELECT", iterating will yield lists of ResultRow objects

    If the type is "ASK", iterating will yield a single bool (or
    bool(result) will return the same bool)

    If the type is "CONSTRUCT" or "DESCRIBE" iterating will yield the
    triples.

    len(result) also works.

    """

    def __init__(self, type_):

        if type_ not in ('CONSTRUCT', 'DESCRIBE', 'SELECT', 'ASK'):
            raise ResultException('Unknown Result type: %s' % type_)

        self.type = type_
        self.vars = None
        self._bindings = None
        self._genbindings = None
        self.askAnswer = None
        self.graph = None

    def _get_bindings(self):
        if self._genbindings:
            self._bindings += list(self._genbindings)
            self._genbindings = None

        return self._bindings

    def _set_bindings(self, b):
        if isinstance(b, (types.GeneratorType, itertools.islice)):
            self._genbindings = b
            self._bindings = []
        else:
            self._bindings = b

    bindings = property(
        _get_bindings, _set_bindings, doc="a list of variable bindings as dicts")

    @staticmethod
    def parse(source=None, format=None, content_type=None, **kwargs):
        from rdflib import plugin

        if format:
            plugin_key = format
        elif content_type:
            plugin_key = content_type.split(";", 1)[0]
        else:
            plugin_key = 'xml'

        parser = plugin.get(plugin_key, ResultParser)()

        return parser.parse(source, content_type=content_type, **kwargs)

    def serialize(
            self, destination=None, encoding="utf-8", format='xml', **args):

        if self.type in ('CONSTRUCT', 'DESCRIBE'):
            return self.graph.serialize(
                destination, encoding=encoding, format=format, **args)

        """stolen wholesale from graph.serialize"""
        from rdflib import plugin
        serializer = plugin.get(format, ResultSerializer)(self)
        if destination is None:
            stream = BytesIO()
            stream2 = EncodeOnlyUnicode(stream)
            serializer.serialize(stream2, encoding=encoding, **args)
            return stream.getvalue()
        if hasattr(destination, "write"):
            stream = destination
            serializer.serialize(stream, encoding=encoding, **args)
        else:
            location = destination
            scheme, netloc, path, params, query, fragment = urlparse(location)
            if netloc != "":
                print("WARNING: not saving as location" +
                      "is not a local file reference")
                return
            fd, name = tempfile.mkstemp()
            stream = os.fdopen(fd, 'wb')
            serializer.serialize(stream, encoding=encoding, **args)
            stream.close()
            if hasattr(shutil, "move"):
                shutil.move(name, path)
            else:
                shutil.copy(name, path)
                os.remove(name)

    def __len__(self):
        if self.type == 'ASK':
            return 1
        elif self.type == 'SELECT':
            return len(self.bindings)
        else:
            return len(self.graph)

    def __bool__(self):
        if self.type == 'ASK':
            return self.askAnswer
        else:
            return len(self) > 0

    if PY2:
        __nonzero__ = __bool__

    def __iter__(self):
        if self.type in ("CONSTRUCT", "DESCRIBE"):
            for t in self.graph:
                yield t
        elif self.type == 'ASK':
            yield self.askAnswer
        elif self.type == 'SELECT':
            # this iterates over ResultRows of variable bindings

            if self._genbindings:
                for b in self._genbindings:
                    if b:  # don't add a result row in case of empty binding {}
                        self._bindings.append(b)
                        yield ResultRow(b, self.vars)
                self._genbindings = None
            else:
                for b in self._bindings:
                    if b:  # don't add a result row in case of empty binding {}
                        yield ResultRow(b, self.vars)

    def __getattr__(self, name):
        if self.type in ("CONSTRUCT", "DESCRIBE") and self.graph is not None:
            return self.graph.__getattr__(self, name)
        elif self.type == 'SELECT' and name == 'result':
            warnings.warn(
                "accessing the 'result' attribute is deprecated."
                " Iterate over the object instead.",
                DeprecationWarning, stacklevel=2)
            # copied from __iter__, above
            return [(tuple(b[v] for v in self.vars)) for b in self.bindings]
        else:
            raise AttributeError(
                "'%s' object has no attribute '%s'" % (self, name))

    def __eq__(self, other):
        try:
            if self.type != other.type:
                return False
            if self.type == 'ASK':
                return self.askAnswer == other.askAnswer
            elif self.type == 'SELECT':
                return self.vars == other.vars \
                    and self.bindings == other.bindings
            else:
                return self.graph == other.graph

        except:
            return False


class ResultParser(object):

    def __init__(self):
        pass

    def parse(self, source, **kwargs):
        """return a Result object"""
        pass  # abstract


class ResultSerializer(object):

    def __init__(self, result):
        self.result = result

    def serialize(self, stream, encoding="utf-8", **kwargs):
        """return a string properly serialized"""
        pass  # abstract
