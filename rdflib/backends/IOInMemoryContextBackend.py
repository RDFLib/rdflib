##############################################################################
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

class IOInMemoryContextBackend(object):
    """\
    An integer-key-optimized-context-aware-in-memory backend.

    Uses nested dictionaries to store triples and context. Each triple
    is stored in three such indices as follows cspo[c][s][p][o] = 1
    and cpos[c][p][o][s] = 1 and cosp[c][o][s][p] = 1.

    Context information is used to track the 'source' of the triple
    data for merging, unmerging, remerging purposes.  context aware
    store backends consume more memory size than non context backends.

    """    

    def __init__(self):
        
        # indexed by [subject][predicate][object] = 1
        self.cspo = {}

        # indexed by [predicate][object][subject] = 1
        self.cpos = {}

        # indexed by [object][subject][predicate] = 1
        self.cosp = {}

        # indexes integer keys to identifiers
        self.forward = {}

        # reverse index of forward
        self.reverse = {}

        self.count = 0

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
        for si in self.cspo[context].keys():
            yield self.forward[si]

    def uniquePredicates(self, context=None):
        for pi in self.cpos[context].keys():
            yield self.forward[pi]

    def uniqueObjects(self, context=None):
        for oi in self.cosp[context].keys():
            yield self.forward[oi]

    def add(self, (subject, predicate, object), context=None):
        """\
        Add a triple to the store.
        """

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
            spo = self.cspo[ci] = {}
        if spo.has_key(si):
            po = spo[si]
        else:
            po = spo[si] = {}
        if po.has_key(pi):
            o = po[pi]
        else:
            o = po[pi] = {}
        o[oi] = 1

        # cpos[c][p][o][s] = 1

        if self.cpos.has_key(ci):
            pos = self.cpos[ci]
        else:
            pos = self.cpos[ci] = {}
        if pos.has_key(pi):
            os = pos[pi]
        else:
            os = pos[pi] = {}
        if os.has_key(oi):
            s = os[oi]
        else:
            s = os[oi] = {}
        s[si] = 1

        # cosp[c][o][s][p] = 1

        if self.cosp.has_key(ci):
            osp = self.cosp[ci]
        else:
            osp = self.cosp[ci] = {}
        if osp.has_key(oi):
            sp = osp[oi]
        else:
            sp = osp[oi] = {}
        if sp.has_key(si):
            p = sp[si]
        else:
            p = sp[si] = {}
        p[pi] = 1

        # TODO: check that triple wasn't already in the store.
        self.count = self.count + 1

    def remove(self, (subject, predicate, object), context=None):
        for subject, predicate, object in self.triples((subject, predicate, object), context):
            si, pi, oi = self.identifierToInt((subject, predicate, object))
            f = self.forward
            r = self.reverse
            del self.cspo[context][si][pi][oi]
            del self.cpos[context][pi][oi][si]
            del self.cosp[context][oi][si][pi]

            self.count = self.count - 1

            # grr!! hafta ref-count these before you can collect them dumbass!
#             del f[si]
#             del f[pi]
#             del f[oi]
#             del r[subject]
#             del r[predicate]
#             del r[object]

    def triples(self, (subject, predicate, object), context=None):
        """A generator over all the triples matching """

        if context is None:
            # TODO: this needs to be replaced with something more efficient
            for context in self.contexts():
                for triple in self.triples((subject, predicate, object), context):
                    yield triple

        si = pi = oi = Any
        ci = self.reverse[context]  # throws a keyerror if not context
        if subject is not Any:
            si = self.reverse[subject] # throws keyerror if subject doesn't exist ;(
        if predicate is not Any:
            pi = self.reverse[predicate]
        if object is not Any:
            oi = self.reverse[object]

        if si != Any: # subject is given
            spo = self.cspo[ci]
            if spo.has_key(si):
                subjectDictionary = spo[si]
                if pi != Any: # subject+predicate is given
                    if subjectDictionary.has_key(pi):
                        if oi!= Any: # subject+predicate+object is given
                            if subjectDictionary[pi].has_key(oi):
                                yield self.intToIdentifier((si, pi, oi))
                            else: # given object not found
                                pass
                        else: # subject+predicate is given, object unbound
                            for o in subjectDictionary[pi].keys():
                                yield self.intToIdentifier((si, pi, o))
                    else: # given predicate not found
                        pass
                else: # subject given, predicate unbound
                    for p in subjectDictionary.keys():
                        if oi != Any: # object is given
                            if subjectDictionary[p].has_key(oi):
                                yield self.intToIdentifier((si, p, oi))
                            else: # given object not found
                                pass
                        else: # object unbound
                            for o in subjectDictionary[p].keys():
                                yield self.intToIdentifier((si, p, o))
            else: # given subject not found
                pass
        elif pi != Any: # predicate is given, subject unbound
            pos = self.cpos[ci]
            if pos.has_key(pi):
                predicateDictionary = pos[pi]
                if oi != Any: # predicate+object is given, subject unbound
                    if predicateDictionary.has_key(oi):
                        for s in predicateDictionary[oi].keys():
                            yield self.intToIdentifier((s, pi, oi))
                    else: # given object not found
                        pass
                else: # predicate is given, object+subject unbound
                    for o in predicateDictionary.keys():
                        for s in predicateDictionary[o].keys():
                            yield self.intToIdentifier((s, pi, o))
        elif oi != Any: # object is given, subject+predicate unbound
            osp = self.cosp[ci]
            if osp.has_key(oi):
                objectDictionary = osp[oi]
                for s in objectDictionary.keys():
                    for p in objectDictionary[s].keys():
                        yield self.intToIdentifier((s, p, oi))
        else: # subject+predicate+object unbound
            spo = self.cspo[ci]
            for s in spo.keys():
                subjectDictionary = spo[s]
                for p in subjectDictionary.keys():
                    for o in subjectDictionary[p].keys():
                        yield self.intToIdentifier((s, p, o))

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
