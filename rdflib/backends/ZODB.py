# Author: Michel Pelletier

Any = None

from rdflib.backends.IOMemory import IOMemory
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
