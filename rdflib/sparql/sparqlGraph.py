from rdflib.Graph import Graph, ConjunctiveGraph

class SPARQLGraph(object):
    """
    A subclass of Graph with a few extra SPARQL bits.
    """
    SPARQL_DATASET=0
    NAMED_GRAPH=1
    __slots__ = ("graphVariable","DAWG_DATASET_COMPLIANCE","identifier","graphKind","graph")
    def __init__(self, graph, graphVariable = None, dSCompliance = False):
        assert not graphVariable or graphVariable[0]!='?',repr(graphVariable)
        self.graphVariable = graphVariable
        self.DAWG_DATASET_COMPLIANCE = dSCompliance
        self.graphKind=None
        if graph is not None:
            self.graph = graph # TODO
            #self.store = graph.store
            if isinstance(graph,ConjunctiveGraph):
                self.graphKind = self.SPARQL_DATASET
                self.identifier = graph.default_context.identifier
            else:
                self.graphKind = self.NAMED_GRAPH
                self.identifier = graph.identifier
        #super(SPARQLGraph, self).__init__(store, identifier)

    def setupGraph(self,store,graphKind=None):
        gKind = graphKind and graphKind or self.graphKind
        self.graph = gKind(store,self.identifier)

    def __reduce__(self):
        return (SPARQLGraph,
                (None,
                 self.graphVariable,
                 self.DAWG_DATASET_COMPLIANCE),
                self.__getstate__())
        
    def __getstate__(self):
        return (self.graphVariable,
                self.DAWG_DATASET_COMPLIANCE,
                self.identifier)#,
                #self.graphKind)

    def __setstate__(self, arg):
        #gVar,flag,identifier,gKind=arg
        gVar,flag,identifier=arg
        self.graphVariable=gVar
        self.DAWG_DATASET_COMPLIANCE=flag
        self.identifier=identifier
        #self.graphKind=gKind
        #self.graph=Graph(store,identifier)

    ##############################################################################################################
    # Clustering methods
    def _clusterForward(self,seed,Cluster) :
        """Cluster the triple store: from a seed, transitively get all
        properties and objects in direction of the arcs.

        @param seed: RDFLib Resource

        @param Cluster: a L{sparqlGraph} instance, that has to be
        expanded with the new arcs
        """
        try :
            # get all predicate and object pairs for the seed.
            # *If not yet in the new cluster, then go with a recursive round with those*
            for (p,o) in self.graph.predicate_objects(seed) :
                if not (seed,p,o) in Cluster.graph :
                    Cluster.add((seed,p,o))
                    self._clusterForward(p,Cluster)
                    self._clusterForward(o,Cluster)
        except :
            pass


    def clusterForward(self,seed,Cluster=None) :
        """
        Cluster the triple store: from a seed, transitively get all
        properties and objects in direction of the arcs.

        @param seed: RDFLib Resource

        @param Cluster: another sparqlGraph instance; if None, a new
        one will be created. The subgraph will be added to this graph.

        @returns: The triple store containing the cluster

        @rtype: L{sparqlGraph}
        """
        if Cluster == None :
            Cluster = SPARQLGraph()

        # This will raise an exception if not kosher...
        check_subject(seed) #print "Wrong type for clustering (probably a literal): %s" % seed
        self._clusterForward(seed,Cluster)
        return Cluster


    def _clusterBackward(self,seed,Cluster) :
        """Cluster the triple store: from a seed, transitively get all
        properties and objects in backward direction of the arcs.

        @param seed: RDFLib Resource

        @param Cluster: a L{sparqlGraph} instance, that has to be
        expanded with the new arcs
        """
        try :
            for (s,p) in self.graph.subject_predicates(seed) :
                if not (s,p,seed) in Cluster.graph :
                    Cluster.add((s,p,seed))
                    self._clusterBackward(s,Cluster)
                    self._clusterBackward(p,Cluster)
        except :
            pass

    def clusterBackward(self,seed,Cluster=None) :
        """
        Cluster the triple store: from a seed, transitively get all
        properties and objects 'backward', ie, following the link back
        in the graph.

        @param seed: RDFLib Resource

        @param Cluster: another sparqlGraph instance; if None, a new
        one will be created. The subgraph will be added to this graph.

        @returns: The triple store containing the cluster

        @rtype: L{sparqlGraph}
        """
        if Cluster == None :
            Cluster = SPARQLGraph()

        # This will raise an exception if not kosher...
        check_object(seed) # print "Wrong type for clustering: %s" % seed
        self._clusterBackward(seed,Cluster)
        return Cluster

    def cluster(self,seed) :
        """
        Cluster up and down, by summing up the forward and backward
        clustering

        @param seed: RDFLib Resource

        @returns: The triple store containing the cluster

        @rtype: L{sparqlGraph}
        """
        raise "Am I getting here?"
        return self.clusterBackward(seed) + self.clusterForward(seed)
