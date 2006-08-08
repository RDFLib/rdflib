# rdflib/syntax/serializers/N3Serializer.py

from rdflib.syntax.serializers.TurtleSerializer import TurtleSerializer, SUBJECT, VERB, OBJECT

class N3Serializer(TurtleSerializer):
    short_name = "n3"

    def __init__(self, store, parent=None):
        super(N3Serializer, self).__init__(store)
        self.parent = parent


    def reset(self):
        super(N3Serializer, self).reset()
        self._stores = {}
        
    def getQName(self, uri):
        qname = None
        if self.parent is not None:
            qname = self.parent.getQName(uri)
        if qname is None:
            qname = super(N3Serializer, self).getQName(uri)
        return qname
        
    def indent(self, modifier=0):
        indent = super(N3Serializer, self).indent(modifier)
        if self.parent is not None:
            indent += self.parent.indent(modifier)
        return indent
    

    def p_clause(self, node, ignore=SUBJECT):
        if (not hasattr(self.store, 'get_clause') 
            or self.store.get_clause(node) is None):
            return False
        self.subjectDone(node)
        self.write(' {')
        self.depth += 1
        serializer = N3Serializer(self.store.get_clause(node), parent=self)
        serializer.serialize(self.stream)
        self.depth -= 1
        self.write('\n'+self.indent()+' }')

        return True

    

    def s_clause(self, subject):
        if (not hasattr(self.store, 'get_clause')
            or self.store.get_clause(subject) is None):
            return False
        self.write('\n'+self.indent())
        self.p_clause(subject, SUBJECT)
        self.predicateList(subject)
        self.write('. ')
        return True
    
    def statement(self, subject):
        self.subjectDone(subject)
        properties = self.buildPredicateHash(subject)
        if len(properties) == 0:
            return
        
        if not self.s_clause(subject):
            super(N3Serializer, self).statement(subject)
            
    def path(self, node, position):
        if not self.p_clause(node, position):
            super(N3Serializer, self).path(node, position)
            
    def startDocument(self):
        ns_list= list(self.namespaces.items())
        ns_list.sort()
                
        for prefix, uri in ns_list:
            self.write('\n'+self.indent()+'@prefix %s: <%s>.'%(prefix, uri))

        if len(ns_list) > 0:
            self.write('\n')
        #if not isinstance(self.store, N3Store):
        #    return
        
        #all_list = [self.label(var) for var in self.store.get_universals(recurse=False)]
        #all_list.sort()
        #some_list = [self.label(var) for var in self.store.get_existentials(recurse=False)]
        #some_list.sort()
        
        
        #for var in all_list:
        #    self.write('\n'+self.indent()+'@forAll %s. '%var)
        #for var in some_list:
        #    self.write('\n'+self.indent()+'@forSome %s. '%var)
        
            
        #if (len(all_list) + len(some_list)) > 0:
        #    self.write('\n')
