##############

from cPickle import Pickler, Unpickler, UnpicklingError
from cStringIO import StringIO


class NodePickler(object):
    def __init__(self):
        self._objects = {}
        self._get_object = self._objects.__getitem__
        self._ids = {}
        self._get_id = self._ids.get

    def get_ids(self, key):
        try:
            return self._ids.get(key)
        except TypeError, e:
            return None

    def register(self, object, id):
        self._objects[id] = object
        self._ids[object] = id

    def loads(self, s):
        up = Unpickler(StringIO(s))
        up.persistent_load = self._get_object
        try:
            return up.load()
        except KeyError, e:
            raise UnpicklingError, "Could not find Node class for %s" % e

    def dumps(self, obj, protocol=None, bin=None):
        src = StringIO()
        p = Pickler(src)
        p.persistent_id = self.get_ids
        p.dump(obj)
        return src.getvalue()

