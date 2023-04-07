"""
Notation 3 (N3) RDF graph serializer for RDFLib.
"""
from rdflib.graph import Graph
from rdflib.namespace import OWL, Namespace
from rdflib.plugins.serializers.turtle import OBJECT, SUBJECT, TurtleSerializer

__all__ = ["N3Serializer"]

SWAP_LOG = Namespace("http://www.w3.org/2000/10/swap/log#")


class N3Serializer(TurtleSerializer):
    short_name = "n3"

    def __init__(self, store: Graph, parent=None):
        super(N3Serializer, self).__init__(store)
        self.keywords.update({OWL.sameAs: "=", SWAP_LOG.implies: "=>"})
        self.parent = parent

    def reset(self):
        super(N3Serializer, self).reset()
        self._stores = {}

    def endDocument(self):
        if not self.parent:
            super(N3Serializer, self).endDocument()

    def indent(self, modifier=0):
        indent = super(N3Serializer, self).indent(modifier)
        if self.parent is not None:
            indent += self.parent.indent()  # modifier)
        return indent

    def preprocessTriple(self, triple):
        super(N3Serializer, self).preprocessTriple(triple)
        if isinstance(triple[0], Graph):
            for t in triple[0]:
                self.preprocessTriple(t)
        if isinstance(triple[1], Graph):
            for t in triple[1]:
                self.preprocessTriple(t)
        if isinstance(triple[2], Graph):
            for t in triple[2]:
                self.preprocessTriple(t)

    def getQName(self, uri, gen_prefix=True):
        qname = None
        if self.parent is not None:
            qname = self.parent.getQName(uri, gen_prefix)
        if qname is None:
            qname = super(N3Serializer, self).getQName(uri, gen_prefix)
        return qname

    def statement(self, subject):
        self.subjectDone(subject)
        properties = self.buildPredicateHash(subject)
        if len(properties) == 0:
            return False
        return self.s_clause(subject) or super(N3Serializer, self).statement(subject)

    def path(self, node, position, newline=False):
        if not self.p_clause(node, position):
            super(N3Serializer, self).path(node, position, newline)

    def s_clause(self, subject):
        if isinstance(subject, Graph):
            self.write("\n" + self.indent())
            self.p_clause(subject, SUBJECT)
            self.predicateList(subject)
            self.write(" .")
            return True
        else:
            return False

    def p_clause(self, node, position):
        if isinstance(node, Graph):
            self.subjectDone(node)
            if position is OBJECT:
                self.write(" ")
            self.write("{")
            self.depth += 1
            serializer = N3Serializer(node, parent=self)
            serializer.serialize(self.stream)
            self.depth -= 1
            self.write(self.indent() + "}")
            return True
        else:
            return False
