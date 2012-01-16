"""
N-Triples RDF graph serializer for RDFLib.
See <http://www.w3.org/TR/rdf-testcases/#ntriples> for details about the
format.
"""
from rdflib.serializer import Serializer
from rdflib.py3compat import b
import warnings

__all__ = ['NTSerializer']

class NTSerializer(Serializer):
    """
    Serializes RDF graphs to NTriples format.
    """

    def serialize(self, stream, base=None, encoding=None, **args):
        if base is not None:
            warnings.warn("NTSerializer does not support base.")
        if encoding is not None:
            warnings.warn("NTSerializer does not use custom encoding.")
        encoding = self.encoding
        for triple in self.store:
            stream.write(_nt_row(triple).encode(encoding, "replace"))
        stream.write(b("\n"))


def _nt_row(triple):
    return u"%s %s %s .\n" % (triple[0].n3(),
            triple[1].n3(),
            _xmlcharref_encode(triple[2].n3()))

# from <http://code.activestate.com/recipes/303668/>
def _xmlcharref_encode(unicode_data, encoding="ascii"):
    """Emulate Python 2.3's 'xmlcharrefreplace' encoding error handler."""
    chars = []

    # nothing to do about xmlchars, but replace newlines with escapes: 
    unicode_data=unicode_data.replace("\n","\\n")
    if unicode_data.startswith('"""'):
        # Updated with Bernhard Schandl's patch...
        # unicode_data = unicode_data.replace('"""', '"')   # original

        last_triplequote_pos = unicode_data.rfind('"""')
        payload = unicode_data[3:last_triplequote_pos]
        trail = unicode_data[last_triplequote_pos+3:]

        # fix three-quotes encoding
        payload = payload.replace('\\"""', '"""')

        # corner case: if string ends with " it is already encoded.
        # so we need to de-escape it before it will be re-escaped in the next step.
        if payload.endswith('\\"'):
            payload = payload.replace('\\"', '"')

        # escape quotes in payload
        payload = payload.replace('"', '\\"')

        # reconstruct result using single quotes
        unicode_data = '"%s"%s' % (payload, trail)

    # Step through the unicode_data string one character at a time in
    # order to catch unencodable characters:                          
    for char in unicode_data:
        try:
            char.encode(encoding, 'strict')
        except UnicodeError:
            if ord(char) <= 0xFFFF:
                chars.append('\\u%04X' % ord(char))
            else:
                chars.append('\\U%08X' % ord(char))
        else:
            chars.append(char)

    return ''.join(chars)

