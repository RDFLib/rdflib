from rdflib.store import Store

from rdflib.util import from_bits
from rdflib import BNode

from bsddb import db
from base64 import b64encode
from base64 import b64decode
from os import mkdir
from os.path import exists


def readable_index(i):
    s, p, o = "?" * 3
    if i & 1: s = "s"
    if i & 2: p = "p"
    if i & 4: o = "o"
    return "%s,%s,%s" % (s, p, o)

def get_key_func(i):
    def get_key(triple, context):
        yield context
        yield triple[i%3]
        yield triple[(i+1)%3]
        yield triple[(i+2)%3]
    return get_key



# TODO: tool to convert old Sleepycat DBs to this version.

class Sleepycat(Store):
    context_aware = True

    def __init__(self, configuration=None):
        self.__open = False
        super(Sleepycat, self).__init__(configuration)
        
        
    def open(self, path, create=True):
        homeDir = path        
        envsetflags  = db.DB_CDB_ALLDB
        envflags = db.DB_INIT_MPOOL | db.DB_INIT_CDB | db.DB_THREAD
        try:
            if not exists(homeDir):
                mkdir(homeDir)
        except Exception, e:
            print e
        self.env = env = db.DBEnv()
        env.set_cachesize(0, 1024*1024*5) # TODO
        #env.set_lg_max(1024*1024)
        env.set_flags(envsetflags, 1)
        env.open(homeDir, envflags | db.DB_CREATE)

        self.__open = True
        
        dbname = None
        dbtype = db.DB_BTREE
        dbopenflags = db.DB_THREAD
        
        dbmode = 0660
        dbsetflags   = 0

        # create and open the DBs
        self.__indicies = [None,] * 3
        for i in xrange(0, 3):
            index_name = "".join(get_key_func(i)(("s", "p", "o"), "c"))
            index = db.DB(env)
            index.set_flags(dbsetflags)
            index.open(index_name, dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)
            self.__indicies[i] = index

        lookup = {}
        for i in xrange(0, 8):
            results = []
            for start in xrange(0, 3):
                score = 1
                len = 0
                for j in xrange(start, start+3):
                    if i & (1<<(j%3)):
                        score = score << 1
                        len += 1
                    else:
                        break
                tie_break = 2-start
                results.append(((score, tie_break), start, len))

            results.sort()
            score, start, len = results[-1]

            def get_prefix_func(start, end):
                def get_prefix(triple, context):
                    if context is None:
                        yield ""
                    else:
                        yield context
                    i = start 
                    while i<end:
                        yield triple[i%3]
                        i += 1
                    yield ""
                return get_prefix

            lookup[i] = (start, get_prefix_func(start, start + len))


        self.__lookup_dict = lookup

        self.__contexts = db.DB(env)
        self.__contexts.set_flags(dbsetflags)
        self.__contexts.open("contexts", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        self.__namespace = db.DB(env)
        self.__namespace.set_flags(dbsetflags)
        self.__namespace.open("namespace", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        self.__prefix = db.DB(env)
        self.__prefix.set_flags(dbsetflags)
        self.__prefix.open("prefix", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)
        
        self.__pending_sync = None
	self.__syncing = False

    def _schedule_sync(self):
        from threading import Timer
        if self.__open and self.__pending_sync is None:
            t = Timer(60.0, self.sync)
            self.__pending_sync = t
            t.setDaemon(True)
            t.start()
    
    def sync(self):
        if self.__open:
	    self.__syncing = True

            for i in xrange(0, 3):
                self.__indicies[i].sync()

            self.__contexts.sync()
            self.__namespace.sync()
            self.__prefix.sync()
        self.__pending_sync = None
	self.__syncing = False

    def close(self):
        self.__open = False
	if self.__pending_sync:
            if self.__syncing:
                self.__pending_sync.join()
            else:
                self.__pending_sync.cancel()

        for i in xrange(0, 3):
            self.__indicies[i].close()

        self.__contexts.close()
        self.__namespace.close()
        self.__prefix.close()
        self.env.close()

    def add(self, (subject, predicate, object), context, quoted=False):
        """\
        Add a triple to the store of triples.
        """
        assert self.__open, "The InformationStore must be open."

        _to_string = self._to_string
        _split = self._split

        s = _to_string(subject)
        p = _to_string(predicate)
        o = _to_string(object)
        c = _to_string(context)
        
        self.__contexts.put(c, "")        

        cspo, cpos, cosp = self.__indicies

        contexts = cspo.get("%s^%s^%s^%s^" % ("", s, p, o))
        if contexts:
            if not c in _split(contexts):
                contexts += "%s^" % c
        else:
            contexts = "%s^" % c
        assert contexts!=None

        #assert context!=self.identifier
        cspo.put("%s^%s^%s^%s^" % (c, s, p, o), contexts)
        cpos.put("%s^%s^%s^%s^" % (c, p, o, s), contexts)
        cosp.put("%s^%s^%s^%s^" % (c, o, s, p), contexts)
        if not quoted:
            cspo.put("%s^%s^%s^%s^" % ("", s, p, o), contexts)
            cpos.put("%s^%s^%s^%s^" % ("", p, o, s), contexts)
            cosp.put("%s^%s^%s^%s^" % ("", o, s, p), contexts)

        self._schedule_sync() 

        # We need some store tests for measuring the real world
        # performance hit for thing like the following:
        #self.sync()


    def remove(self, (subject, predicate, object), context):
        assert self.__open, "The InformationStore must be open."

        cspo, cpos, cosp = self.__indicies

        which, prefix = self.__lookup((subject, predicate, object), context)
        prefix = "^".join(prefix)
        index = self.__indicies[which]

        cursor = index.cursor()
        try:
            current = cursor.set_range(prefix)
        except db.DBNotFoundError:
            current = None
        cursor.close()
        while current:
            key, value = current
            cursor = index.cursor()
            try:
                cursor.set_range(key)
                current = cursor.next()
            except db.DBNotFoundError:
                current = None
            cursor.close()
            if key.startswith(prefix):
                try:
                    # TODO: remove from all the right indices
                    index.delete(key)
                except db.DBNotFoundError, e:
                    print e
            else:
                break            

        #self.sync()
        self._schedule_sync() 


    def __lookup(self, (subject, predicate, object), context):
        _to_string = self._to_string        
        if context is not None:
            context = _to_string(context)
        i = 0
        if subject is not None:
            i += 1
            subject = _to_string(subject)
        if predicate is not None:
            i += 2
            predicate = _to_string(predicate)
        if object is not None:
            i += 4
            object = _to_string(object)
        start, prefix_func = self.__lookup_dict[i]        
        return start, prefix_func((subject, predicate, object), context)


    def triples(self, (subject, predicate, object), context=None):
        """A generator over all the triples matching """
        _split = self._split
        _from_string = self._from_string
        _contexts_from_string = self._contexts_from_string

        assert self.__open, "The InformationStore must be open."

        which, prefix = self.__lookup((subject, predicate, object), context)
        prefix = "^".join(prefix)
        index = self.__indicies[which]

        cursor = index.cursor()
        try:
            current = cursor.set_range(prefix)
        except db.DBNotFoundError:
            current = None
        cursor.close()
        while current:
            key, value = current
            cursor = index.cursor()
            try:
                cursor.set_range(key)
                current = cursor.next()
            except db.DBNotFoundError:
                current = None
            cursor.close()
            if key.startswith(prefix):
                parts = list(_split(key))[1:]
                s = _from_string(parts[(3-which+0)%3])
                p = _from_string(parts[(3-which+1)%3])
                o = _from_string(parts[(3-which+2)%3])
                yield (s, p, o), _contexts_from_string(value)
            else:
                break            


    def __len__(self, context=None):
        if context is None:
            return self.__spo.stat()["nkeys"]
        else:
            count = 0
            for triple in self.triples((None, None, None), context):
                count += 1
            return count


    def bind(self, prefix, namespace):
        if namespace[-1]=="-":
            raise Exception("??")
        prefix = prefix.encode("utf-8")
        namespace = namespace.encode("utf-8")
        bound_prefix = self.__prefix.get(namespace)
        if bound_prefix:
            self.__namespace.delete(bound_prefix)
        self.__prefix[namespace] = prefix
        self.__namespace[prefix] = namespace

    def namespace(self, prefix):
        prefix = prefix.encode("utf-8")        
        return self.__namespace.get(prefix, None)

    def prefix(self, namespace):
        namespace = namespace.encode("utf-8")                
        return self.__prefix.get(namespace, None)

    def namespaces(self):
        cursor = self.__namespace.cursor()
        results = []
        current = cursor.first()
        while current:
            prefix, namespace = current
            results.append((prefix, URIRef(namespace)))
            current = cursor.next()
        cursor.close()
        for prefix, namespace in results:
            yield prefix, namespace


    def contexts(self, triple=None): # TODO: have Graph support triple?
        _from_string = self._from_string
        _to_string = self._to_string        
        _split = self._split

        if triple:
            s, p, o = triple
            s = _to_string(s)
            p = _to_string(p)
            o = _to_string(o)
            contexts = self.__spo.get("%s^%s^%s^" % (s, p, o))
            if contexts:
                for c in _split(contexts):
                    yield _from_string(c)
        else:
            index = self.__contexts
            cursor = index.cursor()
            current = cursor.first()
            cursor.close()
            while current:
                key, value = current
                context = _from_string(key)            
                yield context                            
                cursor = index.cursor()
                try:
                    cursor.set_range(key)
                    current = cursor.next()
                except db.DBNotFoundError:
                    current = None
                cursor.close()
    
    def remove_context(self, identifier):
        _to_string = self._to_string        
        c = _to_string(identifier)
        for triple, cg in self.triples((None, None, None), identifier):
            self.remove(triple, identifier)
        try:
            self.__contexts.delete(c)
        except db.DBNotFoundError, e:
            pass                    
        

    def _from_string(self, s):
        return from_bits(b64decode(s), backend=self)

    def _to_string(self, term):
        return b64encode(term.to_bits())

    def _contexts_from_string(self, contexts):
        for c in _split(contexts):
            yield _from_string(c)

    def _split(self, contexts):
        for part in contexts.split("^"):
            if part:
                yield part

