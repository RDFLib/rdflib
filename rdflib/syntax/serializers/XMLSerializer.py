from xml.sax.saxutils import quoteattr, escape

from rdflib.URIRef import URIRef
from rdflib.Literal import Literal
from rdflib.BNode import BNode
from rdflib.constants import TYPE
from rdflib.util import first, uniq, more_than
from rdflib.exceptions import Error
from rdflib.syntax.serializer import AbstractSerializer

NAMESTART = u'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_'
NAMECHARS = NAMESTART + u'0123456789-.'

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
        self.__predicate_names_map = {}
        self.__serialized = {}        
        
    def update_prefix_map(self):
        self.namespaceCount = len(self.store.ns_prefix_map)        
        possible = uniq(self.store.predicates()) + uniq(self.store.objects(None, TYPE))
        for predicate in possible:
            uri, localName = split_predicate(predicate)            
            if not uri in self.store.ns_prefix_map:
                self.namespaceCount += 1
                prefix = "n%s" % self.namespaceCount
                self.store.ns_prefix_map[uri] = prefix
            else:
                prefix = self.store.ns_prefix_map[uri]
                
            self.__predicate_names_map[predicate] = uri, localName, prefix
            
    def _output(self, stream):
        self.__serialized = {}
        self._stream = stream
        self.update_prefix_map()
        # startDocument
        self.write('<?xml version="1.0" encoding="%s"?>\n' % self.encoding)        

        # startRDF
        #namespaces = self.__namespace_prefix_map
        namespaces = self.store.ns_prefix_map
        write = self.write
        write('<rdf:RDF\n')
        assert(namespaces["http://www.w3.org/1999/02/22-rdf-syntax-ns#"]=='rdf')
        for (namespace, prefix) in namespaces.iteritems():
            self.write('   xmlns:%s="%s"\n' % (prefix, namespace))
        write('>\n')
        
        # Write out subjects that can not be inline
        for subject in self.store.subjects():
            if (None, None, subject) in self.store:
                if (subject, None, subject) in self.store:
                    self.subject(subject, 1)
            else:
                self.subject(subject, 1)
        
        # write out anything that has not yet been reached
        for subject in self.store.subjects():
            self.subject(subject, 1)

        # endRDF
        self.write( "</rdf:RDF>\n" )

        # Set to None so that the memory can get garbage collected.        
        self.__serialized = None 


    def subject(self, subject, depth=1):
        if not subject in self.__serialized:
            self.__serialized[subject] = 1
            write = self.write
            indent = "  " * depth
            type = first(self.store.objects(subject, TYPE))
            if type:
                namespace, localName, prefix = self.__predicate_names_map[type]
                element_name = "%s:%s" % (prefix, localName)
            else:
                element_name = "rdf:Description"
            if isinstance(subject, BNode):
                if more_than(self.store.triples((None, None, subject)), 2):
                    write( '%s<%s rdf:nodeID="%s"' %
                       (indent, element_name, subject))
                else:
                    write( '%s<%s' %
                       (indent, element_name))
            else:
                uri = quoteattr(subject)             
                write( "%s<%s rdf:about=%s" % (indent, element_name, uri))
            if (subject, None, None) in self.store:
                write( ">\n" )                
                for predicate, object in self.store.predicate_objects(subject):
                    if not (predicate==TYPE and object==type):
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
        elif object in self.__serialized or not (object, None, None) in self.store:
            if isinstance(object, BNode):
                
                if more_than(self.store.triples((None, None, object)), 2):
                    write('%s<%s:%s rdf:nodeID="%s"/>\n' %
                          (indent, prefix, localName, object))
                else:
                    write('%s<%s:%s/>\n' %
                          (indent, prefix, localName))
            else:
                write("%s<%s:%s rdf:resource=%s/>\n" %
                      (indent, prefix, localName, quoteattr(object)))
        else:
            write("%s<%s:%s>\n" % (indent, prefix, localName))
            self.subject(object, depth+1)
            write("%s</%s:%s>\n" % (indent, prefix, localName))
