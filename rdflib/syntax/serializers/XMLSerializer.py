from __future__ import generators

from xml.sax.saxutils import quoteattr, escape

from rdflib.URIRef import URIRef
from rdflib.Literal import Literal
from rdflib.BNode import BNode

from rdflib.exceptions import Error
from rdflib.syntax.serializer import AbstractSerializer

NAMESTART = u'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_'
NAMECHARS = NAMESTART + u'0123456789-.'

def unique(sequence):
    seen = {}
    for item in sequence:
        if not item in seen:
            seen[item] = 1
            yield item
    
def split_predicate(predicate):
    predicate = predicate
    length = len(predicate)
    for i in xrange(0, length):
        if not predicate[-i-1] in NAMECHARS:
            for j in xrange(-1-i, length):
                if predicate[j] in NAMESTART:
                    ns = predicate[:j]
                    if not ns:
                        break
                    qn = predicate[j:]
                    return (ns, qn)
            break
    raise Error("This graph cannot be serialized in RDF/XML. Could not split predicate: '%s'" % predicate)


class XMLSerializer(AbstractSerializer):

    short_name = "xml"

    def __init__(self, store):
        super(XMLSerializer, self).__init__(store)

    def __update_prefix_map(self):
        self.namespaceCount = len(self.store.ns_prefix_map)
        ns_prefix_map = self.store.ns_prefix_map
        for predicate in unique(self.store.predicates()): 
            uri, localName = split_predicate(predicate)            
            if not uri in ns_prefix_map:
                self.namespaceCount += 1
                prefix = "n%s" % self.namespaceCount
                assert prefix not in ns_prefix_map
                ns_prefix_map[uri] = prefix
            else:
                prefix = ns_prefix_map[uri]
            self.__predicate_names_map[predicate] = uri, localName, prefix
            
    def serialize(self, stream):
        self.__stream = stream        
        self.__serialized = {}
        self.__predicate_names_map = {}        
        self.__update_prefix_map()
        encoding = self.encoding
        self.write = write = lambda uni: stream.write(uni.encode(encoding, 'replace'))
        
        # startDocument
        write('<?xml version="1.0" encoding="%s"?>\n' % self.encoding)        

        # startRDF
        namespaces = self.store.ns_prefix_map
        write('<rdf:RDF\n')
        assert(namespaces["http://www.w3.org/1999/02/22-rdf-syntax-ns#"]=='rdf')
        for (namespace, prefix) in namespaces.iteritems():
            write('   xmlns:%s="%s"\n' % (prefix, namespace))
        write('>\n')
        
        # write out triples by subject
        for subject in self.store.subjects():
            self.subject(subject, 1)

        # endRDF
        write( "</rdf:RDF>\n" )

        # Set to None so that the memory can get garbage collected.        
        #self.__serialized = None
        del self.__serialized
        del self.__predicate_names_map
        

    def subject(self, subject, depth=1):
        if not subject in self.__serialized:
            self.__serialized[subject] = 1
            write = self.write
            indent = "  " * depth
            element_name = "rdf:Description"
            if isinstance(subject, BNode):
                write( '%s<%s rdf:nodeID="%s"' %
                   (indent, element_name, subject[2:]))
            else:
                uri = quoteattr(subject)             
                write( "%s<%s rdf:about=%s" % (indent, element_name, uri))
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
        namespace, localName, prefix = self.__predicate_names_map[predicate]
        if isinstance(object, Literal):
            attributes = ""
            if object.language:
                attributes += ' xml:lang="%s"'%object.language

            if object.datatype:
                attributes += ' rdf:datatype="%s"'%object.datatype
            
            write("%s<%s:%s%s>%s</%s:%s>\n" %
                  (indent, prefix, localName, attributes,
                   escape(object), prefix, localName) )
        else:
            if isinstance(object, BNode):
                write('%s<%s:%s rdf:nodeID="%s"/>\n' %
                      (indent, prefix, localName, object[2:]))
            else:
                write("%s<%s:%s rdf:resource=%s/>\n" %
                      (indent, prefix, localName, quoteattr(object)))

