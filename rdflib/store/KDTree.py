from __future__ import generators
import sys

class KDNode(object):
    def __init__(self, key, data):
        super(KDNode, self).__init__()

        self.key = key
        self.data = data
        self.left = None
        self.right = None

    def isLeaf(self):
        if self.right != None or self.left != None:
            return 0
        return 1
    
    def matches(self, key):
        for i in range(len(key)):
            if (key[i] != None) and ( key[i] != self.key[i]):
                return 0
        return 1
    
class KDTree(object):
    """\
An in memory implementation of a KD Tree
"""
    def __init__(self, d):
        super(KDTree, self).__init__()
        self.debug = 0
        self.__d = d
        self.__root = None
        self.count = 0

    def setDebug(self, debug):
        self.debug = debug

    def insert(self, key, data):
        if (len(key) != self.__d):
            raise Exception("Wrong keysize inserted into KDTree (Got %d, expected %d)"%(len(key), self.__d))

        tnode = KDNode(key, data)


        if (self.__root == None):
            self.__root = tnode
        else:
            (height, parent) = self.__parentsearch(key)
            if parent == None:
                return
            d = height%self.__d
            if (key[d] < parent.key[d]):
                parent.left = tnode
            else:
                parent.right = tnode

        self.count = self.count + 1
        if (self.debug) and (self.count%1000 == 0):
            print self.count
                

    def __parentsearch(self, key):

        height = 0;

        curr = self.__root

        while (curr != None):

            returnNode = curr
            i = height % self.__d

            if (key[i] == curr.key[i]):
                if (curr.matches(key)):
                    return (-1, None)
                else:
                    curr = curr.right
            elif key[i] < curr.key[i]:
            #if key[i] < curr.key[i]:
                curr = curr.left
            else:
                curr = curr.right

            height = height + 1
            
        
        return (height - 1, returnNode)

    def __parentNode(self, node):
        if node == self.__root:
            return None
        key = node.key
        curr = self.__root
        height = 0

        while (curr != None):
            i = height % self.__d
            if key[i] < curr.key[i]:
                if curr.left == node:
                    return curr
                curr = curr.left
            else:
                if curr.right == node:
                    return curr
                curr = curr.right
            height += 1

        raise Exception("Could not find parent in tree!")
    
    def __leastKey(self, (level, node)):
        stack = [(level, node)]
        leastNode = node
        disc = level % self.__d
        while len(stack) > 0:
            (height, curr) = stack.pop()
            d = height % self.__d

            if curr.key[disc] < leastNode.key[disc]:
                leastNode = curr

            if d == disc:
                if (curr.left != None):
                    stack.append((height + 1, curr.left))
            else:
                if (curr.left != None):
                    stack.append((height + 1, curr.left))
                if (curr.right != None):
                    stack.append((height + 1, curr.right))
        
        return (height, leastNode)
        
        
        
    def search(self, key):
        for (height, node) in self.__search(key):
            yield node
            
        

    def __search(self, key):
        if self.__root == None:
            return
        
        stack = [(0, self.__root)]

        while len(stack) > 0:
            (height, curr) = stack.pop()
            d = height % self.__d

            if curr.matches(key):
                yield (height, curr)
                
            if key[d] == None:
                if curr.right != None:
                    stack.append((height + 1, curr.right))
                if curr.left != None:
                    stack.append((height + 1, curr.left))
            elif key[d] < curr.key[d]:
                if curr.left != None:
                    stack.append((height + 1, curr.left))
            else:
                if curr.right != None:
                    stack.append((height + 1, curr.right))

    
    def __delete(self, (height, node)):
        if node.isLeaf():
            return None
        d = height % self.__d

        # Special case if node.right is empty
        if node.right == None:
            (rheight, r) =  self.__leastKey((height + 1, node.left))
        else:
            (rheight, r) =  self.__leastKey((height + 1, node.right))
        
        f = self.__parentNode(r)
        if (r == f.right):
            f.right = self.__delete((rheight, r))
        else:
            f.left = self.__delete((rheight, r))

        r.left = node.left
        r.right = node.right

        return r
    
    def delete(self, key):
        try:
            while(1):
                iter = self.__search(key)
                (height, node) = iter.next()

                #print "Deleting %s"%((height, node.key),)
                
                n = self.__delete((height, node))
                f = self.__parentNode(node)
                
                if f == None:
                    self.__root = n
                else:
                    if (node == f.right):
                        f.right = n
                    else:
                        f.left = n
                #self.printTree()
        except StopIteration, e:
            pass
            
                
        

    def printnode(self, (height, node), prefix):
    
        if node != None:
            print "%s%s%s"%(" "*height, prefix, node.key)
            self.printnode((height + 1, node.left), "L:")
            self.printnode((height + 1, node.right), "R:")
        else:
            #print "None"
            pass
    def printTree(self):
        print "Printing tree:"
        self.printnode((0, self.__root), "T:")
        
        

if __name__ == "__main__":
    kdt = KDTree(3)

    kdt.insert((0,1,1), None)
    kdt.printTree()
    print "--"
    kdt.insert((1,2,3), None)
    kdt.printTree()
    print "--"
    kdt.insert((2,1,1), None)
    
    kdt.insert((2,1,1), None)
    kdt.insert((0,0,0), None)
    kdt.insert((-1,-1,-1), None)
    kdt.printTree()
    print "--"
    print "Searching for all"
    for i in kdt.search((None,None,None)):
        print i.key

    print "--"
    print "Searching for (None, 1, None)"
    for i in kdt.search((None,1,None)):
        print i.key

    print "--"
    print "Searching for (2,1,1)"
    for i in kdt.search((2,1,1)):
        print i.key
        
    print "--"
    print "Deleting (2,1,1)"
    kdt.delete((2,1,1))
    kdt.printTree()

    print "--"
    print "Deleting (0,1,1)"
    kdt.delete((0,1,1))
    kdt.printTree()

    print "--"
    print "Deleting (None, None, None)"
    kdt.delete((None,None,None))
    kdt.printTree()
