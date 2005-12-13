## Context-aware: An RDF store capable of storing statements within contexts is considered context-aware.
## Essentially, such a store is able to partition the RDF model it represents into individual, named, and addressable sub-graphs.

## Formula-aware: An RDF store capable of distinguishing between statements that are asserted and statements
## that are quoted is considered formula-aware.

## Conjunctive Graph: This refers to the 'top-level' Graph. It is the aggregation of all the contexts
## within it and is also the appropriate, absolute boundary for closed world assumptions / models.

## For the sake of persistence, Conjunctive Graphs must be distinguished by identifiers (that may not
## neccessarily be RDF identifiers or may be an RDF identifier normalized - SHA1/MD5 perhaps - for database
## naming purposes ).

## Conjunctive Query: Any query that doesn't limit the store to search within a named context only. Such a
## query expects a context-aware store to search the entire asserted universe (the conjunctive graph).
## A formula-aware store is expected not to include quoted statements when matching such a query.

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
        """
        This closes the database connection. The commit_pending_transaction parameter specifies whether to
        commit all pending transactions before closing (if the store is transactional).        
        """

    def destroy(self, configuration):
        """
        This destroys the instance of the store identified by the configuration string.        
        """        

    def add(self, (subject, predicate, object), context, quoted=False):
        """
        Adds the given statement to a specific context or to the model. The quoted argument
        is interpreted by formula-aware stores to indicate this statement is quoted/hypothetical
        It should be an error to not specify a context and have the quoted argument be True.
        It should also be an error for the quoted argument to be True when the store is not formula-aware.        
        """

    def remove(self, (subject, predicate, object), context=None):
        """ Remove the set of triples matching the pattern from the store """

    def triples(self, (subject, predicate, object), context=None):
        """ 
        A generator over all the triples matching pattern. Pattern can
        be any objects for comparing against nodes in the store, for
        example, RegExLiteral, Date? DateRange?

        A conjunctive query can be indicated by either providing a value of None
        for the context or the identifier associated with the Conjunctive Graph (if it's context aware).
        """

    # varients of triples will be done if / when optimization is needed

    def __len__(self, context=None):
        """
        Number of statements in the store. This should only account for non-quoted (asserted) statements
        if the context is not specified, otherwise it should return the number of statements in the formula or context given.
        """

    def contexts(self, triple=None):
        """
        Generator over all contexts in the graph. If triple is specified, a generator over all
        contexts the triple is in.
        """

    def remove_context(self, identifier):
        """
        Removes the given context from the graph.
        """        

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


