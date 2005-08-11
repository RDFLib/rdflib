from rdflib.URIRef import URIRef


class Namespace(URIRef):

    def __getitem__(self, key, default=None):
        return URIRef(self + key)

    def __getattr__(self, name):
        return URIRef(self + name)


