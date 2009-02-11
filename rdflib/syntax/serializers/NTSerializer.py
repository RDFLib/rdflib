#$Id: NTSerializer.py,v 1.6 2003/10/29 15:25:24 kendall Exp $

from rdflib.syntax.serializers import Serializer

class NTSerializer(Serializer):

    def __init__(self, store):
        """
        I serialize RDF graphs in NTriples format.
        """
        super(NTSerializer, self).__init__(store)

    def serialize(self, stream, base=None, encoding=None, **args):
        if base is not None:
            print "TODO: NTSerializer does not support base"
        encoding = self.encoding
        write = lambda triple: stream.write((triple[0].n3() + u" " + \
                                             triple[1].n3() + u" " + _xmlcharref_encode(triple[2].n3()) + u".\n").encode(encoding, "replace"))
        map(write, self.store)


# from http://code.activestate.com/recipes/303668/


def _xmlcharref_encode(unicode_data, encoding="ascii"):
    """Emulate Python 2.3's 'xmlcharrefreplace' encoding error handler."""
    chars = []
    # Step through the unicode_data string one character at a time in
    # order to catch unencodable characters:
    for char in unicode_data:
        try:
            chars.append(char.encode(encoding, 'strict'))
        except UnicodeError:
            chars.append('\u%04X' % ord(char))
    return ''.join(chars)

