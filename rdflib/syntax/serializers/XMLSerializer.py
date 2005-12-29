from __future__ import generators

from rdflib.syntax.serializers import Serializer

from rdflib.URIRef import URIRef
from rdflib.Literal import Literal
from rdflib.BNode import BNode

from rdflib.util import uniq
from rdflib.exceptions import Error
from rdflib.syntax.xml_names import split_uri

from xml.sax.saxutils import quoteattr, escape


class XMLSerializer(Serializer):

    def __init__(self, store):
        super(XMLSerializer, self).__init__(store)

    def __bindings(self):
        store = self.store
        nm = store.namespace_manager
        bindings = {}
        for predicate in uniq(store.predicates()):
            prefix, namespace, name = nm.compute_qname(predicate)
            bindings[prefix] = namespace
        RDFNS = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#")                
        if "rdf" in bindings:
            assert bindings["rdf"]==RDFNS
        else:
            bindings["rdf"] = RDFNS
        for prefix, namespace in bindings.iteritems():
            yield prefix, namespace
                
            
    def serialize(self, stream, base=None, encoding=None):
        self.base = base
        self.__stream = stream        
        self.__serialized = {}
        encoding = self.encoding
        self.write = write = lambda uni: stream.write(uni.encode(encoding, 'replace'))
        
        # startDocument
        write('<?xml version="1.0" encoding="%s"?>\n' % self.encoding)        

        # startRDF
        write('<rdf:RDF\n')
        # TODO: assert(namespaces["http://www.w3.org/1999/02/22-rdf-syntax-ns#"]=='rdf')
        bindings = list(self.__bindings())
        bindings.sort()
        for prefix, namespace in bindings:
            if prefix:
                write('   xmlns:%s="%s"\n' % (prefix, namespace))
            else:
                write('   xmlns="%s"\n' % namespace)
        write('>\n')
        
        # write out triples by subject
        for subject in self.store.subjects():
            self.subject(subject, 1)

        # endRDF
        write( "</rdf:RDF>\n" )

        # Set to None so that the memory can get garbage collected.        
        #self.__serialized = None
        del self.__serialized
        

    def subject(self, subject, depth=1):
        if not subject in self.__serialized:
            self.__serialized[subject] = 1
            write = self.write
            indent = "  " * depth
            element_name = "rdf:Description"
            if isinstance(subject, BNode):
                write( '%s<%s rdf:nodeID="%s"' %
                   (indent, element_name, subject))
            else:
                uri = quoteattr(subject)             
                write( "%s<%s rdf:about=%s" % (indent, element_name, self.relativize(uri)))
            if (subject, None, None) in self.store:
                write( ">\n" )                
                for predicate, object in self.store.predicate_objects(subject):
                    self.predicate(predicate, object, depth+1)
                write( "%s</%s>\n" % (indent, element_name))
            else:
                write( "/>\n" )            

    def predicate(self, predicate, object, depth=1):
        write = self.write
        indent = "  " * depth
        qname = self.store.namespace_manager.qname(predicate)
        if isinstance(object, Literal):
            attributes = ""
            if object.language:
                attributes += ' xml:lang="%s"'%object.language

            if object.datatype:
                attributes += ' rdf:datatype="%s"'%object.datatype
            
            write("%s<%s%s>%s</%s>\n" %
                  (indent, qname, attributes,
                   escape(object), qname) )
        else:
            if isinstance(object, BNode):
                write('%s<%s rdf:nodeID="%s"/>\n' %
                      (indent, qname, object))
            else:
                write("%s<%s rdf:resource=%s/>\n" %
                      (indent, qname, quoteattr(self.relativize(object))))

