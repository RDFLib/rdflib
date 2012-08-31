import sys, imp

from rdflib.parser import Parser, StringInputSource, URLInputSource, FileInputSource

# This is the parser interface as it would look when called from the rest of RDFLib
class RDFaParser(Parser) :
	def parse(self, source, graph,
			  pgraph                 = None,
			  media_type             = None,
			  rdfa_version           = None,
			  embedded_rdf           = False,
			  vocab_expansion        = False,
			  vocab_cache            = False,
			  rdfOutput              = False) :
		"""
		@param source: one of the input sources that the RDFLib package defined
		@type source: InputSource class instance
		@param graph: target graph for the triples; output graph, in RDFa spec. parlance
		@type graph: RDFLib Graph
		@keyword pgraph: target for error and warning triples; processor graph, in RDFa spec. parlance. If set to None, these triples are ignored
		@type pgraph: RDFLib Graph
		@keyword media_type: explicit setting of the preferred media type (a.k.a. content type) of the the RDFa source. None means the content type of the HTTP result is used, or a guess is made based on the suffix of a file
		@type media_type: string
		@keyword rdfa_version: 1.0 or 1.1. If the value is None, then, by default, 1.1 is used unless the source has explicit signals to use 1.0 (e.g., using a @version attribute, using a DTD set up for 1.0, etc)
		@type rdfa_version: string
		@keyword embedded_rdf: some formats allow embedding RDF in other formats: (X)HTML can contain turtle in a special <script> element, SVG can have RDF/XML embedded in a <metadata> element. This flag controls whether those triples should be interpreted and added to the output graph. Some languages (e.g., SVG) require this, and the flag is ignored.
		@type embedded_rdf: Boolean
		@keyword vocab_expansion: whether the RDFa @vocab attribute should also mean vocabulary expansion (see the RDFa 1.1 spec for further details)
		@type vocab_expansion: Boolean
		@keyword vocab_cache: in case vocab expansion is used, whether the expansion data (i.e., vocabulary) should be cached locally. This requires the ability for the local application to write on the local file system
		@type vocab_chache: Boolean
		@keyword rdfOutput: whether Exceptions should be catched and added, as triples, to the processor graph, or whether they should be raised.
		@type rdfOutput: Boolean
		"""
		# We need a dynamic way of setting the import path. That ensures that the core of the pyRdfa module
		# can be developed independently of the rdflib package
		path = imp.find_module('rdflib')[1]
		sys.path.insert(0,path+'/plugins/parsers')
		
		try:
			from pyRdfa import pyRdfa, Options
	
			if isinstance(source, StringInputSource) :
				orig_source = source.getByteStream()
			elif isinstance(source, URLInputSource) :
				orig_source = source.url
			elif isinstance(source, FileInputSource) :
				orig_source = source.file.name
				source.file.close()
				
			self.options = Options(output_processor_graph = (pgraph != None),
								   embedded_rdf           = embedded_rdf,
								   vocab_expansion        = vocab_expansion,
								   vocab_cache            = vocab_cache)
			
			baseURI      = source.getPublicId()
			processor    = pyRdfa(self.options, base = baseURI, media_type = media_type, rdfa_version = rdfa_version)
			processor.graph_from_source(orig_source, graph=graph, pgraph=pgraph, rdfOutput = rdfOutput)
		finally :
			sys.path.pop(0)

class MicrodataParser(Parser) :
	def parse(self, source, graph,
			  vocab_expansion        = False,
			  vocab_cache            = False,
			  rdfOutput              = False) :
		"""
		@param source: one of the input sources that the RDFLib package defined
		@type source: InputSource class instance
		@param graph: target graph for the triples; output graph, in RDFa spec. parlance
		@type graph: RDFLib Graph
		@keyword vocab_expansion: whether the RDFa @vocab attribute should also mean vocabulary expansion (see the RDFa 1.1 spec for further details)
		@type vocab_expansion: Boolean
		@keyword vocab_cache: in case vocab expansion is used, whether the expansion data (i.e., vocabulary) should be cached locally. This requires the ability for the local application to write on the local file system
		@type vocab_chache: Boolean
		@keyword rdfOutput: whether Exceptions should be catched and added, as triples, to the processor graph, or whether they should be raised.
		@type rdfOutput: Boolean
		"""
		# We need a dynamic way of setting the import path. That ensures that the core of the pyRdfa module
		# can be developed independently of the rdflib package
		path = imp.find_module('rdflib')[1]
		sys.path.insert(0,path+'/plugins/parsers')
		
		try:
			from pyMicrodata import pyMicrodata
	
			if isinstance(source, StringInputSource) :
				orig_source = source.getByteStream()
			elif isinstance(source, URLInputSource) :
				orig_source = source.url
			elif isinstance(source, FileInputSource) :
				orig_source = source.file.name
				source.file.close()
							
			baseURI      = source.getPublicId()
			processor    = pyMicrodata(base = baseURI)
			processor.graph_from_source(orig_source, graph=graph, rdfOutput = rdfOutput)
		finally :
			sys.path.pop(0)

class StructuredDataParser(Parser) :
	def parse(self, source, graph,
			  pgraph                 = None,
			  embedded_rdf           = True,
			  vocab_expansion        = False,
			  vocab_cache            = False,
			  rdfOutput              = False) :
		"""
		@param source: one of the input sources that the RDFLib package defined
		@type source: InputSource class instance
		@param graph: target graph for the triples; output graph, in RDFa spec. parlance
		@type graph: RDFLib Graph
		@keyword pgraph: target for error and warning triples; processor graph, in RDFa spec. parlance. If set to None, these triples are ignored
		@type pgraph: RDFLib Graph
		@keyword embedded_rdf: some formats allow embedding RDF in other formats: (X)HTML can contain turtle in a special <script> element, SVG can have RDF/XML embedded in a <metadata> element. This flag controls whether those triples should be interpreted and added to the output graph. Some languages (e.g., SVG) require this, and the flag is ignored.
		@type embedded_rdf: Boolean
		@keyword vocab_expansion: whether the RDFa @vocab attribute should also mean vocabulary expansion (see the RDFa 1.1 spec for further details)
		@type vocab_expansion: Boolean
		@keyword vocab_cache: in case vocab expansion is used, whether the expansion data (i.e., vocabulary) should be cached locally. This requires the ability for the local application to write on the local file system
		@type vocab_chache: Boolean
		@keyword rdfOutput: whether Exceptions should be catched and added, as triples, to the processor graph, or whether they should be raised.
		@type rdfOutput: Boolean
		"""
		# We need a dynamic way of setting the import path. That ensures that the core of the pyRdfa module
		# can be developed independently of the rdflib package
		path = imp.find_module('rdflib')[1]
		sys.path.insert(0,path+'/plugins/parsers')
		try:
			if isinstance(source, StringInputSource) :
				orig_source = source.getByteStream()
			elif isinstance(source, URLInputSource) :
				orig_source = source.url
			elif isinstance(source, FileInputSource) :
				orig_source = source.file.name
				source.file.close()
			baseURI      = source.getPublicId()

			# The RDFa part
			from pyRdfa import pyRdfa, Options				
			self.options = Options(output_processor_graph = (pgraph != None),
								   embedded_rdf           = embedded_rdf,
								   vocab_expansion        = vocab_expansion,
								   vocab_cache            = vocab_cache)
			
			processor = pyRdfa(self.options, base = baseURI, media_type = 'text/html', rdfa_version = '1.1')
			processor.graph_from_source(orig_source, graph=graph, pgraph=pgraph, rdfOutput = rdfOutput)
			
			# The Microdata part
			from pyMicrodata import pyMicrodata
			processor    = pyMicrodata(base = baseURI)
			processor.graph_from_source(orig_source, graph=graph, rdfOutput = rdfOutput)
		finally :
			sys.path.pop(0)
