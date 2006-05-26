#!/d/Bin/Python/python.exe
"""Some utility functions built on the top of rdflib
"""
##
# This module contains the {@link #sparqlGraph} class and the related Exceptions.
##

##########################################################################
from rdflib.Graph import Graph
from rdflib.Namespace   import Namespace
from rdflib.URIRef      import URIRef
from rdflib.Literal     import Literal
from rdflib.BNode       import BNode
from rdflib.constants   import RDFNS  as ns_rdf
from rdflib.constants   import RDFSNS as ns_rdfs
from rdflib.constants   import NIL    as nil
from rdflib.exceptions  import Error

from rdflib.util import check_predicate, check_subject, check_object

import sparql

##########################################################################
# strictly speaking this is not an RDF stuff, but comes up so often...

ns_dc  = Namespace("http://purl.org/dc/elements/1.1/")
ns_owl = Namespace("http://www.w3.org/2002/07/owl#")

########################################################################## 
import sys, warnings, sets
from types import *


##
# RDFS Validity Exception (subclass of the RDFLib Exceptions). The small RDFS entailing part may detect errors; this
# exception is then raised
class RDFSValidityError(Error) :
    """An RDFS statement is not properly used"""
    def __init__(self,n1,n2):
        Error.__init__(self, "RDFS is not used properly: %s,%s" % (n1,n2))

##########################################################################

##
# The main wrapper class around RDFLib
class SPARQLGraph(sparql.SPARQL) :
    """A wrapper class around the original triple store, that includes
    some additional utility methods"""
    def __init__(self, graph=None) :
        if graph is None:
            graph = Graph()
        self.graph = graph
        sparql.SPARQL.__init__(self)

    def __getattr__(self, attr):
        if hasattr(self.graph, attr):
            return getattr(self.graph, attr)
        raise AttributeError, '%s has no such attribute %s' % (repr(self), attr)

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
            Cluster = sparqlGraph()
            
        # This will raise an exception if not kosher...
        try :
            check_subject(seed)
        except :
            print "Wrong type for clustering (probably a literal): %s" % seed
            import sys
            sys.exit(0)
            
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
            Cluster = sparqlGraph()

        # This will raise an exception if not kosher...
        try :
            check_object(seed)
        except :
            print "Wrong type for clustering: %s" % seed
            import sys
            sys.exit(0)
            
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
        return self.clusterBackward(seed) + self.clusterForward(seed)
        
    #############################################################################################################
    # Operator methods; 
    #  
    ##
    # Set theoretical union, expressed as an operator
    # @param other the other triple store
    def __add__(self,other) :
        """Set theoretical union"""
        retval = sparqlGraph()
        for x in self.graph:  retval.add(x)
        for y in other.graph: retval.add(y)
        return retval

    ##    
    # Set theoretical intersection, expressed as an operator
    # @param other the other triple store
    def __mul__(self,other) :
        """Set theoretical intersection"""
        retval = sparqlGraph()
        for x in other.graph:
            if x in self.graph: retval.add(x)
        return retval
        
    ##    
    # Set theoretical difference, expressed as an operator
    # @param other the other triple store
    def __sub__(self,other) :
        """Set theoretical difference"""
        retval = sparqlGraph()
        for x in self.graph:
            if not x in other.graph : retval.add(x)
        return retval

        
    
        
                
