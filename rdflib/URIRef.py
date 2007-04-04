from sys import version_info

try:
    from hashlib import md5
except ImportError:
    from md5 import md5    

if version_info[0:2] > (2, 2):
    from unicodedata import normalize
else:
    normalize = None

from urlparse import urlparse, urljoin, urldefrag

from rdflib.Identifier import Identifier
from rdflib.compat import rsplit


class URIRef(Identifier):
    """
    RDF URI Reference: http://www.w3.org/TR/rdf-concepts/#section-Graph-URIref
    """

    __slots__ = ()

    def __new__(cls, value, base=None):
        if base is not None:
            ends_in_hash = value.endswith("#")
            value = urljoin(base, value, allow_fragments=1)
            if ends_in_hash:
                if not value.endswith("#"):
                    value += "#"
        #if normalize and value and value != normalize("NFC", value):
        #    raise Error("value must be in NFC normalized form.")
        try:
            rt = unicode.__new__(cls,value)
        except UnicodeDecodeError:
            rt = unicode.__new__(cls,value,'utf-8')
        return rt

    def n3(self):
        return "<%s>" % self

    def concrete(self):
        if "#" in self:
            return URIRef("/".join(rsplit(self, "#", 1)))
        else:
            return self

    def abstract(self):
        if "#" not in self:
            scheme, netloc, path, params, query, fragment = urlparse(self)
            if path:
                return URIRef("#".join(rsplit(self, "/", 1)))
            else:
                if not self.endswith("#"):
                    return URIRef("%s#" % self)
                else:
                    return self
        else:
            return self


    def defrag(self):
        if "#" in self:
            url, frag = urldefrag(self)
            return URIRef(url)
        else:
            return self

    def __reduce__(self):
        return (URIRef, (unicode(self),))

    def __getnewargs__(self):
        return (unicode(self), )


    def __eq__(self, other):
        if isinstance(other, URIRef):
            return unicode(self)==unicode(other)
        else:
            return False

    def __str__(self):
        return self.encode("unicode-escape")

    def __repr__(self):
        return """rdflib.URIRef('%s')""" % str(self)

    def md5_term_hash(self):
        d = md5(str(self))
        d.update("U")
        return d.hexdigest()
