from rdflib.exceptions import SerializerDispatchNameError, SerializerDispatchNameClashError

from rdflib import plugin

import tempfile, shutil, os
from threading import Lock
from urlparse import urlparse

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class AbstractSerializer(object):

    def __init__(self, store):
        self.store = store
        self.encoding = "UTF-8"
        
    def serialize(self, stream):
        """Abstract method"""


class SerializationDispatcher(object):

    def __init__(self, store):
        self.store = store
        self.__serializer = {}
        self.__save_lock = Lock()
        
    def serializer(self, format):
        serializer = self.__serializer.get(format, None)
        if serializer is None:
            serializer = plugin.get(format, 'serializer')(self.store)
            self.__serializer[format] = serializer
        return serializer

    def serialize(self, destination=None, format="xml"):
        if destination is None:
            stream = StringIO()
            self.serializer(format).serialize(stream)
            return stream.getvalue()
        if hasattr(destination, "write"):
            stream = destination
            self.serializer(format).serialize(stream)            
        else:
            location = destination
            try:
                self.__save_lock.acquire()
                scheme, netloc, path, params, query, fragment = urlparse(location)
                if netloc!="":
                    print "WARNING: not saving as location is not a local file reference"
                    return
                name = tempfile.mktemp()            
                stream = open(name, 'wb')
                self.serializer(format).serialize(stream)
                stream.close()
                if hasattr(shutil,"move"):
                    shutil.move(name, path)
                else:
                    shutil.copy(name, path)
                    os.remove(name)
            finally:
                self.__save_lock.release()
