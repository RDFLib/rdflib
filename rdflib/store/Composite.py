from __future__ import generators


class Composite(object):
    """
    A store that is the composition of a list of stores.
    """
    
    def __init__(self):
        super(CompositeStore, self).__init__()
        self.__stores = list()

    def triples(self, (s, p, o)):
        for store in self.stores():
            for triple in store.triples((s, p, o)):
                yield triple

    def append_store(self, store):
        self.__stores.append(store)

    def remove_store(self, store):
        self.__stores.remove(store)

    def stores(self):
        return iter(self.__stores)
