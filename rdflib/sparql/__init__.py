# -*- coding: utf-8 -*-
#
#
# $Date: 2005/05/19 05:33:18 $, by $Author: ivan $, $Revision: 1.12 $
# The documentation of the module, hence the convention for the documentation of methods and classes,
# is based on the epydoc tool.  This tool parses Python source files
# and generates API descriptions XHTML. 
# The latest release of epydoc (version 2.0) can be
# downloaded from the <a href="http://sourceforge.net/project/showfiles.php?group_id=32455">SourceForge
# download page</a>.
# 
#
"""
Introduction
============
This package is a utility layer on the top of the excellent RDF Library, U{RDFLib<http://rdflib.net">}, created by Daniel Krech.
The documentation for the modules in the package are in:
	

  - L{myTripleStore<rdflibUtils.myTripleStore>}: some simple utilities on top of the RDFLib triple store
  - the core of a L{SPARQL API<rdflibUtils.sparql>} the core of a  implementation on top the triple store (sparql-p)
  - L{Graph Patterns<rdflibUtils.graphPattern>} for the SPARQL API
  - L{Operators<rdflibUtils.sparqlOperators>} for SPARQL

Utilities
=========
Some of the utilities are:

  - L{getPredicateValue<rdflibUtils.myTripleStore.myTripleStore.getPredicateValue>}:  just get the predicate value for a 
  (subject,predicate) pair. The situation where one
  knows from the context that there is only one value anyway occurs quite often, and this saves to write
  always the same cycle/exception handling stuff to do that.

  - L{getPredicateSubject<rdflibUtils.myTripleStore.myTripleStore.getPredicateSubject>}: the obvious counterpart of getPredicateSubject</li>

  - L{getSeq<rdflibUtils.myTripleStore.myTripleStore.getSeq>}: unfortunately, RDFLib does not handle Seq, it just returns an object of type 
  Seq and then one can get a bunch of _1, _2, etc, predicate values. Due to the way rdflib works, a triple search would return
  these in an arbitrary order. getSeq returns a (Python) array that sorts the rdf:li-s, essentially:
  the user can get to the resources in the order as they were defined in the original RDF.

  - L{unfoldCollection<rdflibUtils.myTripleStore.myTripleStore.unfoldCollection>}: does what it says, ie, creates a Python list from a collection.
  
  - L{clusterForward<rdflibUtils.myTripleStore.myTripleStore.clusterForward>}: using a seed as a subject, generates a separate Triple 
  Store with the transitive closure of the seed.
  
  - L{clusterBackward<rdflibUtils.myTripleStore.myTripleStore.clusterBackward>}: using a seed as a object, generates a separate Triple 
  Store with the transitive closure of the seed. 
  
  - L{cluster<rdflibUtils.myTripleStore.myTripleStore.cluster>}: the sum of the forward and backward clusters
			
  - __add__, __mul__,__sub__ methods for set theoretical union, intersection and substraction. Note that
  the original implementation already has __iadd__ and __isub__, meaning that both the a = b+c and a+=b type
  arithmetics are now in place for addition and substraction (but not a *=b! This doe not really make sense...). 
  Note also that the superclass also implements __eq__, ie, triple sets can be compared.
  
  - L{extendRdfs<rdflibUtils.myTripleStore.myTripleStore.extendRdfs>}: a subset of the full RDFS entailement rules.

SPARQL
======

For a general description of the SPARQL API, see the separate, more complete U{description<http://dev.w3.org/cvsweb/%7Echeckout%7E/2004/PythonLib-IH/Doc/sparqlDesc.html>}. Note that the 
L{SPARQL<rdflibUtils.sparql.SPARQL>} class is a superclass of 
L{myTripleStore<rdflibUtils.myTripleStore.myTripleStore>},
ie, by referring to the latter, all SPARQL functionalities are automatically included. Their separation into
separate classes is for a better maintainability only.

Variables, Imports
==================

The top level (__init__.py) module of the Package imports the important classes. In other words, the
user may choose to use the following imports only::
	
	from rdflibUtils   import myTripleStore
	from rdflibUtils   import retrieveRDFFiles
	from rdflibUtils   import UniquenessError, SPARQLError
	from rdflibUtils   import GraphPattern

The module imports and/or creates some frequently used Namespaces, and these can then be imported by the user like::
	
	from rdflibUtils import ns_rdf
	
These are:
	

 - ns_rdf:  the RDF Namespace
 - ns_rdfs: the RDFS Namespace
 - ns_dc:   the Dublic Core namespace
 - ns_owl:  the OWL namespace

Finally, the package also has a set of convenience string defines for XML Schema datatypes (ie, the URI-s of the datatypes); ie, one can use::
	
	from rdflibUtils import type_string
	from rdflibUtils import type_integer
	from rdflibUtils import type_long
	from rdflibUtils import type_double
	from rdflibUtils import type_float
	from rdflibUtils import type_decimal
	from rdflibUtils import type_dateTime
	from rdflibUtils import type_date
	from rdflibUtils import type_time
	from rdflibUtils import type_duration

These are used, for example, in the sparql-p implementation.

The three most important classes in RDFLib for the average user are Namespace, URIRef and Literal; these
are also imported, so the user can also use, eg::
	
	from rdflibUtils import Namespace, URIRef, Literal

History
=======

 - Version 1.0: based on an earlier version of the SPARQL, first released implementation
 - Version 2.0: version based on the March 2005 SPARQL document, also a major change of the core code (introduction of the separate L{GraphPattern<rdflibUtils.graphPattern.GraphPattern>} class, etc). 
 - Version 2.01: minor changes only:
	 - switch to epydoc as a documentation tool, it gives a much better overview of the classes
	 - addition of the SELECT * feature to sparql-p
 - Version 2.02: 
	 - added some methods to L{myTripleStore<rdflibUtils.myTripleStore.myTripleStore>} to handle C{Alt} and C{Bag} the same
	 way as C{Seq}
	 - added also methods to I{add} collections and containers to the triple store, not only retrieve them
	
@author: U{Ivan Herman<http://www.ivan-herman.net>}
@license: This software is available for use under the 
U{W3C Software License<http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231>}
@contact: Ivan Herman, ivan@ivan-herman.net
@version: 2.02


"""

__version__ = "2.02"

# import sys

# These are just useful imports from rdflib; for a user it is nicer if everything
# can be imported from one place...
from rdflib.Graph import Graph
from rdflib.Namespace   import Namespace
from rdflib.URIRef      import URIRef
from rdflib.Literal     import Literal
from rdflib.constants   import RDFNS  as ns_rdf
from rdflib.constants   import RDFSNS as ns_rdfs
from rdflib.constants   import NIL    as nil
from rdflib.exceptions  import Error

from sparqlGraph import ns_dc, ns_owl

# The 'visible' side of sparqlGraph
from sparqlGraph import SPARQLGraph, UniquenessError

# The 'visible' side of sparql
from graphPattern import GraphPattern
from sparql import SPARQLError
from sparql import Query
# Key to be used in global SPARQL operators to access the triple store corresponding to the background graph
from sparql import _graphKey as graphKey

# The datatypes
from sparql import type_string
from sparql import type_integer
from sparql import type_long
from sparql import type_double
from sparql import type_float
from sparql import type_decimal
from sparql import type_dateTime
from sparql import type_date
from sparql import type_time

# The sparql operators
from sparqlOperators import *

from types import *

############################################################################################

def retrieveRDFFiles(rdfFiles, silent = False, extendRdfs=False, graph = None) :
	"""
	Retrieve a list of RDF files (encoded in RDF/XML). The rdflib parser may raise Parse exceptions (see rdflib documentation).
	
	@param rdfFiles: either a string (for one file) or a list of strings
	@param silent: if True, a message is printed after having loaded an RDF file
	@type silent: Boolean
	@param extendRdfs: whether the mini-RDFS entailement should be performed right after the creation of the triple
	store (ie, whether the
	L{extendRdfs<rdflibUtils.sparqlGraph.sparqlGraph.extendRdfs>} method should be invoked or not).
	The user can call that method later if the triple store is built up in several steps
	@type extendRdfs: Boolean
	@param graph: if not None, it is considered to be an existing triple store (for incremental parsing)
	@rtype: L{sparqlGraph<rdflibUtils.sparqlGraph.sparqlGraph>}
	"""
	if graph == None :
		data = SPARQLGraph()
	else :
		data = graph
	if isinstance(rdfFiles,basestring) :
		files = [rdfFiles]
	else :
		files = rdfFiles
	for fileN in files :
		if silent == False :
			print "Load %s..." % (fileN,)
		data.load(fileN)
		if silent == False :
			print "%s loaded" % (fileN,)
	if extendRdfs :
		data.extendRdfs()
	return data

def retrieveRDFData(rdfDirs,rdfFiles, silent = False, extendRdfs=False, graph = None) :
	"""
	Retrieve and parse list of RDF files (encoded in RDF/XML), collecting I{all} files with an
	'.rdf' suffix from a set of directories, plus a number of explicit RDF files. 
	
	@param rdfDirs: either a string (for one directory) or a list of directory paths. Can be set to None (in which case
	it will be ignored). Each directory is searched for RDF/XML files to be parsed and added to the triple store
	@param rdfFiles: either a string (for one file) or a list of strings for the paths of additional RDF files
	@param silent: if True, a message is printed after having loaded an RDF file
	@type silent: Boolean
	@param extendRdfs: whether the mini-RDFS entailement should be performed right after the creation of the triple
	store (ie, whether the
	L{extendRdfs<rdflibUtils.myTripleStore.myTripleStore.extendRdfs>} method should be invoked or not).
	The user can call that method later if the triple store is built up in several steps
	@type extendRdfs: Boolean
	@param graph: if not None, it is considered to be an existing triple store (for incremental parsing)
	@returns: a (store,errmessage) tuple. The store contains all tuples that could be parsed in; errmessage is a list
	of possible sys.exc_info() messages with exceptions that might have been raised during parsing.
	@rtype: (L{myTripleStore<rdflibUtils.myTripleStore.myTripleStore>},errmessage)
	"""
	import os
	files = []
	if rdfDirs != None :
		if type(rdfDirs) == str :
			dirs = [rdfDirs]
		else :
			dirs = rdfDirs
		for path in dirs :
			if os.access(path,os.R_OK) == 1 :
				for f in os.listdir(path) :
					# at some point, hopefully: if f.endswith(".rdf") or f.endswith(".n3")
					if f.endswith(".rdf") :
						files.append(path + "/" + f)
	if type(rdfFiles) == str :
		files = files + [rdfFiles]
	else :
		files = files + rdfFiles
		
	# cycle through the individual files
	store = SPARQLGraph()
	errorMessages = []
	for rdffile in files :
		try :
			retrieveRDFFiles(rdffile,silent,False,store)
		except :
			errorMessages.append(sys.exc_info())
	if extendRdfs :
		store.extendRdfs()
	return (store,errorMessages)
	

############################################################################################
#
def generateCollectionConstraint(triplets,collection,item) :
	"""
	Generate a function that can then be used as a global constaint in sparql to check whether
	the 'item' is an element of the 'collection' (a.k.a. list). Both collection and item can
	be a real resource or a query string. Furthermore, item might be a plain string, that is
	then turned into a literal run-time.

	The function returns an adapted filter method that can then be plugged into a sparql request.
	  
	@param triplets: the L{myTripleStore<rdflibUtils.myTripleStore.myTripleStore>} instance
	@param collection: is either a query string (that has to be bound by the query) or an RDFLib Resource 
	representing the collection
	@param item: is either a query string (that has to be bound by the query) or an RDFLib Resource
	that must be tested to be part of the collection
	@rtype: a function suitable as a sparql filter
	@raises rdflibUtils.sparql.SPARQLError: if the collection or the item parameters are illegal (not valid resources for
	a collection or an object)
	"""
	return isOnCollection(collection,item)

############################################################################################

