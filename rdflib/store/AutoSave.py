from threading import RLock
from threading import Condition

class AutoSave(object):
    def __init__(self):
        super(AutoSave, self).__init__()
        self.dirtyBit = DirtyBit()
        self.auto_save_min_interval = 60*60
        
    def add(self, triple):
        self.dirtyBit.set()
        super(AutoSave, self).add(triple)

    def remove(self, triple):
        self.dirtyBit.set()
        super(AutoSave, self).remove(triple)

    def load(self, location, uri=None, create=0):
        super(AutoSave, self).load(location, uri, create)
        print "Done loading '%s'" % location
        self.dirtyBit.clear() # we just loaded... therefore we are clean
        self._start_thread() 

    def _start_thread(self):
        """Not more often then is in seconds"""
        import threading
        t = threading.Thread(target = self._autosave, args = ())
        t.setDaemon(1)
        t.start()
        
    def _autosave(self):
        while 1:
            try:
                if self.dirtyBit.value()==1:
                    self.dirtyBit.clear()
                    import sys
                    sys.stderr.write("auto saving '%s'\n" % self.location)
                    self.save(self.location, self.uri)
                    self.save("%s-%s" % (self.location, self.date_time_string()), self.uri)
                    # Do not save a backup more often than notMoreOftenThan
                    import time
                    time.sleep(self.auto_save_min_interval)
            except:
                import traceback
                traceback.print_exc()
                sys.stderr.flush()
            # do not bother to check if dirty until we get notified
            self.dirtyBit.wait()

    # TODO: move somewhere more general
    def date_time_string(self, t=None):
        """."""
        import time
        if t==None:
            t = time.time()

        year, month, day, hh, mm, ss, wd, y, z = time.gmtime(t)
        # http://www.w3.org/TR/NOTE-datetime
        s = "%0004d-%02d-%02dT%02d_%02d_%02dZ" % ( year, month, day, hh, mm, ss)        
        return s


class DirtyBit:
    def __init__(self):
        self._mon = RLock()
        self._rc = Condition(self._mon)
        self._dirty = 0
        
    def clear(self):
        self._mon.acquire()
        self._dirty = 0
        #self._rc.notify() only interested in knowing when we are dirty
        self._mon.release()

    def set(self):
        self._mon.acquire()
        self._dirty = 1
        self._rc.notify()
        self._mon.release()

    def value(self):
        return self._dirty

    def wait(self):
        self._mon.acquire()
        self._rc.wait()
        self._mon.release()





