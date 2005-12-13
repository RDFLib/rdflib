from cPickle import dumps

from rdflib.Node import Node


class Statement(Node, tuple):

    def __new__(cls, (subject, predicate, object), context):
        return tuple.__new__(cls, ((subject, predicate, object), context))

    def to_bits(self):
        return dumps((6, (tuple(self))))

