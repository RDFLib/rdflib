from rdflib.URIRef import URIRef


class Namespace(URIRef):

    def __getitem__(self, key, default=None):
        return URIRef(self + key)

    def __getattr__(self, name):
        if name.startswith("__"): # ignore any special Python names!
            raise AttributeError
        else:
            return URIRef(self + name)


