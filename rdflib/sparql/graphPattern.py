#!/d/Bin/Python/python.exe
# -*- coding: utf-8 -*-
#
#
# $Date: 2005/05/19 05:33:18 $, by $Author: ivan $, $Revision: 1.2 $
#
"""
Graph pattern class used by the SPARQL implementation	
"""
import sys, os, time, datetime

from rdflib.Literal     import Literal
from rdflib.BNode       import BNode
from rdflib.URIRef      import URIRef
from types import *


def _isBnode(r) :
	if r and isinstance(r,basestring) and r[0] == "_" :
		return True
	return False

class GraphPattern :
	"""
	Storage of one Graph Pattern, ie, the pattern tuples and the possible (functional) constraints (filters)
	"""
	def __init__(self,patterns=[]) :
		"""
		@param patterns: an initial list of graph pattern tuples
		"""
		self.patterns    = []
		self.constraints = []
		self.unbounds    = []
		self.bnodes      = {}
		if type(patterns) == list :
			self.addPatterns(patterns)
		elif type(patterns) == tuple :
			self.addPattern(patterns)
		else :
			raise SPARQLError("illegal argument, pattern must be a tuple or a list of tuples")
	
	def _generatePattern(self,tupl) :
		"""
		Append a tuple to the local patterns. Possible type literals are converted to real literals on the fly.
		Each tuple should be contain either 3 elements (for an RDF Triplet pattern) or four, where the fourth
		element is a per-pattern constraint (filter). (The general constraint of SPARQL can be optimized by assigning a constraint
		to a specific pattern; because it stops the graph expansion, its usage might be much more optimal than the
		the 'global' constraint).
		
		@param tupl: either a three or four element tuple
		"""
		from sparql import _questChar, SPARQLError, _createResource, _isResQuest, Debug		
		if type(tupl) != tuple :
			raise SPARQLError("illegal argument, pattern must be a tuple, got %s" % type(tupl))
		if len(tupl) != 3 and len(tupl) != 4 :
			raise SPARQLError("illegal argument, pattern must be a tuple of 3 or 4 element, got %s" % len(tupl))
		if len(tupl) == 3 :
			(s,p,o)   = tupl
			f         = None
		else :
			(s,p,o,f) = tupl
		final=[]
		for c in (s,p,o) :
			if _isResQuest(c) :
				if not c in self.unbounds :
					self.unbounds.append(c)
				final.append(c)
			elif _isBnode(c) :
				final.append(c)
			else :
				final.append(_createResource(c))
		final.append(f)
		return tuple(final)

	def addPattern(self,tupl) :
		"""
		Append a tuple to the local patterns. Possible type literals are converted to real literals on the fly.
		Each tuple should be contain either 3 elements (for an RDF Triplet pattern) or four, where the fourth
		element is a per-pattern constraint (filter). (The general constraint of SPARQL can be optimized by assigning a constraint
		to a specific pattern; because it stops the graph expansion, its usage might be much more optimal than the
		the 'global' constraint).
		
		@param tupl: either a three or four element tuple
		"""
		self.patterns.append(self._generatePattern(tupl))

	def insertPattern(self,tupl) :
		"""
		Insert a tuple to to the start of local patterns. Possible type literals are converted to real literals on the fly.
		Each tuple should be contain either 3 elements (for an RDF Triplet pattern) or four, where the fourth
		element is a per-pattern constraint (filter). (The general constraint of SPARQL can be optimized by assigning a constraint
		to a specific pattern; because it stops the graph expansion, its usage might be much more optimal than the
		the 'global' constraint).
		
		Semantically, the behaviour induced by a graphPattern does not depend on the order of the patterns. However,
		due to the behaviour of the expansion algorithm, users may control the speed somewhat by adding patterns
		that would 'cut' the expansion tree soon (ie, patterns that reduce the available triplets significantly). API
		users may be able to do that, hence this additional method.
		
		@param tupl: either a three or four element tuple
		"""
		self.patterns.insert(0,self._generatePattern(tupl))
		
		
	def addPatterns(self,lst) :
		"""
		Append a list of tuples to the local patterns. Possible type literals are converted to real literals on the fly.
		Each tuple should be contain either three elements (for an RDF Triplet pattern) or four, where the fourth
		element is a per-pattern constraint. (The general constraint of SPARQL can be optimized by assigning a constraint
		to a specific pattern; because it stops the graph expansion, its usage might be much more optimal than the
		the 'global' constraint).
		
		@param lst: list consisting of either a three or four element tuples
		"""
		for l in lst:
			self.addPattern(l)

	def insertPatterns(self,lst) :
		"""
		Insert a list of tuples to the start of the local patterns. Possible type literals are converted to real literals on the fly.
		Each tuple should be contain either three elements (for an RDF Triplet pattern) or four, where the fourth
		element is a per-pattern constraint. (The general constraint of SPARQL can be optimized by assigning a constraint
		to a specific pattern; because it stops the graph expansion, its usage might be much more optimal than the
		the 'global' constraint).
		
		Semantically, the behaviour induced by a graphPattern does not depend on the order of the patterns. However,
		due to the behaviour of the expansion algorithm, users may control the speed somewhat by adding patterns
		that would 'cut' the expansion tree soon (ie, patterns that reduce the available triplets significantly). API
		users may be able to do that, hence this additional method.
		
		@param lst: list consisting of either a three or four element tuples
		"""
		for i in xrange(len(lst)-1,-1,-1) :
			self.insertPattern(lst[i])
			
	def addConstraint(self,func) :
		"""
		Add a global filter constraint to the graph pattern. 'func' must be a method with a single input parameter (a dictionary)
		returning a boolean. This method is I{added} to previously added methods, ie, 
		I{all} methods must return True to accept a binding.
		
		@param func: filter function
		"""
		from sparql import SPARQLError		
		if type(func) == FunctionType :
			self.constraints.append(func)
		else :
			raise SPARQLError("illegal argument, constraint must be a function type, got %s" % type(func))
			
	def addConstraints(self,lst) :
		"""
		Add a list of global filter constraints to the graph pattern. Each function in the list must be a method with a single input parameter (a dictionary)
		returning a boolean. These methods are I{added} to previously added methods, ie, 
		I{all} methods must return True to accept a binding.
		
		@param lst: list of functions
		"""
		for l in lst:
			self.addConstraint(l)
						
	def construct(self,tripleStore,bindings) :
		"""
		Add triples to a tripleStore based on a variable bindings of the patterns stored locally. 
		The triples are patterned by the current Graph Pattern. The method is used to construct a graph after a successful querying.
		
		@param tripleStore: an (rdflib) Triple Store
		@param bindings: dictionary
		"""
		from sparql import _questChar, _isResQuest, Debug	
		self.bnodes = {}
		def bind(st) :
			if _isResQuest(st) :
				if st in bindings :
					return bindings[st]
				else :
					return None
			elif _isBnode(st) :
				if not st in self.bnodes :
					self.bnodes[st] = BNode()
				return self.bnodes[st]
			else :
				return st
			
		for pattern in self.patterns :
			(s,p,o,f) = pattern
			triplet = []
			valid = True
			for res in (s,p,o) :
				val = bind(res)
				if val != None :
					triplet.append(val)
				else :
					valid = False
					break
			if valid :
				tripleStore.add(tuple(triplet))
				
	def __add__(self,other) :
		"""Adding means concatenating all the patterns and filters arrays"""
		retval = GraphPattern()
		retval += self
		retval += other
		return retval
				
	def __iadd__(self,other) :
		"""Adding means concatenating all the patterns and filters arrays"""
		self.patterns    += other.patterns
		self.constraints += other.constraints
		for c in other.unbounds :
			if not c in self.unbounds :
				self.unbounds.append(c)
		for c in other.bnodes :
			if not c in self.bnodes :
				self.bnodes[c] = other.bnodes[c]
		return self

	def __repr__(self) :
		retval  = "   Patterns:    %s\n" % self.patterns
		retval += "   Constraints: %s\n" % self.constraints
		retval += "   Unbounds:    %s\n" % self.unbounds
		return retval
		
	def __str__(self) :
		return self.__repr__()

	def isEmpty(self) :
		"""Is the pattern empty?
		@rtype: Boolean
		"""
		return len(self.patterns) == 0
			

if __name__ == '__main__' :
	g1 = GraphPattern([("a","?b",24)])
	g2 = GraphPattern([("q","?r",24333)])
	g3 = GraphPattern([("?r","?c",12345)])
	print g1 + g2
	g1 += g3
	print g1
	q = [("?y","?h",2222),("?b","?h",99999)]
	g2.insertPatterns(q)
	print g2
			
		
	
				
			
			

