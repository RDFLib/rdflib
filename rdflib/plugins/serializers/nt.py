"""
N-Triples RDF graph serializer for RDFLib.
See <http://www.w3.org/TR/rdf-testcases/#ntriples> for details about the
format.
"""
from rdflib.term import Literal
from rdflib.serializer import Serializer

import warnings
import codecs

__all__ = ["NTSerializer"]


class NTSerializer(Serializer):
    """
    Serializes RDF graphs to NTriples format.
    """

    def __init__(self, store):
        Serializer.__init__(self, store)
        self.encoding = "ascii"  # n-triples are ascii encoded

    def serialize(self, stream, base=None, encoding=None, **args):
        if base is not None:
            warnings.warn("NTSerializer does not support base.")
        if encoding is not None and encoding.lower() != self.encoding.lower():
            warnings.warn("NTSerializer does not use custom encoding.")
        encoding = self.encoding
        for triple in self.store:
            stream.write(_nt_row(triple).encode(self.encoding, "_rdflib_nt_escape"))
        stream.write("\n".encode("latin-1"))


class NT11Serializer(NTSerializer):
    """
    Serializes RDF graphs to RDF 1.1 NTriples format.

    Exactly like nt - only utf8 encoded.
    """

    def __init__(self, store):
        Serializer.__init__(self, store)  # default to utf-8


def _nt_row(triple):
    if isinstance(triple[2], Literal):
        return "%s %s %s .\n" % (
            triple[0].n3(),
            triple[1].n3(),
            _quoteLiteral(triple[2]),
        )
    else:
        return "%s %s %s .\n" % (triple[0].n3(), triple[1].n3(), triple[2].n3())


def _quoteLiteral(l_):
    """
    a simpler version of term.Literal.n3()
    """

    encoded = _quote_encode(l_)

    if l_.language:
        if l_.datatype:
            raise Exception("Literal has datatype AND language!")
        return "%s@%s" % (encoded, l_.language)
    elif l_.datatype:
        return "%s^^<%s>" % (encoded, l_.datatype)
    else:
        return "%s" % encoded


def _quote_encode(l_):
    return '"%s"' % l_.replace("\\", "\\\\").replace("\n", "\\n").replace(
        '"', '\\"'
    ).replace("\r", "\\r")


def _nt_unicode_error_resolver(err):
    """
    Do unicode char replaces as defined in https://www.w3.org/TR/2004/REC-rdf-testcases-20040210/#ntrip_strings
    """

    def _replace_single(c):
        c = ord(c)
        fmt = "\\u%04X" if c <= 0xFFFF else "\\U%08X"
        return fmt % c

    string = err.object[err.start : err.end]
    return "".join(_replace_single(c) for c in string), err.end


codecs.register_error("_rdflib_nt_escape", _nt_unicode_error_resolver)
