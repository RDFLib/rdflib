from rdflib.syntax.xml_names import split_uri


class NamespaceManager(object):
    def __init__(self, graph):
        self.graph = graph
        self.__cache = {}
        self.__namespace = {} # mapping for prefix to namespace
        self.__prefix = {}
        self.bind("xml", u"http://www.w3.org/XML/1998/namespace")
        self.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
        
        
    def qname(self, uri):
        qname = self.__cache.get(uri, None)
        if qname is None:
            self.compute_qname(uri)
            return self.qname(uri)
        else:
            return qname

    def compute_qname(self, uri):
        if not uri in self.__cache:
            namespace, name = split_uri(uri)
            prefix = self.__prefix.get(namespace, None)
            if prefix is None:
                prefix = "_%s" % len(self.__namespace)
                self.bind(prefix, namespace)
            if prefix=="":
                self.__cache[uri] = name
            else:
                self.__cache[uri] = ":".join((prefix, name))

    def bind(self, prefix, namespace):
        if prefix in self.__namespace:
            if self.__prefix.get(namespace, None) == prefix:
                return # already bound
            else:
                # prefix already in use for different namespace
                #
                # append number to end of prefix until we find on
                # that's not in use.
                num = 1                
                while 1:
                    new_prefix = "%s%s" % (prefix, num)
                    if new_prefix not in prefix_ns:
                        break
                    num +=1
                self.__prefix[namespace] = new_prefix
                self.__namespace[new_prefix] = namespace
        else:
            self.__namespace[prefix] = namespace
            self.__prefix[namespace] = prefix

    def namespaces(self):
        for prefix, namespace in self.__namespace.iteritems():
            yield prefix, namespace


