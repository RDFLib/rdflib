"""
Trig RDF graph serializer for RDFLib.
See <http://www.w3.org/2010/01/Trig/Trig> for syntax specification.

Originally https://github.com/mammadori/rdflib with some minor changes.

"""
from rdflib.plugins.serializers.turtle import TurtleSerializer, VERB, _GEN_QNAME_FOR_DT
from rdflib.term import BNode, Literal
from collections import defaultdict

__all__ = ['TriGSerializer']

class TriGSerializer(TurtleSerializer):

    short_name = "trig"
    indentString = 4 * u' '

    def __init__(self, store):
        if store.context_aware:
            self.contexts = store.contexts()
        else:
            self.contexts = [store]

        super(TriGSerializer, self).__init__(store)

    def preprocess(self):
        for context in self.contexts:
            for triple in context:
               self.preprocessTriple(triple, context.identifier)

    def preprocessTriple(self, triple, identifier):
        s, p, o = triple
        references = self.refCount(o) + 1
        self._references[o] = references
        self._subjects[s] = True
        self._contexts[identifier].add(s)
        for i, node in enumerate(triple):
            if node in self.keywords:
                continue
            # Don't use generated prefixes for subjects and objects
            self.getQName(node, gen_prefix=(i==VERB))
            if isinstance(node, Literal) and node.datatype:
                self.getQName(node.datatype, gen_prefix=_GEN_QNAME_FOR_DT)
        p = triple[1]
        if isinstance(p, BNode):
            self._references[p] = self.refCount(p) + 1

    def reset(self):
        super(TriGSerializer, self).reset()
        self._contexts = defaultdict(set)

    def serialize(self, stream, base=None, encoding=None, spacious=None, **args):
        self.reset()
        self.stream = stream
        self.base = base

        if spacious is not None:
            self._spacious = spacious

        self.preprocess()
        subjects_list = self.orderSubjects()

        self.startDocument()

        firstTime = True
        for identifier, subjects in self._contexts.items():
            if not isinstance(identifier, BNode) :
                self.write(self.indent() + '\n<%s> {' % identifier)
            else :
                self.write(self.indent() + '\n{')
            self.depth += 1
            for subject in subjects:
                if self.isDone(subject):
                    continue
                if firstTime:
                    firstTime = False
                if self.statement(subject) and not firstTime:
                    self.write('\n')
            self.depth -= 1
            self.write('}\n')

        self.endDocument()
        stream.write(u"\n".encode('ascii'))


