import tempfile, shutil, os
from threading import Lock
from urlparse import urlparse

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class Serializer(object):

    def __init__(self, serializer):
        self.serializer = serializer
        self.__save_lock = Lock()

    def _get_store(self):
        return self.serializer.store

    def _set_store(self, store):
        self.serializer.store = store

    store = property(_get_store, _set_store)

    def serialize(self, destination=None, format="xml", base=None, encoding=None):
        if destination is None:
            stream = StringIO()
            self.serializer.serialize(stream, base=base, encoding=encoding)
            return stream.getvalue()
        if hasattr(destination, "write"):
            stream = destination
            self.serializer.serialize(stream, base=base, encoding=encoding)
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
                self.serializer.serialize(stream, base=base, encoding=encoding)
                stream.close()
                if hasattr(shutil,"move"):
                    shutil.move(name, path)
                else:
                    shutil.copy(name, path)
                    os.remove(name)
            finally:
                self.__save_lock.release()
