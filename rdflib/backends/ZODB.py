# Author: Michel Pelletier

Any = None

from rdflib.backends.IOMemory import IOMemory

# you must export your PYTHONPATH to point to a Z3 installation to get this to work!, like:
# export PYTHONPATH="export PYTHONPATH="/home/michel/dev/Zope3Trunk/src"
from persistent import Persistent

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
