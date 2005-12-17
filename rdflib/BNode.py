# TODO: where can we move _unique_id and _serial_number_generator?
from string import ascii_letters
from random import choice

def _unique_id():
    """Create a (hopefully) unique prefix"""
    id = ""
    for i in xrange(0,8):
        id += choice(ascii_letters)
    return id 

def _serial_number_generator():
    i = 0
    while 1:
        yield i
        i = i + 1    

from rdflib.Identifier import Identifier
from rdflib.syntax.xml_names import is_ncname


class BNode(Identifier):
    """ 
    BNodes 

    "In non-persistent O-O software construction, support for object
    identity is almost accidental: in the simplest implementation,
    each object resides at a certain address, and a reference to the
    object uses that address, which serves as immutable object
    identity.

    ...

    Maintaining object identity in shared databases raises problems:
    every client that needs to create objects must obtain a unique
    identity for them; " -- Bertand Meyer
    """ 
    __slots__ = ()

    def __new__(cls, value=None, # only store implementations should pass in a value
                _sn_gen=_serial_number_generator(), _prefix=_unique_id()):
        if value==None:
            # so that BNode values do not
            # collide with ones created with a different instance of this module
            # at some other time.
            node_id = _sn_gen.next()
            value = "%s%s" % (_prefix, node_id)
        else:
            # TODO: check that value falls within acceptable bnode value range
            # for RDF/XML needs to be something that can be serialzed as a nodeID
            # for N3 ??
            # Unless we require these constraints be enforced elsewhere?
            pass #assert is_ncname(unicode(value)), "BNode identifiers must be valid NCNames"

        return Identifier.__new__(cls, value)
        
    def n3(self):
        return "_:%s" % self

    def __getnewargs__(self):
        return (unicode(self), )
        
    def __reduce__(self):
        return (BNode, (unicode(self),))


