from rdflib.store import Store
from rdflib.util import from_bits

from bsddb import db
from base64 import b64encode
from base64 import b64decode
from os import mkdir
from os.path import exists
from threading import Thread
from time import sleep, time

# TODO: tool to convert old Sleepycat DBs to this version.

class Sleepycat(Store):
    context_aware = True
    formula_aware = True

    def __init__(self, configuration=None, identifier=None):
        self.__open = False
        from rdflib import BNode
        self.identifier = identifier or BNode() # TODO: derive this from CWD, configuration or have graph pass down the logical URI of the Store.
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
        env.set_cachesize(0, 1024*1024*50) # TODO
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
        self.__indicies_info = [None,] * 3
        for i in xrange(0, 3):
            index_name = to_key_func(i)(("s", "p", "o"), "c")
            index = db.DB(env)
            index.set_flags(dbsetflags)
            index.open(index_name, dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)
            self.__indicies[i] = index
            self.__indicies_info[i] = (index, to_key_func(i), from_key_func(i))

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

            lookup[i] = (self.__indicies[start], get_prefix_func(start, start + len), to_key_func(start), from_key_func(start))


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
        
        self.__needs_sync = False
        t = Thread(target=self.__sync_run)
        t.setDaemon(True)
        t.start()
        self.__sync_thread = t


    def __sync_run(self):
        min_seconds, max_seconds = 10, 300
        while self.__open:
            if self.__needs_sync:
                t0 = t1 = time()
                self.__needs_sync = False
                while self.__open:
                    sleep(.1) 
                    if self.__needs_sync:
                        t1 = time()
                        self.__needs_sync = False
                    if time()-t1 > min_seconds or time()-t0 > max_seconds: 
                        self.__needs_sync = False
                        print "sync"
                        self.sync()
                        break
            else:
                sleep(1)

    def sync(self):
        if self.__open:
            for i in self.__indicies:
                i.sync()
            self.__contexts.sync()
            self.__namespace.sync()
            self.__prefix.sync()

    def close(self):
        self.__open = False
        self.__sync_thread.join()
        for i in self.__indicies:
            i.close()
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

        s = _to_string(subject)
        p = _to_string(predicate)
        o = _to_string(object)
        c = _to_string(context)
        
        self.__contexts.put(c, "")        

        cspo, cpos, cosp = self.__indicies

        contexts_value = cspo.get("%s^%s^%s^%s^" % ("", s, p, o)) or ""
        contexts = set(contexts_value.split("^"))
        contexts.add(c)
        contexts_value = "^".join(contexts)
        assert contexts_value!=None

        #assert context!=self.identifier
        cspo.put("%s^%s^%s^%s^" % (c, s, p, o), "")
        cpos.put("%s^%s^%s^%s^" % (c, p, o, s), "")
        cosp.put("%s^%s^%s^%s^" % (c, o, s, p), "")
        if not quoted:
            cspo.put("%s^%s^%s^%s^" % ("", s, p, o), contexts_value)
            cpos.put("%s^%s^%s^%s^" % ("", p, o, s), contexts_value)
            cosp.put("%s^%s^%s^%s^" % ("", o, s, p), contexts_value)

        self.__needs_sync = True

    def __remove(self, (s, p, o), c, quoted=False):
        cspo, cpos, cosp = self.__indicies

        contexts_value = cspo.get("^".join(("", s, p, o, ""))) or ""
        contexts = set(contexts_value.split("^"))
        contexts.discard(c)
        contexts_value = "^".join(contexts)
        for i, _to_key, _from_key in self.__indicies_info:
            i.delete(_to_key((s, p, o), c))
        if not quoted:
            if contexts_value:
                for i, _to_key, _from_key in self.__indicies_info:
                    i.put(_to_key((s, p, o), ""), contexts_value)
            else:
                for i, _to_key, _from_key in self.__indicies_info:
                    i.delete(_to_key((s, p, o), ""))

    def remove(self, (subject, predicate, object), context):
        assert self.__open, "The InformationStore must be open."

#         if context is not None:
#             if context == self: 
#                 context = None

        # TODO: special case if subject and predicate and object and context:
        # TODO: write def __remove(self, (s, p, o), c) where all are known and in string form
        cspo, cpos, cosp = self.__indicies
        index, prefix, to_key, from_key = self.__lookup((subject, predicate, object), context)

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
                c, s, p, o = from_key(key)
                if context is None:
                    contexts_value = index.get(key) # or ""?
                    contexts = set(contexts_value.split("^")) # remove triple from all non quoted contexts 
                    contexts.add("") # and from the conjunctive index
                    for c in contexts:
                        for i, _to_key, _ in self.__indicies_info:
                            i.delete(_to_key((s, p, o), c))
                else:
                    self.__remove((s, p, o), c)
            else:
                break            

        if context is not None:
            if subject is None and predicate is None and object is None:
                # TODO: also if context becomes empty and not just on remove((None, None, None), c)
                try:
                    self.__contexts.delete(self._to_string(context))
                except db.DBNotFoundError, e:
                    pass                    

        self.__needs_sync = True


    def triples(self, (subject, predicate, object), context=None):
        """A generator over all the triples matching """
        assert self.__open, "The InformationStore must be open."

#         if context is not None:
#             if context == self: 
#                 context = None

        _from_string = self._from_string
        index, prefix, to_key, from_key = self.__lookup((subject, predicate, object), context)

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
            if key and key.startswith(prefix):
                c, s, p, o = from_key(key)
                contexts_value = index.get(key)
                yield (_from_string(s), _from_string(p), _from_string(o)), (_from_string(c) for c in contexts_value.split("^") if c)
            else:
                break            

    def __len__(self, context=None):

#         if context is not None:
#             if context == self: 
#                 context = None

        if context is None:
            #return self.__indicies[0].stat()["nkeys"] / 2
            prefix = "^"
        else:
            prefix = "%s^" % self._to_string(context)

        index = self.__indicies[0]
        cursor = index.cursor()
        current = cursor.set_range("^")
        count = 0
        while current:
            count +=1
            current = cursor.next()
        cursor.close()
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

        if triple:
            s, p, o = triple
            s = _to_string(s)
            p = _to_string(p)
            o = _to_string(o)
            contexts = self.__indicies[0].get("%s^%s^%s^%s^" % ("", s, p, o))
            if contexts:
                for c in contexts.split("^"):
                    if c:
                        yield _from_string(c)
                    #else:
                    #    yield self.identifier

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
        self.remove((None, None, None), identifier)
        
    def _from_string(self, s):
        return from_bits(b64decode(s), backend=self)

    def _to_string(self, term):
        return b64encode(term.to_bits())

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
        index, prefix_func, to_key, from_key = self.__lookup_dict[i]        
        prefix = "^".join(prefix_func((subject, predicate, object), context))
        return index, prefix, to_key, from_key


def to_key_func(i):
    def to_key(triple, context):
        "Takes a string; returns key"
        return "^".join((context, triple[i%3], triple[(i+1)%3], triple[(i+2)%3], "")) # "" to tac on the trailing ^
    return to_key

def from_key_func(i):
    def from_key(key):
        "Takes a key; returns string"
        parts = key.split("^")
        return parts[0], parts[(3-i+0)%3+1], parts[(3-i+1)%3+1], parts[(3-i+2)%3+1]
    return from_key

def readable_index(i):
    s, p, o = "?" * 3
    if i & 1: s = "s"
    if i & 2: p = "p"
    if i & 4: o = "o"
    return "%s,%s,%s" % (s, p, o)
