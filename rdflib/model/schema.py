# label and comment methods have been moved to Store and Store no
# longer subclasses from Schema. If anyone is using some of these
# methods they should be able to add this class as a mix-in to there
# Store. Let me know if you are using any these methods... and I'll
# add them back... else they'll go away.

from __future__ import generators

from rdflib.constants import TYPE
from rdflib.constants import STATEMENT, SUBJECT, PREDICATE, OBJECT
from rdflib.constants import RDFS_DOMAIN, RDFS_SUBCLASSOF

class Schema(object):

    def typeless_resources(self):
        for subject in self.subjects():
            if not (subject, TYPE, None) in self:
                yield subject

    # TODO: should we have a version of this that answers for subclasses too?
    def is_of_type(self, subject, type):
        return (subject, TYPE, type) in self

    def subjects_by_type(self, type, predicate, object):
        for subject in self.subjects(predicate, object):
            if self.is_of_type(subject, type):
                yield subject

    def possible_properties(self, type):
        for object in self.transitive_objects(type, RDFS_SUBCLASSOF):
            for subject in self.subjects(RDFS_DOMAIN, object):
                yield subject
        
    def possible_properties_for_subject(self, subject):
        for type in self.objects(subject, TYPE):
            for property in self.possible_properties(type):
                yield property

    def get_statement_uri(self, (subject, predicate, object)):
        """\
        Returns the first statement uri for the given subject, predicate, object.
        """
        for (s, p, o) in self.triples((None, TYPE, STATEMENT)):
            if (s, SUBJECT, subject) in self\
            and (s, PREDICATE, predicate) in self\
            and (s, OBJECT, object) in self:
                return s
        return None

