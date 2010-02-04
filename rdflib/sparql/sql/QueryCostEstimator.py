# -*- coding: utf-8 -*-

from __future__ import generators

import rdflib
from rdflib.graph import ConjunctiveGraph
from rdflib import plugin
from rdflib.store import Store, NO_STORE, VALID_STORE
from rdflib.namespace import Namespace
from rdflib.term import Literal, URIRef
from types import TupleType
import time
#from rdflib.store.FOPLRelationalModel.QuadSlot import *

from DatabaseStats import *
import sys
import random
import math

# Triple Pattern Cost Estimation Methods
EST_METHOD_STOCKER = 'Stocker' # this represents Stocker as a triple pattern cost estimation (not a join ordering algorithm; i.e. independant of the join cost statistics)
EST_METHOD_HARTH = 'Harth'
EST_METHOD_SMALL = 'Small'
EST_METHOD_MEDIUM = 'Medium'
EST_METHOD_LARGE = 'Large'

class QueryTree(object):    
    def __init__(self, cost, cols, colDist):
        self.cost = float(cost)
        self.cols = cols
        self.colDist = colDist
        self.costSum = cost
        
    def Update(self, updatedCost, updatedCols, updatedColDist):     
        self.cost = float(updatedCost)        
        self.cols = updatedCols
        self.colDist = updatedColDist
        self.costSum += float(updatedCost)
        
class QuerySelection(object):
    def __init__(self, vars, exp):
        self.vars = vars
        self.exp = exp
        self.applied = False

def ColDistMax(colDist, cost):
    """ Do a sanity check to ensure there are not more distinct values than estimated tuples. """
    for v in colDist:
        if colDist[v] > cost:
            colDist[v] = math.ceil(cost)
    return colDist


class QueryCostEstimator(object):
    
    def __init__(self, sqlBuilder, stats):
        """
        Create a query cost estimator using 
        a stats object created in DatabaseStats,
        along with the name of an estimation method.
        """
        self.stats = stats
        self.sqlBuilder = sqlBuilder
        
        self.allTables = ['lit','rel','type']
        
        # get predicate list from stats
        self.predicates = []
        for t in self.allTables:
            for key in self.stats[t + '_pat']['(?,%s,?)' % (PREDICATE)]:
                actual = self.stats[t + '_pat']['(?,%s,?)' % (PREDICATE)][key]
                d = Key2Dict(key)
                if d is None:
                    continue
                self.predicates.append(d[PREDICATE])

      
    # Main triple pattern ordering functions
    
    def GreedyOrderTriples(self, triples, method, selections):
        """
        Basic greedy algorithm for relational join ordering.
        [see 'Hector Garcia-Molina, Jeffrey D. Ullman, and Jennifer Widom. Database System Implementation. Prentice Hall: Upper Saddle River, New Jersey, 2000. Chapter 7.']
        
        1. Select the pair of relations with the smallest estimated join size, use it as the first element in query tree
        2. While there are unjoined tables:
            a. Calculate the join cost estimate between the current query tree cost estimate and the remaining tables
            b. Choose the table with the smallest join cost estimate
            c. Update the current query tree cost estimate based on the current join
            
        If includeSelection=True, then we modify the algorithm above to
        take FILTERs into account in the estimates
        """
        if len(triples) < 2:
            return triples # nothing to reorder!
        
        print "    Reordering triples - Greedy(%s):"%(method)
        
        startTime = time.time()        
        
        finalOrder = []
        remaining = {}

        #HACK: see def of ViewHack for details
        triples = self.ViewHack(triples,finalOrder)
        if len(triples) < 2:
            finalOrder.extend(triples)
            return finalOrder

        for tn in range(len(triples)):
            remaining[tn] = True

        #TODO: compare starting from pair with smallest join cost with starting with relation with smallest cost
        #lowCostTn = -1
        #lowCostVal = sys.maxint
        
        # pre-calculate the costs & distinct values for all triple patterns, preprocess selections if possible
        self.SetPatternCosts(triples, method, selections)
        
            
            #TODO: compare starting from pair with smallest join cost with starting with relation with smallest cost
            #if t.cost < lowCostVal:
            #    lowCostVal = t.cost
            #    lowCostTn = tn

        #TODO: compare starting from pair with smallest join cost with starting with relation with smallest cost
        # add lowest cost as first item, use as initial tree cost & # distinct values in columns
        #finalOrder.append(triples[lowCostTn])
        #remaining.pop(lowCostTn)
        
        #treeCost = lowCostVal
        #treeColDist = triples[lowCostTn].colDist
                
        # 1. Select the pair of relations with the smallest estimated join cost
        lowCost = -1
        lowCostTn1 = -1
        lowCostTn2 = -1
        lowSelApplied = []
        lowColDist = {}
        
        for tn1 in range(len(triples)-1):
            t1 = triples[tn1]
            for tn2 in range(tn1+1,len(triples)):
                t2 = triples[tn2]
                cost = self.EstimateJoinSize(t1,t2)
                colDist = self.EstimateJoinColDist(t1, t2)
                # apply selections
                (cost,colDist,selApplied) = self.EstimateSelection(cost, colDist, selections)
                if lowCost < 0 or cost < lowCost:
                    lowCost = cost
                    lowCostTn1 = tn1
                    lowCostTn2 = tn2
                    lowSelApplied = selApplied
                    lowColDist = colDist
                                            
        # put the smaller one first
        if triples[lowCostTn1].cost > triples[lowCostTn2].cost:
            (lowCostTn1, lowCostTn2) = (lowCostTn2, lowCostTn1) #swap

        finalOrder.append(triples[lowCostTn1])
        remaining.pop(lowCostTn1)
        #print "    %s) <%s> (patCost=%s,treeCost=%s)"%(len(triples)-len(remaining),triples[lowCostTn1],triples[lowCostTn1].cost,triples[lowCostTn1].cost)
        finalOrder.append(triples[lowCostTn2])        
        remaining.pop(lowCostTn2)
        #print "    %s) <%s> (patCost=%s,treeCost=%s)"%(len(triples)-len(remaining),triples[lowCostTn2],triples[lowCostTn2].cost,lowCost)
        tree = QueryTree(lowCost, 
                         triples[lowCostTn1].cols | triples[lowCostTn2].cols,
                         lowColDist) 
                         #self.EstimateJoinColDist(triples[lowCostTn1], triples[lowCostTn2]))
        for s in lowSelApplied:
            print "        Applied selection: '%s'"%(repr(s.exp))
            s.applied = True
        
        # 2. While there are unjoined tables:
        while len(remaining) > 0:            
            # a. Calculate the join cost estimate between the current query tree cost estimate and the remaining tables
            lowCost = -1
            lowCostTn = -1
            lowColDist = {}
            lowSelApplied = []
            for tn in remaining:
                t = triples[tn]
                cost = self.EstimateJoinSize(tree, t)                
                colDist = self.EstimateJoinColDist(tree, t)
                (cost,colDist,selApplied) = self.EstimateSelection(cost, colDist, selections)                
                if lowCost < 0 or cost < lowCost:
                    lowCost = cost
                    lowCostTn = tn
                    lowColDist = colDist
                    lowSelApplied = selApplied

            
            # b. Choose the table with the smallest join cost estimate
            t = triples[lowCostTn]
            finalOrder.append(t)
            remaining.pop(lowCostTn)
            
            # c. Update the current query tree cost estimate based on the current join
            tree.Update(lowCost, 
                        tree.cols | t.cols, 
                        lowColDist)
            #print "    %s) <%s> (patCost=%s,treeCost=%s)"%(len(triples)-len(remaining),t,t.cost,lowCost)

            for s in lowSelApplied:
                print "        Applied selection: '%s'"%(repr(s.exp))
                s.applied = True


        # execution statistics
        elapsed = time.time()-startTime

        self.SaveExecutionStats(elapsed, tree.cost, tree.costSum, finalOrder)
        #print "    Final Estimated Cost: %s; Sum cost: %s"%(tree.cost, tree.costSum)

        return finalOrder
    
    def ViewHack(self,triples,finalOrder):
        """
        HACK: if the 'all partitions' view is used,
              MySQL performs _faster_ if the view is joined first!
              This should _not_ be the case, since the optimizer
              should be filtering only the rows in the view
              that meet the conditions; however it does not and
              instead always reads the tables completely!
              
              We deal with this case by forcing the view to be first.
        """
        newTriples = []
        for t in triples:
            if t.allPartitions == True:
                print "WARNING: Performing View Hack to reorder %s first."%(repr(t))
                finalOrder.append(t)
                continue
            newTriples.append(t)
        return newTriples
    
    def SaveExecutionStats(self, elapsed, cost, costSum, finalOrder):
        self.sqlBuilder.rootBuilder.joinOrdering += 1
        self.sqlBuilder.rootBuilder.joinOrderTime += elapsed
        self.sqlBuilder.rootBuilder.joinEstimatedCost += cost
        self.sqlBuilder.rootBuilder.joinEstimatedCostSum += costSum
        #self.sqlBuilder.rootBuilder.joinEstimatedTreeCost += treeCost # add tree cost as well?
        orderString = ""
        for t in finalOrder:
            orderString += str(t)
        self.sqlBuilder.joinOrders.append(orderString)
        
    def SetPatternCosts(self, triples, method, selections):
        """
        Pre-calculate triple pattern costs, columns, & # distinct values and update triple objects.
        """  
        applied = []      
        for tn in range(len(triples)):
            t = triples[tn]
            t.colDist = {}
            t.cols = set()
            
            tableType = None #TODO: get table type from triple pattern (need RdfSqlBuilder help) 
            
            if isinstance(t.sub,Variable): # & B-Node?
                t.colDist[str(t.sub)] = self.PatternDistinct(method, t.subHash, t.predHash, t.objHash, SUBJECT, tableType)
                t.cols.add(str(t.sub))
            if isinstance(t.pred,Variable): # & B-Node?
                t.colDist[str(t.pred)] = self.PatternDistinct(method, t.subHash, t.predHash, t.objHash, PREDICATE, tableType)
                t.cols.add(str(t.pred))
            if isinstance(t.obj,Variable): # & B-Node?
                t.colDist[str(t.obj)] = self.PatternDistinct(method, t.subHash, t.predHash, t.objHash, OBJECT, tableType)
                t.cols.add(str(t.obj))
            #TODO: context?
                
            t.cost = self.PatternSize(method, t.subHash, t.predHash, t.objHash, tableType)
            
            # process selection estimates
            if len(selections) > 0:
                beforeCost = t.cost
                # apply this selection to this triple pattern
                # NOTE: we may apply these kind of selections to more than one triple pattern; this is correct because SELECTION distributes across JOIN in relational algebra 
                (t.cost, t.colDist, selApplied) = self.EstimateSelection(t.cost, t.colDist, selections)            
                applied.extend(selApplied)
                for s in selApplied:
                    print "        Applied selection: '%s' to %s (sel=%s)"%(repr(s.exp), repr(t),t.cost/beforeCost)
                
        # mark selections that can be performed on a single triple pattern as already done, since it would be incorrect to apply the same condition more than once to the same relation
        for s in applied:
            if s.applied == False:
                s.applied = True

    def EstimateSelection(self, cost, colDist, selections):
        """
        Update the current estimates for (joined) relation size
        and number of distinct values in each column, based on a set of
        FILTER expression conditions. Updated estimates and the selections
        that were applied are returned. 
        """
        applied = []
        for s in selections:
            if not s.applied and s.vars.issubset(set(colDist)):
                (cost, colDist, isVar) = s.exp.AdjustCostEstimate(cost, colDist)
                applied.append(s)
        return (cost, colDist, applied)
        
    def EstimateBGPCost(self, triples, method, selections):        
        """
        Estimate the cost of evaluating a set of triple patterns (BGP) in their current order. 
        """
        if len(triples) < 1:
            print "  No triples for estimating cost."  
            return
        
        self.SetPatternCosts(triples, method, selections)        
        
        print "  Estimated BGP cost using method %s:"%(method)
        tree = QueryTree(triples[0].cost, triples[0].cols, triples[0].colDist)
        print "      %s) <%s> (patCost=%s,treeCost=%s)"%(1,triples[0],triples[0].cost,tree.cost)
        
        for n in range(1,len(triples)):
            t = triples[n]
            tree.Update(self.EstimateJoinSize(tree, t), 
                        tree.cols | t.cols,
                        self.EstimateJoinColDist(tree, t))
            print "      %s) <%s> (patCost=%s,treeCost=%s)"%(n+1,t,t.cost,tree.cost)
            
        print "    Final Estimated Cost: %s; Sum cost: %s"%(tree.cost, tree.costSum)
        return (tree.cost, tree.costSum)
        
    def EstimateJoinSize(self, rel1, rel2):
        """
        Given two relations (either triple patterns or joined from multiple triple patterns),
        estimate the number of tuples in the results.
        rel1 and rel2 should have: cost, cols, & colDist. 
        
        Cost(R x S) = Cost(R)*Cost(S)
        Cost(R |><| S) = Cost(R)*Cost(S) / (Sum_shared_col_c(max(V(R,c),V(S,c))))
        """
        cost = float(rel1.cost) * float(rel2.cost)
        sharedCols = rel1.cols & rel2.cols
        
        if len(sharedCols) > 0:
            # not a cross product -- divide by the larger of V(R,c) and V(S,c) for each
            # attribute c that is common to R and S
            for c in sharedCols:
                cost *= 1.0/max(float(rel1.colDist[c]),float(rel2.colDist[c]))        
        return cost
        
    
    def EstimateJoinColDist(self, rel1, rel2):
        """
        Given two relations (either triple patterns or joined from multiple triple patterns),
        estimate the number of distinct values in each column when the tables are (natural) joined
        rel1 and rel2 should have: cost, cols, & colDist.
        
        V(R1 |><| R2,a) = min_i=1..2(V(Ri,a)) 
        """
        allCols = rel1.cols | rel2.cols
        colDist = {}
        for c in allCols:
            colDist[c] = min(rel1.colDist.get(c, sys.maxint), rel2.colDist.get(c, sys.maxint))
        return colDist        

    
    def StockerOrderTriples(self, triples):
        """
        
        Algorithm 1: Find optimized execution plan for g in G
        N <- Nodes(g)
        E <- Edges(g)
        EP[size(N)]
        e <- SelectEdgeMinSel(E)
        EP <- OrderNodesBySel(e)
        while size(EP) <= size(N) do
            e <- SelectEdgeMinSelVisitedNode(EP, E)
            EP <- SelectNotVisitedNode(EP, e)
        end while
        return EP
        """
        if len(triples) < 2:
            return triples # nothing to reorder!
        
        startTime = time.time()

        #HACK: see def of ViewHack for details
        EP = []
        triples = self.ViewHack(triples,EP)
        if len(triples) < 2:
            EP.extend(triples)
            return EP
                        
        # convert to graph where triple patterns are nodes
        # and edges exist if there are shared variables;
        # pre-calculate edge selectivities & find min selectivity
        N = []
        N.extend(triples)
        E = {} # edge as triple n1->n2->cost
        visited = set() # indexes
        unvisited = set(range(len(N))) # indexes

        lowCost = -1
        lowCostN1 = -1
        lowCostN2 = -1
        edges = 0
        for n1 in range(len(N)-1):
            t1 = N[n1]
            for n2 in range(n1+1,len(N)):
                t2 = N[n2]
                cost = self.StockerJoinSel(t1, t2) #self.EstimateJoinSize(t1,t2)
                if cost <= 0.0:
                    continue # can't join these, no variables in common!
                edges += 1
                #print "    %s) Edge (%s,%s)=%s"%(edges,t1,t2,cost)
                # add edges in both directions
                if not E.has_key(n1):
                    E[n1] = {}
                E[n1][n2] = cost
                if not E.has_key(n2):
                    E[n2] = {}
                E[n2][n1] = cost
                if lowCost < 0 or cost < lowCost:
                    lowCost = cost
                    lowCostN1 = n1
                    lowCostN2 = n2
        #print "      Found %s edges in pattern join graph."%(edges)
        
        if lowCostN1 < 0:
            print "WARNING: Graph is entirely disconnected! Using original order."
            return triples
        
        t1 = N[lowCostN1]
        t2 = N[lowCostN2]
        if self.StockerPatternSel(t1.subHash, t1.predHash, t1.objHash) > self.StockerPatternSel(t2.subHash, t2.predHash, t2.objHash):
            # swap order so lower selectivity is first
            (lowCostN1,lowCostN2) = (lowCostN2,lowCostN1)
            (t1, t2) = (t2, t1)
        EP.append(t1)
        visited.add(lowCostN1)        
        unvisited.remove(lowCostN1)         
        EP.append(t2) 
        visited.add(lowCostN2)
        unvisited.remove(lowCostN2)         
        
        while len(EP) < len(N):
            # select edge min selectivity visited node
            lowCost = -1
            lowCostVN = -1
            lowCostN2 = -1
            for vn in visited: # for visited nodes
                remove = []
                for n2 in E[vn]:
                    if not n2 in visited: 
                        # for unvisited nodes
                        cost = E[vn][n2]
                        if lowCost < 0 or cost < lowCost:
                            lowCost = cost
                            lowCostVN = vn
                            lowCostN2 = n2
                    else:
                        # will never go from a visit to a visited node
                        remove.append(n2)
                for n2 in remove:
                    if E[vn].has_key(n2):
                        E[vn].pop(n2) # avoid checking this next time
            
            if lowCostVN < 0:
                # graph disconnected!!!
                print "WARNING: disconnected graph pattern. Processing next pattern."
                #raise Exception("TODO: modify Stocker cost algorithm to handle disconnected graphs (by breaking into different sets of triples)")

                # if only one pattern left, put it last
                if len(EP) + 1 == len(N):
                    for n in unvisited:
                        EP.append(N[n])
                    break

                # start over by selecting lost cost unvisited edge
                lowCost = -1
                lowCostN1 = -1
                lowCostN2 = -1  
                for n1 in unvisited:
                    if not E.has_key(n1):
                        continue
                    for n2 in E[n1]:
                        if n2 in visited:
                            continue
                        cost = E[n1][n2]
                        if lowCost < 0 or cost < lowCost:
                            lowCost = cost
                            lowCostN1 = n1
                            lowCostN2 = n2  
                
                if lowCostN1 < 0:
                    # if no more edges found, put remaining in original relative order     
                    for n in unvisited:
                        EP.append(N[n])
                    break  
                else:
                    # add first two edges of new (disconnected) subgraph
                    t1 = N[lowCostN1]
                    t2 = N[lowCostN2]
                    if self.StockerPatternSel(t1.subHash, t1.predHash, t1.objHash) > self.StockerPatternSel(t2.subHash, t2.predHash, t2.objHash):
                        # swap order so lower selectivity is first
                        (lowCostN1,lowCostN2) = (lowCostN2,lowCostN1)
                        (t1, t2) = (t2, t1)
                    EP.append(t1)
                    visited.add(lowCostN1)        
                    unvisited.remove(lowCostN1)         
                    EP.append(t2) 
                    visited.add(lowCostN2)
                    unvisited.remove(lowCostN2)         
                
            else:            
                # select the not visited node
                EP.append(N[lowCostN2])
                visited.add(lowCostN2)   
                unvisited.remove(lowCostN2)         
        
        elapsed = time.time()-startTime
        
        if len(EP) != len(N):
            raise Exception("BUG: not all triples ordered!")
        
        #(cost,costSum) = self.EstimateBGPCost(EP, EST_METHOD_HARTH, []) # use most accurate stats
        #self.SaveExecutionStats(elapsed, cost, costSum, EP)
        self.SaveExecutionStats(elapsed, 0, 0, EP)
        
        return EP
    
    def StockerPatternSel(self, subHash, predHash, objHash, tableType=None):
        """
        For a given triple pattern, calculate the selectivity (0...1)
        according to the formulas in Stocker et al. (WWW 2008).
        """
        # convert estimated number of rows back into selectivity (0...1)
        # by dividing by the total number of triples.
        
        return float(self.PatternSize(EST_METHOD_STOCKER, subHash, predHash, objHash, tableType))/float(self.Triples(tableType))
    
    def StockerJoinSel(self, t1, t2):
        """
        For two triple patterns, calculate the selectivity (0...1)
        according to the formulas in Stocker et al. (WWW 2008).
        
        sel(P)=(Sp/T^2) [*objectSelectionModifier], 
          where Sp=upper bound join size from summary statistics
        """
        sharedVars = t1.GetUsedVariables(self.sqlBuilder) & t2.GetUsedVariables(self.sqlBuilder)
        joinVars = sharedVars
        
        # remove variables from predicates/context
        v = t1.GetPosVariable(PREDICATE)
        if v != None and v in joinVars:
            joinVars.remove(v)
        v = t2.GetPosVariable(PREDICATE)
        if v != None and v in joinVars:
            joinVars.remove(v)
        v = t1.GetPosVariable(CONTEXT)
        if v != None and v in joinVars:
            joinVars.remove(v)
        v = t2.GetPosVariable(CONTEXT)
        if v != None and v in joinVars:
            joinVars.remove(v)
                            
        if len(joinVars) < 1:
            #print "WARNING: StockerJoinSel(%s,%s) has no shared subject/object variables! Returning -1."%(t1,t2)
            return -1
        elif len(joinVars) > 1:
            print "WARNING: StockerJoinSel(%s,%s) has more than one shared variables! Using first only."%(t1,t2)

        # figure out join type
        var = joinVars.pop()
        
        tableType1 = None #TODO: get table type from triple pattern (need RdfSqlBuilder help) 
        tableType2 = None #TODO: get table type from triple pattern (need RdfSqlBuilder help) 
        
        pos1 = None
        selectedObjModifier = 1.0
        if t1.GetPosVariable(SUBJECT) == var:
            pos1 = SUBJECT
            if t1.GetPosVariable(OBJECT) == None:
                # multiple by sel(p1,class(o1)) if O is set
                selectedObjModifier *= self.StockerPatternSel(t1.subHash, t1.predHash, t1.objHash, tableType1)
        elif t1.GetPosVariable(OBJECT) == var:
            pos1 = OBJECT
            
        pos2 = None
        if t2.GetPosVariable(SUBJECT) == var:
            pos2 = SUBJECT
            if t2.GetPosVariable(OBJECT) == None:
                # multiple by sel(p2,class(o2)) if O is set
                selectedObjModifier *= self.StockerPatternSel(t2.subHash, t2.predHash, t2.objHash, tableType2)
        elif t2.GetPosVariable(OBJECT) == var:
            pos2 = OBJECT
        
        Sp = float(self.PredJoinSize(t1.predHash, pos1, t2.predHash, pos2))
        
        tSq = float(self.Triples(tableType1)) * float(self.Triples(tableType2))    
        return (Sp/tSq)*selectedObjModifier

    
    def RandomOrderTriples(self, triples):
        """
        Generate a random ordering of the triples using Python's built-in
        shuffle function.
        """
        #print "    Reordering triples - Random:"

        startTime = time.time() 
        
        random.shuffle(triples)
        
        elapsed = time.time()-startTime

        #(cost,costSum) = self.EstimateBGPCost(triples, EST_METHOD_HARTH, []) # use most accurate stats
        #self.SaveExecutionStats(elapsed, cost, costSum, triples)
        self.SaveExecutionStats(elapsed, 0, 0, triples)
        return triples
      
    # Main interface functions for Greedy triple pattern join ordering algorithm
      
    def PatternSize(self, method, subHash, predHash, objHash, tableType=None):
        """
        Returns the exact or estimated number of 
        triples matching the triple pattern.
        
        The way this estimate is generated depends 
        on the estimation method.
        """
        
        # we have saved statistics for 100, 200, 400 & 800
        #these need to match values set via DatabaseStats
        subHistNum = 800
        predHistNum = 800
        objHistNum = 800
        
        # (?,?,?)
        if subHash == None and predHash == None and objHash == None:
            # we know exact values already
            return self.Triples(tableType)
        
        #TODO: review division formulas and prevent divide by zero!
        
        # (s,?,?)
        if subHash != None and predHash == None and objHash == None:
            if method == EST_METHOD_HARTH: 
                # actual
                return self.ActualPatternSize(subHash, predHash, objHash, tableType)
            elif method == EST_METHOD_SMALL or method == EST_METHOD_MEDIUM or method == EST_METHOD_LARGE:
                # Size(class(s),?,?)/DistinctClass(class(s))
                (size,dist) = self.ClassStats(subHash, predHash, objHash, subHistNum, -1, -1, tableType)
                if dist < 1:
                    return 0 # subject class not found
                return size/dist
            elif method == EST_METHOD_STOCKER:
                # sel(s)*T [Stocker, 2008] = T/Distinct(Subject)
                subs = self.DistinctSubjects(tableType)
                if subs < 1:
                    return 0 # empty database
                return self.Triples(tableType)/subs
            else:
                raise NotImplementedError('Method %s not supported for (%s,%s,%s).'%(method, subHash, predHash, objHash))
        
        # (?,p,?)
        if subHash == None and predHash != None and objHash == None:
            # always use actual, since it's a small # of stats and highly used!
            return self.ActualPatternSize(subHash, predHash, objHash, tableType)
        
        # (?,?,o)
        if subHash == None and predHash == None and objHash != None:
            if method == EST_METHOD_HARTH: 
                # actual
                return self.ActualPatternSize(subHash, predHash, objHash, tableType)
            elif method == EST_METHOD_SMALL or method == EST_METHOD_MEDIUM or method == EST_METHOD_LARGE:
                # Size(?,?,class(o))/DistinctClass(class(o))
                (size,dist) = self.ClassStats(subHash, predHash, objHash, -1, -1, objHistNum, tableType)
                if dist < 1:
                    return 0 # object class not found
                return size/dist
            elif method == EST_METHOD_STOCKER:
                # sel(o)*T [Stocker, 2008] = Sum_p{Size(?,p,class(o)}
                poSum = 0
                for p in self.predicates:
                    #poHistKey = '%s=%s,%s=%s'%(PREDICATE, p, OBJECT, HistClass(o,h))
                    #poSum += stats[t + '_pat']['(?,%s,%sh%s)' % (PREDICATE,OBJECT,h)][poHistKey]
                    poSum += self.ClassSize(subHash, p, objHash, -1, -1, objHistNum, tableType)
                return poSum 
            else:
                raise NotImplementedError()
        
        # (s,p,?)
        if subHash != None and predHash != None and objHash == None:
            if method == EST_METHOD_HARTH: 
                # actual
                return self.ActualPatternSize(subHash, predHash, objHash, tableType)
            elif method == EST_METHOD_SMALL or method == EST_METHOD_MEDIUM or method == EST_METHOD_LARGE:
                # min{Size(?,p,?)/DistinctSub(p),DistinctObj(p)}                               
                subForPred = self.DistinctSubForPred(predHash, tableType)
                if subForPred < 1:
                    return 0 # predicate not found!
                return min(self.PatternSize(method, None, predHash, None, tableType)/subForPred, self.DistinctObjForPred(predHash, tableType))             
            elif method == EST_METHOD_STOCKER:
                # sel(s)*sel(p)*T [Stocker, 2008] = Size(?,p,?)/Distinct(Subject)
                subs = self.DistinctSubjects(tableType)
                if subs < 1:
                    return 0 # empty database
                return self.PatternSize(method, None, predHash, None, tableType)/subs
            else:
                raise NotImplementedError()
        
        # (?,p,o)
        if subHash == None and predHash != None and objHash != None:
            if method == EST_METHOD_HARTH or method == EST_METHOD_LARGE: 
                # actual
                return self.ActualPatternSize(subHash, predHash, objHash, tableType)
            elif method == EST_METHOD_SMALL:
                # min{Size(?,p,?)/DistinctObj(p), DistinctSub(p)} 
                obsForPred = self.DistinctObjForPred(predHash, tableType)
                if obsForPred < 1:
                    return 0 # predicate not found!
                return min(self.PatternSize(method, None, predHash, None, tableType)/obsForPred, self.DistinctSubForPred(predHash, tableType))
            elif method == EST_METHOD_MEDIUM:
                # Size(?,p,class(o))/DistinctClass(p,class(o))
                (size,dist) = self.ClassStats(subHash, predHash, objHash, -1, -1, objHistNum, tableType)
                if size == 0 or dist == 0:
                    return 0 # not found!
                return size/dist        
            elif method == EST_METHOD_STOCKER:
                # sel(p)*sel(o,p)*T [Stocker, 2008] = Size(?,p,class(o))
                return self.ClassSize(subHash, predHash, objHash, -1, -1, objHistNum, tableType)
            else:
                raise NotImplementedError()
        
        # (s,?,o)
        if subHash != None and predHash == None and objHash != None:
            if method == EST_METHOD_HARTH: 
                # actual
                return self.ActualPatternSize(subHash, predHash, objHash, tableType)
            elif method == EST_METHOD_SMALL or method == EST_METHOD_MEDIUM or method == EST_METHOD_LARGE:
                # (Size(s,?,?)/T * Size(?,?,o)/T)*T [Independent]
                t = self.Triples(tableType)   
                if t < 1:
                    return 0 # empty database             
                return ((self.PatternSize(method, subHash, None, None, tableType)/t)*(self.PatternSize(method, None, None, objHash, tableType)/t))*t
            elif method == EST_METHOD_STOCKER:
                # sel(s)*sel(o)*T [Stocker, 2008] 
                #     = Sum_p{Size(?,p,class(o))}/Distinct(Subject)
                poSum = 0
                for p in self.predicates:
                    poSum += self.ClassSize(subHash, p, objHash, -1, -1, objHistNum, tableType)
                subs = self.DistinctSubjects(tableType)
                if subs < 1:
                    return 0 # empty database
                return poSum / subs
            else:
                raise NotImplementedError()
             
        # (s,p,o)
        #TODO: worth looking up in database if this exists or not?
        return 1 # assuming 1 for now; this will not be very interesting anyway, since it can't be joined with other triples...
    
    def PatternDistinct(self, method, subHash, predHash, objHash, triplePos, tableType=None):
        """
        Returns the exact or estimated number of 
        distinct values in the given triple position
        (subject, predicate, object) of the specified table.
        """
        # (?,?,?)
        if subHash == None and predHash == None and objHash == None:
            # we know exact values already
            if triplePos == SUBJECT:
                return self.DistinctSubjects(tableType)
            elif triplePos == PREDICATE:
                return self.DistinctPredicates(tableType)
            elif triplePos == OBJECT:
                return self.DistinctObjects(tableType)  
            else:
                raise NotImplementedError()
        
        # (s,?,?)
        if subHash != None and predHash == None and objHash == None:
            if triplePos == SUBJECT:
                return 1
            elif triplePos == PREDICATE:
                # min{Distinct(predicate)/Distinct(subject), Size((s,?,?))}
                subs = self.DistinctSubjects(tableType)
                if subs < 1:
                    return 0 # empty database
                return min(self.DistinctPredicates(tableType)/subs, self.PatternSize(method, subHash, predHash, objHash, tableType))
            elif triplePos == OBJECT:
                # min{Distinct(object)/Distinct(subject), Size((s,?,?))}
                subs = self.DistinctSubjects(tableType)
                if subs < 1:
                    return 0 # empty database
                return min(self.DistinctObjects(tableType)/subs, self.PatternSize(method, subHash, predHash, objHash, tableType))
            else:
                raise NotImplementedError()
        
        # (?,p,?)
        if subHash == None and predHash != None and objHash == None:
            if triplePos == SUBJECT:
                return self.DistinctSubForPred(predHash, tableType)
            elif triplePos == PREDICATE:
                return 1
            elif triplePos == OBJECT:
                return self.DistinctObjForPred(predHash, tableType)
            else:
                raise NotImplementedError()
        
        # (?,?,o)
        if subHash == None and predHash == None and objHash != None:
            if triplePos == SUBJECT:
                # min{Distinct(subject)/Distinct(object), Size((?,?,o))}
                obs = self.DistinctObjects(tableType)
                if obs < 1:
                    return 0 # empty database
                return min(self.DistinctSubjects(tableType)/obs, self.PatternSize(method, subHash, predHash, objHash, tableType))
            elif triplePos == PREDICATE:
                # min{Distinct(predicate)/Distinct(object), Size((?,?,o))}
                obs = self.DistinctObjects(tableType)
                if obs < 1:
                    return 0 # empty database
                return  min(self.DistinctPredicates(tableType)/obs, self.PatternSize(method, subHash, predHash, objHash, tableType))
            elif triplePos == OBJECT:
                return 1
            else:
                raise NotImplementedError()
        
        # (s,p,?)
        if subHash != None and predHash != None and objHash == None:
            if triplePos == SUBJECT:
                return 1
            elif triplePos == PREDICATE:
                return 1
            elif triplePos == OBJECT:
                # Size((s,p,?))*
                return self.PatternSize(method, subHash, predHash, objHash, tableType)
            else:
                raise NotImplementedError()
        
        # (?,p,o)
        if subHash == None and predHash != None and objHash != None:
            if triplePos == SUBJECT:
                # Size((?,p,o))*
                return self.PatternSize(method, subHash, predHash, objHash, tableType) 
            elif triplePos == PREDICATE:
                return 1
            elif triplePos == OBJECT:
                return 1 
            else:
                raise NotImplementedError()
        
        # (s,?,o)
        if subHash != None and predHash == None and objHash != None:
            if triplePos == SUBJECT:
                return 1 
            elif triplePos == PREDICATE:
                # Size((s,?,o))*
                return self.PatternSize(method, subHash, predHash, objHash, tableType) 
            elif triplePos == OBJECT:
                return 1 
            else:
                raise NotImplementedError()       
             
        # (s,p,o)
        #TODO: worth looking up in database if this exists or not?
        return 1 # assuming 1 for now; this will not be very interesting anyway, since it can't be joined with other triples...
    
    
    # Main interface function for Stocker 2008 triple pattern join ordering algorithm
    
    def PredJoinSize(self, predHash1, pos1, predHash2, pos2):
        """
        Estimate the join size of 2 triple patterns
        based on the predicates of the 2 patterns.  
        Triple pattern 1 has predicate pred1 and we 
        are joining column pos1; triple pattern 2 has 
        predicate pred2 and we are joining column pos2. 
        """
        if pos1 == SUBJECT:
            p1 = 's'
        elif pos1 == OBJECT:
            p1 = 'o'
        else:
            raise Exception('Bad position triple pattern predicate join estimate: ' + pos1)
        if pos2 == SUBJECT:
            p2 = 's'
        elif pos2 == OBJECT:
            p2 = 'o'
        else:
            raise Exception('Bad position triple pattern predicate join estimate: ' + pos2)
        
        if predHash1 == None or predHash2 == None:
            print "WARNING: missing predicate, estimating as T!"
            return self.stats['triples']
        
        key = (predHash1,predHash2)
        if not self.stats['join_%s-%s'%(p1,p2)].has_key(key):
            return 0
        return self.stats['join_%s-%s'%(p1,p2)][key]
    
    
    # Helper functions
    
    def MakeKey(self, subHash, predHash, objHash):
        list = []
        if (subHash != None):
            list.append('%s=%s'%(SUBJECT, subHash))
        if (predHash != None):
            list.append('%s=%s'%(PREDICATE, predHash))
        if (objHash != None):
            list.append('%s=%s'%(OBJECT, objHash))        
        return ','.join(list)
    
    def MakePatternName(self, subHash, predHash, objHash, subHistNum=-1, predHistNum=-1, objHistNum=-1):
        list = []
        if (subHash != None):
            s = "%s"%(SUBJECT)
            if subHistNum > 0:
                s += "h%s"%(subHistNum)
            list.append(s)
        else:
            list.append('?')
            
        if (predHash != None):
            s = "%s"%(PREDICATE)
            if predHistNum > 0:
                s += "h%s"%(predHistNum)
            list.append(s)
        else:
            list.append('?')
            
        if (objHash != None):
            s = "%s"%(OBJECT)
            if objHistNum > 0:
                s += "h%s"%(objHistNum)
            list.append(s)        
        else:
            list.append('?')
        return '(' + ','.join(list) + ')'
    
    def ActualPatternSize(self, subHash, predHash, objHash, tableType=None):
        key = self.MakeKey(subHash, predHash, objHash)
        patName = self.MakePatternName(subHash, predHash, objHash)
        return self.GetPattern(patName, key, tableType)
    
    def GetPattern(self, patName, key, tableType):
        tables = [tableType]
        if tableType == None:
            tables = self.allTables
        sum = 0  
        for t in tables:
            if self.stats[t + '_pat'][patName].has_key(key):
                sum += self.stats[t + '_pat'][patName][key]
        return sum            
    
    def DistinctSubjects(self, tableType=None):
        if tableType != None:
            return self.stats[tableType + '_subjects']
        return self.stats['subjects']
    
    def DistinctPredicates(self, tableType=None):
        if tableType != None:
            return self.stats[tableType + '_predicates']
        return self.stats['predicates']    
    
    def DistinctObjects(self, tableType=None):
        if tableType != None:
            return self.stats[tableType + '_objects']
        return self.stats['objects']    
    
    def Triples(self, tableType=None):
        if tableType != None:
            return self.stats[tableType + '_triples']
        return self.stats['triples']
    
    def ClassSize(self, subHash, predHash, objHash, subHistNum, predHistNum, objHistNum, tableType=None):
        if subHistNum > 0:
            subHash = HistClass(subHash, subHistNum)
        if predHistNum > 0:
            predHash = HistClass(predHash, predHistNum)
        if objHistNum > 0:
            objHash = HistClass(objHash, objHistNum)
        key = self.MakeKey(subHash, predHash, objHash)
        patName = self.MakePatternName(subHash, predHash, objHash, subHistNum, predHistNum, objHistNum)
        return self.GetPattern(patName, key, tableType)
    
    def ClassDistinct(self, subHash, predHash, objHash, subHistNum, predHistNum, objHistNum, tableType=None):
        if subHistNum > 0:
            subHash = HistClass(subHash, subHistNum)
        if predHistNum > 0:
            predHash = HistClass(predHash, predHistNum)
        if objHistNum > 0:
            objHash = HistClass(objHash, objHistNum)
        key = self.MakeKey(subHash, predHash, objHash)
        patName = self.MakePatternName(subHash, predHash, objHash, subHistNum, predHistNum, objHistNum)
        return self.GetPattern(patName, key + 'dist', tableType)
    
    def ClassStats(self, subHash, predHash, objHash, subHistNum, predHistNum, objHistNum, tableType=None):
        """
        Returns a 2-tuple of (classSize, classDistinct). 
        """
        if subHistNum > 0:
            subHash = HistClass(subHash, subHistNum)
        if predHistNum > 0:
            predHash = HistClass(predHash, predHistNum)
        if objHistNum > 0:
            objHash = HistClass(objHash, objHistNum)
        key = self.MakeKey(subHash, predHash, objHash)
        patName = self.MakePatternName(subHash, predHash, objHash, subHistNum, predHistNum, objHistNum)
        return (self.GetPattern(patName, key, tableType), self.GetPattern(patName, key + 'dist', tableType))
    
    def DistinctSubForPred(self, predHash, tableType=None):
        #TODO: this may not be accurate for 'all' table if a predicate is used in more than one partition table
        if tableType != None:
            if not self.stats[tableType + '_colDist']['sub_for_pred'].has_key(predHash):
                return 0 # not found
            return self.stats[tableType + '_colDist']['sub_for_pred'][predHash]
        
        # since predicate is usually not repeated between partitions, simply sum them
        sum = 0        
        for t in self.allTables:
            if self.stats[t + '_colDist']['sub_for_pred'].has_key(predHash):
                sum += self.stats[t + '_colDist']['sub_for_pred'][predHash]
        return sum
    
    def DistinctObjForPred(self, predHash, tableType=None):
        if tableType != None:
            if not self.stats[tableType + '_colDist']['obj_for_pred'].has_key(predHash):
                return 0 # not found
            return self.stats[tableType + '_colDist']['obj_for_pred'][predHash]
        
        # literals and relations have no overlap; we don't expect relations and types to overlap
        sum = 0        
        for t in self.allTables:
            if self.stats[t + '_colDist']['obj_for_pred'].has_key(predHash):
                sum += self.stats[t + '_colDist']['obj_for_pred'][predHash]
        return sum
    
    
