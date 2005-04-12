from __future__ import generators

from rdflib.backends import Backend

from sys import version_info
if version_info[0:2] > (2, 2):
    # Part of Python's standard library
    try:
        from bsddb import db
    except:
        from bsddb3 import db        
else:
    # http://pybsddb.sourceforge.net/
    from bsddb3 import db

from os import mkdir
from os.path import exists
from struct import pack, unpack

from urllib import quote, unquote

from rdflib.Literal import Literal
from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.exceptions import ContextTypeError

import re
_literal = re.compile(r'''"(?P<value>[^@&]*)"(?:@(?P<lang>[^&]*))?(?:&<(?P<datatype>.*)>)?''')    

def _fromkey(key):
    if key.startswith("<") and key.endswith(">"):
        return URIRef(key[1:-1].decode("UTF-8"))
    elif key.startswith("_"):
        return BNode(key.decode("UTF-8"))
    else:
        m = _literal.match(key)
        if m:
            d = m.groupdict()
            value = d["value"]
            value = unquote(value)
            value = value.decode("UTF-8")
            lang = d["lang"] or ''
            datatype = d["datatype"]            
            return Literal(value, lang, datatype)        
        else:
            msg = "Unknown Key Syntax: '%s'" % key
            raise Exception(msg)

def _tokey(term):
    if isinstance(term, URIRef):
        return '<%s>' % term.encode("UTF-8")
    elif isinstance(term, BNode):
        return term.encode("UTF-8")
    elif isinstance(term, Literal):
        language = term.language
        datatype = term.datatype
        value = quote(term.encode("UTF-8"))        
        if language:
            language = language.encode("UTF-8")
            if datatype:
                datatype = datatype.encode("UTF-8")
                n3 = '"%s"@%s&<%s>' % (value, language, datatype)
            else:
                n3 = '"%s"@%s' % (value, language)
        else:
            if datatype:
                datatype = datatype.encode("UTF-8")                
                n3 = '"%s"&<%s>' % (value, datatype)
            else:
                n3 = '"%s"' % value
        return n3
    else:
        msg = "Unknown term Type for: %s" % term
        raise Exception(msg)


def split(contexts):
    i = 0
    l = len(contexts)
    while i < l:
        start = i
        end = i + 4
        yield contexts[start:end]
        i = end

        
class Sleepycat(Backend):
    def __init__(self):
        super(Sleepycat, self).__init__()
        self.__open = 0
        self.default_context = BNode()
        
    def __len__(self, context=None):
        if context is None:
            return self.__spo.stat()["nkeys"]
        else:
            c = self.__cspo.cursor()
            c.set_range(self.tokey(context))
            count = c.count()
            c.close()
            return count

    def fromkey(self, key):
        return _fromkey(self.__i2k.get(key))

    def tokey(self, term):
        term = _tokey(term)
        k2i = self.__k2i        
        key = k2i.get(term)
        if key==None:
            c = k2i.cursor(flags = db.DB_WRITECURSOR)            
            k, v = c.set("next")
            num = int(v)
            c.put("next", "%s" % (num+1), db.DB_CURRENT)            
            c.close()                        
            key = pack(">L", num)
            k2i.put(term, key)                        
            self.__i2k.put(key, term)
        return key

    def add(self, (subject, predicate, object), context=None):
        """\
        Add a triple to the store of triples.
        """
        assert self.__open, "The InformationStore must be open."

        context = context or self.default_context

        tokey = self.tokey
        s = tokey(subject)
        p = tokey(predicate)
        o = tokey(object)
        c = tokey(context)
        
        self.__contexts.put(c, "")        
        self.__cspo.put("%s%s%s%s" % (c, s, p, o), "")
        self.__cpos.put("%s%s%s%s" % (c, p, o, s), "")
        self.__cosp.put("%s%s%s%s" % (c, o, s, p), "")

        contexts = self.__spo.get("%s%s%s" % (s, p, o))
        if contexts:
            if not c in split(contexts):
                contexts += c
        else:
            contexts = c
        assert contexts!=None
        self.__spo.put("%s%s%s" % (s, p, o), contexts)
        self.__pos.put("%s%s%s" % (p, o, s), "")
        self.__osp.put("%s%s%s" % (o, s, p), "")



    def remove(self, (subject, predicate, object), context):
        assert self.__open, "The InformationStore must be open."

        tokey = self.tokey        
        for subject, predicate, object in self.triples((subject, predicate, object), context):

            s = tokey(subject)
            p = tokey(predicate)
            o = tokey(object)
            if context==None:
                contexts = self.__spo.get("%s%s%s" % (s, p, o))
                if contexts:
                    for c in split(contexts):
                        try:
                            self.__cspo.delete("%s%s%s%s" % (c, s, p, o))
                        except db.DBNotFoundError, e:
                            pass
                        try:
                            self.__cpos.delete("%s%s%s%s" % (c, p, o, s))
                        except db.DBNotFoundError, e:
                            pass
                        try:
                            self.__cosp.delete("%s%s%s%s" % (c, o, s, p))
                        except db.DBNotFoundError, e:
                            pass                        
                    try:
                        self.__spo.delete("%s%s%s" % (s, p, o))
                    except db.DBNotFoundError, e:
                        pass
                    try:
                        self.__pos.delete("%s%s%s" % (p, o, s))
                    except db.DBNotFoundError, e:
                        pass
                    try:
                        self.__osp.delete("%s%s%s" % (o, s, p))
                    except db.DBNotFoundError, e:
                        pass                    
            else:
                c = tokey(context)
                contexts = self.__spo.get("%s%s%s" % (s, p, o))
                if contexts:
                    contexts = list(split(contexts))
                    if c in contexts:
                        contexts.remove(c)
                    if not contexts:
                        try:
                            self.__spo.delete("%s%s%s" % (s, p, o))
                        except db.DBNotFoundError, e:
                            pass                    
                        try:
                            self.__pos.delete("%s%s%s" % (p, o, s))
                        except db.DBNotFoundError, e:
                            pass                    
                        try:
                            self.__osp.delete("%s%s%s" % (o, s, p))
                        except db.DBNotFoundError, e:
                            pass                    
                    else:
                        contexts = "".join(contexts)
                        self.__spo.put("%s%s%s" % (s, p, o), contexts)
                    try:
                        self.__cspo.delete("%s%s%s%s" % (c, s, p, o))
                    except db.DBNotFoundError, e:
                        pass
                    try:
                        self.__cpos.delete("%s%s%s%s" % (c, p, o, s))
                    except db.DBNotFoundError, e:
                        pass
                    try:
                        self.__cosp.delete("%s%s%s%s" % (c, o, s, p))
                    except db.DBNotFoundError, e:
                        pass
        
    def triples(self, (subject, predicate, object), context=None):
        """A generator over all the triples matching """
        assert self.__open, "The InformationStore must be open."

        tokey = self.tokey        

        if subject!=None:
            if predicate!=None:
                if object!=None:
                    s = tokey(subject)
                    p = tokey(predicate)
                    o = tokey(object)
                    if context!=None:
                        c = tokey(context)
                        key = "%s%s%s%s" % (c, s, p, o)
                        if self.__cspo.has_key(key):
                            yield (subject, predicate, object)
                    else:
                        key = "%s%s%s" % (s, p, o)
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


    def _triples(self, context):
        fromkey = self.fromkey
        tokey = self.tokey        
        if context!=None:
            prefix = "%s" % tokey(context)
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
                    c, s, p, o = split(key)
                    yield (fromkey(s), fromkey(p), fromkey(o))
                else:
                    s, p, o = split(key)
                    yield (fromkey(s), fromkey(p), fromkey(o))
            else:
                break
                    
    def _subjects(self, predicate, object, context):
        fromkey = self.fromkey
        tokey = self.tokey        
        if context!=None:
            prefix = "%s" % tokey(context)
            index = self.__cpos
        else:
            prefix = ""
            index = self.__pos
        try:
            prefix += "%s%s" % (tokey(predicate), tokey(object))
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
                    assert(len(key)==16)
                    c, p, o, s = split(key)
                else:
                    assert(len(key)==12)                    
                    p, o, s = split(key)
                s = fromkey(s)
                yield s
            else:
                break            

    def _predicates(self, subject, object, context):
        fromkey = self.fromkey
        tokey = self.tokey        
        if context!=None:
            prefix = "%s" % tokey(context)
            index = self.__cosp
        else:
            prefix = ""
            index = self.__osp
        prefix += "%s%s" % (tokey(object), tokey(subject))
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
                    c, o, s, p = split(key)
                else:
                    o, s, p = split(key)
                yield fromkey(p)
            else:
                break

    def _objects(self, subject, predicate, context):
        fromkey = self.fromkey
        tokey = self.tokey        
        if context!=None:
            prefix = "%s" % tokey(context)
            index = self.__cspo
        else:
            prefix = ""
            index = self.__spo
        prefix += "%s%s" % (tokey(subject), tokey(predicate))
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
                    c, s, p, o = split(key)
                else:
                    s, p, o = split(key)
                yield fromkey(o)
            else:
                break
                    
    def _predicate_objects(self, subject, context):
        fromkey = self.fromkey
        tokey = self.tokey        
        if context!=None:
            prefix = "%s" % tokey(context)
            index = self.__cspo
        else:
            prefix = ""
            index = self.__spo            
        prefix += "%s" % tokey(subject)
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
                    c, s, p, o = split(key)
                else:
                    s, p, o = split(key)
                yield fromkey(p), fromkey(o)
            else:
                break

    def _subject_predicates(self, object, context):
        fromkey = self.fromkey
        tokey = self.tokey        
        if context!=None:
            prefix = "%s" % tokey(context)
            index = self.__cosp
        else:
            prefix = ""
            index = self.__osp            
        prefix += "%s" % tokey(object)
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
                    c, o, s, p = split(key)
                else:
                    o, s, p = split(key)
                yield fromkey(s), fromkey(p)
            else:
                break

    def _subject_objects(self, predicate, context):
        fromkey = self.fromkey
        tokey = self.tokey        
        if context!=None:
            prefix = "%s" % tokey(context)
            index = self.__cpos
        else:
            prefix = ""
            index = self.__pos            
        prefix += "%s" % tokey(predicate)
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
                    c, p, o, s = split(key)
                else:
                    p, o, s = split(key)
                yield fromkey(s), fromkey(o)
            else:
                break

    def contexts(self, triple=None): # TODO: have Graph support triple?
        fromkey = self.fromkey
        tokey = self.tokey        
        if triple:
            s, p, o = triple
            s = tokey(s)
            p = tokey(p)
            o = tokey(o)
            contexts = self.__spo.get("%s%s%s" % (s, p, o))
            if contexts:
                for c in split(contexts):
                    yield fromkey(c)
        else:
            index = self.__contexts
            cursor = index.cursor()
            current = cursor.first()
            cursor.close()
            while current:
                key, value = current
                context = fromkey(key)            
                yield context                            
                cursor = index.cursor()
                try:
                    cursor.set_range(key)
                    current = cursor.next()
                except db.DBNotFoundError:
                    current = None
                cursor.close()
    
    def remove_context(self, identifier):
        tokey = self.tokey        
        c = tokey(identifier)
        for triple in self._triples(identifier):
            self.remove(triple, identifier)
        try:
            self.__contexts.delete(c)
        except db.DBNotFoundError, e:
            pass                    
        

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
        current = cursor.first()
        while current:
            prefix, namespace = current
            yield prefix, namespace
            current = cursor.next()

    def sync(self):
        self.__contexts.sync()
        self.__spo.sync()
        self.__pos.sync()
        self.__osp.sync()
        self.__cspo.sync()
        self.__cpos.sync()
        self.__cosp.sync()
        self.__i2k.sync()
        self.__k2i.sync()

    def open(self, file):
        homeDir = file        
        envsetflags  = db.DB_CDB_ALLDB
        envflags = db.DB_INIT_MPOOL | db.DB_INIT_CDB | db.DB_THREAD
        try:
            if not exists(homeDir):
                mkdir(homeDir)
        except Exception, e:
            print e
        self.env = env = db.DBEnv()
        env.set_cachesize(0, 1024*1024*50)
        #env.set_lg_max(1024*1024)
        env.set_flags(envsetflags, 1)
        env.open(homeDir, envflags | db.DB_CREATE)

        self.__open = 1
        
        dbname = None
        dbtype = db.DB_BTREE
        dbopenflags = db.DB_THREAD
        
        dbmode = 0660
        dbsetflags   = 0

        # create and open the DBs
        self.__contexts = db.DB(env)
        self.__contexts.set_flags(dbsetflags)
        self.__contexts.open("contexts", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)
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

        self.__i2k = db.DB(env)
        self.__i2k.set_flags(dbsetflags)
        
        self.__i2k.open("i2k", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        self.__k2i = db.DB(env)
        self.__k2i.set_flags(dbsetflags)#|db.DB_RECNUM)
        self.__k2i.open("k2i", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        self.__namespace = db.DB(env)
        self.__namespace.set_flags(dbsetflags)
        self.__namespace.open("namespace", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        self.__prefix = db.DB(env)
        self.__prefix.set_flags(dbsetflags)
        self.__prefix.open("prefix", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        
        next = self.__k2i.get("next")
        if next==None:
            self.__k2i.put("next", "%d" % 1)            
        
    def close(self):
        self.__open = 0
        self.__contexts.close()
        self.__spo.close()
        self.__pos.close()
        self.__osp.close()
        self.__cspo.close()
        self.__cpos.close()
        self.__cosp.close()
        self.__k2i.close()
        self.__i2k.close()
        self.__namespace.close()
        self.__prefix.close()
        self.env.close()
