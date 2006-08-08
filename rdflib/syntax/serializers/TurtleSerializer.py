
import urlparse, re
from xml.sax.saxutils import escape, quoteattr

from rdflib.BNode import BNode
from rdflib.Literal import Literal
from rdflib.URIRef import URIRef
from rdflib.syntax.xml_names import split_uri 

from rdflib.syntax.serializers.RecursiveSerializer import RecursiveSerializer
from rdflib.exceptions import Error
from rdflib.constants import RDFNS, RDFSNS, TYPE, FIRST, REST, NIL

#TODO: move
XSD_INTEGER=URIRef('http://www.w3.org/2001/XMLSchema#integer')

SUBJECT = 0
VERB = 1
OBJECT = 2

class TurtleSerializer(RecursiveSerializer):

    short_name="turtle"
    indentString = "    "
    def __init__(self, store):
        super(TurtleSerializer, self).__init__(store)
        self.reset()
        self.stream = None

    def reset(self):
        super(TurtleSerializer, self).reset()
        self._shortNames = {}
        self._started = False
    
    def isValidLocalName(self,name):
        if re.search("[^_A-Za-z0-9]",name): 
            return False
        return True
    
    def getQName(self, uri):
        if not isinstance(uri, URIRef):
            return None
        assert(not uri.startswith('_:'))

        if uri in self._shortNames:
            return self._shortNames[uri]
        
        scheme = urlparse.urlparse(uri)[0]
        if scheme in urlparse.non_hierarchical:
            return None

        if uri.startswith(u"urn"):
            return None
         
        try: 
            split = self.store.compute_qname(uri)
        except: 
            return None
            
        if split is None:
            return None
            
        prefix, base, local = split
        
        if base=='http://':
            return None
        if base.endswith("~"):
            # this is not illegal, but it's ugly
            return None
            
        if not self.isValidLocalName(local):
            return None

        if base==self.base: 
            prefix=""
        
        qname = prefix +':' + local

        if prefix in self.namespaces and self.namespaces[prefix] != base:
            raise Error("Store returned the same prefix for two different uris")
        if self._started and prefix not in self.namespaces:
            return None
        
        if prefix: 
            self.addNamespace(prefix, base)
        self._shortNames[uri] = qname
        return qname

    def preprocessTriple(self, triple):
        super(TurtleSerializer, self).preprocessTriple(triple)
        for node in triple:
            self.getQName(node)
        p = triple[1]
        if isinstance(p, BNode):
            self._references[p] = self.refCount(p) +1
            
    def label(self, node):
        qname = self.getQName(node)
        if qname is None:
            return node.n3()
        return qname

    def startDocument(self):
        self._started = True
        ns_list= list(self.namespaces.items())
        ns_list.sort()
        if len(ns_list) == 0:
            return
        
        for prefix, uri in ns_list:
            self.write('\n'+self.indent()+'@prefix %s: %s.'%(prefix, uri.n3()))
        self.write('\n')

    def endDocument(self):
        pass

    def isValidList(self,l): 
        """Checks if l is a valid RDF list, i.e. no nodes have other properties."""
        try:
            if not self.store.value(l, FIRST):
                return False
        except: 
            return False
        while l:
            if l!=NIL and len(list(self.store.predicate_objects(l)))!=2: return False
            l = self.store.value(l, REST)
        return True
        
    def doList(self,l):
        while l:
            item = self.store.value(l, FIRST)
            if item:
                self.path(item, SUBJECT)
                self.subjectDone(l)
            l = self.store.value(l, REST)
            
    def p_squared(self, node, position):
        if (not isinstance(node, BNode)
            or node in self._serialized
            or self.refCount(node) > 1
            or position == SUBJECT):
            return False
       
        if self.isValidList(node): 
            # this is a list
            self.write(' (')
            self.depth+=2
            self.doList(node)
            self.depth-=2            
            self.write(' )')
            return True
        
        self.subjectDone(node)
        self.write(' [')
        self.depth += 2
        self.predicateList(node)
        self.depth -= 2
        self.write(']')
        return True

    def p_default(self, node, ignore):
        self.write(" "+self.label(node))
        return True
    
    def path(self, node, position):
        if not (self.p_squared(node, position)
                or self.p_default(node, position)):
            raise Error("Cannot serialize node '%s'"%(node, ))

    def verb(self, node):
        if node == TYPE:
            self.write(' a')
        else:
            self.path(node, VERB)
    
    def objectList(self, objects):
        if len(objects) == 0:
            return

        self.path(objects[0], OBJECT)
        for obj in objects[1:]:
            self.write(',\n'+self.indent(2))
            self.path(obj, OBJECT)

    def predicateList(self, subject):
        properties = self.buildPredicateHash(subject)
        propList = self.sortProperties(properties)
        if len(propList) == 0:
            return

        self.verb(propList[0])
        self.objectList(properties[propList[0]])
        for predicate in propList[1:]:
            self.write(';\n'+self.indent(1))
            self.verb(predicate)
            self.objectList(properties[predicate])

    def s_squared(self, subject):
        if (self.refCount(subject) > 0) or not isinstance(subject, BNode):
            return False
        self.write('\n'+self.indent()+" [")
        self.depth+=1
        self.predicateList(subject)
        self.depth-=1
        self.write('].')
        return True

    def s_default(self, subject):
        self.write('\n'+self.indent())
        self.path(subject, SUBJECT)
        self.predicateList(subject)
        self.write('. ')
        return True
    
    def statement(self, subject):
        self.subjectDone(subject)
        if not self.s_squared(subject):
            self.s_default(subject)
            

    def serialize(self, stream, base=None, encoding=None):
        self.reset()
        self.stream = stream
        self.base=base
        
        # In newer rdflibs these are always in the namespace manager
        #self.store.prefix_mapping('rdf', RDFNS)
        #self.store.prefix_mapping('rdfs', RDFSNS)
        
        self.preprocess()
        subjects_list = self.orderSubjects()

        self.startDocument()

        firstTime = True
        for subject in subjects_list:
            if not self.isDone(subject):
                if firstTime:
                    firstTime = False
                else:
                    self.write('\n')
                self.statement(subject)
        
        self.endDocument()
