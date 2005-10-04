

class Store(object):

    #Properties
    #context_aware
    #transaction_aware

    def __init__(self, identifier, configuration=None):
        """ 
        identifier: URIRef of the Store. Defaults to CWD
        configuration: string containing infomation open can use to
        connect to datastore.
        """
        self.identifier = identifier
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

    def add(self, (subject, predicate, object), context=None):
        """ Add a triple to the store of triples. """

    def remove(self, (subject, predicate, object), context):
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
    # Optional nested context / n3 bits ??

    def add_existential(self, resource):

    def add_universal(self, resource):

    def create_clause(self, identifier=None):

    def get_existentials(self, recurse=True):

    def get_universals(self, recurse=True):

    def get_clause(self, identifier):

    def list_clauses(self):

    def remove_clause(self, identifier):
