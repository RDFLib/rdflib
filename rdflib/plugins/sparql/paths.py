from rdflib.py3compat import PY3  # format_doctest_out
if PY3:
    __doc__ = """

This module implements the SPARQL 1.1 Property path operators, as defined in:

http://www.w3.org/TR/sparql11-query/#propertypaths

In SPARQL the syntax is as follows:

iri     - An IRI. A path of length one.

^elt        - Inverse path (object to subject).

elt1 / elt2 - A sequence path of elt1 followed by elt2.

elt1 | elt2 - A alternative path of elt1 or elt2 (all possibilities are tried).

elt*        - A path that connects the subject and object of the path by zero
    or more matches of elt.

elt+        - A path that connects the subject and object of the path by one
    or more matches of elt.

elt?        - A path that connects the subject and object of the path by zero
    or one matches of elt.

!iri or !(iri1| ...|irin) - Negated property set. An IRI which is not one of
    irii. !iri is short for !(iri).

!^iri or !(^iri1| ...|^irin) -  Negated property set where the excluded matches
    are based on reversed path. That is, not one of iri1...irin as
    reverse paths. !^iri is short for !(^iri).

!(iri1| ...|irij|^irij+1| ...|^irin) - A combination of forward and reverse
    properties in a negated property set.
(elt)       A group path elt, brackets control precedence.


This module is used internally be the SPARQL engine, but they property paths
can also be used to query RDFLib Graphs directly.

Where possible the SPARQL syntax is mapped to python operators, and property
path objects can be constructed from existing URIRefs.

(NOTE: This version monkey-patches the operators and path-aware triples
functions into the URIRef and Graph class, when rdflib-sparql is merged
into core rdflib it will be cleaner)

>>> foaf=Namespace('http://xmlns.com/foaf/0.1/')

>>> ~foaf.knows
Path(~http://xmlns.com/foaf/0.1/knows)

>>> foaf.knows/foaf.name
Path(http://xmlns.com/foaf/0.1/knows / http://xmlns.com/foaf/0.1/name)

>>> foaf.name|foaf.firstName
Path(http://xmlns.com/foaf/0.1/name | http://xmlns.com/foaf/0.1/firstName)

Modifiers (?, *, +) are done using % and the strings '*', '?', '+', also
defined as constants in this file

>>> foaf.knows%OneOrMore
Path(http://xmlns.com/foaf/0.1/knows+)

The path objects can be used with the normal graph methods.

First some example data:

>>> g=Graph()

>>> g=g.parse(data='''
... @prefix : <ex:> .
...
... :a :p1 :c ; :p2 :f .
... :c :p2 :e ; :p3 :g .
... :g :p3 :h ; :p2 :j .
... :h :p3 :a ; :p2 :g .
...
... :q :px :q .
...
... ''', format='n3') # doctest: +ELLIPSIS

>>> e=Namespace('ex:')

Graph contains:
>>> (e.a, e.p1/e.p2, e.e) in g
True

Graph generator functions, triples, subjects, objects, etc. :

>>> list(g.objects(e.c, (e.p3%OneOrMore)/e.p2)) #doctest: +NORMALIZE_WHITESPACE
[rdflib.term.URIRef(
    u'ex:j'), rdflib.term.URIRef(u'ex:g'), rdflib.term.URIRef(u'ex:f')]

A more complete set of tests:

>>> list(evalPath(g, (None, e.p1/e.p2, None)))==[(e.a, e.e)]
True
>>> list(evalPath(g, (e.a, e.p1|e.p2, None)))==[(e.a,e.c), (e.a,e.f)]
True
>>> list(evalPath(g, (e.c, ~e.p1, None))) == [ (e.c, e.a) ]
True
>>> list(evalPath(g, (e.a, e.p1%ZeroOrOne, None))) == [(e.a, e.a), (e.a, e.c)]
True
>>> list(evalPath(g, (e.c, e.p3%OneOrMore, None))) == [
...     (e.c, e.g), (e.c, e.h), (e.c, e.a)]
True
>>> list(evalPath(g, (e.c, e.p3%ZeroOrMore, None))) == [(e.c, e.c),
...     (e.c, e.g), (e.c, e.h), (e.c, e.a)]
True
>>> list(evalPath(g, (e.a, -e.p1, None))) == [(e.a, e.f)]
True
>>> list(evalPath(g, (e.a, -(e.p1|e.p2), None))) == []
True
>>> list(evalPath(g, (e.g, -~e.p2, None))) == [(e.g, e.j)]
True
>>> list(evalPath(g, (e.e, ~(e.p1/e.p2), None))) == [(e.e, e.a)]
True
>>> list(evalPath(g, (e.a, e.p1/e.p3/e.p3, None))) == [(e.a, e.h)]
True

>>> list(evalPath(g, (e.q, e.px%OneOrMore, None)))
[(rdflib.term.URIRef('ex:q'), rdflib.term.URIRef('ex:q'))]

>>> list(evalPath(g, (None, e.p1|e.p2, e.c)))
[(rdflib.term.URIRef('ex:a'), rdflib.term.URIRef('ex:c'))]

>>> list(evalPath(g, (None, ~e.p1, e.a))) == [ (e.c, e.a) ]
True
>>> list(evalPath(g, (None, e.p1%ZeroOrOne, e.c))) # doctest: +NORMALIZE_WHITESPACE
[(rdflib.term.URIRef('ex:c'), rdflib.term.URIRef('ex:c')),
 (rdflib.term.URIRef('ex:a'), rdflib.term.URIRef('ex:c'))]

>>> list(evalPath(g, (None, e.p3%OneOrMore, e.a))) # doctest: +NORMALIZE_WHITESPACE
[(rdflib.term.URIRef('ex:h'), rdflib.term.URIRef('ex:a')),
 (rdflib.term.URIRef('ex:g'), rdflib.term.URIRef('ex:a')),
 (rdflib.term.URIRef('ex:c'), rdflib.term.URIRef('ex:a'))]

>>> list(evalPath(g, (None, e.p3%ZeroOrMore, e.a))) # doctest: +NORMALIZE_WHITESPACE
[(rdflib.term.URIRef('ex:a'), rdflib.term.URIRef('ex:a')),
 (rdflib.term.URIRef('ex:h'), rdflib.term.URIRef('ex:a')),
 (rdflib.term.URIRef('ex:g'), rdflib.term.URIRef('ex:a')),
 (rdflib.term.URIRef('ex:c'), rdflib.term.URIRef('ex:a'))]

>>> list(evalPath(g, (None, -e.p1, e.f))) == [(e.a, e.f)]
True
>>> list(evalPath(g, (None, -(e.p1|e.p2), e.c))) == []
True
>>> list(evalPath(g, (None, -~e.p2, e.j))) == [(e.g, e.j)]
True
>>> list(evalPath(g, (None, ~(e.p1/e.p2), e.a))) == [(e.e, e.a)]
True
>>> list(evalPath(g, (None, e.p1/e.p3/e.p3, e.h))) == [(e.a, e.h)]
True

>>> list(evalPath(g, (e.q, e.px%OneOrMore, None))) #doctest: +NORMALIZE_WHITESPACE
[(rdflib.term.URIRef('ex:q'), rdflib.term.URIRef('ex:q'))]

>>> list(evalPath(g, (e.c, (e.p2|e.p3)%ZeroOrMore, e.j)))
[(rdflib.term.URIRef('ex:c'), rdflib.term.URIRef('ex:j'))]

No vars specified
>>> sorted(list(evalPath(g, (None, e.p3%OneOrMore, None)))) #doctest: +NORMALIZE_WHITESPACE
[(rdflib.term.URIRef('ex:c'), rdflib.term.URIRef('ex:a')),
 (rdflib.term.URIRef('ex:c'), rdflib.term.URIRef('ex:g')),
 (rdflib.term.URIRef('ex:c'), rdflib.term.URIRef('ex:h')),
 (rdflib.term.URIRef('ex:g'), rdflib.term.URIRef('ex:a')),
 (rdflib.term.URIRef('ex:g'), rdflib.term.URIRef('ex:h')),
 (rdflib.term.URIRef('ex:h'), rdflib.term.URIRef('ex:a'))]



"""
else:
    __doc__ = """

This module implements the SPARQL 1.1 Property path operators, as defined in:

http://www.w3.org/TR/sparql11-query/#propertypaths

In SPARQL the syntax is as follows:

iri     - An IRI. A path of length one.

^elt        - Inverse path (object to subject).

elt1 / elt2 - A sequence path of elt1 followed by elt2.

elt1 | elt2 - A alternative path of elt1 or elt2 (all possibilities are tried).

elt*        - A path that connects the subject and object of the path by zero
    or more matches of elt.

elt+        - A path that connects the subject and object of the path by one
    or more matches of elt.

elt?        - A path that connects the subject and object of the path by zero
    or one matches of elt.

!iri or !(iri1| ...|irin) - Negated property set. An IRI which is not one of
    irii. !iri is short for !(iri).

!^iri or !(^iri1| ...|^irin) -  Negated property set where the excluded matches
    are based on reversed path. That is, not one of iri1...irin as
    reverse paths. !^iri is short for !(^iri).

!(iri1| ...|irij|^irij+1| ...|^irin) - A combination of forward and reverse
    properties in a negated property set.
(elt)       A group path elt, brackets control precedence.


This module is used internally be the SPARQL engine, but they property paths
can also be used to query RDFLib Graphs directly.

Where possible the SPARQL syntax is mapped to python operators, and property
path objects can be constructed from existing URIRefs.

(NOTE: This version monkey-patches the operators and path-aware triples
functions into the URIRef and Graph class, when rdflib-sparql is merged
into core rdflib it will be cleaner)

>>> foaf=Namespace('http://xmlns.com/foaf/0.1/')

>>> ~foaf.knows
Path(~http://xmlns.com/foaf/0.1/knows)

>>> foaf.knows/foaf.name
Path(http://xmlns.com/foaf/0.1/knows / http://xmlns.com/foaf/0.1/name)

>>> foaf.name|foaf.firstName
Path(http://xmlns.com/foaf/0.1/name | http://xmlns.com/foaf/0.1/firstName)

Modifiers (?, *, +) are done using % and the strings '*', '?', '+', also
defined as constants in this file

>>> foaf.knows%OneOrMore
Path(http://xmlns.com/foaf/0.1/knows+)

The path objects can be used with the normal graph methods.

First some example data:

>>> g=Graph()

>>> g=g.parse(data='''
... @prefix : <ex:> .
...
... :a :p1 :c ; :p2 :f .
... :c :p2 :e ; :p3 :g .
... :g :p3 :h ; :p2 :j .
... :h :p3 :a ; :p2 :g .
...
... :q :px :q .
...
... ''', format='n3') # doctest: +ELLIPSIS

>>> e=Namespace('ex:')

Graph contains:
>>> (e.a, e.p1/e.p2, e.e) in g
True

Graph generator functions, triples, subjects, objects, etc. :

>>> list(g.objects(e.c, (e.p3%OneOrMore)/e.p2)) #doctest: +NORMALIZE_WHITESPACE
[rdflib.term.URIRef(
    u'ex:j'), rdflib.term.URIRef(u'ex:g'), rdflib.term.URIRef(u'ex:f')]

A more complete set of tests:

>>> list(evalPath(g, (None, e.p1/e.p2, None)))==[(e.a, e.e)]
True
>>> list(evalPath(g, (e.a, e.p1|e.p2, None)))==[(e.a,e.c), (e.a,e.f)]
True
>>> list(evalPath(g, (e.c, ~e.p1, None))) == [ (e.c, e.a) ]
True
>>> list(evalPath(g, (e.a, e.p1%ZeroOrOne, None))) == [(e.a, e.a), (e.a, e.c)]
True
>>> list(evalPath(g, (e.c, e.p3%OneOrMore, None))) == [
...     (e.c, e.g), (e.c, e.h), (e.c, e.a)]
True
>>> list(evalPath(g, (e.c, e.p3%ZeroOrMore, None))) == [(e.c, e.c),
...     (e.c, e.g), (e.c, e.h), (e.c, e.a)]
True
>>> list(evalPath(g, (e.a, -e.p1, None))) == [(e.a, e.f)]
True
>>> list(evalPath(g, (e.a, -(e.p1|e.p2), None))) == []
True
>>> list(evalPath(g, (e.g, -~e.p2, None))) == [(e.g, e.j)]
True
>>> list(evalPath(g, (e.e, ~(e.p1/e.p2), None))) == [(e.e, e.a)]
True
>>> list(evalPath(g, (e.a, e.p1/e.p3/e.p3, None))) == [(e.a, e.h)]
True

>>> list(evalPath(g, (e.q, e.px%OneOrMore, None)))
[(rdflib.term.URIRef(u'ex:q'), rdflib.term.URIRef(u'ex:q'))]

>>> list(evalPath(g, (None, e.p1|e.p2, e.c)))
[(rdflib.term.URIRef(u'ex:a'), rdflib.term.URIRef(u'ex:c'))]

>>> list(evalPath(g, (None, ~e.p1, e.a))) == [ (e.c, e.a) ]
True
>>> list(evalPath(g, (None, e.p1%ZeroOrOne, e.c))) # doctest: +NORMALIZE_WHITESPACE
[(rdflib.term.URIRef(u'ex:c'), rdflib.term.URIRef(u'ex:c')),
 (rdflib.term.URIRef(u'ex:a'), rdflib.term.URIRef(u'ex:c'))]

>>> list(evalPath(g, (None, e.p3%OneOrMore, e.a))) # doctest: +NORMALIZE_WHITESPACE
[(rdflib.term.URIRef(u'ex:h'), rdflib.term.URIRef(u'ex:a')),
 (rdflib.term.URIRef(u'ex:g'), rdflib.term.URIRef(u'ex:a')),
 (rdflib.term.URIRef(u'ex:c'), rdflib.term.URIRef(u'ex:a'))]

>>> list(evalPath(g, (None, e.p3%ZeroOrMore, e.a))) # doctest: +NORMALIZE_WHITESPACE
[(rdflib.term.URIRef(u'ex:a'), rdflib.term.URIRef(u'ex:a')),
 (rdflib.term.URIRef(u'ex:h'), rdflib.term.URIRef(u'ex:a')),
 (rdflib.term.URIRef(u'ex:g'), rdflib.term.URIRef(u'ex:a')),
 (rdflib.term.URIRef(u'ex:c'), rdflib.term.URIRef(u'ex:a'))]

>>> list(evalPath(g, (None, -e.p1, e.f))) == [(e.a, e.f)]
True
>>> list(evalPath(g, (None, -(e.p1|e.p2), e.c))) == []
True
>>> list(evalPath(g, (None, -~e.p2, e.j))) == [(e.g, e.j)]
True
>>> list(evalPath(g, (None, ~(e.p1/e.p2), e.a))) == [(e.e, e.a)]
True
>>> list(evalPath(g, (None, e.p1/e.p3/e.p3, e.h))) == [(e.a, e.h)]
True

>>> list(evalPath(g, (e.q, e.px%OneOrMore, None))) #doctest: +NORMALIZE_WHITESPACE
[(rdflib.term.URIRef(u'ex:q'), rdflib.term.URIRef(u'ex:q'))]

>>> list(evalPath(g, (e.c, (e.p2|e.p3)%ZeroOrMore, e.j)))
[(rdflib.term.URIRef(u'ex:c'), rdflib.term.URIRef(u'ex:j'))]

No vars specified
>>> sorted(list(evalPath(g, (None, e.p3%OneOrMore, None)))) #doctest: +NORMALIZE_WHITESPACE
[(rdflib.term.URIRef(u'ex:c'), rdflib.term.URIRef(u'ex:a')),
 (rdflib.term.URIRef(u'ex:c'), rdflib.term.URIRef(u'ex:g')),
 (rdflib.term.URIRef(u'ex:c'), rdflib.term.URIRef(u'ex:h')),
 (rdflib.term.URIRef(u'ex:g'), rdflib.term.URIRef(u'ex:a')),
 (rdflib.term.URIRef(u'ex:g'), rdflib.term.URIRef(u'ex:h')),
 (rdflib.term.URIRef(u'ex:h'), rdflib.term.URIRef(u'ex:a'))]



"""


from rdflib import URIRef, Graph, ConjunctiveGraph, Namespace

DEBUG = True

# property paths

ZeroOrMore = '*'
OneOrMore = '+'
ZeroOrOne = '?'


class Path:
    def eval(self, graph, subj=None, obj=None):
        raise NotImplementedError()


class InvPath(Path):

    def __init__(self, arg):
        self.arg = arg

    def eval(self, graph, subj=None, obj=None):
        for s, o in evalPath(graph, (obj, self.arg, subj)):
            yield o, s

    def __repr__(self):
        return "Path(~%s)" % (self.arg,)


class SequencePath(Path):
    def __init__(self, *args):
        self.args = []
        for a in args:
            if isinstance(a, SequencePath):
                self.args += a.args
            else:
                self.args.append(a)

    def eval(self, graph, subj=None, obj=None):
        def _eval_seq(paths, subj, obj):
            if paths[1:]:
                for s, o in evalPath(graph, (subj, paths[0], None)):
                    for r in _eval_seq(paths[1:], o, obj):
                        yield s, r[1]

            else:
                for s, o in evalPath(graph, (subj, paths[0], obj)):
                    yield s, o

        def _eval_seq_bw(paths, subj, obj):
            if paths[:-1]:
                for s, o in evalPath(graph, (None, paths[-1], obj)):
                    for r in _eval_seq(paths[:-1], subj, s):
                        yield r[0], o

            else:
                for s, o in evalPath(graph, (subj, paths[0], obj)):
                    yield s, o

        if subj:
            return _eval_seq(self.args, subj, obj)
        elif obj:
            return _eval_seq_bw(self.args, subj, obj)
        else:  # no vars bound, we can start anywhere
            return _eval_seq(self.args, subj, obj)

    def __repr__(self):
        return "Path(%s)" % " / ".join(str(x) for x in self.args)


class AlternativePath(Path):
    def __init__(self, *args):
        self.args = []
        for a in args:
            if isinstance(a, AlternativePath):
                self.args += a.args
            else:
                self.args.append(a)

    def eval(self, graph, subj=None, obj=None):
        for x in self.args:
            for y in evalPath(graph, (subj, x, obj)):
                yield y

    def __repr__(self):
        return "Path(%s)" % " | ".join(str(x) for x in self.args)


class ModPath(Path):
    def __init__(self, path, mod):
        self.path = path
        self.mod = mod

        if mod == ZeroOrOne:
            self.zero = True
            self.more = False
        elif mod == ZeroOrMore:
            self.zero = True
            self.more = True
        elif mod == OneOrMore:
            self.zero = False
            self.more = True
        else:
            raise Exception('Unknown modifier %s' % mod)

    def eval(self, graph, subj=None, obj=None, first=True):
        if self.zero and first:
            if subj and obj:
                if subj == obj:
                    yield (subj, obj)
            elif subj:
                yield (subj, subj)
            elif obj:
                yield (obj, obj)

        def _fwd(subj=None, obj=None, seen=None):
            seen.add(subj)

            for s, o in evalPath(graph, (subj, self.path, None)):
                if not obj or o == obj:
                    yield s, o
                if self.more:
                    if o in seen:
                        continue
                    for s2, o2 in _fwd(o, obj, seen):
                        yield s, o2

        def _bwd(subj=None, obj=None, seen=None):
            seen.add(obj)

            for s, o in evalPath(graph, (None, self.path, obj)):
                if not subj or subj == s:
                    yield s, o
                if self.more:
                    if s in seen:
                        continue

                    for s2, o2 in _bwd(None, s, seen):
                        yield s2, o

        def _fwdbwd():
            if self.zero:
                seen1 = set()
                # According to the spec, ALL nodes are possible solutions
                # (even literals)
                # we cannot do this without going through ALL triples
                # unless we keep an index of all terms somehow
                # but lets just hope this query doesnt happen very often...
                for s, o in graph.subject_objects(None):
                    if s not in seen1:
                        seen1.add(s)
                        yield s, s
                    if o not in seen1:
                        seen1.add(o)
                        yield o, o

            for s, o in evalPath(graph, (None, self.path, None)):
                if not self.more:
                    yield s, o
                else:
                    seen = set()
                    f = list(_fwd(s, None, seen))  # cache or recompute?
                    for s3, o3 in _bwd(None, o, seen):
                        for s2, o2 in f:
                            yield s3, o2  # ?

        done = set()  # the spec does by defn. not allow duplicates
        if subj:
            for x in _fwd(subj, obj, set()):
                if x not in done:
                    done.add(x)
                    yield x
        elif obj:
            for x in _bwd(subj, obj, set()):
                if x not in done:
                    done.add(x)
                    yield x
        else:
            for x in _fwdbwd():
                if x not in done:
                    done.add(x)
                    yield x

    def __repr__(self):
        return "Path(%s%s)" % (self.path, self.mod)


class NegatedPath(Path):
    def __init__(self, arg):
        if isinstance(arg, (URIRef, InvPath)):
            self.args = [arg]
        elif isinstance(arg, AlternativePath):
            self.args = arg.args
        else:
            raise Exception(
                'Can only negate URIRefs, InvPaths or ' +
                'AlternativePaths, not: %s' % (arg,))

    def eval(self, graph, subj=None, obj=None):
        for s, p, o in graph.triples((subj, None, obj)):
            for a in self.args:
                if isinstance(a, URIRef):
                    if p == a:
                        break
                elif isinstance(a, InvPath):
                    if (o, a.arg, s) in graph:
                        break
                else:
                    raise Exception('Invalid path in NegatedPath: %s' % a)
            else:
                yield s, o

    def __repr__(self):
        return "Path(! %s)" % ",".join(str(x) for x in self.args)


class PathList(list):
    pass


def path_alternative(self, other):
    if not isinstance(other, (URIRef, Path)):
        raise Exception('Only URIRefs or Paths can be in paths!')
    return AlternativePath(self, other)


def path_sequence(self, other):
    if not isinstance(other, (URIRef, Path)):
        raise Exception('Only URIRefs or Paths can be in paths!')
    return SequencePath(self, other)


def evalPath(graph, t):
    return ((s, o) for s, p, o in graph.triples(t))


def graph_triples(graph, t, context=None):
#    if DEBUG: print ">>>",t
    subj, path, obj = t
    if path is None or isinstance(path, URIRef):
        return graph._triples((subj, path, obj))
    elif isinstance(path, Path):
        return ((s, path, o) for s, o in path.eval(graph, subj, obj))
    else:
        raise Exception('I need a URIRef or path as predicate, not %s' % path)

def conjunctive_graph_triples(graph, t, context=None):

    subj, path, obj = t
    if path is None or isinstance(path, URIRef):
        return graph._triples((subj, path, obj), context)
    elif isinstance(path, Path):
        if context is None:
            return ((s, path, o) for s, o in path.eval(graph, subj, obj))
        else:
            return ((s, path, o) for s, o in path.eval(graph.get_context(context), subj, obj))
    else:
        raise Exception('I need a URIRef or path as predicate, not %s' % path)


URIRef.__or__ = path_alternative
URIRef.__div__ = path_sequence
URIRef.__mod__ = lambda self, mod: ModPath(self, mod)
URIRef.__invert__ = lambda self: InvPath(self)
URIRef.__neg__ = lambda self: NegatedPath(self)

Path.__invert__ = lambda self: InvPath(self)
Path.__neg__ = lambda self: NegatedPath(self)
Path.__mod__ = lambda self, mod: ModPath(self, mod)
Path.__or__ = path_alternative
Path.__div__ = path_sequence

Graph._triples = Graph.triples
Graph.triples = graph_triples
ConjunctiveGraph._triples=ConjunctiveGraph.triples
ConjunctiveGraph.triples=conjunctive_graph_triples

if __name__ == '__main__':

    # print "---------------------"
    # for x in evalPath(g, (e.a, e.p1/(e.p3%ZeroOrMore)/e.p2, None)):
    #     print x

#     g=Graph()
#     g=g.parse(data='''
# @prefix : <ex:> .

#  :a :p1 :c ; :p2 :f .
#  :c :p2 :e ; :p3 :g .
#  :g :p3 :h ; :p2 :j .
#  :h :p3 :a ; :p2 :g .

#  :q :px :q .

#  ''', format='n3')

#     e=Namespace('ex:')
#     print list(evalPath(g, (e.c, (e.p2|e.p3)%ZeroOrMore, e.j)))
    import doctest
    doctest.testmod()
