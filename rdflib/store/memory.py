from __future__ import generators

ANY = None

from rdflib.store import Store

class Memory(Store):
    """\
An in memory implementation of a triple store.

This triple store uses nested dictionaries to store triples. Each
triple is stored in two such indices as follows spo[s][p][o] = 1 and
pos[p][o][s] = 1.
    """
    def __init__(self, configuration=None, identifier=None):
        super(Memory, self).__init__(configuration)
        self.identifier = identifier

        # indexed by [subject][predicate][object]
        self.__spo = {}

        # indexed by [predicate][object][subject]
        self.__pos = {}

        # indexed by [predicate][object][subject]
        self.__osp = {}

        self.__namespace = {}
        self.__prefix = {}

    def add(self, (subject, predicate, object), context, quoted=False):
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

    def remove(self, (subject, predicate, object), context=None):
        for (subject, predicate, object), c in self.triples((subject, predicate, object)):
            del self.__spo[subject][predicate][object]
            del self.__pos[predicate][object][subject]
            del self.__osp[object][subject][predicate]

    def triples(self, (subject, predicate, object), context=None):
        """A generator over all the triples matching """
        if subject!=ANY: # subject is given
            spo = self.__spo
            if subject in spo:
                subjectDictionary = spo[subject]
                if predicate!=ANY: # subject+predicate is given
                    if predicate in subjectDictionary:
                        if object!=ANY: # subject+predicate+object is given
                            if object in subjectDictionary[predicate]:
                                yield (subject, predicate, object), self.__contexts()
                            else: # given object not found
                                pass
                        else: # subject+predicate is given, object unbound
                            for o in subjectDictionary[predicate].keys():
                                yield (subject, predicate, o), self.__contexts()
                    else: # given predicate not found
                        pass
                else: # subject given, predicate unbound
                    for p in subjectDictionary.keys():
                        if object!=ANY: # object is given
                            if object in subjectDictionary[p]:
                                yield (subject, p, object), self.__contexts()
                            else: # given object not found
                                pass
                        else: # object unbound
                            for o in subjectDictionary[p].keys():
                                yield (subject, p, o), self.__contexts()
            else: # given subject not found
                pass
        elif predicate!=ANY: # predicate is given, subject unbound
            pos = self.__pos
            if predicate in pos:
                predicateDictionary = pos[predicate]
                if object!=ANY: # predicate+object is given, subject unbound
                    if object in predicateDictionary:
                        for s in predicateDictionary[object].keys():
                            yield (s, predicate, object), self.__contexts()
                    else: # given object not found
                        pass
                else: # predicate is given, object+subject unbound
                    for o in predicateDictionary.keys():
                        for s in predicateDictionary[o].keys():
                            yield (s, predicate, o), self.__contexts()
        elif object!=ANY: # object is given, subject+predicate unbound
            osp = self.__osp
            if object in osp:
                objectDictionary = osp[object]
                for s in objectDictionary.keys():
                    for p in objectDictionary[s].keys():
                        yield (s, p, object), self.__contexts()
        else: # subject+predicate+object unbound
            spo = self.__spo
            for s in spo.keys():
                subjectDictionary = spo[s]
                for p in subjectDictionary.keys():
                    for o in subjectDictionary[p].keys():
                        yield (s, p, o), self.__contexts()

    def __len__(self, context=None):
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

    def __contexts(self):
        return (c for c in []) # TODO: best way to return empty generator

# Authors: Michel Pelletier, Daniel Krech, Stefan Niederhauser

Any = None

from rdflib.term import BNode
from rdflib.store import Store

class IOMemory(Store):
    """\
    An integer-key-optimized-context-aware-in-memory store.

    Uses nested dictionaries to store triples and context. Each triple
    is stored in six such indices as follows cspo[c][s][p][o] = 1
    and cpos[c][p][o][s] = 1 and cosp[c][o][s][p] = 1 as well as
    spo[s][p][o] = [c] and pos[p][o][s] = [c] and pos[o][s][p] = [c]

    Context information is used to track the 'source' of the triple
    data for merging, unmerging, remerging purposes.  context aware
    store stores consume more memory size than non context stores.

    """

    context_aware = True
    formula_aware = True

    def __init__(self, configuration=None, identifier=None):
        super(IOMemory, self).__init__()

        # indexed by [context][subject][predicate][object] = 1
        self.cspo = self.createIndex()

        # indexed by [context][predicate][object][subject] = 1
        self.cpos = self.createIndex()

        # indexed by [context][object][subject][predicate] = 1
        self.cosp = self.createIndex()

        # indexed by [subject][predicate][object] = [context]
        self.spo = self.createIndex()

        # indexed by [predicate][object][subject] = [context]
        self.pos = self.createIndex()

        # indexed by [object][subject][predicate] = [context]
        self.osp = self.createIndex()

        # indexes integer keys to identifiers
        self.forward = self.createForward()

        # reverse index of forward
        self.reverse = self.createReverse()

        self.identifier = identifier or BNode()

        self.__namespace = self.createPrefixMap()
        self.__prefix = self.createPrefixMap()

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

    def defaultContext(self):
        return self.default_context

    def addContext(self, context):
        """ Add context w/o adding statement. Dan you can remove this if you want """

        if not self.reverse.has_key(context):
            ci=randid()
            while not self.forward.insert(ci, context):
                ci=randid()
            self.reverse[context] = ci

    def intToIdentifier(self, (si, pi, oi)):
        """ Resolve an integer triple into identifers. """
        return (self.forward[si], self.forward[pi], self.forward[oi])

    def identifierToInt(self, (s, p, o)):
        """ Resolve an identifier triple into integers. """
        return (self.reverse[s], self.reverse[p], self.reverse[o])

    def uniqueSubjects(self, context=None):
        if context is None:
            index = self.spo
        else:
            index = self.cspo[context]
        for si in index.keys():
            yield self.forward[si]

    def uniquePredicates(self, context=None):
        if context is None:
            index = self.pos
        else:
            index = self.cpos[context]
        for pi in index.keys():
            yield self.forward[pi]

    def uniqueObjects(self, context=None):
        if context is None:
            index = self.osp
        else:
            index = self.cosp[context]
        for oi in index.keys():
            yield self.forward[oi]

    def createForward(self):
        return {}

    def createReverse(self):
        return {}

    def createIndex(self):
        return {}

    def createPrefixMap(self):
        return {}

    def add(self, triple, context, quoted=False):
        """\
        Add a triple to the store.
        """
        Store.add(self, triple, context, quoted)
        for triple, cg in self.triples(triple, context):
            #triple is already in the store.
            return

        subject, predicate, object = triple

        f = self.forward
        r = self.reverse

        # assign keys for new identifiers

        if not r.has_key(subject):
            si=randid()
            while f.has_key(si):
                si=randid()
            f[si] = subject
            r[subject] = si
        else:
            si = r[subject]

        if not r.has_key(predicate):
            pi=randid()
            while f.has_key(pi):
                pi=randid()
            f[pi] = predicate
            r[predicate] = pi
        else:
            pi = r[predicate]

        if not r.has_key(object):
            oi=randid()
            while f.has_key(oi):
                oi=randid()
            f[oi] = object
            r[object] = oi
        else:
            oi = r[object]

        if not r.has_key(context):
            ci=randid()
            while f.has_key(ci):
                ci=randid()
            f[ci] = context
            r[context] = ci
        else:
            ci = r[context]

        # add dictionary entries for cspo[c][s][p][o] = 1,
        # cpos[c][p][o][s] = 1, and cosp[c][o][s][p] = 1, creating the
        # nested {} where they do not yet exits.
        self._setNestedIndex(self.cspo, ci, si, pi, oi)
        self._setNestedIndex(self.cpos, ci, pi, oi, si)
        self._setNestedIndex(self.cosp, ci, oi, si, pi)

        if not quoted:
            self._setNestedIndex(self.spo, si, pi, oi, ci)
            self._setNestedIndex(self.pos, pi, oi, si, ci)
            self._setNestedIndex(self.osp, oi, si, pi, ci)

    def _setNestedIndex(self, index, *keys):
        for key in keys[:-1]:
            if not index.has_key(key):
                index[key] = self.createIndex()
            index = index[key]
        index[keys[-1]] = 1


    def _removeNestedIndex(self, index, *keys):
        """ Remove context from the list of contexts in a nested index.

        Afterwards, recursively remove nested indexes when they became empty.
        """
        parents = []
        for key in keys[:-1]:
            parents.append(index)
            index = index[key]
        del index[keys[-1]]

        n = len(parents)
        for i in xrange(n):
            index = parents[n-1-i]
            key = keys[n-1-i]
            if len(index[key]) == 0:
                del index[key]

    def remove(self, triple, context=None):
        Store.remove(self, triple, context)
        if context is not None:
            if context == self:
                context = None

        f = self.forward
        r = self.reverse
        if context is None:
            for triple, cg in self.triples(triple):
                subject, predicate, object = triple
                si, pi, oi = self.identifierToInt((subject, predicate, object))
                contexts = list(self.contexts(triple))
                for context in contexts:
                    ci = r[context]
                    del self.cspo[ci][si][pi][oi]
                    del self.cpos[ci][pi][oi][si]
                    del self.cosp[ci][oi][si][pi]

                    self._removeNestedIndex(self.spo, si, pi, oi, ci)
                    self._removeNestedIndex(self.pos, pi, oi, si, ci)
                    self._removeNestedIndex(self.osp, oi, si, pi, ci)
                    # grr!! hafta ref-count these before you can collect them dumbass!
                    #del f[si], f[pi], f[oi]
                    #del r[subject], r[predicate], r[object]
        else:
            subject, predicate, object = triple
            ci = r.get(context, None)
            if ci:
                for triple, cg in self.triples(triple, context):
                    si, pi, oi = self.identifierToInt(triple)
                    del self.cspo[ci][si][pi][oi]
                    del self.cpos[ci][pi][oi][si]
                    del self.cosp[ci][oi][si][pi]

                    try:
                        self._removeNestedIndex(self.spo, si, pi, oi, ci)
                        self._removeNestedIndex(self.pos, pi, oi, si, ci)
                        self._removeNestedIndex(self.osp, oi, si, pi, ci)
                    except KeyError:
                        # the context may be a quoted one in which
                        # there will not be a triple in spo, pos or
                        # osp. So ignore any KeyErrors
                        pass
                    # TODO delete references to resources in self.forward/self.reverse
                    # that are not in use anymore...

            if subject is None and predicate is None and object is None:
                # remove context
                try:
                    ci = self.reverse[context]
                    del self.cspo[ci], self.cpos[ci], self.cosp[ci]
                except KeyError:
                    # TODO: no exception when removing non-existant context?
                    pass


    def triples(self, triple, context=None):
        """A generator over all the triples matching """

        if context is not None:
            if context == self:
                context = None

        subject, predicate, object = triple
        ci = si = pi = oi = Any

        if context is None:
            spo = self.spo
            pos = self.pos
            osp = self.osp
        else:
            try:
                ci = self.reverse[context]  # TODO: Really ignore keyerror here
                spo = self.cspo[ci]
                pos = self.cpos[ci]
                osp = self.cosp[ci]
            except KeyError:
                return
        try:
            if subject is not Any:
                si = self.reverse[subject] # throws keyerror if subject doesn't exist ;(
            if predicate is not Any:
                pi = self.reverse[predicate]
            if object is not Any:
                oi = self.reverse[object]
        except KeyError, e:
            return #raise StopIteration

        if si != Any: # subject is given
            if spo.has_key(si):
                subjectDictionary = spo[si]
                if pi != Any: # subject+predicate is given
                    if subjectDictionary.has_key(pi):
                        if oi!= Any: # subject+predicate+object is given
                            if subjectDictionary[pi].has_key(oi):
                                ss, pp, oo = self.intToIdentifier((si, pi, oi))
                                yield (ss, pp, oo), (c for c in self.contexts((ss, pp, oo)))
                            else: # given object not found
                                pass
                        else: # subject+predicate is given, object unbound
                            for o in subjectDictionary[pi].keys():
                                ss, pp, oo = self.intToIdentifier((si, pi, o))
                                yield (ss, pp, oo), (c for c in self.contexts((ss, pp, oo)))
                    else: # given predicate not found
                        pass
                else: # subject given, predicate unbound
                    for p in subjectDictionary.keys():
                        if oi != Any: # object is given
                            if subjectDictionary[p].has_key(oi):
                                ss, pp, oo = self.intToIdentifier((si, p, oi))
                                yield (ss, pp, oo), (c for c in self.contexts((ss, pp, oo)))
                            else: # given object not found
                                pass
                        else: # object unbound
                            for o in subjectDictionary[p].keys():
                                ss, pp, oo = self.intToIdentifier((si, p, o))
                                yield (ss, pp, oo), (c for c in self.contexts((ss, pp, oo)))
            else: # given subject not found
                pass
        elif pi != Any: # predicate is given, subject unbound
            if pos.has_key(pi):
                predicateDictionary = pos[pi]
                if oi != Any: # predicate+object is given, subject unbound
                    if predicateDictionary.has_key(oi):
                        for s in predicateDictionary[oi].keys():
                            ss, pp, oo = self.intToIdentifier((s, pi, oi))
                            yield (ss, pp, oo), (c for c in self.contexts((ss, pp, oo)))
                    else: # given object not found
                        pass
                else: # predicate is given, object+subject unbound
                    for o in predicateDictionary.keys():
                        for s in predicateDictionary[o].keys():
                            ss, pp, oo = self.intToIdentifier((s, pi, o))
                            yield (ss, pp, oo), (c for c in self.contexts((ss, pp, oo)))
        elif oi != Any: # object is given, subject+predicate unbound
            if osp.has_key(oi):
                objectDictionary = osp[oi]
                for s in objectDictionary.keys():
                    for p in objectDictionary[s].keys():
                        ss, pp, oo = self.intToIdentifier((s, p, oi))
                        yield (ss, pp, oo), (c for c in self.contexts((ss, pp, oo)))
        else: # subject+predicate+object unbound
            for s in spo.keys():
                subjectDictionary = spo[s]
                for p in subjectDictionary.keys():
                    for o in subjectDictionary[p].keys():
                        ss, pp, oo = self.intToIdentifier((s, p, o))
                        yield (ss, pp, oo), (c for c in self.contexts((ss, pp, oo)))

    def __len__(self, context=None):

        if context is not None:
            if context == self:
                context = None

        # TODO: for eff. implementation
        count = 0
        for triple, cg in self.triples((Any, Any, Any), context):
            count += 1
        return count

    def contexts(self, triple=None):
        if triple:
            si, pi, oi = self.identifierToInt(triple)
            for ci in self.spo[si][pi][oi]:
                yield self.forward[ci]
        else:
            for ci in self.cspo.keys():
                yield self.forward[ci]




import random

def randid(randint=random.randint, choice=random.choice, signs=(-1,1)):
    return choice(signs)*randint(1,2000000000)

del random
