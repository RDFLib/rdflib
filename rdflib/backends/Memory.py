from __future__ import generators

ANY = None

from rdflib.backends import Backend

class Memory(Backend):
    """\
An in memory implementation of a triple store.

This triple store uses nested dictionaries to store triples. Each
triple is stored in two such indices as follows spo[s][p][o] = 1 and
pos[p][o][s] = 1.
    """    
    def __init__(self):
        super(Memory, self).__init__()
        self.context_aware = False
        # indexed by [subject][predicate][object]
        self.__spo = {}

        # indexed by [predicate][object][subject]
        self.__pos = {}

        # indexed by [predicate][object][subject]
        self.__osp = {}

        self.__namespace = {}
        self.__prefix = {}

    def add(self, (subject, predicate, object)):
        """\
        Add a triple to the store of triples.
        """
        # add dictionary entries for spo[s][p][p] = 1 and pos[p][o][s]
        # = 1, creating the nested dictionaries where they do not yet
        # exits.
        spo = self.__spo
        try:
            po = spo[subject]
        except:
            po = spo[subject] = {}
        try:
            o = po[predicate]
        except:
            o = po[predicate] = {}
        o[object] = 1
        
        pos = self.__pos
        try:
            os = pos[predicate]
        except:
            os = pos[predicate] = {}
        try:
            s = os[object]
        except:
            s = os[object] = {}
        s[subject] = 1

        osp = self.__osp
        try:
            sp = osp[object]
        except:
            sp = osp[object] = {}
        try:
            p = sp[subject]
        except:
            p = sp[subject] = {}
        p[predicate] = 1

    def remove(self, (subject, predicate, object)):
        for subject, predicate, object in self.triples((subject, predicate, object)):
            del self.__spo[subject][predicate][object]
            del self.__pos[predicate][object][subject]
            del self.__osp[object][subject][predicate]

    def triples(self, (subject, predicate, object)):
        """A generator over all the triples matching """
        if subject!=ANY: # subject is given
            spo = self.__spo
            if subject in spo:
                subjectDictionary = spo[subject]
                if predicate!=ANY: # subject+predicate is given
                    if predicate in subjectDictionary:
                        if object!=ANY: # subject+predicate+object is given
                            if object in subjectDictionary[predicate]:
                                yield (subject, predicate, object)
                            else: # given object not found
                                pass
                        else: # subject+predicate is given, object unbound
                            for o in subjectDictionary[predicate].keys():
                                yield (subject, predicate, o)
                    else: # given predicate not found
                        pass
                else: # subject given, predicate unbound
                    for p in subjectDictionary.keys():
                        if object!=ANY: # object is given
                            if object in subjectDictionary[p]:
                                yield (subject, p, object)
                            else: # given object not found
                                pass
                        else: # object unbound
                            for o in subjectDictionary[p].keys():
                                yield (subject, p, o)
            else: # given subject not found
                pass
        elif predicate!=ANY: # predicate is given, subject unbound
            pos = self.__pos
            if predicate in pos:
                predicateDictionary = pos[predicate]
                if object!=ANY: # predicate+object is given, subject unbound
                    if object in predicateDictionary:
                        for s in predicateDictionary[object].keys():
                            yield (s, predicate, object)
                    else: # given object not found
                        pass
                else: # predicate is given, object+subject unbound
                    for o in predicateDictionary.keys():
                        for s in predicateDictionary[o].keys():
                            yield (s, predicate, o)
        elif object!=ANY: # object is given, subject+predicate unbound
            osp = self.__osp
            if object in osp:
                objectDictionary = osp[object]
                for s in objectDictionary.keys():
                    for p in objectDictionary[s].keys():
                        yield (s, p, object)
        else: # subject+predicate+object unbound
            spo = self.__spo
            for s in spo.keys():
                subjectDictionary = spo[s]
                for p in subjectDictionary.keys():
                    for o in subjectDictionary[p].keys():
                        yield (s, p, o)

    def __len__(self):
        #@@ optimize
        i = 0
        for triple in self.triples((None, None, None)):
            i += 1
        return i
        
    def bind(self, prefix, namespace):
        self.__prefix[namespace] = prefix
        self.__namespace[prefix] = namespace

    def namespace(self, prefix):
        return self.__namespace.get(prefix, None)

    def prefix(self, namespace):
        return self.__prefix.get(namespace, None)

    def namespaces(self):
        for prefix, namespace in self.__namespace.iteritems():
            yield prefix, namespace
