class PropertyValue(object):
    def __init__(self,property,objects):
        self.property = property
        self.objects = objects
        #print 
    def __repr__(self):
        return "%s(%s)"%(self.property,self.objects)
    
class ParsedConstrainedTriples(object):
    """
    A list of Resources associated with a constraint
    """
    def __init__(self,triples,constraint):
        self.triples = triples
        self.constraint = constraint
        
    def __repr__(self):
        return "%s%s"%(self.triples,self.constraint and ' %s'%self.constraint or '')