
import unittest
from rdflib import events

class AddedEvent(events.Event): pass

class RemovedEvent(events.Event): pass

def subscribe_to(source, target):
    target.subscribe(AddedEvent, source._add_handler)
    target.subscribe(RemovedEvent, source._remove_handler)

def subscribe_all(caches):
    for cache in caches:
        for other in caches:
            if other != cache:
                subscribe_to(cache, other)

class Cache(events.Dispatcher):

    def __init__(self, data=None):
        if data is None: data = {}
        self._data = data
        self.subscribe(AddedEvent, self._add_handler)
        self.subscribe(RemovedEvent, self._remove_handler)        

    def _add_handler(self, event):
        self._data[event.key] = event.value

    def _remove_handler(self, event):
        del self._data[event.key]

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self.dispatch(AddedEvent(key=key, value=value))
        
    def __delitem__(self, key):
        self.dispatch(RemovedEvent(key=key))

    def has_key(self, key):
        return self._data.has_key(key)


class EventTestCase(unittest.TestCase):

    def testEvents(self):
        c1 = Cache()
        c2 = Cache()
        c3 = Cache()
        subscribe_all([c1,c2,c3])
        c1['bob'] = 'uncle'
        assert c2['bob'] == 'uncle'
        assert c3['bob'] == 'uncle'
        del c3['bob']
        assert c1.has_key('bob') == False
        assert c2.has_key('bob') == False

if __name__ == "__main__":
    unittest.main()
