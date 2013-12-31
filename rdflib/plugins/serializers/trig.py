"""
Trig RDF graph serializer for RDFLib.
See <http://www.w3.org/TR/trig/> for syntax specification.
"""

from collections import defaultdict

from rdflib.plugins.serializers.turtle import TurtleSerializer, _GEN_QNAME_FOR_DT, VERB

from rdflib.term import BNode, Literal

__all__ = ['TrigSerializer']


class TrigSerializer(TurtleSerializer):

    short_name = "trig"
    indentString = 4 * u' '

    def __init__(self, store):
        if store.context_aware:
            self.contexts = store.contexts()
        else:
            self.contexts = [store]

        super(TrigSerializer, self).__init__(store)

    def preprocess(self):
        for context in self.contexts:
            self.store = context
            self._references = defaultdict(int)
            self._subjects = {}

            for triple in context:
                self.preprocessTriple(triple)

            self._contexts[context]=(self.orderSubjects(), self._subjects, self._references)


    def preprocessTriple(self, triple):
        s, p, o = triple
        self._references[o]+=1
        self._subjects[s] = True
        for i, node in enumerate(triple):
            if node in self.keywords:
                continue
            # Don't use generated prefixes for subjects and objects
            self.getQName(node, gen_prefix=(i == VERB))
            if isinstance(node, Literal) and node.datatype:
                self.getQName(node.datatype, gen_prefix=_GEN_QNAME_FOR_DT)
        p = triple[1]
        if isinstance(p, BNode):
            self._references[p]+=1

    def reset(self):
        super(TrigSerializer, self).reset()
        self._contexts = {}

    def serialize(self, stream, base=None, encoding=None,
                  spacious=None, **args):
        self.reset()
        self.stream = stream
        self.base = base

        if spacious is not None:
            self._spacious = spacious

        self.preprocess()

        self.startDocument()

        firstTime = True
        for store, (ordered_subjects, subjects, ref) in self._contexts.items():
            self._references = ref
            self._serialized = {}
            self.store = store
            self._subjects = subjects

            self.write(self.indent() + '\n<%s> = {' % self.getQName(store.identifier))
            self.depth += 1
            for subject in ordered_subjects:
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
