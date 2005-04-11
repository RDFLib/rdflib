from __future__ import generators

from rdflib.backends import Backend
from rdflib.util import from_n3
from rdflib import BNode

from bsddb import db

from os import mkdir
from os.path import exists


class Sleepycat_new(Backend):
    def __init__(self):
        super(Sleepycat_new, self).__init__()
        self.context_aware = True        
        self.__open = 0
        self.default_context = BNode()
        
    def open(self, file):
        homeDir = file        
        try:
            if not exists(homeDir):
                mkdir(homeDir)
        except Exception, e:
            print e

        envsetflags  = 0 
        envflags = db.DB_INIT_MPOOL | db.DB_INIT_CDB | db.DB_THREAD        

        self.env = env = db.DBEnv()
        env.set_lg_max(1024*1024)        
        env.set_cachesize(0, 1024*1024*1)
        env.set_flags(envsetflags, 1)
        env.open(homeDir, envflags | db.DB_CREATE)
        
        dbname = None
        dbtype = db.DB_BTREE
        dbopenflags = db.DB_THREAD | db.DB_CREATE
        dbmode = 0660
        dbsetflags   = 0

        # create and open the DBs
        self.__forward = db.DB(env)
        self.__forward.set_flags(dbsetflags)
        self.__forward.open("forward", dbname, dbtype, dbopenflags, dbmode)
        
        self.__reverse = db.DB(env)
        self.__reverse.set_flags(dbsetflags)
        self.__reverse.open("reverse", dbname, dbtype, dbopenflags, dbmode)
        
        self.__spo = db.DB(env)
        self.__spo.set_flags(db.DB_DUP)
        self.__spo.open("spo", dbname, dbtype, dbopenflags, dbmode)

        self.__pos = db.DB(env)
        self.__pos.set_flags(db.DB_DUP)
        self.__pos.open("pos", dbname, dbtype, dbopenflags, dbmode)
        
        self.__osp = db.DB(env)
        self.__osp.set_flags(db.DB_DUP)
        self.__osp.open("osp", dbname, dbtype, dbopenflags, dbmode)

        self.__context = db.DB(env)
        self.__context.set_flags(db.DB_DUP)
        self.__context.open("context", dbname, dbtype, dbopenflags, dbmode)

        self.__namespace = db.DB(env)
        self.__namespace.set_flags(dbsetflags)
        self.__namespace.open("namespace", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        self.__prefix = db.DB(env)
        self.__prefix.set_flags(dbsetflags)
        self.__prefix.open("prefix", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        self.__open = 1        

    def close(self):
        self.__open = 0
        self.__forward.close()
        self.__reverse.close()        
        self.__spo.close()
        self.__pos.close()
        self.__osp.close()
        self.__context.close()
        self.__namespace.close()
        self.__prefix.close()
        self.env.close()
    
    def keyToIdentifier(self, key):
        return from_n3(self.__forward[key])

    def identifierToKey(self, identifier):
        if identifier!=None:
            identifier = identifier.n3().encode("utf-8")
            try:
                key = self.__reverse[identifier]
            except:
                key = randkey()
                while self.__forward.has_key(key):
                    key = randkey()
                self.__forward.put(key, identifier)
                self.__reverse.put(identifier, key)
            return key
        else:
            # Wildcard stays wildcard
            return None
    
    def add(self, (subject, predicate, object), context):
        """\
        Add a triple to the store of triples.
        """
        assert self.__open, "This Graph must be open first."
        
        if context is None:
            context = self.default_context
        identifierToKey = self.identifierToKey
        si = identifierToKey(subject)
        pi = identifierToKey(predicate)
        oi = identifierToKey(object)
        ci = identifierToKey(context)        

        self.__spo.put("^".join((si, pi, oi)), ci)
        self.__pos.put("^".join((pi, oi, si)), ci)
        self.__osp.put("^".join((oi, si, pi)), ci)

        self.__context.put(ci, "^".join((si, pi, oi)))

    def remove(self, (subject, predicate, object), context=None):
        assert self.__open, "This Graph must be open first."
        
        spo = self.__spo
        pos = self.__pos
        osp = self.__osp
        identifierToKey = self.identifierToKey
        if context is None:        
            for s, p, o in self.triples((subject, predicate, object), context):
                s = identifierToKey(s)
                p = identifierToKey(p)
                o = identifierToKey(o)
                spo.delete("^".join((s, p, o)))
                pos.delete("^".join((p, o, s)))
                osp.delete("^".join((o, s, p)))
        else:
            c = self.__context
            c.set("^".join((si, pi, oi)))
            c.delete()
            c.close()
            for s, p, o in self.triples((subject, predicate, object), context):
                s = identifierToKey(s)
                p = identifierToKey(p)
                o = identifierToKey(o)
                
                c = spo.cursor()
                rec = c.set("^".join((s, p, o)))
                while rec is not None:
                    c.delete()
                    rec = c.next_dup()
                c.close()

                c = pos.cursor()
                rec = c.set("^".join((p, o, s)))
                while rec is not None:
                    c.delete()
                    rec = c.next_dup()
                c.close()
                
                c = osp.cursor()
                rec = c.set("^".join((o, s, p)))
                while rec is not None:
                    c.delete()
                    rec = c.next_dup()
                c.close()
                
    def triples(self, (subject, predicate, object), context=None):
        """A generator over all the triples matching """
        assert self.__open, "This Graph must be open first."        
        keyToIdentifier = self.keyToIdentifier
        identifierToKey = self.identifierToKey        
        s_key = identifierToKey(subject)
        p_key = identifierToKey(predicate)
        o_key = identifierToKey(object)

        Any = None

        # TMP TMP

        spo = self.__spo
        c_key = identifierToKey(context)                                
        cursor = spo.cursor()
        rec = cursor.first()
        cursor.close()
        while rec is not None:
            key, value = rec
            s, p, o = key.split("^")
            c = value
            if (not subject or s_key==s) and \
               (not predicate or p_key==p) and \
               (not object or o_key==o) and \
               (not context or c_key==c):
                yield keyToIdentifier(s), keyToIdentifier(p), keyToIdentifier(o)
            cursor = spo.cursor()
            cursor.set(key)
            rec = cursor.next_nodup()
            cursor.close()
        return


        if s_key!=Any:
            if p_key!=Any:
                if o_key!=Any:
                        if self.__spo.has_key("^".join((s_key, p_key, o_key))):
                            yield subject, predicate, object
                        return
                else:
                    index = self.__spo
                    first = "^".join((s_key, p_key))
                    order = lambda (s, p, o): (s, p, o)
                    pattern = lambda s, p, o: s==s_key and p==p_key
                    result = lambda s, p, o: (subject, predicate, keyToIdentifier(o))
            else:
                if o_key!=Any:
                    index = self.__osp
                    first = "^".join((o_key, s_key))
                    order = lambda (o, s, p): (s, p, o)
                    pattern = lambda s, p, o: s==s_key and o==o_key
                    result = lambda s, p, o: (subject, keyToIdentifier(p), object)
                else:
                    index = self.__spo
                    first = s_key
                    order = lambda (s, p, o): (s, p, o)
                    pattern = lambda s, p, o: s==s_key
                    result = lambda s, p, o: (subject, keyToIdentifier(p), keyToIdentifier(o))
        else:
            if p_key!=Any:
                if o_key!=Any:
                    index = self.__pos
                    first = "^".join((p_key, o_key))
                    order = lambda (p, o, s): (s, p, o)
                    pattern = lambda s, p, o: p==p_key and o==o_key
                    result = lambda s, p, o: (keyToIdentifier(s), predicate, object)
                else:
                    index = self.__pos
                    first = p_key
                    order = lambda (p, o, s): (s, p, o)
                    pattern = lambda s, p, o: p==p_key
                    result = lambda s, p, o: (keyToIdentifier(s), predicate, keyToIdentifier(o))
            else:
                if o_key!=Any:
                    index = self.__osp
                    first = o_key
                    order = lambda (o, s, p): (s, p, o)
                    pattern = lambda s, p, o: o==o_key
                    result = lambda s, p, o: (keyToIdentifier(s), keyToIdentifier(p), object)
                else:
                    if context is None:
                        index = self.__spo
                        first = ""
                        order = lambda (s, p, o): (s, p, o)
                        pattern = lambda s, p, o: 1
                        result = lambda s, p, o: (keyToIdentifier(s), keyToIdentifier(p), keyToIdentifier(o))
                    else:
                        c_key = identifierToKey(context)                                
                        c = self.__context.cursor()
                        rec = c.set(c_key)
                        while rec is not None:
                            key, value = rec
                            s, p, o = value.split("^")
                            yield keyToIdentifier(s), keyToIdentifier(p), keyToIdentifier(o)
                            rec = c.next_dup()
                        c.close()
                        return
                        
        # TODO: how to inline these so we don't need to set index,
        # first, order, pattern, and result
        if context is None:
            key = first
            while 1:
                cursor = index.cursor()
                current = cursor.set_range(key)
                next = cursor.next()
                cursor.close()                    
                if not next:
                    break
                key, value = next
                s, p, o = order(key.split("^"))
                if pattern(s, p, o):
                    yield result(s, p, o)
                else:
                    break
        else:
            _context = self.__context
            key = first
            while 1:
                cursor = index.cursor()
                current = cursor.set(key) 
                next = cursor.next()
                cursor.close()                    
                if not next:
                    break
                key, value = next
                s, p, o = order(key.split("^"))
                if pattern(s, p, o):
                    if _context.get_both(c_key, "^".join(s, p, o)):
                        yield result(s, p, o)
                else:
                    break
            
    def contexts(self, triple=None): # TODO: have Graph support triple?
        assert self.__open, "This Graph must be open first."        
    
    def remove_context(self, identifier):
        assert self.__open, "This Graph must be open first."        
        

    def bind(self, prefix, namespace):
        assert self.__open, "This Graph must be open first."        
        prefix = prefix.encode("utf-8")
        namespace = namespace.encode("utf-8")
        bound_prefix = self.__prefix.get(namespace)
        if bound_prefix:
            self.__namespace.delete(bound_prefix)
        self.__prefix[namespace] = prefix
        self.__namespace[prefix] = namespace

    def namespace(self, prefix):
        assert self.__open, "This Graph must be open first."        
        prefix = prefix.encode("utf-8")        
        return self.__namespace.get(prefix, None)

    def prefix(self, namespace):
        assert self.__open, "This Graph must be open first."        
        namespace = namespace.encode("utf-8")                
        return self.__prefix.get(namespace, None)

    def namespaces(self):
        assert self.__open, "This Graph must be open first."        
        cursor = self.__namespace.cursor()
        current = cursor.first()
        while current:
            prefix, namespace = current
            yield prefix, namespace
            current = cursor.next()
                
    def __len__(self, context=None):
        assert self.__open, "This Graph must be open first."
        return self.__spo.stat()["nkeys"]        
#         if context is None:
#             return self.__spo.stat()["nkeys"]
#         else:
#             raise "NYI"


from random import choice
from string import ascii_letters

def randkey(n=8, ascii_letters=ascii_letters, choice=choice):
    return "".join(choice(ascii_letters) for x in xrange(0, n))

del choice, ascii_letters
