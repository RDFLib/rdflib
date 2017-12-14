"""
N-Triples RDF graph serializer for RDFLib.
See <http://www.w3.org/TR/rdf-testcases/#ntriples> for details about the
format.
"""
from rdflib.term import Literal
from rdflib.serializer import Serializer
from six import b

import warnings
import codecs

__all__ = ['NTSerializer']


class NTSerializer(Serializer):
    """
    Serializes RDF graphs to NTriples format.
    """

    def __init__(self, store):
        Serializer.__init__(self, store)
        self.encoding = 'ascii' # n-triples are ascii encoded

    def serialize(self, stream, base=None, encoding=None, **args):
        if base is not None:
            warnings.warn("NTSerializer does not support base.")
        if encoding is not None and encoding.lower() != self.encoding.lower():
            warnings.warn("NTSerializer does not use custom encoding.")
        encoding = self.encoding
        for triple in self.store:
            stream.write(_nt_row(triple).encode(self.encoding, "_rdflib_nt_escape"))
        stream.write(b("\n"))


class NT11Serializer(NTSerializer):
    """
    Serializes RDF graphs to RDF 1.1 NTriples format.

    Exactly like nt - only utf8 encoded.
    """

    def __init__(self, store):
        Serializer.__init__(self, store) # default to utf-8


def _nt_row(triple):
    if isinstance(triple[2], Literal):
        return u"%s %s %s .\n" % (
            triple[0].n3(),
            triple[1].n3(),
            _quoteLiteral(triple[2]))
    else:
        return u"%s %s %s .\n" % (triple[0].n3(),
                                  triple[1].n3(),
                                  triple[2].n3())


def _quoteLiteral(l):
    '''
    a simpler version of term.Literal.n3()
    '''

    encoded = _quote_encode(l)

    if l.language:
        if l.datatype:
            raise Exception("Literal has datatype AND language!")
        return '%s@%s' % (encoded, l.language)
    elif l.datatype:
        return '%s^^<%s>' % (encoded, l.datatype)
    else:
        return '%s' % encoded


def _quote_encode(l):
    return '"%s"' % l.replace('\\', '\\\\')\
        .replace('\n', '\\n')\
        .replace('"', '\\"')\
        .replace('\r', '\\r')

def _nt_unicode_error_resolver(err):

    """
    Do unicode char replaces as defined in https://www.w3.org/TR/2004/REC-rdf-testcases-20040210/#ntrip_strings
    """

    def _replace_single(c):
        c = ord(c)
        fmt = u'\\u%04X' if c <= 0xFFFF else u'\\U%08X'
        return fmt % c

    string = err.object[err.start:err.end]
    return ( "".join( _replace_single(c) for c in string ), err.end )

codecs.register_error('_rdflib_nt_escape', _nt_unicode_error_resolver)
