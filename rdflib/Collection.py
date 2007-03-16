from rdflib import RDF, BNode, Literal
from rdflib.Graph import Graph

class Collection(object):
    """
    See 3.3.5 Emulating container types: http://docs.python.org/ref/sequence-types.html#l2h-232
    
    >>> listName = BNode()
    >>> g = Graph('IOMemory')
    >>> listItem1 = BNode()
    >>> listItem2 = BNode()
    >>> g.add((listName,RDF.first,Literal(1)))
    >>> g.add((listName,RDF.rest,listItem1))
    >>> g.add((listItem1,RDF.first,Literal(2)))
    >>> g.add((listItem1,RDF.rest,listItem2))
    >>> g.add((listItem2,RDF.rest,RDF.nil))
    >>> g.add((listItem2,RDF.first,Literal(3)))
    >>> c=Collection(g,listName)
    >>> print list(c)
    [rdflib.Literal('1', language=None, datatype=rdflib.URIRef('http://www.w3.org/2001/XMLSchema#int')), rdflib.Literal('2', language=None, datatype=rdflib.URIRef('http://www.w3.org/2001/XMLSchema#int')), rdflib.Literal('3', language=None, datatype=rdflib.URIRef('http://www.w3.org/2001/XMLSchema#int'))]
    >>> 1 in c
    True
    >>> len(c)
    3
    >>> c._get_container(1) == listItem1
    True
    >>> c.index(Literal(2)) == 1
    True
    """
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

    def index(self, item):
        """
        Returns the 0-based numerical index of the item in the list          
        """
        listName = self.uri
        index = 0
        while True:
            if (listName,RDF.first,item) in self.graph:
                return index
            else:
                newLink = list(self.graph.objects(listName,RDF.rest))
                index += 1
                if newLink == [RDF.nil]:
                    raise ValueError("%s is not in %s"%(item,self.uri))
                elif not newLink:
                    raise Exception("Malformed RDF Collection: %s"%self.uri)
                else:
                    assert len(newLink)==1, "Malformed RDF Collection: %s"%self.uri
                    listName = newLink[0]

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
        if key==len(self)-1:
            graph.remove((current, RDF.first, None))
            graph.remove((current, RDF.rest, None))
        else:
            next = self._get_container(key+1)
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

    def clear(self):
        container = self.uri
        graph = self.graph
        while container:
            rest = graph.value(container, RDF.rest)
            graph.remove((container, RDF.first, None))
            graph.remove((container, RDF.rest, None))
            container = rest
def test():
    import doctest
    doctest.testmod()

if __name__=="__main__":
    test()

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

    c.clear()

    assert len(c)==0

