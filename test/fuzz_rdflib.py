#!/usr/bin/python3

import atheris

with atheris.instrument_imports():
    import sys
    from xml.sax import SAXParseException

    from rdflib import Graph
    from rdflib.exceptions import ParserError
    from rdflib.plugins.parsers.notation3 import BadSyntax


def test_one_input(data):
    # arbitrary byte 'data' created by atheris that mutates each time
    # this allows you to manipulate the 'data' into strings, integers, lists of integers etc.
    fdp = atheris.FuzzedDataProvider(data)

    format_list = ["xml", "trix", "turtle", "n3", "nt"]
    g = Graph()
    try:
        g.parse(
            format=fdp.PickValueInList(format_list),
            data=fdp.ConsumeUnicodeNoSurrogates(fdp.ConsumeIntInRange(1, 100)),
        )
    # Data generated is not appropriate, so ignore BadSyntax, SAXParseException and ParserError
    except (BadSyntax, SAXParseException, ParserError):
        pass


atheris.Setup(sys.argv, test_one_input)
atheris.Fuzz()
