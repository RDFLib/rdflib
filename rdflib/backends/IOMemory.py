#############################################################################
#
# Copyright (c) 2004-1005 Michel Pelletier
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

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
        
        # indexed by [subject][predicate][object] = 1
        self.cspo = self.createIndex()

        # indexed by [predicate][object][subject] = 1
        self.cpos = self.createIndex()

        # indexed by [object][subject][predicate] = 1
        self.cosp = self.createIndex()

        # indexes integer keys to identifiers
        self.forward = self.createForward()

        # reverse index of forward
        self.reverse = self.createReverse()

        if default_context is None:
            default_context = BNode()
            
        self.default_context = default_context

        self.ns_prefix_map = self.createPrefixMap()
        self.prefix_ns_map = self.createPrefixMap()

        self.count = 0

    def _get_ns_prefix_map(self):
        return self.ns_prefix_map

    def _get_prefix_ns_map(self):
        return self.prefix_ns_map

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

    def uniqueSubjects(self, context=None):
        for si in self.cspo[context].keys():
            yield self.forward[si]

    def uniquePredicates(self, context=None):
        for pi in self.cpos[context].keys():
            yield self.forward[pi]

    def uniqueObjects(self, context=None):
        for oi in self.cosp[context].keys():
            yield self.forward[oi]

    def createForward(self):
        return {}

    def createReverse(self):
        return {}

    def createIndex(self):
        return {}

    def createPrefixMap(self):
        return {}

    def add(self, triple):
        """\
        Add a triple to the store.
        """

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

        # assign cspo[c][s][p][o] = 1

        if self.cspo.has_key(ci):
            spo = self.cspo[ci]
        else:
            spo = self.cspo[ci] = self.createIndex()
        if spo.has_key(si):
            po = spo[si]
        else:
            po = spo[si] = self.createIndex()
        if po.has_key(pi):
            o = po[pi]
        else:
            o = po[pi] = self.createIndex()
        o[oi] = 1

        # cpos[c][p][o][s] = 1

        if self.cpos.has_key(ci):
            pos = self.cpos[ci]
        else:
            pos = self.cpos[ci] = self.createIndex()
        if pos.has_key(pi):
            os = pos[pi]
        else:
            os = pos[pi] = self.createIndex()
        if os.has_key(oi):
            s = os[oi]
        else:
            s = os[oi] = self.createIndex()
        s[si] = 1

        # cosp[c][o][s][p] = 1

        if self.cosp.has_key(ci):
            osp = self.cosp[ci]
        else:
            osp = self.cosp[ci] = self.createIndex()
        if osp.has_key(oi):
            sp = osp[oi]
        else:
            sp = osp[oi] = self.createIndex()
        if sp.has_key(si):
            p = sp[si]
        else:
            p = sp[si] = self.createIndex()
        p[pi] = 1

        # TODO: check that triple wasn't already in the store.
        self.count = self.count + 1

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
