from __future__ import generators
import random, time
from KDTree import KDTree

ANY = None
random.seed(time.time())

class KDTreeStore(object):
    """\
An in memory kd-tree implementation of a triple store.

This triple store uses a kd-tree to store the keys, with the data
pointer being nil (reserved marking deleted items (bah, must read
Samet on how to delete properly))
"""

    def __init__(self):
        super(KDTreeStore, self).__init__()
        self.__kdt = KDTree(3)
        self.debug = 0
        self.__table = []
        self.__rtable = []
        for i in range(3):
            self.__table.append( {})
            self.__rtable.append({})

    def __convertNode(self, node, pos):
        if node == None:
            return None
        try:
            a = self.__table[pos][node]            
        except:
            a = random.randint(-2000000,2000000)
            while (self.__rtable[pos].has_key(a)):
                a = random.randint(-2000000,2000000)
            self.__table[pos][node] = a
            self.__rtable[pos][a] = node
            
        return a

    def __convertTuple(self, tuple):
        a = self.__convertNode( tuple[0], 0)
        b = self.__convertNode( tuple[1], 1)
        c = self.__convertNode( tuple[2], 2)

        return (a,b,c)

    def __revertTuple(self, tuple):
        a = self.__rtable[0][tuple[0]]
        b = self.__rtable[1][tuple[1]]
        c = self.__rtable[2][tuple[2]]
        return (a,b,c)

    def add(self, tuple):
        ntuple = self.__convertTuple(tuple)
        self.__kdt.insert(ntuple, None)
        #self.__kdt.insert(tuple, None)

    def remove(self, tuple):
        ntuple = self.__convertTuple(tuple)
        self.__kdt.delete(ntuple)
        #self.__kdt.delete(tuple)

    def triples(self, tuple):
        tuple[0]
        self.__table[0]
        if not (((tuple[0] == None) or (self.__table[0].has_key(tuple[0]))) and
                ((tuple[1] == None) or (self.__table[1].has_key(tuple[1]))) and
                ((tuple[2] == None) or (self.__table[2].has_key(tuple[2])))):
            return
            
            
        ntuple = self.__convertTuple(tuple)
        for i in self.__kdt.search(tuple):
            yield self.__revertTuple(i.key)
        #for i in self.__kdt.search(tuple):
        #    yield i.key
    def setDebug(self, debug):
        self.debug = debug
        self.__kdt.setDebug(debug)
        

    
