
import rdflib
from rdflib.graph import Graph
from rdflib.term import URIRef, Node, BNode, Literal
try:
    import RDF
except ImportError:
    import warnings
    warnings.warn("Redlands not installed")
    __test__=False

from rdflib.store import Store

def _t(i):
    if isinstance(i, rdflib.term.URIRef):
        return RDF.Node(RDF.Uri(unicode(i)))
    if isinstance(i, rdflib.term.BNode):
        return RDF.Node(blank=str(i))
    if isinstance(i, rdflib.term.Literal):
        return RDF.Node(literal=str(i))
    if isinstance(i, Graph):
        return _t(i.identifier)
    if i is None:
        return None
    raise TypeError, 'Cannot convert %s' % `i`

def _c(i):
    return _t(i)


def _f(i):
    if isinstance(i, RDF.Uri):
        return rdflib.term.URIRef(i)
    if isinstance(i, RDF.Node):
        if i.is_blank():
            return rdflib.term.BNode(i.blank_identifier)
        elif i.is_literal():
            return rdflib.term.Literal(i)
        else:
            return URIRef(i.uri)
    if i is None:
        return None
    raise TypeError, 'Cannot convert %s' % `i`


class Redland(Store):
    context_aware = True
    def __init__(self, model=None):
        super(Redland, self).__init__()
        if model is None:
            model = RDF.Model(RDF.MemoryStorage(options_string="contexts='yes'"))
        self.model = model

    def __len__(self, context=None):
        """ Return number of triples (statements in librdf). """

        count = 0
        for triple, cg in self.triples((None, None, None), context):
            count += 1
        return count

    def add(self, (subject, predicate, object), context=None, quoted=False):
        """\
        Add a triple to the store of triples.
        """
        if context is not None:
            self.model.append(RDF.Statement(_t(subject), _t(predicate), _t(object)), _c(context))
        else:
            self.model.append(RDF.Statement(_t(subject), _t(predicate), _t(object)))

    def remove(self, (subject, predicate, object), context, quoted=False):
        if context is None:
            contexts = self.contexts()
        else:
            contexts = [context]
        for context in contexts:
            if subject is None and predicate is None and object is None:
                self.model.remove_statements_with_context(_c(context))
            else:
                del self.model[RDF.Statement(_t(subject), _t(predicate), _t(object)), _c(context)]

    def triples(self, (subject, predicate, object), context=None):
        """A generator over all the triples matching """
        cgraph = RDF.Model()
        triple = RDF.Statement(_t(subject), _t(predicate), _t(object))
        for statement, c in self.model.find_statements_context(triple):
            if context is None or _f(c) == context.identifier:
                cgraph.append(statement)
        for statement in cgraph.find_statements(triple):
            ret = []
            for c in self.model.get_contexts():
                if self.model.contains_statement_context(statement, _c(context)):
                    ret.append(c)
            yield (_f(statement.subject), _f(statement.predicate), _f(statement.object)), iter(ret)

    def contexts(self, triple=None): # TODO: have Graph support triple?
        for context in self.model.get_contexts():
            yield Graph(self, _f(context))

    def bind(self, prefix, namespace):
        pass

    def namespace(self, prefix):
        pass

    def prefix(self, namespace):
        pass

    def namespaces(self):
        pass

