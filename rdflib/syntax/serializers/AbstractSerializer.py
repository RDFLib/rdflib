from rdflib import URIRef

class AbstractSerializer(object):

    def __init__(self, store):
        self.store = store
        self.encoding = "UTF-8"
        self.base = None

    def serialize(self, stream, base=None, encoding=None):
        """Abstract method"""

    def relativize(self, uri):
        base = self.base
        if base is not None and uri.startswith(base):
            uri = URIRef(uri.replace(base, "", 1))
        return uri

