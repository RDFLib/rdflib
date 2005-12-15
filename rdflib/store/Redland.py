
import rdflib
import RDF

from rdflib.store import Store

def _t(i):
    if isinstance(i, rdflib.URIRef):
        return RDF.Uri(unicode(i))
    if isinstance(i, rdflib.BNode):
        return RDF.Node(blank=unicode(i))
    if isinstance(i, rdflib.Literal):
        return RDF.Node(literal=unicode(i))
    if i is None:
        return None
    raise TypeError, 'Cannot convert %s' % `i`

def _f(i):
    if isinstance(i, RDF.Uri):
        return rdflib.URIRef(i)
    if isinstance(i, RDF.Node):
        if i.is_blank():
            return rdflib.BNode(i)
        else:
            return rdflib.Literal(i)
    if i is None:
        return None
    raise TypeError, 'Cannot convert %s' % `i`
    

class Redland(Store):
    def __init__(self, model=None):
        super(Redland, self).__init__()
        if model is None:
            model = RDF.Model()
        self.model = model
        
    def __len__(self, context=None):
        """ Return number of triples (statements in librdf). """
        return self.model.size()

    def add(self, (subject, predicate, object), context=None):
        """\
        Add a triple to the store of triples.
        """
        if context is not None:
            self.model.append(RDF.Statement(_t(subject), _t(predicate), _t(object)), _t(context))
        else:
            self.model.append(RDF.Statement(_t(subject), _t(predicate), _t(object)))

    def remove(self, (subject, predicate, object), context):
        if context is not None:
            del self.model[RDF.Statement(_t(subject), _t(predicate), _t(object)), _t(context)]
        else:
            del self.model[RDF.Statement(_t(subject), _t(predicate), _t(object))]
        
    def triples(self, (subject, predicate, object), context=None):
        """A generator over all the triples matching """
        for statement in self.model.find_statements(RDF.Statement(_t(subject), _t(predicate), _t(object)), _t(context)):
            yield _f(statement.subject), _f(statement.predicate), _f(statement.object)
            
    def contexts(self, triple=None): # TODO: have Graph support triple?
        for context in self.model.get_contexts():
            yield URIRef(context)
    
    def bind(self, prefix, namespace):
        pass

    def namespace(self, prefix):
        pass

    def prefix(self, namespace):
        pass

    def namespaces(self):
        pass

