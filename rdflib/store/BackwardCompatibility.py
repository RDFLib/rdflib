from __future__ import generators

class BackwardCompatibility(object):

    def add(self, triple_or_subject, p=None, o=None):
        # RedNode uses the second argument to specify context. So, we
        # will assume that any call to add with an o==None is old an
        # *not* an old style call.
        #if p==None and o==None:
        if o==None:            
            triple = triple_or_subject
        else:
            triple = (triple_or_subject, p, o)
        super(BackwardCompatibility, self).add(triple)            

    def remove(self, triple_or_subject, p=None, o=None):
        if o==None:            
            triple = triple_or_subject
        else:
            triple = (triple_or_subject, p, o)
        super(BackwardCompatibility, self).remove(triple)            

    def triples(self, triple_or_subject, p=None, o=None):
        if o==None:            
            triple = triple_or_subject
        else:
            triple = (triple_or_subject, p, o)
        for t in super(BackwardCompatibility, self).triples(triple):
            yield t
    
    def remove_triples(self, triple_or_subject, p=None, o=None):
        if o==None:            
            triple = triple_or_subject
        else:
            triple = (triple_or_subject, p, o)
        super(BackwardCompatibility, self).remove_triples(triple)            

    def load(self, location, uri=None, create=0):
        if uri!=None:
            print "WARNING: Load's uri argument has been deprecated."
        if create!=0:
            print \
"WARNING: Load's create argument has been deprecated and is no longer \
necessary."
        super(BackwardCompatibility, self).load(location)

    def exists(self, subject, predicate, object):
        return (subject, predicate, object) in self
        
    def output(self, stream):
        self.serialize(write=stream.write)
