from __future__ import generators

from BTrees.OOBTree import OOBTree

from ZODB import DB
from ZODB.FileStorage import FileStorage
from ZODB.Transaction import Transaction

from rdflib.store.TypeCheck import check_subject, check_predicate, check_object
from rdflib.store.AbstractTripleStore import AbstractTripleStore
from rdflib.model.schema import Schema
from rdflib.syntax.loadsave import LoadSave

ANY = None


class ZBacked(object):
    def __init__(self):
        super(ZBacked, self).__init__()
        self.__indices = None
        
    def __check(self, indices):
        if not indices.has_key("spo"):
            indices["spo"] =  OOBTree()
        if not indices.has_key("pos"):
            indices["pos"] =  OOBTree()
        if not indices.has_key("contexts"):
            indices["contexts"] =  OOBTree()
    
    def __get_indices(self):
        indices = self.__indices
        if not indices:
            self.__indices = indices = {}
            self.__check(indices)
        return indices

    # Declare indices as a property of ZBacked
    indices = property(__get_indices)

    def __get_spo(self, context):
        indices = self.indices
        if context:
            contexts = indices["contexts"]
            if not contexts.has_key(context):
                ci = contexts[context] = {}
            else:
                ci = contexts[context] 
            spo = ci.setdefault("spo", {})
        else:
            spo = indices["spo"]
        return spo

    def __get_pos(self, context):
        indices = self.indices        
        if context:
            contexts = indices["contexts"]
            if not contexts.has_key(context):
                ci = contexts[context] = {}
            else:
                ci = contexts[context] 
            pos = ci.setdefault("pos", {})
        else:
            pos = indices["pos"]
        return pos

    def add(self, (subject, predicate, object), context=None):
        """\
        Add a triple to the store of triples.
        """
        check_subject(subject)
        check_predicate(predicate)
        check_object(object)

        context = context or self.context.identifier

        indices = self.indices

        contexts = indices["contexts"]
            
        try:
            ci = contexts[context]
        except:
            ci = contexts[context] = {}
        spo = ci.setdefault("spo", {})
        sp = spo.setdefault(subject, {})
        sp.setdefault(predicate, {})[object] = 1

        pos = ci.setdefault("pos", {})
        po = pos.setdefault(predicate, {})
        po.setdefault(object, {})[subject] = 1

        spo = indices["spo"]
        try:
            po = spo[subject]
        except:
            po = spo[subject] = {}
        try:
            o = po[predicate]
        except:
            o = po[predicate] = {}
        try:
            c = o[object]
        except:
            c = o[object] = {}
        c[context] = 1

        pos = indices["pos"]
        try:
            os = pos[predicate]
        except:
            os = pos[predicate] = {}
        try:
            s = os[object]
        except:
            s = os[object] = {}
        try:
            c = s[subject]
        except:
            c = s[subject] = {}
        c[context] = 1

        spo[subject] = spo[subject]
        pos[predicate] = pos[predicate]
        contexts[context] = contexts[context]


    def remove(self, (subject, predicate, object), context=None):
        check_subject(subject)
        check_predicate(predicate)
        check_object(object)

        indices = self.indices
        spo = indices["spo"]
        pos = indices["pos"]
        contexts = indices["contexts"]
        if context==None:
            c = spo[subject][predicate][object]
            for context in c:
                ci = contexts[context]
                del ci["spo"][subject][predicate][object]
                del ci["pos"][predicate][object][subject]
                contexts[context] = contexts[context]
            del spo[subject][predicate][object]
            del pos[predicate][object][subject]
        else:
            ci = contexts[context]
            del ci["spo"][subject][predicate][object]
            del ci["pos"][predicate][object][subject]

            c = spo[subject][predicate][object]
            del c[context]
            if not c:
                del spo[subject][predicate][object]
            c = pos[predicate][object][subject]
            del c[context]
            if not c:
                del pos[predicate][object][subject]
            contexts[context] = contexts[context]
        spo[subject] = spo[subject]
        pos[predicate] = pos[predicate]
        contexts[context] = contexts[context]        

    def triples(self, (subject, predicate, object), context=None):
        """A generator over all the triples matching """

        if subject:
            check_subject(subject)
        if predicate:
            check_predicate(predicate)
        if object:
            check_object(object)

        if subject!=ANY: # subject is given
            spo = self.__get_spo(context)
            if spo.has_key(subject):
                subjectDictionary = spo[subject]
                if predicate!=ANY: # subject+predicate is given
                    if predicate in subjectDictionary:
                        if object!=ANY: # subject+predicate+object is given
                            if object in subjectDictionary[predicate]:
                                yield subject, predicate, object
                            else: # given object not found
                                pass
                        else: # subject+predicate is given, object unbound
                            for o in subjectDictionary[predicate].keys():
                                yield subject, predicate, o
                    else: # given predicate not found
                        pass
                else: # subject given, predicate unbound
                    for p in subjectDictionary.keys():
                        if object!=ANY: # object is given
                            if object in subjectDictionary[p]:
                                yield subject, p, object
                            else: # given object not found
                                pass
                        else: # object unbound
                            for o in subjectDictionary[p].keys():
                                yield subject, p, o
            else: # given subject not found
                pass
        elif predicate!=ANY: # predicate is given, subject unbound
            pos = self.__get_pos(context)
            if pos.has_key(predicate):
                predicateDictionary = pos[predicate]
                if object!=ANY: # predicate+object is given, subject unbound
                    if object in predicateDictionary:
                        for s in predicateDictionary[object].keys():
                            yield s, predicate, object
                    else: # given object not found
                        pass
                else: # predicate is given, object+subject unbound
                    for o in predicateDictionary.keys():
                        for s in predicateDictionary[o].keys():
                            yield s, predicate, o
        elif object!=ANY: # object is given, subject+predicate unbound
            pos = self.__get_pos(context)
            for p in pos.keys():
                predicateDictionary = pos[p]
                if object in predicateDictionary:
                    for s in predicateDictionary[object].keys():
                        yield s, p, object
                else: # given object not found
                    pass
        else: # subject+predicate+object unbound
            spo = self.__get_spo(context)
            for s in spo.keys():
                subjectDictionary = spo[s]
                for p in subjectDictionary.keys():
                    for o in subjectDictionary[p].keys():
                        yield s, p, o

    def open(self, file):
        _t = Transaction(None)

        def get_transaction(_t=_t):
            return _t
        
        import __builtin__
        __builtin__.get_transaction=get_transaction
        del __builtin__
        
        storage = FileStorage(file)
        self.db = db = DB(storage)
        try:
            db.pack()
        except:
            pass
        self.connection = connection = db.open()

        indices = connection.root()
        self.__check(indices)
        self.__indices = indices

    def commit(self):
        indices = self.connection.root()
        indices["spo"] = indices["spo"]
        indices["pos"] = indices["pos"]
        indices["contexts"] = indices["contexts"]        
        get_transaction().commit()
        
    def close(self):
        self.commit()
        self.connection.close()

    def contexts(self, triple=None):
        if triple:
            subject, predicate, object = triple
            indices = self.indices            
            # Contexts for triple
            spo = indices["spo"]
            try:
                po = spo[subject]
            except:
                po = spo[subject] = {}
            try:
                o = po[predicate]
            except:
                o = po[predicate] = {}
            try:
                c = o[object]
            except:
                c = o[object] = {}
            for context in c:
                yield context
        else:
            # All contexts
            contexts = self.indices["contexts"]
            for context in contexts.keys():
                yield context







