

class Store(object):
    def __init__(self):
        self.context_aware = True

    def add(self, (subject, predicate, object), context=None):
        """ Add a triple to the store of triples. """

    def remove(self, (subject, predicate, object), context):
        """ Remove a triple from the store """

    def triples(self, (subject, predicate, object), context=None):
        """A generator over all the triples matching pattern"""

    def __len__(self, context=None):
	""" Number of statements in the store. """

    def contexts(self, triple=None):
	""" """
    def remove_context(self, identifier):
        """ """        

    def bind(self, prefix, namespace):
        """ """

    def prefix(self, namespace):
        """ """

    def namespace(self, prefix):
        """ """

    def namespaces(self):
        """ """

    def open(self, path):
        """ """
        
    def close(self):
        """ """

    def sync(self):
        """ """

