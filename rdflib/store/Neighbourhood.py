from __future__ import generators


class Neighbourhood(object):
    def __init__(self, local, neighbours):
        super(Neighbourhood, self).__init__()
        self.local = local
        self.neighbours = neighbours

    def triples(self, pattern):
        for triple in self.local.triples(pattern):
            yield triple
        for triple in self.neighbours.triples(pattern):
            yield triple

