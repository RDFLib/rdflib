
from rdflib.syntax.xml_names import split_uri

XMLLANG = u"http://www.w3.org/XML/1998/namespace#lang"


class QNameProvider(object):
    def __init__(self):
        self.__cache = {}
        self.__namespace = {} # mapping for prefix to namespace
        self.__prefix = {}
        self.set_prefix("xml", u"http://www.w3.org/XML/1998/namespace")
        # TODO: explain -- the following is needed for XMLLANG as defined above to work
        self.__prefix[u"http://www.w3.org/XML/1998/namespace#"] = "xml" 
        
    def get(self, uri):
        qname = self.__cache.get(uri, None)
        if qname is None:
            self.compute(uri)
            return self.get(uri)
        else:
            return qname

    def compute(self, uri):
        if not uri in self.__cache:
            namespace, name = split_uri(uri)
            prefix = self.__prefix.get(namespace, None)
            if prefix is None:
                prefix = "_%s" % len(self.__namespace)
                self.set_prefix(prefix, namespace)
            if prefix=="":
                self.__cache[uri] = name
            else:
                self.__cache[uri] = ":".join((prefix, name))

    def set_prefix(self, prefix, namespace):
        if prefix in self.__namespace:
            raise "NYI: prefix already set"
        self.__namespace[prefix] = namespace
        self.__prefix[namespace] = prefix

    def namespaces(self):
        for prefix, namespace in self.__namespace.iteritems():
            yield prefix, namespace


