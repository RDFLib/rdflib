from __future__ import generators

from rdflib.Resource import Resource

class Resources(object):
    """Mix in to provide resources"""

    def __getitem__(self, subject):
        return Resource(subject, self)

    def resources(self, (subject, predicate, object)):
        d = {}
        for s, p, o in self.triples((subject, predicate, object)):
            if not s in d:
                d[s] = r = Resource(s, self)
                for subject in r.subjects:
                    d[subject] = r                        
        for item in d.itervalues():
            yield item
