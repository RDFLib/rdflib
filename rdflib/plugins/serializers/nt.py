"""
N-Triples RDF graph serializer for RDFLib.
See <http://www.w3.org/TR/rdf-testcases/#ntriples> for details about the
format.
"""
from rdflib.serializer import Serializer
import warnings


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
        stream.write("\n")


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
    if unicode_data.startswith('"""'): unicode_data=unicode_data[2:-2]

    # Step through the unicode_data string one character at a time in
    # order to catch unencodable characters:
    for char in unicode_data:
        try:
            chars.append(char.encode(encoding, 'strict'))
        except UnicodeError:
            chars.append('\u%04X' % ord(char))
    return ''.join(chars)

