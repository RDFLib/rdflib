from __future__ import generators

import os

from urlparse import urlparse, urljoin, urldefrag
from urllib import pathname2url, url2pathname
from threading import Lock

from xml.sax.xmlreader import InputSource

from rdflib import URIRef
from rdflib.URLInputSource import URLInputSource

from rdflib.syntax.serializer import SerializationDispatcher
from rdflib.syntax.parser import ParserDispatcher

class LoadSave(object):
    """LoadSave

    Mixed-in with a store that implements add and visit and provides
    I/O for that class. Also, needs to be mixed in with something that
    provides parse_URI and output methods.
    """
    
    def __init__(self):
        super(LoadSave, self).__init__()
        self.ns_prefix_map = {}
        self.prefix_ns_map = {}        
        self.ns_prefix_map["http://www.w3.org/1999/02/22-rdf-syntax-ns#"] = 'rdf'
        self.ns_prefix_map["http://www.w3.org/2000/01/rdf-schema#"] = 'rdfs'
        self.serialize = SerializationDispatcher(self)
        self.parse = ParserDispatcher(self)                
        self.location = None
        self.__lock = Lock()


    def prefix_mapping(self, prefix, namespace):
        map = self.ns_prefix_map    
        map[namespace] = prefix

    def load(self, location):
        if isinstance(location, InputSource):
            self.parse(location)
        else:
            cwd = urljoin("file:", pathname2url(os.getcwd()))
            location = urljoin("%s/" % cwd, location)
            location, frag = urldefrag(location)            
            scheme, netloc, path, params, query, fragment = urlparse(location)
            if netloc=="":
                path = url2pathname(path)
                # If local and it does not exist then create one.
                if not os.access(path, os.F_OK): # TODO: is this equiv to os.path.exists?
                    self.save(path)
            # TODO:
            if location[-3:]==".nt":
                #self.parse_nt_URI(location, None)
                self.parse(location, format="nt")
            else:
                source = URLInputSource(location)                    
                self.parse(source)

            if not self.location:
                self.location = location        
            

    def save(self, location=None, format="xml"):
        try:
            self.__lock.acquire()
            location = location or self.location
            if not location:
                print "WARNING: not saving as no location has been set"
                return
            scheme, netloc, path, params, query, fragment = urlparse(location)
            if netloc!="":
                print "WARNING: not saving as location is not a local file reference"
                return

            import tempfile, shutil, os
            name = tempfile.mktemp()            
            stream = open(name, 'wb')
            self.serialize(format=format, stream=stream)            
            stream.close()

            if os.path.isfile(path):
                os.remove(path)
            shutil.copy(name, path)
            os.unlink(name)

        finally:
            self.__lock.release()

