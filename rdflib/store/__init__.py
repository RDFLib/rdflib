

class Store(object):

    #Properties
    #context_aware
    #transaction_aware

    def __init__(self, identifier, configuration=None):
        """ identifier: URIRef of the Store. Defaults to CWD
            configuration: string containing infomation open can use to connect to datastore.
        """
        self.identifier = identifier
        if configuration:
            self.open(configuration)

    def open(self, configuration):
        """ """

    def close(self, commit_pending_transaction=False):
        """ """

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

    # Optional Namespace methods

    def bind(self, prefix, namespace):
        """ """

    def prefix(self, namespace):
        """ """

    def namespace(self, prefix):
        """ """

    def namespaces(self):
        """ """

    # Optional Transactional methods

    def commit(self):
        """ """
    
    def rollback(self):
        """ """
