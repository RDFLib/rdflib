#!/d/Bin/Python/python.exe
"""Some utility functions built on the top of rdflib
"""
##
# This module contains the {@link #myTripleStore} class and the related Exceptions.
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


##########################################################################
##
# Uniqueness Error Exception (subclass of the RDFLib Exceptions). Raised if the methods expect a unique
# value and they hit more...
class UniquenessError(Error) :
    """A uniqueness assumption was made in the context, and that is not true"""
    def __init__(self,n1,n2):
        Error.__init__(self, "Uniqueness assumption is not fullfilled: %s,%s" % (n1,n2))

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
    """A wrapper class around the original triple store, that includes some additional utility methods"""
    def __init__(self, graph=None) :
        if graph is None:
            graph = Graph()
        self.graph = graph
        sparql.SPARQL.__init__(self)

    def __getattr__(self, attr):
        if hasattr(self.graph, attr):
            return getattr(self.graph, attr)
        raise AttributeError, '%s has no such attribute %s' % (repr(self), attr)

    def getPredicateValue(self,s,p) :
        """
        Get a predicate value for an subject. Useful if one knows that there may only be one...
        Returns None if no value exists.
        
        It is one of those situations that occur a lot, hence this 'macro' like utility.
        
        @param s: subject 
        @param p: predicate
        @rtype: an RDFLib Resource
        @raise UniquenessError: the triple store contains more than one value for the (s,p) pair
        """    
        retval = None
        for v in self.store.objects(s,p) :
            if retval != None :
                # this can happen only if the value is not unique!
                raise UniquenessError(s,p)
            else :
                retval = v
        return retval
    
    def getPredicateSubject(self,p,v) :
        """Get a subject value for predicate and a value. Useful if one knows that there may only be one...
        Returns None if no value exists.
        
        It is one of those situations that occur a lot, hence this 'macro' like utility.
        
        @param p: predicate
        @param v: value 
        @rtype: RDFLib Resource
        @raise UniquenessError: the triple store contains more than one subject for the (p,v) pair
        """    
        retval = None
        for s in self.store.subjects(p,v) :
            if retval != None :
                # this can happen only if the value is not unique!
                raise UniquenessError(p,v)
            else :
                retval = s
        return retval

    def isTrue(self,s,p,o) :
        """Checking the truthfulness of a triplet, ie, its existence. Returns True/False. It is just an idiom...
        
        
        @depreciated: I realized later that using 'in' is by far the simplest thing that would not really need a separate method,
        but I left it here for backward compatibility. 
        
        @param s: subject 
        @param p: predicate
        @param o: object
        @rtype: Boolean
        """
        return (s,p,o) in self

    def unfoldCollection(self,resource) :
        """
        Return a list of, well, list (collection) elements in RDF.
           
        Rdflib's store has a  method called 
        item, which is generator over list elements. In some cases this is just 
        enough. However, the advantage of using this method is that it 
        returns a Python list that can be, for example, sliced, massaged, etc,
        and that is sometimes quite useful.
           
        @param resource: and RDFLib Resource
        @rtype: list
        @raise ListError: the resource is not a proper RDF collection
        """
        return map(None,self.store.items(resource))


    def _buildCollection(self,elements,father) :
        """
        Recursively build a list.
        
        @param elements: list of Literal, BNode or URIRef instances. The first element is added to the collection, the rest is
        handled by a recursive call to the same method
        @param father: the resource to which the head and the tail should be attached
        """
        if len(elements) == 0 :
            # This should not happen, in fact...
            return
        self.store.add((father,ns_rdf["first"],elements[0]))
        if len(elements) == 1 :
            # Close the list
            self.store.add((father,ns_rdf["rest"],ns_rdf["nil"]))
        else :
            # Generate a new head
            next = BNode()
            self.store.add((next,ns_rdf["type"],ns_rdf["List"]))
            self.store.add((father,ns_rdf["rest"],next))
            self._buildCollection(elements[1:],next)
        
    def storeCollection(self,elements,name=None) :
        """
        Store a (Python) list as an RDF List, ie, a collection.
        
        @param elements: list of Literal, BNode or URIRef instances
        @param name: the nodeId of the head of the list (if None, the system sets the nodeId as for all other BNodes)
        """
        lst = BNode(name)
        self.store.add((lst,ns_rdf["type"],ns_rdf["List"]))
        self._buildCollection(elements,lst)
        return lst        
        
    def getSeq(self,resource) :
        """
        Check if resource is an rdf:Seq. If yes, it returns a Seq class instance, None otherwise.
        
        @param resource: and RDFLib Resource
        @rtype: L{Seq<rdflibUtils.myTripleStore.Seq>}        
        """
        try :
            if (resource,ns_rdf['type'],ns_rdf['Seq']) in self :
                return Seq(self,resource)
            else :
                return None
        except :
            return None
            
    def getAlt(self,resource) :
        """
        Check if resource is an rdf:Alt. If yes, it returns a Alt class instance, None otherwise.
        
        @param resource: and RDFLib Resource
        @rtype: L{Alt<rdflibUtils.myTripleStore.Alt>}        
        """
        try :
            if (resource,ns_rdf['type'],ns_rdf['Alt']) in self :
                return Alt(self,resource)
            else :
                return None
        except :
            return None

    def getBag(self,resource) :
        """
        Check if resource is an rdf:Bag. If yes, it returns a Bag class instance, None otherwise.
        
        @param resource: and RDFLib Resource
        @rtype: L{Bag<rdflibUtils.myTripleStore.Bag>}        
        """
        try :
            if (resource,ns_rdf['type'],ns_rdf['Bag']) in self :
                return Bag(self,resource)
            else :
                return None
        except :
            return None
            
    def _storeContainer(self,elements,contType,name) :
        """
        Store a container. Elements given as an array are added to the triple store. 
        The BNode for the container is created on the fly.
        
        @param elements: an array of RDF resources, ie, URIRefs, BNodes, or Literals
        @param contType: name of the container (one of "Seq", "Alt", or "Bag")
        @type contType: string
        @param name: the nodeId of the BNode for the rdf:Seq (if None, the system sets the nodeId as for all other BNodes)
        @returns: the new Seq instance
        @rtype: BNode
        """
        seq = BNode(name)
        self.store.add((seq,ns_rdf["type"],ns_rdf[contType]))
        for i in range(0,len(elements)) :
            pred = ns_rdf["_%d" % (i+1)]
            self.store.add((seq,pred,elements[i]))
        return seq

    def storeSeq(self,elements,name=None) :
        """
        Store a Seq container. Elements given as an array are added to the triple store. 
        The BNode for the container is created on the fly.
        
        @param elements: an array of RDF resources, ie, URIRefs, BNodes, or Literals
        @param name: the nodeId of the BNode for the rdf:Seq (if None, the system sets the nodeId as for all other BNodes)
        @returns: the new Seq instance
        @rtype: L{Seq<rdflibUtils.myTripleStore.Seq>}
        """
        return Seq(self,self._storeContainer(elements,"Seq",name))
        
    def storeBag(self,elements,name=None) :
        """
        Store a Seq container. Elements given as an array are added to the triple store. 
        The BNode for the container is created on the fly.
        
        @param elements: an array of RDF resources, ie, URIRefs, BNodes, or Literals
        @param name: the nodeId of the BNode for the rdf:Seq (if None, the system sets the nodeId as for all other BNodes)
        @returns: the new Seq instance
        @rtype: L{Bag<rdflibUtils.myTripleStore.Bag>}
        """
        return Bag(self,self._storeContainer(elements,"Bag",name))
        
    def storeAlt(self,elements,name=None) :
        """
        Store a Seq container. Elements given as an array are added to the triple store. 
        The BNode for the container is created on the fly.
        
        @param elements: an array of RDF resources, ie, URIRefs, BNodes, or Literals
        @param name: the nodeId of the BNode for the rdf:Seq (if None, the system sets the nodeId as for all other BNodes)
        @returns: the new Seq instance
        @rtype: L{Alt<rdflibUtils.myTripleStore.Alt>}
        """
        return Alt(self,self._storeContainer(elements,"Alt",name))

    ##############################################################################################################
    # Clustering methods
    def _clusterForward(self,seed,Cluster) :
        """Cluster the triple store: from a seed, transitively get all properties and objects in direction of the arcs.
        
        @param seed: RDFLib Resource
        @param Cluster: a L{myTripleStore} instance, that has to be expanded with the new arcs
        """
        try :        
            # get all predicate and object pairs for the seed. 
            # *If not yet in the new cluster, then go with a recursive round with those*
            for (p,o) in self.store.predicate_objects(seed) :
                if not (seed,p,o) in Cluster :
                    Cluster.add((seed,p,o))
                    self._clusterForward(p,Cluster)
                    self._clusterForward(o,Cluster)
        except :
            pass
        

    def clusterForward(self,seed,Cluster=None) :
        """
        Cluster the triple store: from a seed, transitively get all properties and objects in direction of the arcs.
        
        @param seed: RDFLib Resource
        @param Cluster: another myTripleStore instance; if None, a new one will be created. The subgraph will be added
        to this store.
        @returns: The triple store containing the cluster
        @rtype: L{myTripleStore}
        """
        if Cluster == None :
            Cluster = myTripleStore()
            
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
        """Cluster the triple store: from a seed, transitively get all properties and objects in backward direction of the arcs.
        
        @param seed: RDFLib Resource
        @param Cluster: a L{myTripleStore} instance, that has to be expanded with the new arcs
        """
        try :
            for (s,p) in self.store.subject_predicates(seed) :
                if not (s,p,seed) in Cluster :
                    Cluster.add((s,p,seed))
                    self._clusterBackward(s,Cluster)
                    self._clusterBackward(p,Cluster)
        except :
            pass
            
    def clusterBackward(self,seed,Cluster=None) :
        """
        Cluster the triple store: from a seed, transitively get all properties and objects 'backward', ie,
        following the link back in the graph.
        
        @param seed: RDFLib Resource
        @param Cluster: another myTripleStore instance; if None, a new one will be created. The subgraph will be added
        to this store.
        @returns: The triple store containing the cluster
        @rtype: L{myTripleStore}
        """
        if Cluster == None :
            Cluster = myTripleStore()

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
        Cluster up and down, by summing up the forward and backward clustering
        
        @param seed: RDFLib Resource
        @returns: The triple store containing the cluster
        @rtype: L{myTripleStore}
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
        retval = myTripleStore()
        for x in self:  retval.add(x)
        for y in other: retval.add(y)
        return retval

    ##    
    # Set theoretical intersection, expressed as an operator
    # @param other the other triple store
    def __mul__(self,other) :
        """Set theoretical intersection"""
        retval = myTripleStore()
        for x in other:
            if x in self: retval.add(x)
        return retval
        
    ##    
    # Set theoretical difference, expressed as an operator
    # @param other the other triple store
    def __sub__(self,other) :
        """Set theoretical difference"""
        retval = myTripleStore()
        for x in self:
            if not x in other : retval.add(x)
        return retval

        
    #############################################################################################################
    # Poor man's RDFS
    def _extendTypesR(self,target,res,typ) :
        """
        Semi-reification for subClassOf. For all X such as (typ,rdf:subClassOf,X) and for all resources such as
        (res,rdf:type,typ), the (res,rdf:type,X) is added to target, and then this is done recursively for (target,res,X).
        
        @param target: L{myTripleStore}, where the new arcs will be accumulated
        @param res: RDFLib Resource
        @param typ: RDFLib Resource    
        """
        for nTyp in self.store.objects(typ,ns_rdfs["subClassOf"]) :
            if not isinstance(nTyp,URIRef) :
                raise RDFSValidityError("rdfs:subClassOf",nTyp)                
            target.add((res,ns_rdf["type"],nTyp))
            self._extendTypesR(target,res,nTyp)
            
    def _extendTypes(self) :
        """
        Extend the graph by a recursively adding the new types based on rdf:subClassOf (calling L{_extendTypesR} for possible combinations).
        
        @raise RDFSValidityError: if a triple in the triple store is invalid (o or s is a Literal for an rdf:type triplet).
        """
        target = myTripleStore()
        for (s,o) in self.store.subject_objects(ns_rdf["type"]) :
            if isinstance(o,Literal) :
                raise RDFSValidityError("rdfs:type",o)
            if isinstance(s,Literal) :
                raise RDFSValidityError("rdfs:type",s)
            self._extendTypesR(target,s,o)
        self += target
        
    def _extendPropertiesR(self,target,s,o,prop) :
        """
        Semi-reification for subPropertyOf: for a (s,prop,o) (s,P,o) is also added where (prop,subPropertyOf,P), and this is
        done recursively by adding it to target.
        
        @param target: L{myTripleStore}, where the new arcs will be accumulated
        @param s: RDFLib Resource (for subject)
        @param o: RDFLib Resource (for object)
        @param prop: RDFLib Resource (for property)
        
        """
        target.add((s,prop,o))
        for neP in self.store.objects(prop,ns_rdfs["subPropertyOf"]) :
            if not isinstance(neP,URIRef) :
                raise RDFSValidityError("rdfs:subClassOf",neP)                
            self._extendPropertiesR(target,s,o,neP)
        
    def _extendProperties(self) :
        """
        Extend the graph by a recursively adding the new triples for subproperies (calling L{_extendPropertiesR} for possible 
        combinations).
        
        @raise RDFSValidityError: if a triple in the triple store is invalid (prop is not a URIRef).
        """
        target = myTripleStore() 
        for (prop,supProp) in self.store.subject_objects(ns_rdfs["subPropertyOf"]) :
            if not isinstance(prop,URIRef) :
                raise RDFSValidityError("rdfs:subClassOf",prop)                
            for (s,o) in self.store.subject_objects(prop) :
                self._extendPropertiesR(target,s,o,prop)
        self += target
    
    def _extendRangeDomain(self) :
        """
        Extend the graph with the range and domains by adding new types for all predicates in the original graphs.
        @raise RDFSValidityError: If range or domain uses anything else then URIRefs
        """
        for (P,C) in self.store.subject_objects(ns_rdfs["range"]) :
            if not isinstance(P,URIRef) :
                raise RDFSValidityError("rdfs:range",P)                
            if not isinstance(C,URIRef) :
                raise RDFSValidityError("rdfs:range",C)                
            for (s,o) in self.store.subject_objects(P) :
                if isinstance(s,Literal) :
                    raise RDFSValidityError(P,s)                
                self.store.add((o,ns_rdf["type"],C))
        for (P,C) in self.store.subject_objects(ns_rdfs["domain"]) :
            if not isinstance(P,URIRef) :
                raise RDFSValidityError("rdfs:domain",P)                
            if not isinstance(C,URIRef) :
                raise RDFSValidityError("rdfs:domain",C)                
            for (s,o) in self.store.subject_objects(P) :
                if isinstance(s,Literal) :
                    raise RDFSValidityError(P,s)                
                self.store.add((s,ns_rdf["type"],C))

    def extendRdfs(self) :
        """
        Poor man's RDFS entailement. The method does not do a full RDFS entailement (this would 
        greatly increase the size of the triple store, and RDFLib may not be efficient enough for that).
        Instead:
            
          - extend the subproperties defined in the triple store (ie, if p is subProperty of q, then for all
          (s p o) the (s q o) triplets are created and added to the store, and this is done recursively).
          
          - expand range and domain, ie if the range (domain) are defined for a property, all object (subject)
          resources for that property are properly typed via rdf:type
          
          - extend the subtypes defined in the triple store, similarly to subproperties.
        
        Though not a full entailement, I believe that it covers a large number of useful cases for the user.    
        
        @raise RDFSValidityError: if the triple store contains incorrect triples
        """
        self._extendProperties()
        self._extendRangeDomain()
        self._extendTypes()
        
        
###########################################################################################################
##
# Wrapper around an RDF Seq resource. It implements a container type that can be used
# with the usual [..] methods or next

class Container :
    """
    Wrapper around an RDF Container resource. 
    
    This class is not really used by itself, rather through its subclasses: 
    L{Seq<rdflibUtils.myTripleStore.Seq>}, L{Bag<rdflibUtils.myTripleStore.Bag>}, or
    L{Alt<rdflibUtils.myTripleStore.Alt>}.
    
    @ivar resource: the RDFLib resource for the Container
    @type resource: BNode
    @ivar triplets: the triple for the container instance
    @type triplets: L{myTripleStore<rdflibUtils.myTripleStore.myTripleStore>}        
    """
    _keys  = []
    _list  = {}
    _index = 0
    def __init__(self,triplets,resource) :
        """The triplets is of type myTripleStore, the resource
        is simply the resource which is supposed to be a Seq.
        
        The 'target' resources are initially collected in a dictionary,
        keyed with the predicate names. The of keys is stored apart, and
        the iteration/getitem goes through the keys set to retrieve the
        dictionary content.
        
        @param triplets: the triplets for the triple store
        @type triplets: myTripleStore
        @param resource: an (RDFLib) resource, ie, the Seq, Alt, or Bag. Note that the init
        does not check whether this is a Seq, this is done by whoever creates this
        instance!
        """
        # The array of predicate and objects is created; it is supposed
        # to filter out the one which simply states that the resource
        # itself is a Seq
        self._list = {}
        for (p,o) in triplets.predicate_objects(resource) :
            if o != ns_rdf['Seq'] :
                key = "%s" % p
                self._list[key] = o
        # here is the trick: the predicates are _1, _2, _3, etc. Ie, 
        # by sorting the keys we have what we want!
        self._keys = self._list.keys()
        self._index = 0
        self.triplets = triplets
        self.resource = resource

    def __iter__(self) :
        """returns self!"""
        self._index = 0
        return self
        
    def next(self):
        """Obvious iteration through the content using the sorted keys.
        
        @raises StopIteration: when the end of the sequence has been reached
        """
        if self._index == len(self._keys) :
            raise StopIteration
        else :
            retval = self._list[self._keys[self._index]]
            self._index += 1
            return retval
    
    def __len__(self) :
        return len(self._keys)
    
    def __getitem__(self,index) :
        """Obvious getitem using the sorted keys."""
        if index < 0 or index >= len(self._keys) :
            raise IndexError
        else :
            return self._list[self._keys[index]]

    def addItem(self,res) :
        """Add a new resource to the list (as the last element).
        @param res: an RDFLib resource (BNode, URIRef, or Literal)
        """
        i = len(self._keys)
        key = "_%d" % (i+1)
        p = ns_rdf[key]
        self.triplets.add((self.resource,p,res))
        self._list[key] = res
        self._keys = self._list.keys()
        

class Seq (Container) :
    """
    The keys, inherited from L{Container<rdflibUtils.myTripleStore.Container>}, are sorted both when the class
    is created and when a new item is added. That ensures the right order in getting the data, as required by the 
    semantics of rdf:Seq.
    """
    def __init__(self,triplets,resource) :
        """The triplets is of type myTripleStore, the resource
        is simply the resource which is supposed to be a Seq.
        
        The 'target' resources are initially collected in a dictionary,
        keyed with the predicate names. The sorted list of keys is stored apart, and
        the iteration/getitem goes through the sorted key set to retrieve the
        dictionary content.
        
        @param triplets: the triplets for the triple store
        @type triplets: myTripleStore
        @param resource: an (RDFLib) resource, ie, the Seq. Note that the init
        does not check whether this is a Seq, this is done by whoever creates this
        instance!
        """
        Container.__init__(self,triplets,resource)
        self._keys.sort()
            
    def addItem(self,res) :
        Container.addItem(self,res)
        self._keys.sort()
        
class Alt(Container) :
    """This is just a placeholder class for naming, does not add any functionality to a Container"""
    pass
        
class Bag(Container) :
    """This is just a placeholder class for naming, does not add any functionality to a Container"""
    pass
    
        
                
