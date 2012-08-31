# -*- coding: utf-8 -*-
"""
Wrapper around RDFLib's Graph object. The issue is that, in RDFLib 2.X, the turtle and the RDF/XML serialization both have some issues (bugs and ugly output). As a result, the package’s own serializers should be registered and used. On the other hand, in RDFLib 3.X this becomes unnecessary, it is better to keep to the library’s own version. This wrapper provides a subclass of RDFLib’s Graph overriding the serialize method to register, if necessary, a different serializer and use that one.

Also, some bindings (in the RDFLib sense) are done automatically, to ensure a nicer output for widely used schemas…

@summary: Shell around RDLib's Graph
@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}

@var _bindings: Default bindings. This is just for the beauty of things: bindings are added to the graph to make the output nicer. If this is not done, RDFlib defines prefixes like "_1:", "_2:" which is, though correct, ugly…
"""

"""
$Id: graph.py,v 1.6 2012/03/23 14:06:25 ivan Exp $ $Date: 2012/03/23 14:06:25 $

"""

import rdflib
if rdflib.__version__ >= "3.0.0" :
	from rdflib	import Graph
else :
	from rdflib.Graph import Graph
from rdflib	import Namespace

_xml_serializer_name	= "my-rdfxml"
_turtle_serializer_name	= "my-turtle"
_json_serializer_name	= "my-json-ld"

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

# Default bindings. This is just for the beauty of things: bindings are added to the graph to make the output nicer. If this is not done, RDFlib defines prefixes like "_1:", "_2:" which is, though correct, ugly...
_bindings = [	
]

	
#########################################################################################################
class MyGraph(Graph) :
	"""
	Wrapper around RDFLib's Graph object. The issue is that the serializers in RDFLib are buggy:-(
	
	In RDFLib 2.X both the Turtle and the RDF/XML serializations have issues (bugs and ugly output). In RDFLib 3.X
	the Turtle serialization seems to be fine, but the RDF/XML has problems:-(
	
	This wrapper provides a subclass of RDFLib’s Graph overriding the serialize method to register,
	if necessary, a different serializer and use that one.

	@cvar xml_serializer_registered_2: flag to avoid duplicate registration for RDF/XML for rdflib 2.*
	@type xml_serializer_registered_2: boolean
	@cvar xml_serializer_registered_3: flag to avoid duplicate registration for RDF/XML for rdflib 3.*
	@type xml_serializer_registered_3: boolean
	@cvar json_serializer_registered: flag to avoid duplicate registration for JSON-LD for rdflib 3.*
	@type json_serializer_registered: boolean
	@cvar turtle_serializer_registered_2: flag to avoid duplicate registration for Turtle for rdflib 2.*
	@type turtle_serializer_registered_2: boolean
	"""
	xml_serializer_registered_2		= False
	xml_serializer_registered_3		= False
	turtle_serializer_registered_2	= False
	json_serializer_registered      = False
	
	def __init__(self) :
		Graph.__init__(self)
		for (prefix,uri) in _bindings :
			self.bind(prefix,Namespace(uri))

	def _register_XML_serializer_3(self) :
		"""The default XML Serializer of RDFLib 3.X is buggy, mainly when handling lists. An L{own version<serializers.prettyXMLserializer_3>} is
		registered in RDFlib and used in the rest of the package. 
		"""
		if not MyGraph.xml_serializer_registered_3 :
			from rdflib.plugin import register
			from rdflib.serializer import Serializer
			if rdflib.__version__ > "3.1.0" :
				register(_xml_serializer_name, Serializer,
						 "pyRdfa.serializers.prettyXMLserializer_3_2", "PrettyXMLSerializer")
			else :
				register(_xml_serializer_name, Serializer,
						 "pyRdfa.serializers.prettyXMLserializer_3", "PrettyXMLSerializer")
			MyGraph.xml_serializer_registered_3 = True

	def _register_JSON_serializer_3(self) :
		"""JSON LD serializer 
		"""
		if not MyGraph.json_serializer_registered :
			from rdflib.plugin import register
			from rdflib.serializer import Serializer
			register(_json_serializer_name, Serializer,
					 "pyRdfa.serializers.jsonserializer", "JsonSerializer")
			MyGraph.json_serializer_registered = True

	def _register_XML_serializer_2(self) :
		"""The default XML Serializer of RDFLib 2.X is buggy, mainly when handling lists.
		An L{own version<serializers.prettyXMLserializer>} is
		registered in RDFlib and used in the rest of the package. This is not used for RDFLib 3.X.
		"""
		if not MyGraph.xml_serializer_registered_2 :
			from rdflib.plugin import register
			from rdflib.syntax import serializer, serializers
			register(_xml_serializer_name, serializers.Serializer,
					 "pyRdfa.serializers.prettyXMLserializer", "PrettyXMLSerializer")
			MyGraph.xml_serializer_registered_2 = True

	def _register_Turtle_serializer_2(self) :
		"""The default Turtle Serializers of RDFLib 2.X is buggy and not very nice as far as the output is concerned.
		An L{own version<serializers.TurtleSerializer>} is registered in RDFLib and used in the rest of the package.
		This is not used for RDFLib 3.X.
		"""
		if not MyGraph.turtle_serializer_registered_2 :
			from rdflib.plugin import register
			from rdflib.syntax import serializer, serializers
			register(_turtle_serializer_name, serializers.Serializer,
					 "pyRdfa.serializers.turtleserializer", "TurtleSerializer")
			MyGraph.turtle_serialzier_registered_2 = True
			
	def add(self, (s,p,o)) :
		"""Overriding the Graph's add method to filter out triples with possible None values. It may happen
		in case, for example, a host language is not properly set up for the distiller"""
		if s == None or p == None or o == None :
			return
		else :
			Graph.add(self, (s,p,o))
		
	def serialize(self, format = "xml") :
		"""Overriding the Graph's serialize method to adjust the output format"""
		if rdflib.__version__ >= "3.0.0" :
			# this is the easy case
			if format == "xml" or format == "pretty-xml" :
				self._register_XML_serializer_3()
				return Graph.serialize(self, format=_xml_serializer_name)
			elif format == "json-ld" or format == "json" :
				# The new version of the serialziers in RDFLib 3.2.X require this extra round...
				# I do not have the patience of working out why that is so.
				self._register_JSON_serializer_3()
				stream = StringIO()
				Graph.serialize(self, format=_json_serializer_name, destination = stream)
				return stream.getvalue()
			elif format == "nt" :
				return Graph.serialize(self, format="nt")
			elif format == "n3" or format == "turtle" :
				retval =""
				return Graph.serialize(self, format="turtle")
		else :
			if format == "xml" or format == "pretty-xml" :
				self._register_XML_serializer_2()
				return Graph.serialize(self, format=_xml_serializer_name)
			elif format == "nt" :
				return Graph.serialize(self, format="nt")
			elif format == "n3" or format == "turtle" :
				self._register_Turtle_serializer_2()
				return Graph.serialize(self, format=_turtle_serializer_name)


