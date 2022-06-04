__doc__ = r"""

This module implements the SPARQL 1.1 Property path operators, as
defined in:

http://www.w3.org/TR/sparql11-query/#propertypaths

In SPARQL the syntax is as follows:

+--------------------+-------------------------------------------------+
|Syntax              | Matches                                         |
+====================+=================================================+
|iri                 | An IRI. A path of length one.                   |
+--------------------+-------------------------------------------------+
|^elt                | Inverse path (object to subject).               |
+--------------------+-------------------------------------------------+
|elt1 / elt2         | A sequence path of elt1 followed by elt2.       |
+--------------------+-------------------------------------------------+
|elt1 | elt2         | A alternative path of elt1 or elt2              |
|                    | (all possibilities are tried).                  |
+--------------------+-------------------------------------------------+
|elt*                | A path that connects the subject and object     |
|                    | of the path by zero or more matches of elt.     |
+--------------------+-------------------------------------------------+
|elt+                | A path that connects the subject and object     |
|                    | of the path by one or more matches of elt.      |
+--------------------+-------------------------------------------------+
|elt?                | A path that connects the subject and object     |
|                    | of the path by zero or one matches of elt.      |
+--------------------+-------------------------------------------------+
|!iri or             | Negated property set. An IRI which is not one of|
|!(iri\ :sub:`1`\ \| | iri\ :sub:`1`...iri\ :sub:`n`.                  |
|... \|iri\ :sub:`n`)| !iri is short for !(iri).                       |
+--------------------+-------------------------------------------------+
|!^iri or            | Negated property set where the excluded matches |
|!(^iri\ :sub:`1`\ \|| are based on reversed path. That is, not one of |
|...\|^iri\ :sub:`n`)| iri\ :sub:`1`...iri\ :sub:`n` as reverse paths. |
|                    | !^iri is short for !(^iri).                     |
+--------------------+-------------------------------------------------+
|!(iri\ :sub:`1`\ \| | A combination of forward and reverse            |
|...\|iri\ :sub:`j`\ | properties in a negated property set.           |
|\|^iri\ :sub:`j+1`\ |                                                 |
|\|... \|^iri\       |                                                 |
|:sub:`n`)|          |                                                 |
+--------------------+-------------------------------------------------+
|(elt)               | A group path elt, brackets control precedence.  |
+--------------------+-------------------------------------------------+

This module is used internally by the SPARQL engine, but the property paths
can also be used to query RDFLib Graphs directly.

Where possible the SPARQL syntax is mapped to Python operators, and property
path objects can be constructed from existing URIRefs.

>>> from rdflib import Graph, Namespace
>>> from rdflib.namespace import FOAF

>>> ~FOAF.knows
Path(~http://xmlns.com/foaf/0.1/knows)

>>> FOAF.knows/FOAF.name
Path(http://xmlns.com/foaf/0.1/knows / http://xmlns.com/foaf/0.1/name)

>>> FOAF.name|FOAF.givenName
Path(http://xmlns.com/foaf/0.1/name | http://xmlns.com/foaf/0.1/givenName)

Modifiers (?, \*, +) are done using \* (the multiplication operator) and
the strings '\*', '?', '+', also defined as constants in this file.

>>> FOAF.knows*OneOrMore
Path(http://xmlns.com/foaf/0.1/knows+)

The path objects can also be used with the normal graph methods.

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

>>> e = Namespace('ex:')

Graph contains:

>>> (e.a, e.p1/e.p2, e.e) in g
True

Graph generator functions, triples, subjects, objects, etc. :

>>> list(g.objects(e.c, (e.p3*OneOrMore)/e.p2)) # doctest: +NORMALIZE_WHITESPACE
[rdflib.term.URIRef('ex:j'), rdflib.term.URIRef('ex:g'),
    rdflib.term.URIRef('ex:f')]

A more complete set of tests:

>>> list(evalPath(g, (None, e.p1/e.p2, None)))==[(e.a, e.e)]
True
>>> list(evalPath(g, (e.a, e.p1|e.p2, None)))==[(e.a,e.c), (e.a,e.f)]
True
>>> list(evalPath(g, (e.c, ~e.p1, None))) == [ (e.c, e.a) ]
True
>>> list(evalPath(g, (e.a, e.p1*ZeroOrOne, None))) == [(e.a, e.a), (e.a, e.c)]
True
>>> list(evalPath(g, (e.c, e.p3*OneOrMore, None))) == [
...     (e.c, e.g), (e.c, e.h), (e.c, e.a)]
True
>>> list(evalPath(g, (e.c, e.p3*ZeroOrMore, None))) == [(e.c, e.c),
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

>>> list(evalPath(g, (e.q, e.px*OneOrMore, None)))
[(rdflib.term.URIRef('ex:q'), rdflib.term.URIRef('ex:q'))]

>>> list(evalPath(g, (None, e.p1|e.p2, e.c)))
[(rdflib.term.URIRef('ex:a'), rdflib.term.URIRef('ex:c'))]

>>> list(evalPath(g, (None, ~e.p1, e.a))) == [ (e.c, e.a) ]
True
>>> list(evalPath(g, (None, e.p1*ZeroOrOne, e.c))) # doctest: +NORMALIZE_WHITESPACE
[(rdflib.term.URIRef('ex:c'), rdflib.term.URIRef('ex:c')),
 (rdflib.term.URIRef('ex:a'), rdflib.term.URIRef('ex:c'))]

>>> list(evalPath(g, (None, e.p3*OneOrMore, e.a))) # doctest: +NORMALIZE_WHITESPACE
[(rdflib.term.URIRef('ex:h'), rdflib.term.URIRef('ex:a')),
 (rdflib.term.URIRef('ex:g'), rdflib.term.URIRef('ex:a')),
 (rdflib.term.URIRef('ex:c'), rdflib.term.URIRef('ex:a'))]

>>> list(evalPath(g, (None, e.p3*ZeroOrMore, e.a))) # doctest: +NORMALIZE_WHITESPACE
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

>>> list(evalPath(g, (e.q, e.px*OneOrMore, None)))
[(rdflib.term.URIRef('ex:q'), rdflib.term.URIRef('ex:q'))]

>>> list(evalPath(g, (e.c, (e.p2|e.p3)*ZeroOrMore, e.j)))
[(rdflib.term.URIRef('ex:c'), rdflib.term.URIRef('ex:j'))]

No vars specified:

>>> sorted(list(evalPath(g, (None, e.p3*OneOrMore, None)))) #doctest: +NORMALIZE_WHITESPACE
[(rdflib.term.URIRef('ex:c'), rdflib.term.URIRef('ex:a')),
 (rdflib.term.URIRef('ex:c'), rdflib.term.URIRef('ex:g')),
 (rdflib.term.URIRef('ex:c'), rdflib.term.URIRef('ex:h')),
 (rdflib.term.URIRef('ex:g'), rdflib.term.URIRef('ex:a')),
 (rdflib.term.URIRef('ex:g'), rdflib.term.URIRef('ex:h')),
 (rdflib.term.URIRef('ex:h'), rdflib.term.URIRef('ex:a'))]

"""


from functools import total_ordering
from typing import TYPE_CHECKING, Callable, Iterator, Optional, Tuple, Union

from rdflib.term import Node, URIRef

if TYPE_CHECKING:
    from rdflib.graph import Graph, _ObjectType, _SubjectType


# property paths

ZeroOrMore = "*"
OneOrMore = "+"
ZeroOrOne = "?"


@total_ordering
class Path(object):

    __or__: Callable[["Path", Union["URIRef", "Path"]], "AlternativePath"]
    __invert__: Callable[["Path"], "InvPath"]
    __neg__: Callable[["Path"], "NegatedPath"]
    __truediv__: Callable[["Path", Union["URIRef", "Path"]], "SequencePath"]
    __mul__: Callable[["Path", str], "MulPath"]

    def eval(
        self,
        graph: "Graph",
        subj: Optional["_SubjectType"] = None,
        obj: Optional["_ObjectType"] = None,
    ) -> Iterator[Tuple["_SubjectType", "_ObjectType"]]:
        raise NotImplementedError()

    def __lt__(self, other):
        if not isinstance(other, (Path, Node)):
            raise TypeError(
                "unorderable types: %s() < %s()" % (repr(self), repr(other))
            )
        return repr(self) < repr(other)


class InvPath(Path):
    def __init__(self, arg):
        self.arg = arg

    def eval(self, graph, subj=None, obj=None):
        for s, o in evalPath(graph, (obj, self.arg, subj)):
            yield o, s

    def __repr__(self):
        return "Path(~%s)" % (self.arg,)

    def n3(self):
        return "^%s" % self.arg.n3()


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

    def n3(self):
        return "/".join(a.n3() for a in self.args)


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

    def n3(self):
        return "|".join(a.n3() for a in self.args)


class MulPath(Path):
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
            raise Exception("Unknown modifier %s" % mod)

    def eval(self, graph, subj=None, obj=None, first=True):
        if self.zero and first:
            if subj and obj:
                if subj == obj:
                    yield subj, obj
            elif subj:
                yield subj, subj
            elif obj:
                yield obj, obj

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

        def _all_fwd_paths():
            if self.zero:
                seen1 = set()
                # According to the spec, ALL nodes are possible solutions
                # (even literals)
                # we cannot do this without going through ALL triples
                # unless we keep an index of all terms somehow
                # but let's just hope this query doesn't happen very often...
                for s, o in graph.subject_objects(None):
                    if s not in seen1:
                        seen1.add(s)
                        yield s, s
                    if o not in seen1:
                        seen1.add(o)
                        yield o, o

            seen = set()
            for s, o in evalPath(graph, (None, self.path, None)):
                if not self.more:
                    yield s, o
                else:
                    if s not in seen:
                        seen.add(s)
                        f = list(_fwd(s, None, set()))
                        for s1, o1 in f:
                            assert s1 == s
                            yield s1, o1

        done = set()  # the spec does, by defn, not allow duplicates
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
            for x in _all_fwd_paths():
                if x not in done:
                    done.add(x)
                    yield x

    def __repr__(self):
        return "Path(%s%s)" % (self.path, self.mod)

    def n3(self):
        return "%s%s" % (self.path.n3(), self.mod)


class NegatedPath(Path):
    def __init__(self, arg):
        if isinstance(arg, (URIRef, InvPath)):
            self.args = [arg]
        elif isinstance(arg, AlternativePath):
            self.args = arg.args
        else:
            raise Exception(
                "Can only negate URIRefs, InvPaths or "
                + "AlternativePaths, not: %s" % (arg,)
            )

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
                    raise Exception("Invalid path in NegatedPath: %s" % a)
            else:
                yield s, o

    def __repr__(self):
        return "Path(! %s)" % ",".join(str(x) for x in self.args)

    def n3(self):
        return "!(%s)" % ("|".join(self.args))


class PathList(list):
    pass


def path_alternative(self, other):
    """
    alternative path
    """
    if not isinstance(other, (URIRef, Path)):
        raise Exception("Only URIRefs or Paths can be in paths!")
    return AlternativePath(self, other)


def path_sequence(self, other):
    """
    sequence path
    """
    if not isinstance(other, (URIRef, Path)):
        raise Exception("Only URIRefs or Paths can be in paths!")
    return SequencePath(self, other)


def evalPath(graph, t):
    return ((s, o) for s, p, o in graph.triples(t))


def mul_path(p, mul):
    """
    cardinality path
    """
    return MulPath(p, mul)


def inv_path(p):
    """
    inverse path
    """
    return InvPath(p)


def neg_path(p):
    """
    negated path
    """
    return NegatedPath(p)


if __name__ == "__main__":
    pass
else:
    # monkey patch
    # (these cannot be directly in terms.py
    #  as it would introduce circular imports)

    URIRef.__or__ = path_alternative
    # ignore typing here as URIRef inherits from str,
    # which has an incompatible definition of __mul__.
    URIRef.__mul__ = mul_path  # type: ignore
    URIRef.__invert__ = inv_path
    URIRef.__neg__ = neg_path
    URIRef.__truediv__ = path_sequence

    Path.__invert__ = inv_path
    Path.__neg__ = neg_path
    Path.__mul__ = mul_path
    Path.__or__ = path_alternative
    Path.__truediv__ = path_sequence
