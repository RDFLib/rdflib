#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
RDFPipe is a commandline tool for parsing RDF in different formats from files
(or stdin) and serializing the resulting graph in a chosen format.
"""

from rdflib import plugin
from rdflib.store import Store
from rdflib.graph import Graph
from rdflib.namespace import Namespace, RDF, RDFS, OWL, _XSD_NS
from rdflib.syntax.parsers import Parser
from rdflib.syntax.serializers import Serializer

from rdflib_tools.pathutils import guess_format

import sys
from optparse import OptionParser


RDFLIB_CONNECTION = ''
RDFLIB_STORE = 'IOMemory'

DEFAULT_INPUT_FORMAT = 'xml'
DEFAULT_OUTPUT_FORMAT = 'n3'

NS_BINDINGS = {
    'rdf':  RDF,
    'rdfs': RDFS,
    'owl':  OWL,
    'xsd':  _XSD_NS,
    'dc':   "http://purl.org/dc/elements/1.1/",
    'dct':  "http://purl.org/dc/terms/",
    'foaf': "http://xmlns.com/foaf/0.1/",
    'wot':  "http://xmlns.com/wot/0.1/"
}


def read_and_serialize(input_files, input_format, output_format, guess, ns_bindings):
    store = plugin.get(RDFLIB_STORE, Store)()
    store.open(RDFLIB_CONNECTION)
    graph = Graph(store)

    for prefix, uri in ns_bindings.items():
        graph.namespace_manager.bind(prefix, uri, override=False)

    for fpath in input_files:
        use_format = input_format
        if fpath == '-':
            fpath = sys.stdin
        elif not input_format and guess:
            use_format = guess_format(fpath) or DEFAULT_INPUT_FORMAT
        # TODO: get extra kwargs to serializer (by parsing output_format key)?
        graph.parse(fpath, format=use_format)

    out = graph.serialize(destination=None, format=output_format, base=None)
    store.rollback()
    return out


_get_plugin_names = lambda kind: ", ".join(repr(p.name) for p in plugin.plugins(kind=kind))

def make_option_parser():
    parser_names = _get_plugin_names(Parser)
    serializer_names = _get_plugin_names(Serializer)

    oparser = OptionParser(
            "%prog [-h] [-i INPUT_FORMAT] [-o OUTPUT_FORMAT] [--ns=PFX=NS ...] [-] [FILE ...]")

    oparser.add_option('-i', '--input-format',
            type=str, #default=DEFAULT_INPUT_FORMAT,
            help="Format of the input document(s). One of: %s." % parser_names,
            metavar="INPUT_FORMAT")

    oparser.add_option('-o', '--output-format',
            type=str, default=DEFAULT_OUTPUT_FORMAT,
            help="Format of the final serialized RDF graph. One of: %s." % serializer_names,
            metavar="OUTPUT_FORMAT")

    oparser.add_option("--ns",
            action="append", type=str,
            help="Register a namespace binding (QName prefix to a base URI). "
                    "This can be used more than once.",
            metavar="PREFIX=NAMESPACE")

    oparser.add_option("--no-guess", dest='guess',
            action='store_false', default=True,
            help="Don't guess format based on file suffix.")

    return oparser


def main():
    oparser = make_option_parser()
    opts, args = oparser.parse_args()
    if len(args) < 1:
        oparser.print_usage()
        oparser.exit()

    ns_bindings = dict(NS_BINDINGS)
    if opts.ns:
        for ns_kw in opts.ns:
            pfx, uri = ns_kw.split('=')
            ns_bindings[pfx] = uri

    print read_and_serialize(args,
            opts.input_format, opts.output_format, opts.guess,
            ns_bindings)


if __name__ == "__main__":
    main()

