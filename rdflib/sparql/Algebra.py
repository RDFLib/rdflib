#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
An implementation of the W3C SPARQL Algebra on top of sparql-p's expansion trees

See: http://www.w3.org/TR/rdf-sparql-query/#sparqlAlgebra

For each symbol in a SPARQL abstract query, we define an operator for evaluation. 
The SPARQL algebra operators of the same name are used to evaluate SPARQL abstract 
query nodes as described in the section "Evaluation Semantics".

We define eval(D(G), graph pattern) as the evaluation of a graph pattern with respect 
to a dataset D having active graph G. The active graph is initially the default graph.
"""
import unittest
from StringIO import StringIO
from rdflib.Graph import Graph, ReadOnlyGraphAggregate
from rdflib import URIRef, Variable, plugin, BNode, Literal
from rdflib.store import Store 
from rdflib.sparql.bison.Query import AskQuery, SelectQuery
from rdflib.sparql.bison.IRIRef import NamedGraph,RemoteGraph
from rdflib.sparql.bison.SolutionModifier import ASCENDING_ORDER
from rdflib.sparql import sparqlGraph, sparqlOperators, SPARQLError, Query
from rdflib.sparql.bison.SPARQLEvaluate import unRollTripleItems, _variablesToArray
from rdflib.sparql.bison.GraphPattern import *
from rdflib.sparql.graphPattern import BasicGraphPattern
from rdflib.sparql.bison.Triples import ParsedConstrainedTriples
from rdflib.sparql.bison.SPARQLEvaluate import createSPARQLPConstraint, CONSTRUCT_NOT_SUPPORTED, convertTerm

def ReduceGraphPattern(graphPattern,prolog):
    """
    Takes parsed graph pattern and converts it into a BGP operator
    
    .. Replace all basic graph patterns by BGP(list of triple patterns) ..
    """
    if isinstance(graphPattern.triples[0],list) and len(graphPattern.triples) == 1:
        graphPattern.triples = graphPattern.triples[0]
    items = []
    for triple in graphPattern.triples:
        if isinstance(triple,ParsedConstrainedTriples):
            if not triple.triples:
                #FIlter(expr,{})
                bgp = BasicGraphPattern([])
            else:
                bgp = BasicGraphPattern(list(unRollTripleItems(triple.triples,prolog)))
            constr = createSPARQLPConstraint(triple.constraint, prolog)
            bgp.addConstraint(constr)
            items.append(bgp)
        else:
            items.append(BasicGraphPattern(list(unRollTripleItems(triple,prolog))))
    if len(items) == 1:
        assert isinstance(items[0],BasicGraphPattern), repr(items)
        return items[0]
    elif len(items) > 1:
        #@note: should this concatenate BGPs?
        return reduce(Join,items)
    else:
        #an empty BGP?
        raise

def ReduceToAlgebra(left,right):
    """
    
    12.2.1 Converting Graph Patterns
    
    GraphPattern              ::=  FilteredBasicGraphPattern ( GraphPatternNotTriples '.'? GraphPattern )?
    FilteredBasicGraphPattern ::=  BlockOfTriples? ( Constraint '.'? FilteredBasicGraphPattern )?
    GraphPatternNotTriples    ::=  OptionalGraphPattern | GroupOrUnionGraphPattern | GraphGraphPattern              
    """
    if not isinstance(left,AlgebraExpression):
        if left:
            if not isinstance(left,BasicGraphPattern):
                assert isinstance(left,GraphPattern), repr(left)
                #A parsed Graph Pattern
                if left.triples:
                    if isinstance(left.nonTripleGraphPattern,ParsedOptionalGraphPattern):
                        # LeftJoin(BGP(..triples ..),{..})
                        leftTriples = ReduceGraphPattern(left,prolog)
                        left = LeftJoin(leftTriples,
                                        reduce(ReduceToAlgebra,
                                               left.nonTripleGraphPattern.graphPatterns,
                                               None))
                    elif isinstance(left.nonTripleGraphPattern,ParsedGraphGraphPattern):
                        #Join(..triples..,Graph(?name,{..}))
                        left = Join(ReduceGraphPattern(left,prolog),
                                    GraphExpression(left.nonTripleGraphPattern.name,
                                                    reduce(ReduceToAlgebra,
                                                           left.nonTripleGraphPattern.graphPatterns,
                                                           None)))

                    elif isinstance(left.nonTripleGraphPattern,
                                    ParsedAlternativeGraphPattern):
                        #Join(..triples..,Union(..))
                        unionList =\
                          [ reduce(ReduceToAlgebra,i.graphPatterns,None) for i in 
                              left.nonTripleGraphPattern.alternativePatterns ]
                        left = Join(ReduceGraphPattern(left,prolog),reduce(Union,unionList))
                else:
                    assert left.nonTripleGraphPattern
                    if isinstance(left.nonTripleGraphPattern,ParsedGraphGraphPattern):
                        #Graph(?name,{..})
                        left = GraphExpression(left.nonTripleGraphPattern.name,
                                               reduce(ReduceToAlgebra,
                                                      left.nonTripleGraphPattern.graphPatterns,
                                                      None))
                    elif isinstance(left.nonTripleGraphPattern,ParsedOptionalGraphPattern):
                        # LeftJoin({},left) => left
                        #Undefined?: see - http://lists.w3.org/Archives/Public/public-rdf-dawg/2007AprJun/0046.html
                        raise
                        left = reduce(ReduceToAlgebra,
                                      left.nonTripleGraphPattern.graphPatterns,
                                      None)
                    elif isinstance(left.nonTripleGraphPattern,
                                    ParsedAlternativeGraphPattern):
                        #Union(..)
                        unionList =\
                          [ reduce(ReduceToAlgebra,i.graphPatterns,None) for i in 
                              left.nonTripleGraphPattern.alternativePatterns ]
                        left = reduce(Union,unionList)
    if not isinstance(right,AlgebraExpression):
        assert isinstance(right,GraphPattern),type(right)
        #Parsed Graph Pattern
        if right.triples:
            if right.nonTripleGraphPattern: 
                #left is None, just return right (a GraphPatternNotTriples)
                if isinstance(right.nonTripleGraphPattern,ParsedGraphGraphPattern):
                    right = GraphExpression(right.nonTripleGraphPattern.name,
                                            reduce(ReduceToAlgebra,
                                                   right.nonTripleGraphPattern.graphPatterns,
                                                   None))
                elif isinstance(right.nonTripleGraphPattern,ParsedOptionalGraphPattern):
                    # LeftJoin(..triples..,{..})
                    rightTriples = ReduceGraphPattern(right,prolog)
                    right = LeftJoin(rightTriples,
                                    reduce(ReduceToAlgebra,
                                           right.nonTripleGraphPattern.graphPatterns,
                                           None))
                elif isinstance(right.nonTripleGraphPattern,ParsedAlternativeGraphPattern):
                    #Join(..triples..,Union(..))
                    unionList =\
                      [ reduce(ReduceToAlgebra,i.graphPatterns,None) for i in 
                          right.nonTripleGraphPattern.alternativePatterns ]                        
                    right = Join(ReduceGraphPattern(right,prolog),reduce(Union,unionList))
            else:
                #BGP({}...)
                right = ReduceGraphPattern(right,prolog)
        else:
            if right.nonTripleGraphPattern is None:
                assert left
                return left
            if right.nonTripleGraphPattern:
                if isinstance(right.nonTripleGraphPattern,ParsedGraphGraphPattern):
                    # Join(left,Graph(...))
                    right = GraphExpression(right.nonTripleGraphPattern.name,
                                            reduce(ReduceToAlgebra,
                                                   right.nonTripleGraphPattern.graphPatterns,
                                                   None))
                elif isinstance(right.nonTripleGraphPattern,ParsedOptionalGraphPattern):
                    if left:
                        # LeftJoin(left,right)
                        return LeftJoin(left,
                                        reduce(ReduceToAlgebra,
                                               right.nonTripleGraphPattern.graphPatterns,
                                               None))
                    else:
                        # LeftJoin({},right)
                        #see - http://lists.w3.org/Archives/Public/public-rdf-dawg/2007AprJun/0046.html
                        #raise
                        return EmptyGraphPatternExpression()
                elif isinstance(right.nonTripleGraphPattern,ParsedAlternativeGraphPattern):
                    #right = Union(..)
                    unionList =\
                      map(lambda i: reduce(ReduceToAlgebra,i.graphPatterns,None),
                          right.nonTripleGraphPattern.alternativePatterns)
                    right = reduce(Union,unionList)
    if not left:
        return right
    else:
        return Join(left,right)

def TopEvaluate(query,dataset,passedBindings = None,DEBUG=False):
    """
    The outcome of executing a SPARQL is defined by a series of steps, starting 
    from the SPARQL query as a string, turning that string into an abstract 
    syntax form, then turning the abstract syntax into a SPARQL abstract query
    comprising operators from the SPARQL algebra. This abstract query is then 
    evaluated on an RDF dataset.
    """
    if not passedBindings:
        passedBindings = {}
    global prolog
    if query.prolog:
        query.prolog.DEBUG = DEBUG
    prolog = query.prolog    
    if query.query.dataSets:
        graphs = []
        for dtSet in query.query.dataSets:
            if isinstance(dtSet,NamedGraph):
                graphs.append(Graph(dataset.store,dtSet))
            else:
                #GRDDL hook here...
                memStore = plugin.get('IOMemory',Store)()
                memGraph = Graph(memStore)
                try:
                    #Try as RDF/XML first
                    memGraph.parse(dtSet)
                except:
                    try:
                        #Parse as Notation 3 instead
                        memGraph.parse(dtSet,format='n3')
                    except:
                        #RDFa?
                        memGraph.parse(dtSet,format='rdfa')
                graphs.append(memGraph)
        tripleStore = sparqlGraph.SPARQLGraph(ReadOnlyGraphAggregate(graphs,store=dataset.store))
    else:        
        tripleStore = sparqlGraph.SPARQLGraph(dataset)    
    if isinstance(query.query,SelectQuery) and query.query.variables:
        query.query.variables = [convertTerm(item,query.prolog) for item in query.query.variables]
    else:
        query.query.variables = []

    expr = reduce(ReduceToAlgebra,query.query.whereClause.parsedGraphPattern.graphPatterns,
                  None)
    if isinstance(expr,BasicGraphPattern):
        retval = None
        bindings = Query._createInitialBindings(expr)
        if passedBindings:
            bindings.update(passedBindings)
        top = Query._SPARQLNode(None,bindings,expr.patterns, tripleStore)
        top.expand(expr.constraints)
        result = Query.Query(top, tripleStore)
    else:
        assert isinstance(expr,AlgebraExpression), repr(expr)
        if DEBUG:
            print "## Full SPARQL Algebra expression ##"
            print expr
            print "###################################"
        result = expr.evaluate(tripleStore,passedBindings,query.prolog)
        if isinstance(result,BasicGraphPattern):
            retval = None
            bindings = Query._createInitialBindings(result)
            if passedBindings:
                bindings.update(passedBindings)
            top = Query._SPARQLNode(None,bindings,result.patterns, result.tripleStore)
            top.expand(result.constraints)
            result = Query.Query(top, tripleStore)
        assert isinstance(result,Query.Query),repr(result)
    #result = queryObject(tripleStore, basicPatterns,optionalPatterns,passedBindings)
    if result == None :
        # generate some proper output for the exception :-)
        msg = "Errors in the patterns, no valid query object generated; "
        msg += ("pattern:\n%s\netc..." % basicPatterns[0])
        raise SPARQLError(msg)

    if isinstance(query.query,AskQuery):
        return result.ask()

    elif isinstance(query.query,SelectQuery):
        orderBy = None
        orderAsc = None
        if query.query.solutionModifier.orderClause:
            orderBy     = []
            orderAsc    = []
            for orderCond in query.query.solutionModifier.orderClause:
                # is it a variable?
                if isinstance(orderCond,Variable):
                    orderBy.append(orderCond)
                    orderAsc.append(ASCENDING_ORDER)
                # is it another expression, only variables are supported
                else:
                    expr = orderCond.expression
                    assert isinstance(expr,Variable),"Support for ORDER BY with anything other than a variable is not supported: %s"%expr
                    orderBy.append(expr)                    
                    orderAsc.append(orderCond.order == ASCENDING_ORDER)

        limit = query.query.solutionModifier.limitClause and int(query.query.solutionModifier.limitClause) or None

        offset = query.query.solutionModifier.offsetClause and int(query.query.solutionModifier.offsetClause) or 0
        return result.select(query.query.variables,
                             query.query.distinct,
                             limit,
                             orderBy,
                             orderAsc,
                             offset
                             ),_variablesToArray(query.query.variables,"selection"),result._getAllVariables(),orderBy,query.query.distinct
    else:
        raise NotImplemented(CONSTRUCT_NOT_SUPPORTED,repr(query))
                    
class AlgebraExpression(object):
    """
    For each symbol in a SPARQL abstract query, we define an operator for 
    evaluation. The SPARQL algebra operators of the same name are used 
    to evaluate SPARQL abstract query nodes as described in the section 
    "Evaluation Semantics".
    """
    def __repr__(self):
        return "%s(%s,%s)"%(self.__class__.__name__,self.left,self.right)

    def evaluate(self,tripleStore,initialBindings,prolog):
        """
        12.5 Evaluation Semantics
        
        We define eval(D(G), graph pattern) as the evaluation of a graph pattern
        with respect to a dataset D having active graph G. The active graph is 
        initially the default graph.
        """        
        raise Exception(repr(self))

class EmptyGraphPatternExpression(AlgebraExpression):
    """
    A placeholder for evaluating empty graph patterns - which
    should result in an empty multiset of solution bindings
    """
    def __repr__(self):
        return "EmptyGraphPatternExpression(..)"
    def evaluate(self,tripleStore,initialBindings,prolog):
        #raise NotImplementedError("Empty Graph Pattern expressions, not supported")
        if prolog.DEBUG:
            print "eval(%s,%s,%s)"%(self,initialBindings,tripleStore.graph)
        empty = Query._SPARQLNode(None,{},[],tripleStore)
        empty.bound = False
        return Query.Query(empty, tripleStore)

def _fetchBoundLeaves(node):
    """
    Takes a SPARQLNode and returns a generator
    over its bound leaves
    """
    if len(node.children) == 0 :
        if node.bound and not node.clash:
            yield node
    else :
        for c in node.children :
            for proxy in _fetchBoundLeaves(c):
                yield proxy

def _ExpandJoin(node,expression,tripleStore,prolog,optionalTree=False):
    """
    Traverses to the leaves of expansion trees to implement the Join
    operator
    """
    if len(node.children) == 0  :
        # this is a leaf in the original expansion
        if isinstance(expression,AlgebraExpression):
            #If an algebra expression evaluate it passing on the leaf bindings
            if prolog.DEBUG:
                print "passing on bindings to %s\n:%s"%(expression,node.bindings.copy())
            expression = expression.evaluate(tripleStore,node.bindings.copy(),prolog)
        if isinstance(expression,BasicGraphPattern):
            if prolog.DEBUG:
                print "Evaluated left node and traversed to leaf, expanding with ", expression
                print "has tripleStore? ", hasattr(expression,'tripleStore')
                print node.tripleStore.graph
                tmp = Query._createInitialBindings(expression)
                tmp.update(node.bindings)
                print tmp
            exprBindings = Query._createInitialBindings(expression)
            exprBindings.update(node.bindings)
            #An indicator for whether this node has any descendant optional expansions
            #we should consider instead
            #in Join(LeftJoin(A,B),X), if the inner LeftJoin is successful, then X is joined
            #against the cumulative bindings ( instead of just A )
            descendantOptionals = node.optionalTrees and \
                [o for o in node.optionalTrees if list(_fetchBoundLeaves(o))] 
            if not descendantOptionals:
                top = node
            else:
                top = None
            child = None            
            if not node.clash and not descendantOptionals:
                #It has compatible bindings and either no optional expansions
                #or no *valid* optional expansions
                child = Query._SPARQLNode(top,
                                          exprBindings,
                                          expression.patterns,
                                          hasattr(expression,'tripleStore') and \
                                            expression.tripleStore or node.tripleStore)
                child.expand(expression.constraints)
                if prolog.DEBUG:
                    print "Has compatible bindings and no valid optional expansions"
                    print "Newly bound descendants: ", list(_fetchBoundLeaves(child))
        else:
            assert isinstance(expression,Query.Query) and expression.top, repr(expression)            
            #Already been evaluated (non UNION), just attach the SPARQLNode
            child = expression.top
            
        if node.clash == False and child is not None:
            node.children.append(child)
            if prolog.DEBUG:
                print "Adding %s to %s"%(child,node)
        for optTree in node.optionalTrees:
            #Join the optional paths as well - those that are bound and valid
            for validLeaf in _fetchBoundLeaves(optTree):
                _ExpandJoin(validLeaf,expression,tripleStore,prolog,optionalTree=True)
    else :
        for c in node.children :
            _ExpandJoin(c,expression,tripleStore,prolog)

class Join(AlgebraExpression):
    """
    [[(P1 AND P2)]](D,G) = [[P1]](D,G) compat [[P2]](D,G)
    
    Join(Ω1, Ω2) = { merge(μ1, μ2) | μ1 in Ω1 and μ2 in Ω2, and μ1 and μ2 are \
                     compatible }
    
    Pseudocode implementation:
    
    Evaluate BGP1
    Traverse to leaves (expand and expandOption leaves) of BGP1, set 'rest' to 
    triple patterns in BGP2 (filling out bindings).
    Trigger another round of expand / expandOptions (from the leaves)    
    """
    def __init__(self,BGP1,BGP2):
        self.left  = BGP1
        self.right = BGP2
            
    def evaluate(self,tripleStore,initialBindings,prolog):
        if prolog.DEBUG:
            print "eval(%s,%s,%s)"%(self,initialBindings,tripleStore.graph)
        if isinstance(self.left,AlgebraExpression):
            self.left = self.left.evaluate(tripleStore,initialBindings,prolog)
        if isinstance(self.left,BasicGraphPattern):        
            retval = None
            bindings = Query._createInitialBindings(self.left)
            if initialBindings:
                bindings.update(initialBindings)
            if hasattr(self.left,'tripleStore'):
                #Use the prepared tripleStore
                tripleStore = self.left.tripleStore
            top = Query._SPARQLNode(None,
                                    bindings,
                                    self.left.patterns,
                                    tripleStore)
            top.expand(self.left.constraints)
            _ExpandJoin(top,self.right,tripleStore,prolog)
            return Query.Query(top, tripleStore)
        else:
            assert isinstance(self.left,Query.Query), repr(self.left)
            if self.left.parent1 and self.left.parent2:
                #union branch.  We need to unroll both operands
                _ExpandJoin(self.left.parent1.top,self.right,tripleStore,prolog)
                _ExpandJoin(self.left.parent2.top,self.right,tripleStore,prolog)
            else:
                _ExpandJoin(self.left.top,self.right,tripleStore,prolog)
            return self.left

def _ExpandLeftJoin(node,expression,tripleStore,prolog,optionalTree=False):
    """
    Traverses to the leaves of expansion trees to implement the LeftJoin
    operator
    """
    if len(node.children) == 0  :
        # this is a leaf in the original expansion
        if prolog.DEBUG:
            print "Performing a left join on ", node
        if node.clash:
            if prolog.DEBUG:
                print "Bypassing clashed node"
            return
        if isinstance(expression,AlgebraExpression):
            #If a Graph pattern evaluate it passing on the leaf bindings
            #(possibly as solutions to graph names
            if prolog.DEBUG:
                print "evaluating B in LeftJoin(A,B)"
                print "passing on bindings to %s\n:%s"%(expression,node.bindings.copy())
            expression = expression.evaluate(tripleStore,node.bindings.copy(),prolog)
        if isinstance(expression,BasicGraphPattern):
            rightBindings = Query._createInitialBindings(expression)
            rightBindings.update(node.bindings)
            optTree = Query._SPARQLNode(None,rightBindings,expression.patterns,tripleStore)
            optTree.proxy = False
            if prolog.DEBUG:
                print "evaluating B in LeftJoin(A,B) - a BGP: ", expression
                print "Passing on bindings ",rightBindings 
            optTree.expand(expression.constraints)
        else:
            if prolog.DEBUG:
                print "Attaching previously evaluated node: ", expression.top
            assert isinstance(expression,Query.Query) and expression.top, repr(expression)            
            #Already been evaluated (non UNION), just attach the SPARQLNode
            optTree = expression.top
        if prolog.DEBUG:
            print "Optional tree: ", optTree
        proxy = None
        for proxy in _fetchBoundLeaves(optTree):
            if prolog.DEBUG:
                print "Marking proxy: ", proxy
            proxy.proxy = True
            assert len(list(_fetchBoundLeaves(optTree))) == 1,optTree
            break
        if proxy is None:
            if prolog.DEBUG:
                print "No OPT proxy"            
        node.optionalTrees.append(optTree)            
    else :
        for c in node.children :
            _ExpandLeftJoin(c,expression,tripleStore,prolog)
        
class LeftJoin(AlgebraExpression):
    """
    [[(P1 OPT P2)]](D,G) = LeftJoin1([[P1]](D,G),[[P2]](D,G))
    I.   Omega1 ⋉ Omega2          = {μ1 ∪ μ2 | μ1 ∈ Omega1, μ2 ∈ Omega2 are 
                                      compatible mappings } 
    II.  Omega1 ∪ Omega2           = {μ | μ1 ∈ Omega1 or μ2 ∈ Omega2 }
    III. Omega1 \ Omega2           = {μ1 ∈ Omega1 | for all μ′ ∈ Omega2, μ and
                                         μ′ are not compatible }
    IV.  LeftJoin1(Omega1, Omega2) = ( Omega1 ⋉ Omega2 ) ∪ ( Omega1 \ Omega2 )     
    """
    def __init__(self,BGP1,BGP2,expr=None):
        self.left  = BGP1
        self.right = BGP2

    def evaluate(self,tripleStore,initialBindings,prolog):
        if prolog.DEBUG:
            print "eval(%s,%s,%s)"%(self,initialBindings,tripleStore.graph)
        if isinstance(self.left,AlgebraExpression):
            self.left = self.left.evaluate(tripleStore,initialBindings,prolog)
        if isinstance(self.left,BasicGraphPattern):        
            retval = None
            bindings = Query._createInitialBindings(self.left)
            if initialBindings:
                bindings.update(initialBindings)
            if hasattr(self.left,'tripleStore'):
                #Use the prepared tripleStore
                tripleStore = self.left.tripleStore
            top = Query._SPARQLNode(None,bindings,self.left.patterns, tripleStore)
            top.expand(self.left.constraints)
            _ExpandLeftJoin(top,self.right,tripleStore,prolog)
            return Query.Query(top, tripleStore)
        else:
            assert isinstance(self.left,Query.Query), repr(self.left)
            _ExpandLeftJoin(self.left.top,self.right,tripleStore,prolog)
            return self.left

class Union(AlgebraExpression):
    """
    II. [[(P1 UNION P2)]](D,G) = [[P1]](D,G) OR [[P2]](D,G)
    
    Union(Ω1, Ω2) = { μ | μ in Ω1 or μ in Ω2 }
    
    """
    def __init__(self,BGP1,BGP2):
        self.left  = BGP1
        self.right = BGP2

    def evaluate(self,tripleStore,initialBindings,prolog):
        if isinstance(self.left,AlgebraExpression):
            self.left = self.left.evaluate(tripleStore,initialBindings,prolog)
        if isinstance(self.left,BasicGraphPattern):        
            #The left expression has not been evaluated
            retval = None
            bindings = Query._createInitialBindings(self.left)
            if initialBindings:
                bindings.update(initialBindings)
            top = Query._SPARQLNode(None,bindings,self.left.patterns, tripleStore)
            top.expand(self.left.constraints)
            top = Query.Query(top, tripleStore)
        else:
            #The left expression has already been evaluated 
            assert isinstance(self.left,Query.Query), repr(self.left)
            top = self.left
        #Now we evaluate the right expression (independently)
        if isinstance(self.right,GraphExpression):
            #If it is a GraphExpression, 'reduce' it
            self.right = self.right.evaluate(tripleStore,initialBindings,prolog)           
        assert isinstance(self.right,BasicGraphPattern)

        rightBindings = Query._createInitialBindings(self.right)
        rightNode = Query._SPARQLNode(None,rightBindings,self.right.patterns,tripleStore)
        rightNode.expand(self.right.constraints)
        #The UNION semantics are implemented by the overidden __add__ method                
        return top + Query.Query(rightNode, tripleStore)

class GraphExpression(AlgebraExpression):
    """
    [24] GraphGraphPattern ::=  'GRAPH'  VarOrIRIref  GroupGraphPattern
    eval(D(G), Graph(IRI,P)) = eval(D(D[i]), P)
    eval(D(G), Graph(var,P)) =
        multiset-union over IRI i in D : Join( eval(D(D[i]), P) , Omega(?v->i) )    
    """
    def __init__(self,iriOrVar,GGP):
        self.iriOrVar  = iriOrVar
        self.GGP = GGP

    def __repr__(self):
        return "Graph(%s,%s)"%(self.iriOrVar,self.GGP)

    def evaluate(self,tripleStore,initialBindings,prolog):
        """
        .. The GRAPH keyword is used to make the active graph one of all of the 
           named graphs in the dataset for part of the query ...
        """
        if prolog.DEBUG:
            print "eval(%s,%s,%s)"%(self,initialBindings,tripleStore.graph)
        if isinstance(self.iriOrVar,Variable):
            #A variable: 
            if self.iriOrVar in initialBindings:
                assert initialBindings[self.iriOrVar], "Empty binding for GRAPH variable!"
                if prolog.DEBUG:
                    print "Passing on unified graph name: ", initialBindings[self.iriOrVar]
                tripleStore = sparqlGraph.SPARQLGraph(Graph(tripleStore.store,initialBindings[self.iriOrVar]))
            else: 
                if prolog.DEBUG:
                    print "Setting up BGP to return additional bindings for %s"%self.iriOrVar
                tripleStore = sparqlGraph.SPARQLGraph(tripleStore.graph,graphVariable = self.iriOrVar)
        else:
            graphName =  self.iriOrVar
            graphName  = convertTerm(graphName,prolog)
            if isinstance(tripleStore.graph,ReadOnlyGraphAggregate):
                targetGraph = [g for g in tripleStore.graph.graphs if g.identifier == graphName]
                assert len(targetGraph) == 1
                targetGraph = targetGraph[0]
            else:
                targetGraph = Graph(tripleStore.store,graphName)
            tripleStore = sparqlGraph.SPARQLGraph(targetGraph)
        if isinstance(self.GGP,AlgebraExpression):
            #Dont evaluate
            return self.GGP.evaluate(tripleStore,initialBindings,prolog)
        else:
            assert isinstance(self.GGP,BasicGraphPattern),repr(self.GGP)
            #Attach the prepared triple store to the BGP
            self.GGP.tripleStore = tripleStore
            return self.GGP

#########################################

#         Tests                         # 

#########################################

    
TEST1="SELECT * WHERE { ?s :p1 ?v1 ; :p2 ?v2 }"
#BGP( ?s :p1 ?v1 .?s :p2 ?v2 )
TEST1_REPR=\
"BGP([(u'?s', rdflib.URIRef('p1'), u'?v1', None), (u'?s', rdflib.URIRef('p2'), u'?v2', None)])"

TEST2 = "SELECT * WHERE { { ?s :p1 ?v1 } UNION {?s :p2 ?v2 } }"
#Union( BGP(?s :p1 ?v1) , BGP(?s :p2 ?v2) )
TEST2_REPR=\
"Union(BGP([(u'?s', rdflib.URIRef('p1'), u'?v1', None)]),BGP([(u'?s', rdflib.URIRef('p2'), u'?v2', None)]))"

TEST3 = "SELECT * WHERE { ?s :p1 ?v1 OPTIONAL {?s :p2 ?v2 } }"
#LeftJoin(BGP(?s :p1 ?v1), BGP(?s :p2 ?v2), true)
TEST3_REPR=\
"LeftJoin(BGP([(u'?s', rdflib.URIRef('p1'), u'?v1', None)]),BGP([(u'?s', rdflib.URIRef('p2'), u'?v2', None)]))"

TEST4 = "SELECT * WHERE { ?s :p ?o. { ?s :p1 ?v1 } UNION {?s :p2 ?v2 } }"
#Join(BGP(?s :p ?v),Union(BGP(?s :p1 ?v1), BGP(?s :p2 ?v2)))
TEST4_REPR=\
"Join(BGP([(u'?s', rdflib.URIRef('p'), u'?o', None)]),Union(BGP([(u'?s', rdflib.URIRef('p1'), u'?v1', None)]),BGP([(u'?s', rdflib.URIRef('p2'), u'?v2', None)])))"

TEST5 = "SELECT * WHERE { OPTIONAL { ?s :p1 ?v1 } }"
#Join(BGP(?s :p ?v),Union(BGP(?s :p1 ?v1), BGP(?s :p2 ?v2)))
TEST5_REPR=\
"BGP([(u'?s', rdflib.URIRef('p1'), u'?v1', None)])"

TEST6="SELECT * WHERE { ?a :b :c OPTIONAL {:x :y :z} { :x1 :y1 :z1 } UNION { :x2 :y2 :z2 } }"
TEST6_REPR=\
"Join(LeftJoin(BGP([(u'?a', rdflib.URIRef('b'), rdflib.URIRef('c'), None)]),BGP([(rdflib.URIRef('x'), rdflib.URIRef('y'), rdflib.URIRef('z'), None)])),Union(BGP([(rdflib.URIRef('x1'), rdflib.URIRef('y1'), rdflib.URIRef('z1'), None)]),BGP([(rdflib.URIRef('x2'), rdflib.URIRef('y2'), rdflib.URIRef('z2'), None)])))"

TEST7="SELECT * WHERE { ?s :p1 ?v1 OPTIONAL { ?s :p2 ?v2. FILTER( ?v1 < 3 ) } }"
TEST7_REPR=\
"LeftJoin(BGP([(u'?s', rdflib.URIRef('p1'), u'?v1', None)]),BGP([(u'?s', rdflib.URIRef('p2'), u'?v2', None)]))"

TEST8="SELECT * WHERE { ?s :p1 ?v1. FILTER ( ?v1 < 3 ) OPTIONAL { ?s :p3 ?v3 } }"
TEST8_REPR=\
"LeftJoin(BGP([(u'?s', rdflib.URIRef('p1'), u'?v1', None)]),BGP([(u'?s', rdflib.URIRef('p3'), u'?v3', None)]))"

TEST10=\
"""
PREFIX  data:  <http://example.org/foaf/>
PREFIX  foaf:  <http://xmlns.com/foaf/0.1/>
PREFIX  rdfs:  <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?mbox ?nick ?ppd
FROM NAMED <http://example.org/foaf/aliceFoaf>
FROM NAMED <http://example.org/foaf/bobFoaf>
WHERE
{
  GRAPH data:aliceFoaf
  {
    ?alice foaf:mbox <mailto:alice@work.example> ;
           foaf:knows ?whom .
    ?whom  foaf:mbox ?mbox ;
           rdfs:seeAlso ?ppd .
    ?ppd  a foaf:PersonalProfileDocument .
  } .
  GRAPH ?ppd
  {
      ?w foaf:mbox ?mbox ;
         foaf:nick ?nick
  }
}"""


ExprTests = \
[
    (TEST1,TEST1_REPR),
    (TEST2,TEST2_REPR),
    (TEST3,TEST3_REPR),
    (TEST4,TEST4_REPR),
#    (TEST5,TEST5_REPR),
    (TEST6,TEST6_REPR),
    (TEST7,TEST7_REPR),
    (TEST8,TEST8_REPR),
    #(,),    
    #(,),
    #(,),        
]

test_graph_a = """
@prefix  foaf:     <http://xmlns.com/foaf/0.1/> .
@prefix  rdf:      <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix  rdfs:     <http://www.w3.org/2000/01/rdf-schema#> .

_:a  foaf:name     "Alice" .
_:a  foaf:mbox     <mailto:alice@work.example> .
_:a  foaf:knows    _:b .

_:b  foaf:name     "Bob" .
_:b  foaf:mbox     <mailto:bob@work.example> .
_:b  foaf:nick     "Bobby" .
_:b  rdfs:seeAlso  <http://example.org/foaf/bobFoaf> .

<http://example.org/foaf/bobFoaf>
     rdf:type      foaf:PersonalProfileDocument ."""
     
test_graph_b = """
@prefix  foaf:     <http://xmlns.com/foaf/0.1/> .
@prefix  rdf:      <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix  rdfs:     <http://www.w3.org/2000/01/rdf-schema#> .

_:z  foaf:mbox     <mailto:bob@work.example> .
_:z  rdfs:seeAlso  <http://example.org/foaf/bobFoaf> .
_:z  foaf:nick     "Robert" .

<http://example.org/foaf/bobFoaf>
     rdf:type      foaf:PersonalProfileDocument ."""     
     
scopingQuery=\
"""
PREFIX  data:  <http://example.org/foaf/>
PREFIX  foaf:  <http://xmlns.com/foaf/0.1/>
PREFIX  rdfs:  <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?ppd
FROM NAMED <http://example.org/foaf/aliceFoaf>
FROM NAMED <http://example.org/foaf/bobFoaf>
WHERE
{
  GRAPH ?ppd { ?b foaf:name "Bob" . } .
  GRAPH ?ppd { ?doc a foaf:PersonalProfileDocument . }
}"""     

class TestSPARQLAlgebra(unittest.TestCase):
    def setUp(self):
        self.store = plugin.get('IOMemory', Store)()
        self.graph1 = Graph(self.store,identifier=URIRef('http://example.org/foaf/aliceFoaf'))
        self.graph1.parse(StringIO(test_graph_a), format="n3")
        self.graph2 = Graph(self.store,identifier=URIRef('http://example.org/foaf/bobFoaf'))
        self.graph2.parse(StringIO(test_graph_b), format="n3")
        self.unionGraph = ReadOnlyGraphAggregate(graphs=[self.graph1,self.graph2],store=self.store)
        
    def testScoping(self):
        from rdflib.sparql.bison.Processor import Parse
        from rdflib.sparql.QueryResult import SPARQLQueryResult
        from rdflib.sparql.bison.Query import Prolog  
        p = Parse(scopingQuery)
        prolog = p.prolog
        if prolog is None:
            prolog = Prolog(u'',[])
            prolog.DEBUG = True
        rt = TopEvaluate(p,self.unionGraph,passedBindings = {},DEBUG=False)
        rt = SPARQLQueryResult(rt).serialize(format='python')
        self.failUnless(len(rt) == 1,"Expected 1 item solution set")
        for ppd in rt:
            self.failUnless(ppd == URIRef('http://example.org/foaf/aliceFoaf'),
                            "Unexpected ?mbox binding :\n %s" % ppd)
    def testExpressions(self):
        from rdflib.sparql.bison.Processor import Parse
        global prolog
        for inExpr,outExpr in ExprTests:
            p = Parse(inExpr)
            prolog = p.prolog
            p = p.query.whereClause.parsedGraphPattern.graphPatterns
            if prolog is None:
                from rdflib.sparql.bison.Query import Prolog  
                prolog = Prolog(u'',[])
                prolog.DEBUG = True
            self.assertEquals(repr(reduce(ReduceToAlgebra,p,None)),outExpr)

    def testSimpleGraphPattern(self):
        from rdflib.sparql.bison.Processor import Parse
        global prolog
        p = Parse("SELECT ?ptrec WHERE { GRAPH ?ptrec { ?data :foo 'bar'. } }")
        prolog = p.prolog
        p = p.query.whereClause.parsedGraphPattern.graphPatterns
        if prolog is None:
            from rdflib.sparql.bison.Query import Prolog  
            prolog = Prolog(u'',[])
            prolog.DEBUG = True
        assert isinstance(reduce(ReduceToAlgebra,p,None),GraphExpression)
        print reduce(ReduceToAlgebra,p,None)

    def testGraphEvaluation(self):
        from rdflib.sparql.bison.Processor import Parse
        p = Parse(TEST10)
        print TEST10
        rt = TopEvaluate(p,self.unionGraph,passedBindings = {})
        from rdflib.sparql.QueryResult import SPARQLQueryResult
        rt = SPARQLQueryResult(rt).serialize(format='python')
        self.failUnless(len(rt) == 1,"Expected 1 item solution set")
        for mbox,nick,ppd in rt:
            self.failUnless(mbox == URIRef('mailto:bob@work.example'),
                            "Unexpected ?mbox binding :\n %s" % mbox)
            self.failUnless(nick  == Literal("Robert"),
                            "Unexpected ?nick binding :\n %s" % nick)
            self.failUnless(ppd == URIRef('http://example.org/foaf/bobFoaf'),
                            "Unexpected ?ppd binding :\n %s" % ppd)

if __name__ == '__main__':
    unittest.main()
