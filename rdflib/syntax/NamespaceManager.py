from __future__ import generators

from rdflib import URIRef, Literal, RDFS, Variable
from rdflib.syntax.xml_names import split_uri

from urlparse import urljoin, urldefrag
from urllib import pathname2url, url2pathname
import os, sys, new


class NamespaceManager(object):
    def __init__(self, graph):
        self.graph = graph
        self.__cache = {}
        self.__log = None
        self.bind("xml", u"http://www.w3.org/XML/1998/namespace")
        self.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")

    def reset(self):
        self.__cache = {}

    def __get_store(self):
        return self.graph.store
    store = property(__get_store)

    def qname(self, uri):
        prefix, namespace, name = self.compute_qname(uri)
        if prefix=="":
            return name
        else:
            return ":".join((prefix, name))

    def normalizeUri(self,rdfTerm):
        """
        Takes an RDF Term and 'normalizes' it into a QName (using the registered prefix)
        or (unlike compute_qname) the Notation 3 form for URIs: <...URI...> 
        """
        try:
            namespace, name = split_uri(rdfTerm)
        except:
            if isinstance(rdfTerm,Variable):
                return "?%s"%rdfTerm
            else:
                return "<%s>"%rdfTerm
        prefix = self.store.prefix(namespace)
        if prefix is None and isinstance(rdfTerm,Variable):
            return "?%s"%rdfTerm
        elif prefix is None:
            return "<%s>"%rdfTerm
        else:
            qNameParts = self.compute_qname(rdfTerm)         
            return ':'.join([qNameParts[0],qNameParts[-1]])    

    def compute_qname(self, uri):
        if not uri in self.__cache:
            namespace, name = split_uri(uri)
            prefix = self.store.prefix(namespace)
            if prefix is None:
                prefix = "_%s" % len(list(self.store.namespaces()))
                self.bind(prefix, namespace)
            self.__cache[uri] = (prefix, namespace, name)
        return self.__cache[uri]

    def bind(self, prefix, namespace, override=True):
        # When documenting explain that override only applies in what cases
        if prefix is None:
            prefix = ''
        bound_namespace = self.store.namespace(prefix)
        if bound_namespace and bound_namespace!=namespace:
            # prefix already in use for different namespace
            #
            # append number to end of prefix until we find one
            # that's not in use.
            if not prefix:
                prefix = "default"
            num = 1
            while 1:
                new_prefix = "%s%s" % (prefix, num)
                if not self.store.namespace(new_prefix):
                    break
                num +=1
            self.store.bind(new_prefix, namespace)
        else:
            bound_prefix = self.store.prefix(namespace)
            if bound_prefix is None:
                self.store.bind(prefix, namespace)
            elif bound_prefix == prefix:
                pass # already bound
            else:
                if override or bound_prefix.startswith("_"): # or a generated prefix
                    self.store.bind(prefix, namespace)

    def namespaces(self):
        for prefix, namespace in self.store.namespaces():
            yield prefix, namespace

    def absolutize(self, uri, defrag=1):
        base = urljoin("file:", pathname2url(os.getcwd()))
        result = urljoin("%s/" % base, uri, allow_fragments=not defrag)
        if defrag:
            result = urldefrag(result)[0]
        if not defrag:
            if uri and uri[-1]=="#" and result[-1]!="#":
                result = "%s#" % result
        return URIRef(result)
