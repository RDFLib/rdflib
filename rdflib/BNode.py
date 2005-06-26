from string import ascii_letters
from random import choice

from rdflib.Identifier import Identifier
from rdflib.Literal import Literal

# Create a (hopefully) unique prefix so that BNode values do not
# collide with ones created with a different instance of this module.
prefix = ""
for i in xrange(0,8):
    prefix += choice(ascii_letters)

node_id = 0
class BNode(Identifier):
    __slots__ = ()
    def __new__(cls, value=None):
        if value==None:
            global node_id
            node_id += 1
            value = "_%s%s" % (prefix, node_id)
        else:
            if not value.startswith("_"):
                value = "".join(("_", value))
        return Identifier.__new__(cls, value)
        
    def n3(self):
        if not self.startswith("_:"):
	    if self.startswith("_"):
		return "_:%s" % self[1:]
	    else:
		return "_:%s"
        return str(self)


