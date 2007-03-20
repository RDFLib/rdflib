from rdflib.URIRef import URIRef

import logging

_logger = logging.getLogger(__name__)


class Namespace(URIRef):

    def term(self, name):
        return URIRef(self + name)

    def __getitem__(self, key, default=None):
        return self.term(key)

    def __getattr__(self, name):
        if name.startswith("__"): # ignore any special Python names!
            raise AttributeError
        else:
            return self.term(name)


class NamespaceDict(dict):

    def __new__(cls, uri=None, context=None):
        inst = dict.__new__(cls)
        inst.uri = uri # TODO: do we need to set these both here and in __init__ ??
        inst.__context = context
        return inst

    def __init__(self, uri, context=None):
        self.uri = uri
        self.__context = context

    def term(self, name):
        uri = self.get(name)
        if uri is None:
            uri = URIRef(self.uri + name)
            if self.__context and (uri, None, None) not in self.__context:
                _logger.warning("%s not defined" % uri)
            self[name] = uri
        return uri 

    def __getattr__(self, name):
        return self.term(name)

    def __getitem__(self, key, default=None):
        return self.term(key) or default

    def __str__(self):
        return self.uri

    def __repr__(self):
        return """rdflib.NamespaceDict('%s')""" % str(self.uri)

