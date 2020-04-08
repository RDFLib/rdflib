from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from rdflib.namespace import RDF
from rdflib.term import BNode
from rdflib.term import Literal
from rdflib import URIRef
from pprint import pprint
from random import randint


'''Default type of container is a bag'''
class Container(object):
    

    def __init__(self, graph, uri, seq=[],typee="Bag"):
        
        self.graph = graph
        self.uri = uri or BNode()
        self._len=0
        self._type=typee# Bag or Seq or Alt

        self.append_multiple(seq)
        
        
        pred_uri='http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
        container_uri='http://www.w3.org/1999/02/22-rdf-syntax-ns#'+str(self._type)
        container = self.uri
        self.graph.add((container, URIRef(pred_uri), URIRef(container_uri)))#adding triple corresponding to container type
        

    def n3(self):
        
        items=[]
        for i in range(len(self)):
            
            v=self[i+1]
            items.append(v)
        

        return "( %s )" % (' '.join([a.n3() for a in items]))

    def _get_container(self):
        """ Returns the URI of the container"""
        container = self.uri
        
        return container

    def __len__(self):
        """number of items in container."""

        return self._len

    def type_of_conatiner(self):
        '''returns container type- bag or seq or alt'''
        return self._type

    def index(self, item):
        """
        Returns the 1-based numerical index of the item in the container

        """

        container = self.uri
        pred=self.graph.predicates(container,item)
        if not pred:
            raise ValueError("%s is not in %s" % (item,"container"))
        LI_INDEX = URIRef(str(RDF) + "_")

        for p in pred:

            i = int(p.replace(LI_INDEX, ''))
        return i
        

    def __getitem__(self, key):
        """returns item of the container at index key"""
        c = self._get_container()
        
        assert isinstance(key,int)
        elem_uri='http://www.w3.org/1999/02/22-rdf-syntax-ns#_'+str(key)
        if (key<=0) or (key>len(self)):
            raise KeyError(key)
        v = self.graph.value(c, URIRef(elem_uri))
        if v:
            return v
        else:
            raise KeyError(key)
       

    def __setitem__(self, key, value):
        """ sets the item at index key or predicate rdf:_key of the container to value"""

        assert isinstance(key,int)
        
        c = self._get_container()
        elem_uri='http://www.w3.org/1999/02/22-rdf-syntax-ns#_'+str(key)
        if key<=0 or key>len(self):
            raise KeyError(key)
        
        self.graph.set((c, URIRef(elem_uri), value))
        

    def __delitem__(self, key):

        '''removing the item with index key or predicate rdf:_key'''
        
        assert isinstance(key,int)
        if key<=0 or key>len(self):
            raise KeyError(key)
        
        graph = self.graph
        container = self.uri
        elem_uri='http://www.w3.org/1999/02/22-rdf-syntax-ns#_'+str(key)
        graph.remove((container,URIRef(elem_uri), None))
        for j in range(key+1,len(self)+1):
            elem_uri='http://www.w3.org/1999/02/22-rdf-syntax-ns#_'+str(j)
            v=graph.value(container,URIRef(elem_uri))
            graph.remove((container,URIRef(elem_uri),v))
            elem_uri='http://www.w3.org/1999/02/22-rdf-syntax-ns#_'+str(j-1)
            graph.add((container,URIRef(elem_uri),v))

        self._len-=1
        
    def items(self):
        """returns a list of all items in the container"""
        l=[]
        container = self.uri
        i=1
        while True:
            elem_uri='http://www.w3.org/1999/02/22-rdf-syntax-ns#_'+str(i)

            if(container, URIRef(elem_uri), None) in self.graph:
                i+=1
                l.append(self.graph.value(container,URIRef(elem_uri)))
            else:
                break
        return l

    '''
    '''
    def end(self):#
        # find end index (1-based) of container
        container = self.uri
        i=1
        while True:
            elem_uri='http://www.w3.org/1999/02/22-rdf-syntax-ns#_'+str(i)

            if(container, URIRef(elem_uri), None) in self.graph:
                i+=1
            else:
                return i-1
            
    def append(self, item):
        ''' adding item to the end of the container'''
        

        end = self.end()
        elem_uri='http://www.w3.org/1999/02/22-rdf-syntax-ns#_'+str(end+1)
        container = self.uri
        self.graph.add((container, URIRef(elem_uri), item))
        self._len+=1
        
        

    def append_multiple(self, other):

        '''adding multiple elements to the container to the end which are in python list other'''

        end = self.end() #it should return the last index
        
        container = self.uri
        for item in other:
            
            end+=1
            self._len+=1
            elem_uri='http://www.w3.org/1999/02/22-rdf-syntax-ns#_'+str(end)
            self.graph.add((container, URIRef(elem_uri), item))


        

    def clear(self):
        '''removing all elements from the container'''
        container = self.uri
        graph = self.graph
        i=1
        while True:
            elem_uri='http://www.w3.org/1999/02/22-rdf-syntax-ns#_'+str(i)
            if(container, URIRef(elem_uri), None) in self.graph:
                graph.remove((container, URIRef(elem_uri), None))
                i+=1
            else:
                break
        self._len=0

        

class Bag(Container):
    '''unordered container (no preference order of elements)'''
    def __init__(self, graph, uri, seq=[]):
        Container.__init__(self,graph,uri,seq,"Bag")

class Alt(Container):
    def __init__(self, graph, uri, seq=[]):
        Container.__init__(self,graph,uri,seq,"Alt")

    '''returns any one item of the Alt Container randomly, this functionality added since semantic meaning of ALt is anyone of the elements of the container'''
    def anyone(self):
        if (len(self)==0):
            raise  NoElementException()
        else:
            p=randint(1,len(self))
            item=self.__getitem__(p)
            return item

class Seq(Container):
    def __init__(self, graph, uri, seq=[]):
        Container.__init__(self,graph,uri,seq,"Seq")

    '''adds the item at position pos, valid values are 1 to len+1, this functionality added since sematic meaning of seq is that elements are arranged in decreasing order of preference'''
    '''user can add the element at the position according to the preference he wants to give to the newly added element '''
    def add_at_position(self,pos,item):
        assert isinstance(pos,int)
        if pos<=0 or pos>(len(self)+1):
            raise ValueError("Invalid Position for inserting element in rdf:seq")

        if (pos==(len(self)+1)):
            self.append(item)
        else:
            for j in range(len(self),pos-1,-1):
                container=self._get_container()
                elem_uri='http://www.w3.org/1999/02/22-rdf-syntax-ns#_'+str(j)
                v=self.graph.value(container,URIRef(elem_uri))
                self.graph.remove((container,URIRef(elem_uri),v))
                elem_uri='http://www.w3.org/1999/02/22-rdf-syntax-ns#_'+str(j+1)
                self.graph.add((container,URIRef(elem_uri),v))
            elem_uri_pos='http://www.w3.org/1999/02/22-rdf-syntax-ns#_'+str(pos)
            self.graph.add((container,URIRef(elem_uri_pos),item))
            self._len+=1








class NoElementException(Exception):
    def __init__(message="Alt Container is empty"):
        self.message=message

    def __str__(self):
        return message





if __name__ == "__main__":
    #test()

    from rdflib import Graph
    g = Graph()

    c = Bag(g, BNode())

    assert len(c) == 0

    cc = Bag(
        g, BNode(), [Literal("1"), Literal("2"), Literal("3"), Literal("4")])

    print (cc.items())

    from pprint import pprint
    pprint (cc.n3())
    assert len(cc) == 4
    cc.append(Literal("5"))
    del cc[2]
    
    assert len(cc)==4
    assert cc.index(Literal("5"))==4

    assert cc[2] == Literal("3")
    print (cc.items())
    cc[2]=Literal("9")
    assert cc[2] == Literal("9")
    from pprint import pprint
    pprint (cc.n3())
    cc.clear()
    assert len(cc)==0
    cc.append_multiple([Literal("80"),Literal("90")])
    assert cc[1] == Literal("80")
    assert cc[2] == Literal("90")
    assert len(cc)==2
    assert cc.end()==2
    cc = Alt(
        g, BNode(), [Literal("1"), Literal("2"), Literal("3"), Literal("4")])
    assert cc.anyone() in [Literal("1"), Literal("2"), Literal("3"), Literal("4")]
    cc = Seq(
        g, BNode(), [Literal("1"), Literal("2"), Literal("3"), Literal("4")])
    cc.add_at_position(3,Literal("60"))
    assert len(cc)==5
    assert cc.index(Literal("60"))==3
    assert cc.index(Literal("3"))==4
    assert cc.index(Literal("4"))==5
    print ("All tests passed")       
