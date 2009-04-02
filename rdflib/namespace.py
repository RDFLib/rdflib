import logging

_logger = logging.getLogger(__name__)

from rdflib.term import URIRef


class Namespace(URIRef):

    @property
    def title(self):
        return URIRef(self + 'title')

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
        return """rdflib.namespace.NamespaceDict('%s')""" % str(self.uri)


class ClosedNamespace(object):
    """
    
    """

    def __init__(self, uri, terms):
        self.uri = uri
        self.__uris = {}
        for t in terms:
            self.__uris[t] = URIRef(self.uri + t)

    def term(self, name):
        uri = self.__uris.get(name)
        if uri is None:
            raise Exception("term '%s' not in namespace '%s'" % (name, self.uri))
        else:
            return uri

    def __getitem__(self, key, default=None):
        return self.term(key)

    def __getattr__(self, name):
        if name.startswith("__"): # ignore any special Python names!
            raise AttributeError
        else:
            return self.term(name)

    def __str__(self):
        return self.uri

    def __repr__(self):
        return """rdf.namespace.ClosedNamespace('%s')""" % str(self.uri)


class _RDFNamespace(ClosedNamespace):
    def __init__(self):
        super(_RDFNamespace, self).__init__(
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#"), 
            terms=[
        # Syntax Names
        "RDF", "Description", "ID", "about", "parseType", "resource", "li", "nodeID", "datatype", 
        
        # RDF Classes
        "Seq", "Bag", "Alt", "Statement", "Property", "XMLLiteral", "List", 
        
        # RDF Properties
        "subject", "predicate", "object", "type", "value", "first", "rest", 
        # and _n where n is a non-negative integer
        
        # RDF Resources          
        "nil"]
            )

    def term(self, name):
        try:
            i = int(name)
            return URIRef("%s_%s" % (self.uri, i))
        except ValueError, e:
            return super(_RDFNamespace, self).term(name)
        
RDF = _RDFNamespace()

RDFS = ClosedNamespace(
    uri = URIRef("http://www.w3.org/2000/01/rdf-schema#"), 
    terms = [
        "Resource", "Class", "subClassOf", "subPropertyOf", "comment", "label", 
        "domain", "range", "seeAlso", "isDefinedBy", "Literal", "Container", 
        "ContainerMembershipProperty", "member", "Datatype"]
    )

OWL = Namespace('http://www.w3.org/2002/07/owl#')
