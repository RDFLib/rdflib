#!/usr/bin/env python
"""
Extraction parsers for structured data embedded into HTML or XML files.
The former may include RDFa or microdata. The syntax and the extraction
procedures are based on:

* The RDFa specifications: http://www.w3.org/TR/#tr_RDFa
* The microdata specification: http://www.w3.org/TR/microdata/
* The specification of the microdata to RDF conversion:
http://www.w3.org/TR/microdata-rdf/

License: W3C Software License,
http://www.w3.org/Consortium/Legal/copyright-software
Author: Ivan Herman
Copyright: W3C

"""

from rdflib.parser import Parser, StringInputSource, URLInputSource, FileInputSource

try:
    import html5lib

    assert html5lib
    html5lib = True
except ImportError:
    import warnings

    warnings.warn(
        "html5lib not found! RDFa and Microdata " + "parsers will not be available."
    )
    html5lib = False


def _get_orig_source(source):
    """
    A bit of a hack; the RDFa/microdata parsers need more than what the
    upper layers of RDFLib provide...
    This method returns the original source references.
    """
    if isinstance(source, StringInputSource):
        orig_source = source.getByteStream()
    elif isinstance(source, URLInputSource):
        orig_source = source.url
    elif isinstance(source, FileInputSource):
        orig_source = source.file.name
        source.file.close()
    else:
        orig_source = source.getByteStream()
    baseURI = source.getPublicId()
    return (baseURI, orig_source)


class MicrodataParser(Parser):
    """
    Wrapper around an HTML5 microdata, extracted and converted into RDF. For
    the specification of microdata, see the relevant section of the HTML5
    spec: http://www.w3.org/TR/microdata/; for the algorithm used to extract
    microdata into RDF, see http://www.w3.org/TR/microdata-rdf/.
    """

    def parse(self, source, graph):
        """
        @param source: one of the input sources that the RDFLib package defined
        @type source: InputSource class instance
        @param graph: target graph for the triples; output graph, in RDFa
        spec. parlance
        @type graph: RDFLib Graph
        @keyword vocab_expansion: whether the RDFa @vocab attribute should
        also mean vocabulary expansion (see the RDFa 1.1 spec for further
            details)
        @type vocab_expansion: Boolean
        @keyword vocab_cache: in case vocab expansion is used, whether the
        expansion data (i.e., vocabulary) should be cached locally. This
        requires the ability for the local application to write on the
        local file system
        @type vocab_chache: Boolean
        @keyword rdfOutput: whether Exceptions should be catched and added,
        as triples, to the processor graph, or whether they should be raised.
        @type rdfOutput: Boolean
        """
        if html5lib is False:
            raise ImportError(
                "html5lib is not installed, cannot use RDFa " + "and Microdata parsers."
            )

        (baseURI, orig_source) = _get_orig_source(source)
        self._process(graph, baseURI, orig_source)

    def _process(self, graph, baseURI, orig_source):
        from pyMicrodata import pyMicrodata

        processor = pyMicrodata(base=baseURI)
        processor.graph_from_source(orig_source, graph=graph, rdf_output=False)


class StructuredDataParser(Parser):
    """
    Convenience parser to extract both RDFa (including embedded Turtle)
    and microdata from an HTML file.
    It is simply a wrapper around the specific parsers.
    """

    def parse(
        self,
        source,
        graph,
        pgraph=None,
        rdfa_version="",
        vocab_expansion=False,
        vocab_cache=False,
        media_type="text/html",
    ):
        """
        @param source: one of the input sources that the RDFLib package defined
        @type source: InputSource class instance
        @param graph: target graph for the triples; output graph, in RDFa
        spec. parlance
        @keyword rdfa_version: 1.0 or 1.1. If the value is "", then, by
        default, 1.1 is used unless the source has explicit signals to use 1.0
        (e.g., using a @version attribute, using a DTD set up for 1.0, etc)
        @type rdfa_version: string
        @type graph: RDFLib Graph
        @keyword pgraph: target for error and warning triples; processor
        graph, in RDFa spec. parlance. If set to None, these triples are
        ignored
        @type pgraph: RDFLib Graph
        @keyword vocab_expansion: whether the RDFa @vocab attribute should
        also mean vocabulary expansion (see the RDFa 1.1 spec for further
            details)
        @type vocab_expansion: Boolean
        @keyword vocab_cache: in case vocab expansion is used, whether the
        expansion data (i.e., vocabulary) should be cached locally. This
        requires the ability for the local application to write on the
        local file system
        @type vocab_chache: Boolean
        @keyword rdfOutput: whether Exceptions should be catched and added,
        as triples, to the processor graph, or whether they should be raised.
        @type rdfOutput: Boolean
        """
        # Note that the media_type argument is ignored, and is here only to avoid an 'unexpected argument' error.
        # This parser works for text/html only anyway...
        (baseURI, orig_source) = _get_orig_source(source)
        if rdfa_version == "":
            rdfa_version = "1.1"

        try:
            from pyRdfa.rdflibparsers import RDFaParser, HTurtleParser

            RDFaParser()._process(
                graph,
                pgraph,
                baseURI,
                orig_source,
                media_type="text/html",
                rdfa_version=rdfa_version,
                vocab_expansion=vocab_expansion,
                vocab_cache=vocab_cache,
            )

            HTurtleParser()._process(
                graph, baseURI, orig_source, media_type="text/html"
            )
        except ImportError:
            warnings.warn("pyRDFa not installed, will only parse Microdata")

        MicrodataParser()._process(graph, baseURI, orig_source)
