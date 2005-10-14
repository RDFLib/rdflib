from rdflib.backends import Backend
from rdflib.util import from_n3

from bsddb import db
from base64 import b64encode
from base64 import b64decode
from os import mkdir
from os.path import exists

# TODO: tool to convert old Sleepycat DBs to this version.

class Sleepycat(Backend):
    def __init__(self):
        super(Sleepycat, self).__init__()
        self.__open = False
        
    def open(self, path):
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
        self.__spo = db.DB(env)
        self.__spo.set_flags(dbsetflags)
        self.__spo.open("spo", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        self.__pos = db.DB(env)
        self.__pos.set_flags(dbsetflags)
        self.__pos.open("pos", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        self.__osp = db.DB(env)
        self.__osp.set_flags(dbsetflags)
        self.__osp.open("osp", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        self.__cspo = db.DB(env)
        self.__cspo.set_flags(dbsetflags)
        self.__cspo.open("cspo", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        self.__cpos = db.DB(env)
        self.__cpos.set_flags(dbsetflags)
        self.__cpos.open("cpos", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        self.__cosp = db.DB(env)
        self.__cosp.set_flags(dbsetflags)
        self.__cosp.open("cosp", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

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
            self.__spo.sync()
            self.__pos.sync()
            self.__osp.sync()

            self.__cspo.sync()
            self.__cpos.sync()
            self.__cosp.sync()

            self.__contexts.sync()
            self.__namespace.sync()
            self.__prefix.sync()
        self.__pending_sync = None
	self.__syncing = False

    def close(self):
        self.__open = False

	if self.__pending_sync and self.__syncing:
	    self.__pending_sync.join()

        self.__spo.close()
        self.__pos.close()
        self.__osp.close()

        self.__cspo.close()
        self.__cpos.close()
        self.__cosp.close()

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
        self.__cspo.put("%s^%s^%s^%s" % (c, s, p, o), "")
        self.__cpos.put("%s^%s^%s^%s" % (c, p, o, s), "")
        self.__cosp.put("%s^%s^%s^%s" % (c, o, s, p), "")

        contexts = self.__spo.get("%s^%s^%s" % (s, p, o))
        if contexts:
            if not c in _split(contexts):
                contexts += "^%s" % c
        else:
            contexts = c
        assert contexts!=None
        if not quoted:
            self.__spo.put("%s^%s^%s" % (s, p, o), contexts)
            self.__pos.put("%s^%s^%s" % (p, o, s), "")
            self.__osp.put("%s^%s^%s" % (o, s, p), "")

        self._schedule_sync() 

        # We need some store tests for measuring the real world
        # performance hit for thing like the following:
        #self.sync()


    def remove(self, (subject, predicate, object), context):
        assert self.__open, "The InformationStore must be open."

        _to_string = self._to_string        
        _split = self._split

        for subject, predicate, object in self.triples((subject, predicate, object), context):

            s = _to_string(subject)
            p = _to_string(predicate)
            o = _to_string(object)
            if context==None:
                contexts = self.__spo.get("%s^%s^%s" % (s, p, o))
                if contexts:
                    for c in _split(contexts):
                        try:
                            self.__cspo.delete("%s^%s^%s^%s" % (c, s, p, o))
                        except db.DBNotFoundError, e:
                            pass
                        try:
                            self.__cpos.delete("%s^%s^%s^%s" % (c, p, o, s))
                        except db.DBNotFoundError, e:
                            pass
                        try:
                            self.__cosp.delete("%s^%s^%s^%s" % (c, o, s, p))
                        except db.DBNotFoundError, e:
                            pass                        
                    try:
                        self.__spo.delete("%s^%s^%s" % (s, p, o))
                    except db.DBNotFoundError, e:
                        pass
                    try:
                        self.__pos.delete("%s^%s^%s" % (p, o, s))
                    except db.DBNotFoundError, e:
                        pass
                    try:
                        self.__osp.delete("%s^%s^%s" % (o, s, p))
                    except db.DBNotFoundError, e:
                        pass                    
            else:
                c = _to_string(context)
                contexts = self.__spo.get("%s^%s^%s" % (s, p, o))
                if contexts:
                    contexts = list(_split(contexts))
                    if c in contexts:
                        contexts.remove(c)
                    if not contexts:
                        try:
                            self.__spo.delete("%s^%s^%s" % (s, p, o))
                        except db.DBNotFoundError, e:
                            pass                    
                        try:
                            self.__pos.delete("%s^%s^%s" % (p, o, s))
                        except db.DBNotFoundError, e:
                            pass                    
                        try:
                            self.__osp.delete("%s^%s^%s" % (o, s, p))
                        except db.DBNotFoundError, e:
                            pass                    
                    else:
                        contexts = "".join(contexts)
                        self.__spo.put("%s^%s^%s" % (s, p, o), contexts)
                    try:
                        self.__cspo.delete("%s^%s^%s^%s" % (c, s, p, o))
                    except db.DBNotFoundError, e:
                        pass
                    try:
                        self.__cpos.delete("%s^%s^%s^%s" % (c, p, o, s))
                    except db.DBNotFoundError, e:
                        pass
                    try:
                        self.__cosp.delete("%s^%s^%s^%s" % (c, o, s, p))
                    except db.DBNotFoundError, e:
                        pass
        #self.sync()
        self._schedule_sync() 


    def triples(self, (subject, predicate, object), context=None):
        """A generator over all the triples matching """
        assert self.__open, "The InformationStore must be open."

        _to_string = self._to_string        

        if subject!=None:
            if predicate!=None:
                if object!=None:
                    s = _to_string(subject)
                    p = _to_string(predicate)
                    o = _to_string(object)
                    if context!=None:
                        c = _to_string(context)
                        key = "%s^%s^%s^%s" % (c, s, p, o)
                        if self.__cspo.has_key(key):
                            yield (subject, predicate, object)
                    else:
                        key = "%s^%s^%s" % (s, p, o)
                        if self.__spo.has_key(key):
                            yield (subject, predicate, object)
                else:
                    for o in self._objects(subject, predicate, context):
                        yield (subject, predicate, o)
            else:
                if object!=None:
                    for p in self._predicates(subject, object, context):
                        yield (subject, p, object)
                else:
                    for p, o in self._predicate_objects(subject, context):
                        yield (subject, p, o)
        else:
            if predicate!=None:
                if object!=None:
                    for s in self._subjects(predicate, object, context):
                        yield (s, predicate, object)
                else:
                    for s, o in self._subject_objects(predicate, context):
                        yield (s, predicate, o)
            else:
                if object!=None:
                    for s, p in self._subject_predicates(object, context):
                        yield (s, p, object)
                else: 
                    for s, p, o in self._triples(context):
                        yield (s, p, o)


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
            contexts = self.__spo.get("%s^%s^%s" % (s, p, o))
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
        for triple in self._triples(identifier):
            self.remove(triple, identifier)
        try:
            self.__contexts.delete(c)
        except db.DBNotFoundError, e:
            pass                    
        

    def _from_string(self, s):
        return from_n3(b64decode(s))

    def _to_string(self, term):
        return b64encode(term.n3())

    def _split(self, contexts):
        for part in contexts.split("^"):
            yield part

    def _triples(self, context):
        _from_string = self._from_string
        _to_string = self._to_string        
        _split = self._split

        if context!=None:
            prefix = "%s^" % _to_string(context)
            index = self.__cspo
        else:
            prefix = ""
            index = self.__spo
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
                if context!=None:
                    c, s, p, o = _split(key)
                    yield (_from_string(s), _from_string(p), _from_string(o))
                else:
                    s, p, o = _split(key)
                    yield (_from_string(s), _from_string(p), _from_string(o))
            else:
                break
                    
    def _subjects(self, predicate, object, context):
        _from_string = self._from_string
        _to_string = self._to_string        
        _split = self._split

        if context!=None:
            prefix = "%s^" % _to_string(context)
            index = self.__cpos
        else:
            prefix = ""
            index = self.__pos
        try:
            prefix += "%s^%s^" % (_to_string(predicate), _to_string(object))
        except Exception, e:
            print e, predicate, object
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
                if context!=None:
                    #assert(len(key)==16)
                    c, p, o, s = _split(key)
                else:
                    #assert(len(key)==12)                    
                    p, o, s = _split(key)
                s = _from_string(s)
                yield s
            else:
                break            

    def _predicates(self, subject, object, context):
        _from_string = self._from_string
        _to_string = self._to_string        
        _split = self._split

        if context!=None:
            prefix = "%s^" % _to_string(context)
            index = self.__cosp
        else:
            prefix = ""
            index = self.__osp
        prefix += "%s^%s^" % (_to_string(object), _to_string(subject))
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
                if context!=None:
                    c, o, s, p = _split(key)
                else:
                    o, s, p = _split(key)
                yield _from_string(p)
            else:
                break

    def _objects(self, subject, predicate, context):
        _from_string = self._from_string
        _to_string = self._to_string   
        _split = self._split
     
        if context!=None:
            prefix = "%s^" % _to_string(context)
            index = self.__cspo
        else:
            prefix = ""
            index = self.__spo
        prefix += "%s^%s^" % (_to_string(subject), _to_string(predicate))
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
                if context!=None:
                    c, s, p, o = _split(key)
                else:
                    s, p, o = _split(key)
                yield _from_string(o)
            else:
                break
                    
    def _predicate_objects(self, subject, context):
        _from_string = self._from_string
        _to_string = self._to_string        
        _split = self._split

        if context!=None:
            prefix = "%s^" % _to_string(context)
            index = self.__cspo
        else:
            prefix = ""
            index = self.__spo            
        prefix += "%s^" % _to_string(subject)
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
                if context!=None:
                    c, s, p, o = _split(key)
                else:
                    s, p, o = _split(key)
                yield _from_string(p), _from_string(o)
            else:
                break

    def _subject_predicates(self, object, context):
        _from_string = self._from_string
        _to_string = self._to_string        
        _split = self._split

        if context!=None:
            prefix = "%s^" % _to_string(context)
            index = self.__cosp
        else:
            prefix = ""
            index = self.__osp            
        prefix += "%s^" % _to_string(object)
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
                if context!=None:
                    c, o, s, p = _split(key)
                else:
                    o, s, p = _split(key)
                yield _from_string(s), _from_string(p)
            else:
                break

    def _subject_objects(self, predicate, context):
        _from_string = self._from_string
        _to_string = self._to_string        
        _split = self._split

        if context!=None:
            prefix = "%s^" % _to_string(context)
            index = self.__cpos
        else:
            prefix = ""
            index = self.__pos            
        prefix += "%s^" % _to_string(predicate)
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
                if context!=None:
                    c, p, o, s = _split(key)
                else:
                    p, o, s = _split(key)
                yield _from_string(s), _from_string(o)
            else:
                break

