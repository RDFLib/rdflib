# Author: Michel Pelletier

Any = None

from rdflib.store.IOMemory import IOMemory

# you must export your PYTHONPATH to point to a Z2.8 or Z3+ installation to get this to work!, like:
#export PYTHONPATH="/home/michel/dev/Zope3Trunk/src"

try:
    # Zope 3
    from persistent import Persistent
except ImportError:
    # < Zope 2.8?
    try: 
        from Persistence import Persistent
    except: 
        raise Exception("You do not appear to have Zope installed")

from BTrees.IOBTree import IOBTree
from BTrees.OIBTree import OIBTree
from BTrees.OOBTree import OOBTree

class ZODB(Persistent, IOMemory):

    def createForward(self):
        return IOBTree()

    def createReverse(self):
        return OIBTree()

    def createIndex(self):
        return IOBTree()

    def createPrefixMap(self):
        return OOBTree()
