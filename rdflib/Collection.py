
class Collection(object):
    """See 3.3.5 Emulating container types: http://docs.python.org/ref/sequence-types.html#l2h-232"""
    
    def __init__(self, graph, uri, seq=[]):
        self.graph = graph
        self.uri = uri or BNode()
        for item in seq:
            self.append(item)

    def _get_container(self, index):
        """Gets the first, rest holding node at index."""
        assert isinstance(index, int)
        graph = self.graph
        container = self.uri
        i = 0
        while i<index: 
            i += 1
            container = graph.value(container, RDF.rest)
            if container is None:
                break
        return container

    def __len__(self):
        """length of items in collection."""
        count = 0
        for item in self.graph.items(self.uri):
            count += 1
        return count

    def __getitem__(self, key):
        """TODO"""
        c = self._get_container(key)
        if c:
            v = self.graph.value(c, RDF.first)
            if v:
                return v
            else:
                raise KeyError, key
        else:
            raise IndexError, key

    def __setitem__(self, key, value):
        """TODO"""
        c = self._get_container(key)
        if c:
            self.graph.add((c, RDF.first, value))
        else:
            raise IndexError, key
        

    def __delitem__(self, key):
        """..."""
        self[key] # to raise any potential key exceptions
        graph = self.graph
        current = self._get_container(key)
        assert current
        next = self._get_container(key+1)
        # TODO: delete last element in list
        assert next
        first = graph.value(next, RDF.first)
        rest = graph.value(next, RDF.rest)

        graph.set((current, RDF.first, first))
        graph.set((current, RDF.rest, rest))

    def __iter__(self):
        """Iterator over items in Collections"""
        return self.graph.items(self.uri)
        
    def append(self, item):
        container = self.uri
        graph = self.graph
        while True:
            first = graph.value(container, RDF.first)
            if first is None:
                graph.add((container, RDF.first, item))
                return
            else:
                rest = graph.value(container, RDF.rest)
                if rest:
                    container = rest
                else:
                    node = BNode()
                    graph.add((container, RDF.rest, node))
                    container = node



if __name__=="__main__":
    from rdflib import *

    g = Graph()

    c = Collection(g, BNode())

    assert len(c)==0

    c = Collection(g, BNode(), [Literal("1"), Literal("2"), Literal("3"), Literal("4")])

    assert len(c)==4

    assert c[1]==Literal("2"), c[1]

    del c[1]

    assert list(c)==[Literal("1"), Literal("3"), Literal("4")], list(c)

    try:
        del c[500]
    except IndexError, i:
        pass

    c.append(Literal("5"))

    print list(c)

    for i in c:
        print i

    del c[3]
