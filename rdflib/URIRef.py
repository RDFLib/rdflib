from sys import version_info
if version_info[0:2] > (2, 2):
    from unicodedata import normalize
else:
    normalize = None

from urlparse import urlparse, urljoin, urldefrag

from rdflib.Identifier import Identifier
from rdflib.Literal import Literal
from rdflib.compat import rsplit


class URIRef(Identifier):

    __slots__ = ()

    def __new__(cls, value, base=None):
        if base is not None:
            value = urljoin(base, value, allow_fragments=1)
        #if normalize and value and value != normalize("NFC", value):
        #    raise Error("value must be in NFC normalized form.")
        return unicode.__new__(cls,value)

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

   
