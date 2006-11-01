from rdflib.URIRef import URIRef


class Namespace(object):

    def __init__(self, value):
        self.__value = value

    def __getitem__(self, key, default=None):
        return URIRef(self.__value + key)

    def __getattr__(self, name):
        if name.startswith("__"): # ignore any special Python names!
            raise AttributeError
        else:
            return URIRef(self.__value + name)


