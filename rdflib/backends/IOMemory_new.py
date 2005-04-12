# Authors: Michel Pelletier, Daniel Krech

Any = None

from rdflib import Triple, BNode
from rdflib.backends import Backend

class IOMemory(Backend):
    """\
    An integer-key-optimized-context-aware-in-memory backend.

    Uses nested dictionaries to store triples and context. Each triple
    is stored in three such indices as follows cspo[c][s][p][o] = 1
    and cpos[c][p][o][s] = 1 and cosp[c][o][s][p] = 1.

    Context information is used to track the 'source' of the triple
    data for merging, unmerging, remerging purposes.  context aware
    store backends consume more memory size than non context backends.

    """    

    def __init__(self, default_context=None):
        super(IOMemory, self).__init__()
        
        # indexed by [subject][predicate][object][context]
        self.spoc = self.create_index()

        # indexed by [predicate][object][subject][context]
        self.posc = self.create_index()

        # indexed by [object][subject][predicate][context]
        self.ospc = self.create_index()

        # indexed by [context][subject][predicate][object]
        self.cspo = self.create_index()

        # indexes integer keys to identifiers
        self.forward = self.create_forward()

        # reverse index of forward
        self.reverse = self.create_reverse()

        if default_context is None:
            default_context = BNode()
            
        self.default_context = default_context

        self.__namespace = self.createPrefixMap()
        self.__prefix = self.createPrefixMap()

        self.count = 0

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

    def intToIdentifier(self, (si, pi, oi, ci)):
        """ Resolve an integer triple into identifers. """
        return (self.forward[si], self.forward[pi], self.forward[oi], self.forward[ci])

    def identifierToInt(self, (s, p, o)):
        """ Resolve an identifier triple into integers. """
        return (self.reverse[s], self.reverse[p], self.reverse[o])

    def unique_subjects(self, context=None):
        for si in self.spoc.keys():
            yield self.forward[si]

    def unique_predicates(self, context=None):
        for pi in self.posc.keys():
            yield self.forward[pi]

    def unique_objects(self, context=None):
        for oi in self.ospc.keys():
            yield self.forward[oi]

    def create_forward(self):
        return {}

    def create_reverse(self):
        return {}

    def create_index(self):
        return {}

    def createPrefixMap(self):
        return {}

    def add(self, triple):
        """\
        Add a triple to the store.
        """

        for triple in self.triples(triple):
            #triple is already in the store.            
            return
        self.count = self.count + 1

        subject, predicate, object = triple
        context = triple.context or self.default_context
        
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

        # assign [s][p][o][c]

        if self.spoc.has_key(si):
            poc = self.spoc[si]
        else:
            poc = spoc[si] = self.create_index()
        if poc.has_key(pi):
            oc = poc[pi]
        else:
            oc = poc[pi] = self.create_index()
        if oc.has_key(oi):
            c = oc[oi]
        else:
            c = oc[oi] = self.create_index()
        c[ci] = 1

        # assign [p][o][s][c]

        if self.posc.has_key(pi):
            osc = self.posc[pi]
        else:
            osc = self.posc[pi] = self.create_index()
        if osc.has_key(oi):
            sc = poc[oi]
        else:
            sc = osc[oi] = self.create_index()
        if sc.has_key(si):
            c = sc[si]
        else:
            c = sc[ci] = self.create_index()
        c[ci] = 1

        # assign [o][s][p][c]

        if self.ospc.has_key(oi):
            spc = self.ospc[oi]
        else:
            spc = self.ospc[oi] = self.create_index()
        if spc.has_key(si):
            pc = scp[si]
        else:
            pc = scp[si] = self.create_index()
        if pc.has_key(pi):
            c = pc[pi]
        else:
            c = pc[pi] = self.create_index()
        c[ci] = 1

        # assign [c][s][p][o]

        if self.cspo.has_key(ci):
            spo = self.cspo[ci]
        else:
            spo = self.cspo[ci] = self.create_index()
        if spo.has_key(si):
            po = spo[si]
        else:
            po = spo[si] = self.create_index()
        if po.has_key(pi):
            o = po[pi]
        else:
            o = po[pi] = self.create_index()
        o[oi] = 1

    def remove_context(self, context):
        self.remove(Triple(Any, Any, Any, context))

    def remove(self, triple):
        f = self.forward
        r = self.reverse
        for triple in self.triples(triple):
            try:
                subject, predicate, object = triple        
                si, pi, oi = self.identifierToInt((subject, predicate, object))
                context = triple.context            
                ci = r[context]
                del self.cspo[ci][si][pi][oi]
                del self.cpos[ci][pi][oi][si]
                del self.cosp[ci][oi][si][pi]
                self.count = self.count - 1
            except KeyError:
                continue

            # grr!! hafta ref-count these before you can collect them dumbass!
#             del f[si]
#             del f[pi]
#             del f[oi]
#             del r[subject]
#             del r[predicate]
#             del r[object]



    def triples(self, triple):
        """A generator over all the triples matching """
        subject, predicate, object = triple
        context = triple.context
        if context is None:
            # TODO: this needs to be replaced with something more efficient
            for c in self.contexts():
                triple.context = c
                for triple in self.triples(triple):
                    yield triple
            return

        ci = si = pi = oi = Any
        try:
            ci = self.reverse[context]  # throws a keyerror if not context
            if subject is not Any:
                si = self.reverse[subject] # throws keyerror if subject doesn't exist ;(
            if predicate is not Any:
                pi = self.reverse[predicate]
            if object is not Any:
                oi = self.reverse[object]
        except KeyError, e:
            return #raise StopIteration

        if si != Any: # subject is given
            spo = self.cspo[ci]
            if spo.has_key(si):
                subjectDictionary = spo[si]
                if pi != Any: # subject+predicate is given
                    if subjectDictionary.has_key(pi):
                        if oi!= Any: # subject+predicate+object is given
                            if subjectDictionary[pi].has_key(oi):
                                ss, pp, oo, cc = self.intToIdentifier((si, pi, oi, ci))
                                yield Triple(ss, pp, oo, cc)
                            else: # given object not found
                                pass
                        else: # subject+predicate is given, object unbound
                            for o in subjectDictionary[pi].keys():
                                ss, pp, oo, cc = self.intToIdentifier((si, pi, o, ci))
                                yield Triple(ss, pp, oo, cc)
                    else: # given predicate not found
                        pass
                else: # subject given, predicate unbound
                    for p in subjectDictionary.keys():
                        if oi != Any: # object is given
                            if subjectDictionary[p].has_key(oi):
                                ss, pp, oo, cc = self.intToIdentifier((si, p, oi, ci))
                                yield Triple(ss, pp, oo, cc)
                            else: # given object not found
                                pass
                        else: # object unbound
                            for o in subjectDictionary[p].keys():
                                ss, pp, oo, cc = self.intToIdentifier((si, p, o, ci))    
                                yield Triple(ss, pp, oo, cc)
            else: # given subject not found
                pass
        elif pi != Any: # predicate is given, subject unbound
            pos = self.cpos[ci]
            if pos.has_key(pi):
                predicateDictionary = pos[pi]
                if oi != Any: # predicate+object is given, subject unbound
                    if predicateDictionary.has_key(oi):
                        for s in predicateDictionary[oi].keys():
                            ss, pp, oo, cc = self.intToIdentifier((s, pi, oi, ci))
                            yield Triple(ss, pp, oo, cc)
                    else: # given object not found
                        pass
                else: # predicate is given, object+subject unbound
                    for o in predicateDictionary.keys():
                        for s in predicateDictionary[o].keys():
                            ss, pp, oo, cc = self.intToIdentifier((s, pi, o, ci))
                            yield Triple(ss, pp, oo, cc)
        elif oi != Any: # object is given, subject+predicate unbound
            osp = self.cosp[ci]
            if osp.has_key(oi):
                objectDictionary = osp[oi]
                for s in objectDictionary.keys():
                    for p in objectDictionary[s].keys():
                        ss, pp, oo, cc = self.intToIdentifier((s, p, oi, ci))
                        yield Triple(ss, pp, oo, cc)
        else: # subject+predicate+object unbound
            spo = self.cspo[ci]
            for s in spo.keys():
                subjectDictionary = spo[s]
                for p in subjectDictionary.keys():
                    for o in subjectDictionary[p].keys():
                        ss, pp, oo, cc = self.intToIdentifier((s, p, o, ci))
                        yield Triple(ss, pp, oo, cc)

    def __len__(self):
        return self.count
        #

    def contexts(self, triple=None):
        for ci in self.cspo.keys():
            yield self.forward[ci]




import random

def randid(randint=random.randint, choice=random.choice, signs=(-1,1)):
    return choice(signs)*randint(1,2000000000)

del random
