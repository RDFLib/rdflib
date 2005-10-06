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


class BNode(Identifier):
    __slots__ = ()
    def __new__(cls, value=None, # only store implementations should pass in a value
		_sn_gen=_serial_number_generator(), _prefix=_unique_id()):
        if value==None:
	    # so that BNode values do not
	    # collide with ones created with a different instance of this module
	    # at some other time.
            node_id = _sn_gen.next()
            value = "%s%s" % (_prefix, node_id)
        return Identifier.__new__(cls, value)
        
    def n3(self):
        return "_:%s" % self
