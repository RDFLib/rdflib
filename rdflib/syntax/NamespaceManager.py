from rdflib import URIRef, Literal, RDFS
from rdflib.syntax.xml_names import split_uri

from urlparse import urljoin, urldefrag
from urllib import pathname2url, url2pathname
import os, sys, new, logging


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
           
    def __get_backend(self):
        return self.graph.backend
    backend = property(__get_backend)

    def _get_log(self):
        if self.__log is None:
            #self.__log = logging.getLogger("rdflib.syntax.NamespaceManager")
            self.__log = logging
        return self.__log
    log = property(_get_log)
        
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
            prefix = self.backend.prefix(namespace)
            if prefix is None:
                prefix = "_%s" % len(list(self.backend.namespaces()))
                self.bind(prefix, namespace)
            if prefix=="":
                self.__cache[uri] = name
            else:
                self.__cache[uri] = ":".join((prefix, name))
            return prefix, namespace, name

    def bind(self, prefix, namespace, override=True):
        # When documenting explain that override only applies in what cases
        if prefix is None:
            prefix = ''
        bound_namespace = self.backend.namespace(prefix)
        if bound_namespace and bound_namespace!=namespace:
            # prefix already in use for different namespace
            #
            # append number to end of prefix until we find on
            # that's not in use.
            num = 1                
            while 1:
                new_prefix = "%s%s" % (prefix, num)
                if not self.backend.namespace(new_prefix):
                    break
                num +=1
            self.backend.bind(new_prefix, namespace)
        else:
            bound_prefix = self.backend.prefix(namespace)
            if bound_prefix is None:
                self.backend.bind(prefix, namespace)            
            elif bound_prefix == prefix:
                pass # already bound
            else:
                if override:
                    self.backend.bind(prefix, namespace)

    def namespaces(self):
        for prefix, namespace in self.backend.namespaces():
            yield prefix, namespace

    def absolutize(self, uri, defrag=1):
        base = urljoin("file:", pathname2url(os.getcwd()))        
        uri = urljoin("%s/" % base, uri)
        if defrag:
            uri, frag = urldefrag(uri)            
        return URIRef(uri)

    def context_id(self, uri):
        """ URI#context """
        uri = uri.split("#", 1)[0]
        return URIRef("%s#context" % uri)
        
    def namespace(self, uri):
        #if uri[-1]!="#":
        #    self.log.warning("Namespace should end in #: '%s'" % uri)
        # TODO: assume this context is loaded from its namespace location:
        uri = URIRef(uri)
        context_uri = URIRef(uri[0:-1])
        #try:
        if not (uri, None, None) in self.graph:
            self.log.info("loading namespace: %s" % uri)
            context = self.graph.load(context_uri)
            if not (uri, RDFS.label, None) in context:
                context.add((uri, RDFS.label, Literal("-")))
        else:
            cid = self.context_id(context_uri)
            context = self.graph.get_context(cid)
        #except Exception, e:
        #    raise Exception("While trying to load namespace %s encountered the following error:\n%s" % (uri, e))

        module_name = uri
        module = sys.modules.get(module_name, None)
        if module:
            return module

        safe_module_name = "namespace_%s" % hash(module_name)
        module = new.module(safe_module_name)
        module.__name__ = module_name 
        module.__file__ = module_name
        module.__ispkg__ = 0

        from rdflib.util import uniq

        d = module.__dict__
        d["NS"] = uri
        #d["__getitem__"] = module.__dict__.__getitem__
        for subject in uniq(context.subjects(None, None)):
            if subject.startswith(uri):
                ns, qname = subject.split(uri)
                d[qname] = subject

        sys.modules[module_name] = module
        return sys.modules[module_name]
