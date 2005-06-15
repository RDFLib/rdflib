#!/d/Bin/Python/python.exe
"""SPARQL implementation on top of RDFLib
Implementation of the <a href="http://www.w3.org/TR/rdf-sparql-query/">W3C SPARQL</a> language (version April 2005).
The basic class here is supposed to be a superclass of L{rdflibUtils.myTripleStore}; it has been separated only for a better
maintainability. 

There is a separate U{description<http://dev.w3.org/cvsweb/%7Echeckout%7E/2004/PythonLib-IH/Doc/sparqlDesc.html>}
for the functionalities.

"""

##########################################################################
from rdflib.Identifier  import Identifier
from rdflib.Literal     import Literal
from rdflib.BNode       import BNode
from rdflib.URIRef      import URIRef
from rdflib.exceptions  import Error
from rdflib.util       import check_predicate, check_subject, check_object

from graphPattern import GraphPattern

################
# This was used in a previous, work version of the implementation, but it may be unnecessary. I keep it for now, because
# the operators are also prepared to this. If it proves to be really unnecessary, I can always throw it away, it does
# not really influence efficiency or anything else.
JunkResource = URIRef("http://www.ivan-herman.net/SPARQLJunk")

import sys, sets, datetime
from types import *

Debug = False


##########################################################################
# XML Schema datatypes
type_string   = "http://www.w3.org/2001/XMLSchema#string"
type_integer  = "http://www.w3.org/2001/XMLSchema#integer"
type_long     = "http://www.w3.org/2001/XMLSchema#long"
type_double   = "http://www.w3.org/2001/XMLSchema#double"
type_float    = "http://www.w3.org/2001/XMLSchema#float"
type_decimal  = "http://www.w3.org/2001/XMLSchema#decimal"
type_dateTime = "http://www.w3.org/2001/XMLSchema#dateTime"
type_date     = "http://www.w3.org/2001/XMLSchema#date"
type_time     = "http://www.w3.org/2001/XMLSchema#time"

# Mapping from the Python types to the corresponding XML Schema types. Note that, for internal purposes, strings 
# are just used in a plain format, not with the XML Schema version (the XML Schema string is a default for 
# an RDF datatype, hence this here)
_basicTypes = {
    IntType     : type_integer,
    FloatType   : type_float,
    StringType  : "",
    UnicodeType : "",
    LongType    : type_long
}

# Some extra types that are not based on the basic Pythong types but on existing library classes.
_extraTypes = {
    datetime.datetime  : type_dateTime,
    datetime.date      : type_date,
    datetime.time      : type_time,
}

##########################################################################
# Utilities

# Note that the SPARQL draft allows the usage of a different query character, but I decided not to be that
# generous, and keep to one only. I put it into a separate variable to avoid problems if the group decides
# to change the syntax on that detail...
_questChar  = "?"

# Key (in the final bindings) for the background graph for the specific query
_graphKey = "$$GRAPH$$"

##
# SPARQL Error Exception (subclass of the RDFLib Exceptions)
class SPARQLError(Error) :
    """Am SPARQL error has been detected"""
    def __init__(self,msg):
        Error.__init__(self, ("SPARQL Error: %s." % msg))

		
def _schemaType(v) :
	"""Return an XML Schema type starting from a Python variable. An exception is raised if the variable
	does not corresponds to any of the schema types that are allowed by this implementation. A
	SPARQLError Exception is raised if the type represents a non-implemented type.
	
	@param v: Python variable
	@return: URI for the XML Datatype
	@rtype: string
	@raise SPARQLError: if the type of 'v' is not implemented
	"""
	# First the basic Types
	for t in _basicTypes :
		if type(v) is t :
			return _basicTypes[t]
	# Then the extra types
	for t in _extraTypes :
		if isinstance(v,t) :
			return _extraTypes[t]
	# if we got here, the type is illegal...
	raise SPARQLError("%s is not an accepted datatype" % v)

def _createResource(v) :
	"""Create an RDFLib Literal instance with the corresponding XML Schema datatype set. If the variable
	is already an RDFLib resource, it simply returns the resource; otherwise the corresponding Literal.
	A SPARQLError Exception is raised if the type is not implemented.
	
	The Literal contains the string representation of the variable (as Python does it by default) with the
	corresponding XML Schema URI set.
	
	@param v: Python variable
	@return: either an RDFLib Literal (if 'v' is not an RDFLib Resource), or the same variable if it is already
	an RDFLib resource (ie, Literal, BNode, or URIRef)
	@raise SPARQLError: if the type of 'v' is not implemented	
	"""
	if isinstance(v,Literal) or isinstance(v,BNode) or isinstance(v,URIRef) :
		# just do nothing
		return v
	else :
		xmlDatatype = _schemaType(v)
		# note: if there was an error with the type, an exception has been raised at this point
		# unfortunately, some of the default python data->string conversions are not the same
		# as required by the XML Schema datatype document :-(
		# Otherwise, relies on the fact that the init of Literal uses, essentially, the `` operator of
		# python to store the value.
		if xmlDatatype == type_dateTime :
			# XML Schema requires a "T" separator, and this is not the default for the conversion...
			return Literal(v.isoformat(sep="T"),datatype=xmlDatatype)
		else :
			return Literal(v,datatype=xmlDatatype)

def _isResQuest(r) :
	"""
	Is 'r' a request string (ie, of the form "?XXX")?
	
	@rtype: Boolean
	"""
	if r and isinstance(r,basestring) and r[0] == _questChar :
		return True
	return False

	
def _checkOptionals(pattern,optionals) :
	"""
	The following remark in the SPARQL document is important:
		
	"If a new variable is mentioned in an optional block (as mbox and hpage are mentioned 
	in the previous example), that variable can be mentioned in that block and can not be 
	mentioned in a subsequent block."
	
	What this means is that the various optional blocks do not interefere at this level
	and there is no need for a check whether a binding in a subsequent block
	clashes with an earlier optional block.
	
	This method checks whether this requirement is fulfilled. Raises a SPARQLError exception
	if it is not (the rest of the algorithm relies on this, so checking it is a good idea...)
	
	@param pattern: graph pattern
	@type pattern: L{GraphPattern<rdflibUtils.GraphPattern>}
	@param optionals: graph pattern
	@type optionals: L{GraphPattern<rdflibUtils.GraphPattern>}
	@raise SPARQLError: if the requirement is not fulfilled
	"""
	for i in xrange(0,len(optionals)) :
		for c in optionals[i].unbounds :
			if c in pattern.unbounds :
				# this is fine, an optional query variable can appear in the main pattern, too
				continue
			if i > 0 :
				for j in xrange(0,i) :
					if c in optionals[j].unbounds :
						# This means that:
						#   - the variable is not in the main pattern (because the previous if would have taken care of it)
						#   - the variable is in the previous optional: ie, Error!
						raise SPARQLError("%s is an illegal query string, it appear in a previous OPTIONAL clause" % c)
	
def _createInitialBindings(pattern) :
	"""Creates an initial binding directory for the Graph Pattern by putting a None as a value for each
	query variable.
	
	@param pattern: graph pattern
	@type pattern: L{GraphPattern<rdflibUtils.GraphPattern>}
	"""
	bindings = {}
	for c in pattern.unbounds :
		bindings[c] = None
	return bindings
	
def _processResults(select,arr) :
	'''
	The result in an expansion node is in the form of an array of binding dictionaries.
	The caller should receive an array of tuples, each tuple representing the final binding (or
	None) I{in the order of the original select}. This method is the last step of processing by 
	processing these values to produce the right result.
	
	
	@param select: the original selection list. If None, then the binding should be taken as a whole (this corresponds to the
	SELECT * feature of SPARQL)
	@param arr: the array of bindings
	@type arr: an array of dictionaries
	@return: a list of tuples with the selection results
	'''
	retval = []
	if select :
		for bind in arr :
			# each result binding must be taken separately
			qresult = []
			for s in select :
				if s in bind :
					qresult.append(bind[s])
				else :
					qresult.append(None)
			# as a courtesy to the user, if the selection has one single element only, than we do no
			# put in a tuple, just add it that way:
			if len(select) == 1 :
				retval.append(qresult[0])
			else :
				retval.append(tuple(qresult))
	else :
		# this is the case corresponding to a SELECT * query call
		for bind in arr:
			qresult = bind.values()
			if len(qresult) == 1 :
				retval.append(qresult[0])
			else :
				retval.append(tuple(qresult))
	return retval


	
##########################################################################
# This utility is necessary to maintain the deprecated interfaces. When those disappear,
# this utility can be deleted, too
def _unfoldNestedLists(args) :
	"""To unfold nested lists of the sort = [t,[t1,t2],tt,ttt] into
	[t,t1,tt,ttt] and [t,t2,tt,ttt]. Returns the list of lists. 
	
	This utility is necessary to maintain the deprecated interfaces. When those disappear,
	this utility can be deleted, too
	
	@param args: list
	@return: unfolded list of lists
	"""	
	allBranches = [[]]
	for arg in args :
		if type(arg) is tuple :
			for x in allBranches :
				x.append(arg)
		elif type(arg) is list :
			# All lists in allBranches must be copied as many times as there are tuples in 
			# arg, and the elements of arg must be appended to them
			newAllBranches = []
			for x in allBranches :
				for z in arg:
					xz = [ q for q in x ]
					if type(z) is tuple :
						xz.append(z)
					elif type(z) is list :
						xz = xz + z
					newAllBranches.append(xz)
			allBranches = newAllBranches
	return allBranches

##########################################################################

class SPARQL :
	"""
	A wrapper class around the RDFLib triple store implementing the Sparql utilities. This class is
	a superclass of the L{myTripleStore<myTripleStore.myTripleStore>}
	class; in other words, the methods are usualy 'seen' through an instance of that class rather than directly.
	"""
	##########################################################################################################
	# Deprecated methods. Should be deleted in a next release...
	
	def sparqlQuery(self,selectU,where,constraints=[],optional=[]) :
		"""
		A shorthand for the creation of a L{Query} instance and returning
		the result of a selection right away. Good for most of the usage,
		when no more action (clustering, etc) is necessary.
		
		B{This method is deprecated and may disappear from future releases.} Use the L{query} method.
		
		@param selectU: a tuple with the selection criteria. Each entry is a string that begins with a "?". If not, it is ignored.
		If the selection is only one single string, then the parameter can also be a single string instead
		of a tuple.
		
		@param where: an array of statement tuples. The tuples are either three or four elements long. 
		Each of the first three entries in the tuples is either a string or an RDFLib Identifier (ie, a Literal
		or a URIRef). If a string and if the string begins by "?", it is an unbound variable, otherwise a Literal
		is created on the fly. The optional fourth entry in the tuple is a function reference, ie, a per-pattern
		condition. The method is invoked with the bound versions of the tuple variables; if it returns False,
		the query is stopped for those bindings. An additional tweak: an element in 'where' may be a list of tuples, instead of a tuple. This is
		interpreted as an 'or', ie, several queries will be issued by replacing the list with its elements
		respectively, and the resulting bindings will be concatenated.
		
		@param constraints: a list of functions. All functions will be invoked with a full binding if found. The input is a dictionary for
		the binding, the return value should be true or false.
		The conditions are 'and'-d, ie, if one returns false, that particular binding is rejected.
		
		@param optional: like the 'where' array. The subgraph is optional: ie, if no triple are found for these
		subgraph, the search goes on (and the corresponding select entry is set to None)
		
		@return: list of query results
		@depreciated: this was an earlier implementation version and is kept for backward compatibility only
		"""
		obj = self._sparqlObject(selectU,where,constraints=constraints,optional=optional)
		return obj.select(selectU)
	
	def _sparqlObject(self,select,where,constraints=[],optional=[]) :
		"""
		Creation of a L{Query} instance.
		
		@param select: a tuple with the selection criteria. Each entry is a string that begins with a "?". If not, it is ignored.
		If the selection is only one single string, then the parameter can also be a single string instead
		of a tuple.
		
		@param where: an array of statement tuples. The tuples are either three or four elements long. 
		Each of the first three entries in the tuples is either a string or an RDFLib Identifier (ie, a Literal
		or a URIRef). If a string and if the string begins by "?", it is an unbound variable, otherwise a Literal
		is created on the fly. The optional fourth entry in the tuple is a function reference, ie, a per-pattern
		condition. The method is invoked with the bound versions of the tuple variables; if it returns False,
		the query is stopped for those bindings. An additional tweak: an element in 'where' may be a list of tuples, instead of a tuple. This is
		interpreted as an 'or', ie, several queries will be issued by replacing the list with its elements
		respectively, and the resulting bindings will be concatenated.
		
		@param constraints: a list of functions. All functions will be invoked with a full binding if found. The input is a dictionary for
		the binding, the return value should be true or false.
		The conditions are 'and'-d, ie, if one returns false, that particular binding is rejected.
		
		@param optional: like the 'where' array. The subgraph is optional: ie, if no triple are found for these
		subgraph, the search goes on (and the corresponding select entry is set to None)
		
		@return: a L{Query} instance
		@depreciated: this is used by L{sparqlQuery} only and may disappear in later releases.
		"""
		if type(select) == str :
			selectA = (select,)
		elif type(select) == list or type(select) == tuple :
			selectA = select
		else :
			raise SPARQLError("'select' argument must be a string, a list or a tuple")
		if type(where) == tuple :
			whereA = [where]
		elif type(where) == list :
			whereA = where
		else :
			raise SPARQLError("'where' argument must be a list or a tuple")

		if type(constraints) == FunctionType :
			constraintsA = (constraints,)
		elif type(constraints) == list or type(constraints) == tuple :
			constraintsA = constraints
		else :
			raise SPARQLError("'constraints' argument must be a function, a list or a tuple")
			
		if optional :
			if type(optional) == tuple :
				optionalA = [optional]
			elif type(optional) == list :
				optionalA = optional
			else :
				raise SPARQLError("'optional' argument must be a list or a tuple" % t)
		else :
			optionalA = []
			
		allWhere    = _unfoldNestedLists(whereA)
		allOptional = _unfoldNestedLists(optionalA)
		basicPatterns = []
		optPatterns   = []
		for w in allWhere :
			pattern = GraphPattern(w)
			pattern.addConstraints(constraintsA)
			basicPatterns.append(pattern)
		for o in allOptional :
			optPatterns.append(GraphPattern(o))
		r = self.queryObject(basicPatterns,optPatterns)
		return r
			
	
	###############################################################################################
	def __init__(self) :
		pass		
		
	def query(self,selection,patterns,optionalPatterns=[]) :
		"""
		A shorthand for the creation of a L{Query} instance, returning
		the result of a L{Query.select} right away. Good for most of the usage,
		when no more action (clustering, etc) is required.
		
		@param selection: a list or tuple with the selection criteria, or a single string. Each entry is a string that begins with a "?". 

		@param patterns: either a L{GraphPattern<rdflibUtils.graphPattern.GraphPattern>} instance or a 
		list of instances thereof. Each pattern in the list represent an 'OR' (or 'UNION') branch in SPARQL.
		
		@param optionalPatterns: either a L{GraphPattern<rdflibUtils.graphPattern.GraphPattern>} instance or a 
		list of instances thereof. For each elements in the 'patterns' parameter is combined with each of the optional patterns and
		the results are concatenated. The list may be empty.
		
		@return: list of query results
		@rtype: list of tuples
		"""
		result = self.queryObject(patterns,optionalPatterns)
		if result == None :
			# generate some proper output for the exception :-)
			msg = "Errors in the patterns, no valid query object generated; "
			if isinstance(patterns,GraphPattern) :
				msg += ("pattern:\n%s" % patterns)
			else :
				msg += ("pattern:\n%s\netc..." % patterns[0])
			raise SPARQLError(msg)
		return result.select(selection)
		
	def queryObject(self,patterns,optionalPatterns=[]) :
		"""
		Creation of a L{Query} instance.
		
		@param patterns: either a L{GraphPattern<rdflibUtils.graphPattern.GraphPattern>} instance or a 
		list of instances thereof. Each pattern in the list represent an 'OR' (or 'UNION') branch in SPARQL.
		
		@param optionalPatterns: either a L{GraphPattern<rdflibUtils.graphPattern.GraphPattern>} instance or a 
		list of instances thereof. For each elements in the 'patterns' parameter is combined with each of the optional patterns and
		the results are concatenated. The list may be empty.
		
		@return: Query object
		@rtype: L{Query}
		"""
		def checkArg(arg,error) :
			if arg == None :
				return []
			elif isinstance(arg,GraphPattern) :
				return [arg]
			elif type(arg) == list or type(arg) == tuple :
				for p in arg :
					if not isinstance(p,GraphPattern) :
						raise SPARQLError("'%s' argument must be a GraphPattern or a list of those" % error)
				return arg
			else :
				raise SPARQLError("'%s' argument must be a GraphPattern or a list of those" % error)

		finalPatterns         = checkArg(patterns,"patterns")
		finalOptionalPatterns = checkArg(optionalPatterns,"optionalPatterns")	

		retval = None
		for pattern in finalPatterns :
			# Check whether the query strings in the optional clauses are fine. If a problem occurs,
			# an exception is raised by the function
			_checkOptionals(pattern,finalOptionalPatterns)			
			bindings = _createInitialBindings(pattern)
			# This is the crucial point: the creation of the expansion tree and the expansion. That
			# is where the real meal is, we had only an apetizer until now :-)
			top = _SPARQLNode(None,bindings,pattern.patterns,self)
			top.expand(pattern.constraints)
			for opt in finalOptionalPatterns :
				bindings = _createInitialBindings(opt)
				top.expandOptions(bindings,opt.patterns,opt.constraints)
			r = Query(top,self)
			if retval == None :
				retval = r
			else :
				# This branch is, effectively, the UNION clause of the draft
				retval = retval + r
		return retval
			
############################################################################################
class Query :
	"""
	Result of a SPARQL query. It stores to the top of the query tree, and allows some subsequent
	inquiries on the expanded tree. B{This class should not be
	instantiated by the user,} it is done by the L{queryObject<SPARQL.queryObject>} method.
	
	"""
	def __init__(self,sparqlnode,triples,parent1=None,parent2=None) :
		"""
		@param sparqlnode: top of the expansion tree
		@type sparqlnode: _SPARQLNode
		@param triples: triple store
		@type triples: L{myTripleStore<rdflibUtils.myTripleStore>}
		@param parent1: possible parent Query when queries are combined by summing them up
		@type parent1: L{Query}
		@param parent2: possible parent Query when queries are combined by summing them up
		@type parent2: L{Query}
		"""
		self.top             = sparqlnode
		self.triples         = triples
		# if this node is the result of a sum...
		self.parent1         = parent1
		self.parent2         = parent2
		
	def __add__(self,other) :
		"""This may be useful when several queries are performed and one wants the 'union' of those.
		Caveat: the triple store must be the same for each argument. This method is used internally 
		only anyway...
		Efficiency trick (I hope it works): the various additions on subgraphs are not done here; 
		the results are calculated only if really necessary, ie, in a lazy evaluation manner.
		This is achieved by storing self and the 'other' in the new object
		"""
		return Query(None,self.triples,self,other)
		
	def select(self,selection,distinct=True,limit=None) :
		"""
		Run a selection on the query.
		
		@param selection: Either a single query string, or an array or tuple thereof.
		@param distinct: if True, identical results are filtered out
		@type distinct: Boolean
		@param limit: if set to an integer value, the first 'limit' number of results are returned; all of them otherwise
		@type limit: non negative integer
		@return: selection results
		@rtype: list of tuples
		@raise SPARQLError: invalid selection argument
		"""
		def _uniquefyList(lst) :
			"""Return a copy of the list but possible duplicate elements are taken out. Used to
			post-process the outcome of the query
			@param lst: input list
			@return: result list
			"""
			if len(lst) <= 1 :
				return lst
			else :
				return list(sets.Set(lst))
		# Select may be a single query string, or an array/tuple thereof
		if isinstance(selection,basestring) :
			if selection == "*" :
				selectionF = None
			else :
				selectionF = (selection,)
		elif type(selection) == list or type(selection) == tuple :
			selectionF = selection
		else :
			raise SPARQLError("'selection' argument must be a string, a list, or a tuple")

		if self.parent1 != None and self.parent2 != None :
			results = self.parent1.select(selectionF) + self.parent2.select(selectionF)
		else :
			# remember: _processResult turns the expansion results (an array of dictionaries)
			# into an array of tuples in the right, original order
			results = _processResults(selectionF,self.top.returnResult(selectionF))
		if distinct :
			retval = _uniquefyList(results)
		else :
			retval = results
		if limit != None and limit < len(retval) :
			return retval[0:limit]
		else :
			return retval
			
	def construct(self,pattern=None) :
		"""
		Expand the subgraph based on the pattern or, if None, the internal bindings.
		
		In the former case the binding is used to instantiate the triplets in the patterns; in the latter,
		the original statements are used as patterns.
		
		The result is a separate triple store containing the subgraph.
		
		@param pattern: a L{GraphPattern<rdflibUtils.graphPattern.GraphPattern>} instance or None
		@return: a new triple store
		@rtype: L{myTripleStore<rdflibUtils.myTripleStore>}
		"""
                from sparqlGraph import SPARQLGraph

		if self.parent1 != None and self.parent2 != None :
			return self.parent1.construct(pattern) + self.parent2.construct(pattern)
		else :
			subgraph = SPARQLGraph()
			self.top.expandSubgraph(subgraph,pattern)
			return subgraph
		
	def ask(self) :
		"""
		Whether a specific pattern has a solution or not.
		@rtype: Boolean
		"""
		return len(self.select('*')) != 0
	
	#########################################################################################################
	# The methods below are not really part of SPARQL, or may be used to a form of DESCRIBE. However, that latter
	# is still in a flux in the draft, so we leave it here, pending
	
	def clusterForward(self,selection) :
		"""
		Forward clustering, using all the results of the query as seeds (when appropriate). It is
		based on the usage of the 
		L{cluster forward<rdflibUtils.myTripleStore.clusterForward>}
		method for triple store.
		
		@param selection: a selection to define the seeds for clustering via the selection; the result of select
		used for the clustering seed
		@return: a new triple store	
		@rtype: L{myTripleStore<rdflibUtils.myTripleStore>}
		"""
                from sparqlGraph import SPARQLGraph

		if self.parent1 != None and self.parent2 != None :
			return self.parent1.clusterForward(selection) + self.parent2.clusterForward(selection)
		else :
			clusterF = SPARQLGraph()
			for r in reduce(lambda x,y: list(x) + list(y),self.select(selection),()) :
				try :
					check_subject(r)
					self.triples.clusterForward(r,clusterF)
				except :
					# no real problem, this is a literal, just forget about it
					continue					
			return clusterF
		
	def clusterBackward(self,selection) :
		"""
		Backward clustering, using all the results of the query as seeds (when appropriate). It is
		based on the usage of the 
		L{cluster backward<rdflibUtils.myTripleStore.clusterBackward>}
		method for triple store.
		
		@param selection: a selection to define the seeds for clustering via the selection; the result of select
		used for the clustering seed
		@return: a new triple store	
		@rtype: L{myTripleStore<rdflibUtils.myTripleStore>}
		"""
                from sparqlGraph import SPARQLGraph

		if self.parent1 != None and self.parent2 != None :
			return self.parent1.clusterBackward(selection) + self.parent2.clusterBackward(selection)
		else :
			clusterB = SPARQLGraph()
			# to be on the safe side, see if the query has been properly finished
			for r in reduce(lambda x,y: list(x) + list(y),self.select(selection),()) :
				self.triples.clusterBackward(r,clusterB)
			return clusterB

	def cluster(self,selection) :
		"""
		Cluster: a combination of L{Query.clusterBackward} and 
		L{Query.clusterForward}.
		@param selection: a selection to define the seeds for clustering via the selection; the result of select
		used for the clustering seed
		"""
		return self.clusterBackward(selection) + self.clusterForward(selection)
		
	def describe(self,selection,forward=True,backward=True) :
		"""
		The DESCRIBE Form in the SPARQL draft is still in state of flux, so this is just a temporary method, in fact.
		It may not correspond to what the final version of describe will be (if it stays in the draft at all, that is).
		At present, it is simply a wrapper around L{cluster}.
		
		@param selection: a selection to define the seeds for clustering via the selection; the result of select
		used for the clustering seed
		@param forward: cluster forward yes or no
		@type forward: Boolean
		@param backward: cluster backward yes or no
		@type backward: Boolean
		"""
                from sparqlGraph import SPARQLGraph

		if forward and backward :
			return self.cluster(selection)
		elif forward :
			return self.clusterForward(selection)
		elif backward :
			return self.clusterBackward(selection)
		else :
			return SPARQLGraph()

class _SPARQLNode:
	"""
	The SPARQL implementation is based on the creation of a tree, each level for each statement in the
	'where' clause of SPARQL. 
	
	Each node maintains a 'binding' dictionary, with the variable names and either a None if not yet
	bound, or the binding itself. The method 'expand' tries to make one more step of binding by looking at the next
	statement: it takes the statement of the current node, binds the variables if there is already a binding, and
	looks at the triple store for the possibilities. If it finds valid new triplets, that will bind some more variables,
	and children will be created with the next statement in the 'where' array with a new level of bindings. This is done
	for each triplet found in the store, thereby branching off the tree. If all variables are already bound but the
	statement, with the bound variables, is not 'true' (ie, there is no such triple in the store), the node is marked
	as 'clash' and no more expansion is made; this node will then be thrown away by the parent. If I{all} children of a
	node is a clash, then it is marked as a clash itself.
	
	At the end of the process, the leaves of the tree are searched; if a leaf is such that:
		
	  - all variables are bound
	  - there is no clash
	  
	then the bindings are returned as possible answers to the query.
	
	The optional clauses are treated separately: each 'valid' leaf is assigned an array of expansion trees that
	contain the optional clauses (that may have some unbound variables bound at the leaf, though).
	
	@ivar parent: parent in the tree
	@type parent: _SPARQLNode
	@ivar children: the children (in an array)
	@type children: array of _SPARQLNode
	@ivar bindings:  copy of the bindings locally
	@type bindings: dictionary
	@ivar statement:  the current statement
	@type statement: a (s,p,o,f) tuple ('f' is the local filter or None)
	@ivar rest:  the rest of the statements (an array)
	@ivar clash: intialized to False
	@type clash: Boolean
	@ivar bound:  True or False depending on whether all variables are bound in self.binding
	@type bound: Boolean
	@ivar optionalTrees: expansion trees for optional statements
	@type optionalTrees: array of _SPARQLNode instances
	"""
	def __init__(self,parent,bindings,statements,tripleStore) :
		""" 
		@param parent:     parent node
		@param bindings:   a dictionary with the bindings that are already done or with None value if no binding yet
		@param statements: array of statements from the 'where' clause. The first element is
		for the current node, the rest for the children. If empty, then no
		expansion occurs (ie, the node is a leaf)
		@param tripleStore: the 'owner' triple store
		@type tripleStore: L{myTripleStore<rdflibUtils.myTripleStore.myTripleStore>}
		"""
		self.tripleStore         = tripleStore
		self.bindings            = bindings
		self.bindings[_graphKey] = tripleStore
		self.optionalTrees       = []		
		if None in bindings.values() :
			self.bound = False
		else :
			self.bound = True			
		self.clash     = False
		
		self.parent    = parent
		self.children  = []
		
		if len(statements) > 0 :
			self.statement = statements[0]
			self.rest      = statements[1:]
		else :
			self.statement = None
			self.rest      = None

	def returnResult(self,select) :
		"""
		Collect the result by search the leaves of the the tree. The variables in the select are exchanged against
		their bound equivalent (if applicable). This action is done on the valid leaf nodes only, the intermediate
		nodes only gather the children's results and combine it in one array.
		
		@param select: the array of unbound variables in the original select that do not appear in any of the optionals. If
		None, the full binding should be considered (this is the case for the SELECT * feature of SPARQL)
		@returns: an array of dictionaries with non-None bindings.
		"""
		if len(self.children) > 0 :
			# combine all the results of all the kids into one array
			retval = []
			for c in self.children :
				res = c.returnResult(select)
				# res is a list of dictionaries, so each tuple should be taken out and added to the result
				for t in res :
					retval.append(t)
			return retval
		else :
			retval = []
			if self.bound == True and self.clash == False :
				# This node should be able to contribute to the final results:
				result = {}
				# This where the essential happens: the binding values are used to construct the selection result
				if select :
					for a in select :
						if a in self.bindings :
							result[a] = self.bindings[a]
				else :
					result = self.bindings.copy()
				# Initial return block. If there is no optional processing, that is the result, in fact,
				# because the for cycle below will not happen
				retval = [result]
				# The following remark in the SPARQL document is important at this point:
				# "If a new variable is mentioned in an optional block (as mbox and hpage are mentioned 
				#  in the previous example), that variable can be mentioned in that block and can not be 
				#  mentioned in a subsequent block."
				# What this means is that the various optional blocks do not interefere at this point
				# and there is no need for a check whether a binding in a subsequent block
				# clashes with an earlier optional block.
				# The API checks this at the start.
				# What happens here is that the result of the optional expantion is added to what is already
				# there. Note that this may lead to a duplication of the result so far, if there are several
				# alternatives returned by the optionals!
				for optTree in self.optionalTrees :
					# get the results from the optional Tree...
					optionals = optTree.returnResult(select)
					# ... and extend the results accumulated so far with the new bindings
					# It is worth separating the case when there is only one optional block; it avoids
					# unnecessary copying
					if len(optionals) == 0 :
						# no contribution at all :-(
						continue
					elif len(optionals) == 1 :
						optResult = optionals[0]
						for res in retval :
							for k in optResult :
								if optResult[k] != None :
									res[k] = optResult[k]								
					else :
						newRetval = []
						for optResult in optionals :
							# Each binding dictionary we have so far should be copied with the new values
							for res in retval :
								dct = {}
								# copy the content of the exisiting bindings ...
								dct = res.copy()
								# ... and extend it with the optional results
								for k in optResult :
									if optResult[k] != None :
										dct[k] = optResult[k]
								newRetval.append(dct)
						retval = newRetval
			return retval


	def expandSubgraph(self,subTriples,pattern) :
		"""
		Method used to collect the results. There are two ways to invoke the method:
			
		  - if the pattern argument is not None, then this means the construction of a separate triple store
		  with the results. This means taking the bindings in the node, and constuct the graph via the
		  L{construct<rdflibUtils.graphPattern.GraphPattern.construct>} method. This happens on the valid leafs; intermediate
		  nodes call the same method recursively
		  - otherwise, a leaf returns an array of the bindings, and intermediate methods aggregate those.
		  
		In both cases, leaf nodes may successifely expand the optional trees that they may have.
		
		@param subTriples: the triples so far
		@type subTriples: L{myTripleStore<rdflibUtils.myTripleStore.myTripleStore>}
		@param pattern: a graph pattern used to construct a graph
		@type pattern: L{GraphPattern<rdflibUtils.graphPattern.GraphPattern>}
		@return: if pattern is not None, an array of binding dictionaries
		"""
		def b(r,bind) :
			if type(r) == str :
				val = bind[r]
				if val == None :
					raise RuntimeError()
				return bind[r]
			else :
				return r
		if len(self.children) > 0 :
			# all children return an array of bindings (each element being a dictionary)
			if pattern == None :
				retval = reduce(lambda x,y: x+y, [x.expandSubgraph(subTriples,None) for x in self.children],[])
				(s,p,o,func) = self.statement
				for bind in retval :
					try :
						st = (b(s,bind),b(p,bind),b(o,bind))
						subTriples.add(st)
					except :
						# any exception means a None value creeping in, or something similar..
						pass
				return retval
			else :
				for x in self.children :
					x.expandSubgraph(subTriples,pattern)
		else :
			# return the local bindings if any. Not the optional trees should be added, too!
			if self.bound == True and self.clash == False :
				# Get the possible optional branches:
				for t in self.optionalTrees :
					t.expandSubgraph(subTriples,pattern)
				if pattern == None :
					return [self.bindings]
				else :
					pattern.construct(subTriples,self.bindings)
			else :
				return []
				
				
	def _bind(self,r) :
		"""
		@param r: string
		@return: returns None if no bindings occured yet, the binding otherwise
		"""
		if isinstance(r,basestring) and not isinstance(r,Identifier)  :
			if self.bindings[r] == None :
				return None
			else :
				return self.bindings[r]
		else :
			return r					

	def expand(self,constraints) :
		"""
		The expansion itself. See class comments for details.
		
		@param constraints: array of global constraining (filter) methods		
		"""
		# if there are no more statements, that means that the constraints have been fully expanded
		if self.statement :
			# decompose the statement into subject, predicate and object
			# default setting for the search statement
			# see if subject (resp. predicate and object) is already bound. This
			# is done by taking over the content of self.dict if not None and replacing
			# the subject with that binding
			# the (search_subject,search_predicate,search_object) is then created
			(s,p,o,func) = self.statement
			# put the bindings we have so far into the statement; this may add None values,
			# but that is exactly what RDFLib uses in its own search methods!
			(search_s,search_p,search_o) = (self._bind(s),self._bind(p),self._bind(o))
			for (result_s,result_p,result_o) in self.tripleStore.graph.triples((search_s,search_p,search_o)) :
				# if a user defined constraint has been added, it should be checked now
				if func != None and func(result_s,result_p,result_o) == False :
					# Oops, this result is not acceptable, jump over it!
					continue
				# create a copy of the current bindings, by also adding the new ones from result of the search
				new_bindings = self.bindings.copy()
				if search_s == None : new_bindings[s] = result_s
				if search_p == None : new_bindings[p] = result_p
				if search_o == None : new_bindings[o] = result_o
					
				# Recursion starts here: create and expand a new child
				child = _SPARQLNode(self,new_bindings,self.rest,self.tripleStore)
				child.expand(constraints)
				# if the child is a clash then no use adding it to the tree, it can be forgotten
				if self.clash == False :
					self.children.append(child)
					
			if len(self.children) == 0 :
				# this means that the constraints could not be met at all with this binding!!!!
				self.clash = True
		else :
			# this is if all bindings are done; the conditions (ie, global constraints) are still to be checked
			if self.bound == True and self.clash == False :
				self.bindings[_graphKey] = self.tripleStore
				for func in constraints :
					if func(self.bindings) == False :
						self.clash = True
						break
				
	def expandOptions(self,bindings,statements,constraints) :
		"""
		Managing optional statements. These affect leaf nodes only, if they contain
		'real' results. A separate Expansion tree is appended to such a node, one for each optional call.
		
		@param bindings: current bindings dictionary
		@param statements: array of statements from the 'where' clause. The first element is
		for the current node, the rest for the children. If empty, then no
		expansion occurs (ie, the node is a leaf). The bindings at this node are taken into account
		(replacing the unbound variables with the real resources) before expansion
		@param constraints: array of constraint (filter) methods
		"""
		def replace(key,resource,tupl) :
			s,p,o,func = tupl
			if key == s : s = resource
			if key == p : p = resource
			if key == o : o = resource
			return (s,p,o,func)
			
		if len(self.children) == 0  :
			# this is a leaf in the original expansion
			if self.bound == True and self.clash == False :
				# see if the optional bindings can be reduced because they are already
				# bound by this node
				for key in self.bindings :
					statements = [ replace(key,self.bindings[key],t) for t in statements ]
					if key in bindings :
						del bindings[key]
				optTree = _SPARQLNode(None,bindings,statements,self.tripleStore)
				self.optionalTrees.append(optTree)
				optTree.expand(constraints)
		else :
			for c in self.children :
				c.expandOptions(bindings,statements,constraints)


