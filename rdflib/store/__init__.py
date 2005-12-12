

class Store(object):

    #Properties
    context_aware = False
    formula_aware = False
    transaction_aware = False

    def __init__(self, configuration=None, identifier=None):
        """ 
        identifier: URIRef of the Store. Defaults to CWD
        configuration: string containing infomation open can use to
        connect to datastore.
        """
        if configuration:
            self.open(configuration)

    def open(self, configuration, create=True):
        """ 
        Opens the store specified by the configuration string. If
	create is True a store will be created if it does not already
	exist. If create is False and a store does not already exist
	an exception is raised. An exception is also raised if a store
	exists, but there is insufficient permissions to open the
	store.
        """

    def close(self, commit_pending_transaction=False):
        """ """

    def destroy(self, configuration):
        """ """        

    def add(self, (subject, predicate, object), context, quoted=False):
        """ Add a triple to the store of triples. """

    def remove(self, (subject, predicate, object), context=None):
        """ Remove a triple from the store """

    def triples(self, (subject, predicate, object), context=None):
        """ 
        A generator over all the triples matching pattern. Pattern can
        be any objects for comparing against nodes in the store, for
        example, RegExLiteral, Date? DateRange?
        """

    # varients of triples will be done if / when optimization is needed

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


