from __future__ import generators
from BTrees.OOBTree import OOBTree

ANY = None


class BTreeStore(object):
    """An BTree based TripleStore backend.

This triple store uses BTrees with nested dictionaries to store
triples. Each triple is stored in two such indices as follows
spo[s][p][o] = 1 and pos[p][o][s] = 1.
    """    
    def __init__(self):
        super(BTreeStore, self).__init__()
        # indices["spo"] -- indexed by [subject][predicate][object]
        # indices["pos"] -- indexed by [predicate][object][subject]

    def open(self, file):
        # setup the database
        storage = FileStorage(file)
        db = DB(storage)
        try:
            db.pack()
        except:
            pass
        self.connection = connection = db.open()
        self.set_indices(connection.root())

    def close(self):
        indices = self.connection.root()
        indices["spo"] = indices["spo"]
        indices["pos"] = indices["pos"]
        get_transaction().commit()        
        self.connection.close()

    def set_indices(self, indices):
        if not indices.has_key("spo"):
            indices["spo"] = OOBTree()
        if not indices.has_key("pos"):
            indices["pos"] = OOBTree()
        self.__spo = indices["spo"]
        self.__pos = indices["pos"]                

    def add(self, (subject, predicate, object)):
        """\
        Add a triple to the store of triples.
        """
        # add dictionary entries for spo[s][p][p] = 1 and pos[p][o][s]
        # = 1, creating the nested dictionaries where they do not yet
        # exits.
        spo = self.__spo
        pos = self.__pos
        if not spo.has_key(subject):
            sp = spo[subject] = {}
        else:
            sp = spo[subject]
        sp.setdefault(predicate, {})[object] = 1

        if not pos.has_key(predicate):
            po = pos[predicate] = {}
        else:
            po = pos[predicate]
        po.setdefault(object, {})[subject] = 1

        spo[subject] = spo[subject]
        pos[predicate] = pos[predicate]        

    def remove(self, (subject, predicate, object)):
        spo = self.__spo
        pos = self.__pos
        del spo[subject][predicate][object]
        del pos[predicate][object][subject]
        spo[subject] = spo[subject]
        pos[predicate] = pos[predicate]        

    def triples(self, (subject, predicate, object)):
        """A generator over all the triples matching """
        if subject!=ANY: # subject is given
            spo = self.__spo
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
                            for o in subjectDictionary[predicate]:
                                yield subject, predicate, o
                    else: # given predicate not found
                        pass
                else: # subject given, predicate unbound
                    for p in subjectDictionary:
                        if object!=ANY: # object is given
                            if object in subjectDictionary[p]:
                                yield subject, p, object
                            else: # given object not found
                                pass
                        else: # object unbound
                            for o in subjectDictionary[p]:
                                yield subject, p, o
            else: # given subject not found
                pass
        elif predicate!=ANY: # predicate is given, subject unbound
            pos = self.__pos
            if pos.has_key(predicate):
                predicateDictionary = pos[predicate]
                if object!=ANY: # predicate+object is given, subject unbound
                    if object in predicateDictionary:
                        for s in predicateDictionary[object]:
                            yield s, predicate, object
                    else: # given object not found
                        pass
                else: # predicate is given, object+subject unbound
                    for o in predicateDictionary:
                        for s in predicateDictionary[o]:
                            yield s, predicate, o
        elif object!=ANY: # object is given, subject+predicate unbound
            pos = self.__pos
            for p in pos.keys():
                predicateDictionary = pos[p]
                if object in predicateDictionary:
                    for s in predicateDictionary[object]:
                        yield s, p, object
                else: # given object not found
                    pass
        else: # subject+predicate+object unbound
            spo = self.__spo
            for s in spo.keys():
                subjectDictionary = spo[s]
                for p in subjectDictionary:
                    for o in subjectDictionary[p]:
                        yield s, p, o

