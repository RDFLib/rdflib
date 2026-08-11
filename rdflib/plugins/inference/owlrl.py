#
"""
This module is a **brute force** implementation of the OWL 2 RL profile.

RDFLib works with 'generalized' RDF, meaning that triples with a BNode predicate are *allowed*. This is good because,
e.g., some of the triples generated for RDF from an OWL 2 functional syntax might look like :code:`[ owl:inverseOf p ]`, and the
RL rules would then operate on such generalized triple. However, as a last, post processing steps, these triples are
removed from the graph before serialization to produce 'standard' RDF (which is o.k. for RL, too, because the
consequent triples are all right, generalized triples might have had a role in the deduction steps only).

**Requires**: `RDFLib`_, 7.5.0 and higher.

.. _RDFLib: https://github.com/RDFLib/rdflib

**License**: This software is available for use under the `W3C Software License`_.

.. _W3C Software License: http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231

**Organization**: `World Wide Web Consortium`_

.. _World Wide Web Consortium: http://www.w3.org

**Author**: `Ivan Herman`_

.. _Ivan Herman: http://www.w3.org/People/Ivan/

"""
from __future__ import annotations

__author__ = "Ivan Herman"
__contact__ = "Ivan Herman, ivan@w3.org"
__license__ = "W3C® SOFTWARE NOTICE AND LICENSE, http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231"


from collections import defaultdict
from typing import Union

import rdflib
from rdflib import BNode, Graph
from rdflib.namespace import OWL, RDF, RDFS
from rdflib.plugins.inference.axiomatictriples import (
    OWLRL_Axiomatic_Triples,
    OWLRL_D_Axiomatic_Triples,
    OWLRL_Datatypes_Disjointness,
)
from rdflib.plugins.inference.closure import Core

OWLRL_Annotation_properties = [
    RDFS.label,
    RDFS.comment,
    RDFS.seeAlso,
    RDFS.isDefinedBy,
    OWL.deprecated,
    OWL.versionInfo,
    OWL.priorVersion,
    OWL.backwardCompatibleWith,
    OWL.incompatibleWith,
]

from rdflib.plugins.inference.datatypehandling import AltXSDToPYTHON  # noqa: E402
from rdflib.plugins.inference.xsddatatypes import (  # noqa: E402
    OWL_Datatype_Subsumptions,
    OWL_RL_Datatypes,
)

# ruff: noqa: E731 E741 N801 N806

# mypy: disable_error_code = "arg-type, attr-defined, operator, var-annotated, valid-type, union-attr"

identity = lambda v: v


#######################################################################################################################


# OWL-R Semantics class
#
#
# As an editing help: each rule is prefixed by RULE XXXX where XXXX is the acronym given in the profile document.
# This helps in referring back to the spec...
# noinspection PyPep8Naming, PyPep8Naming, PyBroadException
class OWLRL_Semantics(Core):
    """
    OWL 2 RL Semantics class, i.e., implementation of the OWL 2 RL closure graph.

    .. note:: Note that the module does *not* implement the so called Datatype entailment rules, simply because the underlying
        RDFLib does not implement the datatypes (i.e., RDFLib will not make the literal "1.00" and "1.00000" identical,
        although even with all the ambiguities on datatypes, this *should* be made equal...).

        Also, the so-called extensional entailment rules (Section 7.3.1 in the RDF Semantics document) have not been
        implemented either.

    The comments and references to the various rule follow the names as used in the `OWL 2 RL
    document`_.

    .. _OWL 2 RL document: http://www.w3.org/TR/owl2-profiles/#Reasoning_in_OWL_2_RL_and_RDF_Graphs_using_Rules

    :param graph: The RDF graph to be extended.
    :type graph: :class:`rdflib.Graph`

    :param axioms: Whether (non-datatype) axiomatic triples should be added or not.
    :type axioms: bool

    :param daxioms: Whether datatype axiomatic triples should be added or not.
    :type daxioms: bool

    :param rdfs: Whether RDFS inference is also done (used in subclassed only).
    :type rdfs: bool
    """

    def __init__(
        self,
        graph: Graph,
        axioms,
        daxioms,
        rdfs: bool = False,
        destination: Union[None, Graph] = None,
    ):
        """
        @param graph: the RDF graph to be extended
        @type graph: rdflib.Graph
        @param axioms: whether (non-datatype) axiomatic triples should be added or not
        @type axioms: bool
        @param daxioms: whether datatype axiomatic triples should be added or not
        @type daxioms: bool
        @param rdfs: whether RDFS inference is also done (used in subclassed only)
        @type rdfs: boolean
        @param destination: the destination graph to which the results are written. If None, use the source graph.
        @type destination: rdflib.Graph
        """
        Core.__init__(self, graph, axioms, daxioms, rdfs=rdfs, destination=destination)
        self.bnodes = []

    def _list(self, l):
        """
        Shorthand to get a list of values (ie, from an rdf:List structure) starting at a head

        @param l: RDFLib resource, should be the head of an rdf:List
        @return: array of resources
        """
        return [ch for ch in self.graph.items(l)]

    def post_process(self):
        """
        Remove triples with Bnode predicates. The Bnodes in the graph are collected in the first cycle run.
        """
        to_be_removed = []
        for b in self.bnodes:
            for t in self.graph.triples((None, b, None)):
                if t not in to_be_removed:
                    to_be_removed.append(t)
        for t in to_be_removed:
            self.destination.remove(t)
            self.graph.remove(t)

    def add_axioms(self):
        """
        Add axioms
        """
        for t in OWLRL_Axiomatic_Triples:
            self.destination.add(t)

    def add_d_axioms(self):
        """
        Add the datatype axioms
        """
        for t in OWLRL_D_Axiomatic_Triples:
            self.destination.add(t)

    def restriction_typing_check(self, v, t):
        """
        Helping method to check whether a type statement is in line with a possible
        restriction. This method is invoked by rule "cls-avf" before setting a type
        on an allValuesFrom restriction.

        The method is a placeholder at this level. It is typically implemented by subclasses for
        extra checks, e.g., for datatype facet checks.

        :param v: The resource that is to be 'typed'.
        :param t: The targeted type (ie, Class).
        :return: Boolean.
        :rtype: bool
        """
        return True

    def _one_time_rules_datatypes(self):
        """
        Some of the rules in the rule set are axiomatic in nature, meaning that they really have to be added only
        once, there is no reason to add these in a cycle. These are performed by this method that is invoked only once
        at the beginning of the process.

        These are: cls-thing, cls-nothing1, prp-ap, dt-types1, dt-types2, dt-eq, dt-diff.

        .. note:: Note, however, that the dt-* are executed only partially, limited by the possibilities offered by RDFLib. These
            may not cover all the edge cases of OWL RL. Especially, dt-not-type has not (yet?) been implemented (I wonder
            whether RDFLib should not raise exception for those anyway...
        """

        # noinspection PyShadowingNames
        def _add_to_explicit(s, o):
            explicit[s].add(o)

        # noinspection PyShadowingNames
        def _append_to_explicit(s, o):
            explicit[s].add(o)

        # noinspection PyShadowingNames
        def _handle_subsumptions(r, dt):
            if dt in OWL_Datatype_Subsumptions:
                for new_dt in OWL_Datatype_Subsumptions[dt]:
                    self.store_triple((r, RDF.type, new_dt))
                    self.store_triple((new_dt, RDF.type, RDFS.Datatype))
                    used_datatypes.add(new_dt)

        # explicit object->datatype relationships: those that came from an object being typed as a datatype
        # or a sameAs. The values are arrays of datatypes to which the resource belong
        explicit = defaultdict(set)

        # For processing later:
        # implicit object->datatype relationships: these come from real
        # literals which are present in the graph
        implicit = {
            o: o.datatype
            for s, p, o in self.graph.triples((None, None, None))
            if isinstance(o, rdflib.Literal) and o.datatype in OWL_RL_Datatypes
        }

        # datatypes in use by the graph (directly or indirectly). This will be used at the end to add the
        # necessary disjointness statements (but not more)
        used_datatypes = set(implicit.values())

        # RULE dt-type2: for all explicit literals the corresponding bnode should get the right type
        # definition. The 'implicit' dictionary is also filled on the fly
        # RULE dt-not-type: see whether an explicit literal is valid in terms of the defined datatype
        for lt in implicit:  # note that all non-RL datatypes are ignored
            # add the explicit typing triple
            self.store_triple((lt, RDF.type, lt.datatype))

            # for dt-not-type
            # This is a dirty trick: rdflib's Literal includes a method that raises an exception if the
            # lexical value cannot be mapped on the value space.
            converter = AltXSDToPYTHON.get(lt.datatype, identity)
            try:
                converter(str(lt))
            except ValueError:
                self.add_error(
                    "Lexical value of the literal '%s' does not match"
                    " its datatype (%s)" % (lt, lt.datatype)
                )

        # RULE dt-diff
        # RULE dt-eq
        # Compare literals whether they are different or not. This rules
        # are skipped on purpose at the moment.

        # Other datatype definitions can come from explicitly defining some nodes as datatypes (though rarely used,
        # it is perfectly possible...
        # there may be explicit relationships set in the graph, too!
        for s, p, o in self.graph.triples((None, RDF.type, None)):
            if o in OWL_RL_Datatypes:
                used_datatypes.add(o)
                if s not in implicit:
                    _add_to_explicit(s, o)

        # Finally, there may be sameAs statements that bind nodes to some of the existing ones. This does not introduce
        # new datatypes, so the used_datatypes array does not get extended
        for s, p, o in self.graph.triples((None, OWL.sameAs, None)):
            if o in implicit:
                _add_to_explicit(s, implicit[o])
            # note that s in implicit would mean that the original graph has
            # a literal in subject position which is not allowed at the moment, so I do not bother
            if o in explicit:
                _append_to_explicit(s, o)
            if s in explicit:
                _append_to_explicit(o, s)

        # what we have now:
        # explicit+implicit contains all the resources of type datatype;
        # implicit contains those that are given by an explicit literal
        # explicit contains those that are given by general resources, and there can be a whole array for each entry

        # RULE dt-type1: add a Datatype typing for all those
        # Note: the strict interpretation of OWL RL is to do that for all allowed datatypes, but this is
        # under discussion right now. The optimized version uses only what is really in use
        for dt in OWL_RL_Datatypes:
            self.store_triple((dt, RDF.type, RDFS.Datatype))
        for dts in explicit.values():
            for dt in dts:
                self.store_triple((dt, RDF.type, RDFS.Datatype))

        # Datatype reasoning means that certain datatypes are subtypes of one another.
        # I could simply generate the extra subclass relationships into the graph and let the generic
        # process work its way, but it seems to be an overkill. Instead, I prefer to add the explicit typing
        # into the graph 'manually'
        for r in explicit:
            # these are the datatypes that this resource has
            dtypes = explicit[r]
            for dt in dtypes:
                _handle_subsumptions(r, dt)

        for r, dt in implicit.items():
            _handle_subsumptions(r, dt)

        # Last step: add the datatype disjointness relationships. This is done only for
        #  - 'top' level datatypes
        #  - used in the graph
        for t in OWLRL_Datatypes_Disjointness:
            (l, pred, r) = t
            if l in used_datatypes and r in used_datatypes:
                self.store_triple(t)

    def _one_time_rules_misc(self):
        """
        Rules executed: cls-thing, cls-nothing, prp-ap.
        """
        # RULE cls-thing
        self.store_triple((OWL.Thing, RDF.type, OWL.Class))

        # RULE cls-nothing
        self.store_triple((OWL.Nothing, RDF.type, OWL.Class))

        # RULE prp-ap
        for an in OWLRL_Annotation_properties:
            self.store_triple((an, RDF.type, OWL.AnnotationProperty))

    def one_time_rules(self):
        """
        Some of the rules in the rule set are axiomatic in nature, meaning that they really have to be added only
        once, there is no reason to add these in a cycle. These are performed by this method that is invoked only once
        at the beginning of the process.

        These are: cls-thing, cls-nothing1, prp-ap, dt-types1, dt-types2, dt-eq, dt-diff.
        """
        self._one_time_rules_misc()
        self._one_time_rules_datatypes()

    def rules(self, t, cycle_num):
        """
        Go through the various rule groups, as defined in the OWL-RL profile text and implemented via
        local methods. (The calling cycle takes every tuple in the graph.)

        :param t: A triple (in the form of a tuple).
        :param cycle_num: Which cycle are we in, starting with 1. This value is forwarded to all local rules; it is
            also used locally to collect the bnodes in the graph.
        """
        if cycle_num == 1:
            for r in t:
                if isinstance(r, BNode) and r not in self.bnodes:
                    self.bnodes.append(r)

        self._properties(t, cycle_num)
        self._equality(t, cycle_num)
        self._classes(t, cycle_num)
        self._class_axioms(t, cycle_num)
        self._schema_vocabulary(t, cycle_num)

    def _property_chain(self, p, x):
        """
        Implementation of the property chain axiom, invoked from inside the property axiom handler. This is the
        implementation of rule prp-spo2, taken aside for an easier readability of the code.
        """
        chain = self._list(x)
        # The complication is that, at each step of the chain, there may be spawns, leading to a multitude
        # of 'sub' chains:-(
        if len(chain) > 0:
            for u1, _y, _z in self.graph.triples((None, chain[0], None)):
                # At least the chain can be started, because the leftmost property has at least
                # one element in its extension
                finalList = [(u1, _z)]
                chainExists = True
                for pi in chain[1:]:
                    newList = []
                    for _u, ui in finalList:
                        for u in self.graph.objects(ui, pi):
                            # what is stored is only last entry with u1, the intermediate results
                            # are not of interest
                            newList.append((u1, u))
                    # I have now, in new list, all the intermediate results
                    # until pi
                    # if new list is empty, that means that is a blind alley
                    if len(newList) == 0:
                        chainExists = False
                        break
                    else:
                        finalList = newList
                if chainExists:
                    for _u, un in finalList:
                        self.store_triple((u1, p, un))

    def _equality(self, triple, cycle_num):
        """
        Table 4: Semantics of equality. Essentially, the eq-* rules.
        @param triple: triple to work on
        @param cycle_num: which cycle are we in, starting with 1. Can be used for some optimization.
        """
        # In many of the 'if' branches, corresponding to rules in the document,
        # the branch begins by a renaming of variables (eg, pp, c = s, o).
        # There is no programming reasons for doing that, but by renaming the
        # variables it becomes easier to compare the declarative rules
        # in the document with the implementation
        s, p, o = triple
        # RULE eq-ref
        self.store_triple((s, OWL.sameAs, s))
        self.store_triple((o, OWL.sameAs, o))
        self.store_triple((p, OWL.sameAs, p))
        if p == OWL.sameAs:
            x, y = s, o
            # RULE eq-sym
            self.store_triple((y, OWL.sameAs, x))
            # RULE eq-trans
            for z in self.graph.objects(y, OWL.sameAs):
                self.store_triple((x, OWL.sameAs, z))
            # RULE eq-rep-s
            for pp, oo in self.graph.predicate_objects(s):
                self.store_triple((o, pp, oo))
            # RULE eq-rep-p
            for ss, oo in self.graph.subject_objects(s):
                self.store_triple((ss, o, oo))
            # RULE eq-rep-o
            for ss, pp in self.graph.subject_predicates(o):
                self.store_triple((ss, pp, s))
            # RULE eq-diff1
            if (s, OWL.differentFrom, o) in self.graph or (
                o,
                OWL.differentFrom,
                s,
            ) in self.graph:
                self.add_error(
                    "'sameAs' and 'differentFrom' cannot be used on the same subject-object pair: (%s, %s)"
                    % (s, o)
                )

        # RULES eq-diff2 and eq-diff3
        if p == RDF.type and o == OWL.AllDifferent:
            x = s
            # the objects method are generators, we cannot simply concatenate them. So we turn the results
            # into lists first. (Otherwise the body of the for loops should be repeated verbatim, which
            # is silly and error prone...
            m1 = [i for i in self.graph.objects(x, OWL.members)]
            m2 = [i for i in self.graph.objects(x, OWL.distinctMembers)]
            for y in m1 + m2:
                zis = self._list(y)
                for i in range(0, len(zis) - 1):
                    zi = zis[i]
                    for j in range(i + 1, len(zis) - 1):
                        zj = zis[j]
                        if (
                            (zi, OWL.sameAs, zj) in self.graph
                            or (zj, OWL.sameAs, zi) in self.graph
                        ) and zi != zj:
                            self.add_error(
                                "'sameAs' and 'AllDifferent' cannot be used on the same subject-object "
                                "pair: (%s, %s)" % (zi, zj)
                            )

    def _properties(self, triple, cycle_num):
        """
        Table 5: The Semantics of Axioms about Properties. Essentially, the prp-* rules.
        @param triple: triple to work on
        @param cycle_num: which cycle are we in, starting with 1. Can be used for some optimization.
        """
        # In many of the 'if' branches, corresponding to rules in the document,
        # the branch begins by a renaming of variables (eg, pp, c = s, o).
        # There is no programming reasons for doing that, but by renaming the
        # variables it becomes easier to compare the declarative rules
        # in the document with the implementation
        p, t, o = triple

        # RULE prp-ap
        if cycle_num == 1 and t in OWLRL_Annotation_properties:
            self.store_triple((t, RDF.type, OWL.AnnotationProperty))

        # RULE prp-dom
        if t == RDFS.domain:
            for x, y in self.graph.subject_objects(p):
                self.store_triple((x, RDF.type, o))

        # RULE prp-rng
        elif t == RDFS.range:
            for x, y in self.graph.subject_objects(p):
                self.store_triple((y, RDF.type, o))

        elif t == RDF.type:
            # RULE prp-fp
            if o == OWL.FunctionalProperty:
                # Property axiom #3
                for x, y1 in self.graph.subject_objects(p):
                    for y2 in self.graph.objects(x, p):
                        # Optimization: if the two resources are identical, the samAs is already
                        # taken place somewhere else, unnecessary to add it here
                        if y1 != y2:
                            self.store_triple((y1, OWL.sameAs, y2))

            # RULE prp-ifp
            elif o == OWL.InverseFunctionalProperty:
                for x1, y in self.graph.subject_objects(p):
                    for x2 in self.graph.subjects(p, y):
                        # Optimization: if the two resources are identical, the samAs is already
                        # taken place somewhere else, unnecessary to add it here
                        if x1 != x2:
                            self.store_triple((x1, OWL.sameAs, x2))

            # RULE prp-irp
            elif o == OWL.IrreflexiveProperty:
                for x, y in self.graph.subject_objects(p):
                    if x == y:
                        self.add_error(
                            "Irreflexive property used on %s with %s" % (x, p)
                        )

            # RULE prp-symp
            elif o == OWL.SymmetricProperty:
                for x, y in self.graph.subject_objects(p):
                    self.store_triple((y, p, x))

            # RULE prp-asyp
            elif o == OWL.AsymmetricProperty:
                for x, y in self.graph.subject_objects(p):
                    if (y, p, x) in self.graph:
                        self.add_error(
                            "Erroneous usage of asymmetric property %s on %s and %s"
                            % (p, x, y)
                        )

            # RULE prp-trp
            elif o == OWL.TransitiveProperty:
                for x, y in self.graph.subject_objects(p):
                    for z in self.graph.objects(y, p):
                        self.store_triple((x, p, z))

            #
            # Breaking the order here, I take some additional rules here to the branch checking the type...
            #
            # RULE prp-adp
            elif o == OWL.AllDisjointProperties:
                x = p
                for y in self.graph.objects(x, OWL.members):
                    pis = self._list(y)
                    for i in range(0, len(pis) - 1):
                        pi = pis[i]
                        for j in range(i + 1, len(pis) - 1):
                            pj = pis[j]
                            for x, y in self.graph.subject_objects(pi):
                                if (x, pj, y) in self.graph:
                                    self.add_error(
                                        "Disjoint properties in an 'AllDisjointProperties' are not really "
                                        "disjoint: (%s, %s,%s) and (%s,%s,%s)"
                                        % (x, pi, y, x, pj, y)
                                    )

        # RULE prp-spo1
        elif t == RDFS.subPropertyOf:
            p1, p2 = p, o
            for x, y in self.graph.subject_objects(p1):
                self.store_triple((x, p2, y))

        # RULE prp-spo2
        elif t == OWL.propertyChainAxiom:
            self._property_chain(p, o)

        # RULES prp-eqp1 and prp-eqp2
        elif t == OWL.equivalentProperty:
            p1, p2 = p, o
            # Optimization: it clearly does not make sense to run these
            # if the two properties are identical (a separate axiom
            # does create an equivalent property relations among identical
            # properties, too...)
            if p1 != p2:
                # RULE prp-eqp1
                for x, y in self.graph.subject_objects(p1):
                    self.store_triple((x, p2, y))
                # RULE prp-eqp2
                for x, y in self.graph.subject_objects(p2):
                    self.store_triple((x, p1, y))

        # RULE prp-pdw
        elif t == OWL.propertyDisjointWith:
            p1, p2 = p, o
            for x, y in self.graph.subject_objects(p1):
                if (x, p2, y) in self.graph:
                    self.add_error(
                        "Erroneous usage of disjoint properties %s and %s on %s and %s"
                        % (p1, p2, x, y)
                    )

        # RULES prp-inv1 and prp-inv2
        elif t == OWL.inverseOf:
            p1, p2 = p, o
            # RULE prp-inv1
            for x, y in self.graph.subject_objects(p1):
                self.store_triple((y, p2, x))
            # RULE prp-inv2
            for x, y in self.graph.subject_objects(p2):
                self.store_triple((y, p1, x))

        # RULE prp-key
        elif t == OWL.hasKey:
            c, u = p, o
            pis = self._list(u)
            if len(pis) > 0:
                for x in self.graph.subjects(RDF.type, c):
                    # "Calculate" the keys for 'x'. The complication is that there can be various combinations
                    # of the keys, and that is the structure one has to build up here...
                    #
                    # The final list will be a list of lists, with each constituents being the possible combinations
                    # of the key values.
                    # startup the list
                    finalList = [[zi] for zi in self.graph.objects(x, pis[0])]
                    for pi in pis[1:]:
                        newList = []
                        for zi in self.graph.objects(x, pi):
                            newList = newList + [l + [zi] for l in finalList]
                        finalList = newList

                    # I am not sure this can happen, but better safe then sorry... ruling out
                    # the value lists whose length are not kosher
                    # (To be checked whether this is necessary in the first place)
                    valueList = [l for l in finalList if len(l) == len(pis)]

                    # Now we can look for the y-s, to see if they have the same key values
                    for y in self.graph.subjects(RDF.type, c):
                        # rule out the existing equivalences
                        if not (
                            y == x
                            or (y, OWL.sameAs, x) in self.graph
                            or (x, OWL.sameAs, y) in self.graph
                        ):
                            # 'calculate' the keys for the y values and see if there is a match
                            for vals in valueList:
                                same = True
                                for i in range(0, len(pis) - 1):
                                    if (y, pis[i], vals[i]) not in self.graph:
                                        same = False
                                        # No use going with this property line
                                        break
                                if same:
                                    self.store_triple((x, OWL.sameAs, y))
                                    # Look for the next 'y', this branch is finished, no reason to continue
                                    break

        # RULES prp-npa1 and prp-npa2
        elif t == OWL.sourceIndividual:
            x, i1 = p, o
            for p1 in self.graph.objects(x, OWL.assertionProperty):
                for i2 in self.graph.objects(x, OWL.targetIndividual):
                    if (i1, p1, i2) in self.graph:
                        self.add_error(
                            "Negative (object) property assertion violated for: (%s, %s, %s)"
                            % (i1, p1, i2)
                        )
                for i2 in self.graph.objects(x, OWL.targetValue):
                    if (i1, p1, i2) in self.graph:
                        self.add_error(
                            "Negative (datatype) property assertion violated for: (%s, %s, %s)"
                            % (i1, p1, i2)
                        )

    def _classes(self, triple, cycle_num):
        """
        Table 6: The Semantics of Classes. Essentially, the cls-* rules
        @param triple: triple to work on
        @param cycle_num: which cycle are we in, starting with 1. Can be used for some optimization.
        """
        # In many of the 'if' branches, corresponding to rules in the document,
        # the branch begins by a renaming of variables (eg, pp, c = s, o).
        # There is no programming reasons for doing that, but by renaming the
        # variables it becomes easier to compare the declarative rules
        # in the document with the implementation
        c, p, x = triple

        # RULE cls-nothing2
        if p == RDF.type and x == OWL.Nothing:
            self.add_error("%s is defined of type 'Nothing'" % c)

        # RULES cls-int1 and cls-int2
        if p == OWL.intersectionOf:
            classes = self._list(x)
            # RULE cls-int1
            # Optimization: by looking at the members of class[0] right away one
            # reduces the search spaces a bit. Individuals not in that class
            # are without interest anyway
            # I am not sure how empty lists are sanctioned, so having an extra check
            # on that does not hurt..
            if len(classes) > 0:
                for y in self.graph.subjects(RDF.type, classes[0]):
                    if False not in [
                        (y, RDF.type, cl) in self.graph for cl in classes[1:]
                    ]:
                        self.store_triple((y, RDF.type, c))
            # RULE cls-int2
            for y in self.graph.subjects(RDF.type, c):
                for cl in classes:
                    self.store_triple((y, RDF.type, cl))

        # RULE cls-uni
        elif p == OWL.unionOf:
            for cl in self._list(x):
                for y in self.graph.subjects(RDF.type, cl):
                    self.store_triple((y, RDF.type, c))

        # RULE cls-comm
        elif p == OWL.complementOf:
            c1, c2 = c, x
            for x1 in self.graph.subjects(RDF.type, c1):
                if (x1, RDF.type, c2) in self.graph:
                    self.add_error(
                        "Violation of complementarity for classes %s and %s on element %s"
                        % (c1, c2, x)
                    )

        # RULES cls-svf1 and cls=svf2
        elif p == OWL.someValuesFrom:
            xx, y = c, x
            # RULE cls-svf1
            # RULE cls-svf2
            for pp in self.graph.objects(xx, OWL.onProperty):
                for u, v in self.graph.subject_objects(pp):
                    if y == OWL.Thing or (v, RDF.type, y) in self.graph:
                        self.store_triple((u, RDF.type, xx))

        # RULE cls-avf
        elif p == OWL.allValuesFrom:
            xx, y = c, x
            for pp in self.graph.objects(xx, OWL.onProperty):
                for u in self.graph.subjects(RDF.type, xx):
                    for v in self.graph.objects(u, pp):
                        if self.restriction_typing_check(v, y):
                            self.store_triple((v, RDF.type, y))
                        else:
                            self.add_error(
                                "Violation of type restriction for allValuesFrom in %s for datatype %s on "
                                "value %s" % (pp, y, v)
                            )

        # RULES cls-hv1 and cls-hv2
        elif p == OWL.hasValue:
            xx, y = c, x
            for pp in self.graph.objects(xx, OWL.onProperty):
                # RULE cls-hv1
                for u in self.graph.subjects(RDF.type, xx):
                    self.store_triple((u, pp, y))
                # RULE cls-hv2
                for u in self.graph.subjects(pp, y):
                    self.store_triple((u, RDF.type, xx))

        # RULES cls-maxc1 and cls-maxc1
        elif p == OWL.maxCardinality:
            # This one is a bit complicated, because the literals have been
            # exchanged against bnodes...
            #
            # The construct should lead to an integer. Something may go wrong along the line
            # leading to an exception...
            xx = c
            if x.value == 0:
                # RULE cls-maxc1
                for pp in self.graph.objects(xx, OWL.onProperty):
                    for u, y in self.graph.subject_objects(pp):
                        # This should not occur:
                        if (u, RDF.type, xx) in self.graph:
                            self.add_error(
                                "Erroneous usage of maximum cardinality with %s and %s"
                                % (xx, y)
                            )
            elif x.value == 1:
                # RULE cls-maxc2
                for pp in self.graph.objects(xx, OWL.onProperty):
                    for u, y1 in self.graph.subject_objects(pp):
                        if (u, RDF.type, xx) in self.graph:
                            for y2 in self.graph.objects(u, pp):
                                if y1 != y2:
                                    self.store_triple((y1, OWL.sameAs, y2))

        # RULES cls-maxqc1, cls-maxqc2, cls-maxqc3, cls-maxqc4
        elif p == OWL.maxQualifiedCardinality:
            # This one is a bit complicated, because the literals have been
            # exchanged against bnodes...
            #
            # The construct should lead to an integer. Something may go wrong along the line
            # leading to an exception...
            xx = c
            if x.value == 0:
                # RULES cls-maxqc1 and cls-maxqc2 folded in one
                for pp in self.graph.objects(xx, OWL.onProperty):
                    for cc in self.graph.objects(xx, OWL.onClass):
                        for u, y in self.graph.subject_objects(pp):
                            # This should not occur:
                            if (
                                (y, RDF.type, cc) in self.graph or cc == OWL.Thing
                            ) and (u, RDF.type, xx) in self.graph:
                                self.add_error(
                                    "Erroneous usage of maximum qualified cardinality with %s, %s and %s"
                                    % (xx, cc, y)
                                )
            elif x.value == 1:
                # RULE cls-maxqc3 and cls-maxqc4 folded in one
                for pp in self.graph.objects(xx, OWL.onProperty):
                    for cc in self.graph.objects(xx, OWL.onClass):
                        for u, y1 in self.graph.subject_objects(pp):
                            if (u, RDF.type, xx) in self.graph:
                                if cc == OWL.Thing:
                                    for y2 in self.graph.objects(u, pp):
                                        if y1 != y2:
                                            self.store_triple((y1, OWL.sameAs, y2))
                                else:
                                    if (y1, RDF.type, cc) in self.graph:
                                        for y2 in self.graph.objects(u, pp):
                                            if (
                                                y1 != y2
                                                and (y2, RDF.type, cc) in self.graph
                                            ):
                                                self.store_triple((y1, OWL.sameAs, y2))

            # TODO: what if x.value not in (0, 1)? according to the spec
            # the cardinality shall be no more than 1, so add an # error?

        # RULE cls-oo
        elif p == OWL.oneOf:
            for y in self._list(x):
                self.store_triple((y, RDF.type, c))

    def _class_axioms(self, triple, cycle_num):
        """
        Table 7: Class Axioms. Essentially, the cax-* rules.
        @param triple: triple to work on
        @param cycle_num: which cycle are we in, starting with 1. Can be used for some optimization.
        """
        # In many of the 'if' branches, corresponding to rules in the document,
        # the branch begins by a renaming of variables (eg, pp, c = s, o).
        # There is no programming reasons for doing that, but by renaming the
        # variables it becomes easier to compare the declarative rules
        # in the document with the implementation
        c1, p, c2 = triple
        # RULE cax-sco
        if p == RDFS.subClassOf:
            # Other axioms sets classes to be subclasses of themselves, to one can optimize the trivial case
            if c1 != c2:
                for x in self.graph.subjects(RDF.type, c1):
                    self.store_triple((x, RDF.type, c2))

        # RULES cax-eqc1 and cax-eqc1
        # Other axioms set classes to be equivalent to themselves, one can optimize the trivial case
        elif p == OWL.equivalentClass and c1 != c2:
            # RULE cax-eqc1
            for x in self.graph.subjects(RDF.type, c1):
                self.store_triple((x, RDF.type, c2))
            # RULE cax-eqc1
            for x in self.graph.subjects(RDF.type, c2):
                self.store_triple((x, RDF.type, c1))

        # RULE cax-dw
        elif p == OWL.disjointWith:
            for x in self.graph.subjects(RDF.type, c1):
                if (x, RDF.type, c2) in self.graph:
                    self.add_error(
                        "Disjoint classes %s and %s have a common individual %s"
                        % (c1, c2, x)
                    )

        # RULE cax-adc
        elif p == RDF.type and c2 == OWL.AllDisjointClasses:
            x = c1
            for y in self.graph.objects(x, OWL.members):
                classes = self._list(y)
                if len(classes) > 0:
                    for i in range(0, len(classes) - 1):
                        cl1 = classes[i]
                        for z in self.graph.subjects(RDF.type, cl1):
                            for cl2 in classes[(i + 1) :]:
                                if (z, RDF.type, cl2) in self.graph:
                                    self.add_error(
                                        "Disjoint classes %s and %s have a common individual %s"
                                        % (cl1, cl2, z)
                                    )

    def _schema_vocabulary(self, triple, cycle_num):
        """
        Table 9: The Semantics of Schema Vocabulary. Essentially, the scm-* rules
        @param triple: triple to work on
        @param cycle_num: which cycle are we in, starting with 1. Can be used for some optimization.
        """
        # In many of the 'if' branches, corresponding to rules in the document,
        # the branch begins by a renaming of variables (eg, pp, c = s, o).
        # There is no programming reasons for doing that, but by renaming the
        # variables it becomes easier to compare the declarative rules
        # in the document with the implementation
        s, p, o = triple

        # RULE scm-cls
        if p == RDF.type and o == OWL.Class:
            c = s
            self.store_triple((c, RDFS.subClassOf, c))
            self.store_triple((c, OWL.equivalentClass, c))
            self.store_triple((c, RDFS.subClassOf, OWL.Thing))
            self.store_triple((OWL.Nothing, RDFS.subClassOf, c))

        # RULE scm-sco
        # Rule scm-eqc2
        elif p == RDFS.subClassOf:
            c1, c2 = s, o
            # RULE scm-sco
            # Optimize out the trivial identity case (set elsewhere already)
            if c1 != c2:
                for c3 in self.graph.objects(c2, RDFS.subClassOf):
                    # Another axiom already sets that...
                    if c1 != c3:
                        self.store_triple((c1, RDFS.subClassOf, c3))
            # RULE scm-eqc2
            if (c2, RDFS.subClassOf, c1) in self.graph:
                self.store_triple((c1, OWL.equivalentClass, c2))

        # RULE scm-eqc
        elif p == OWL.equivalentClass and s != o:
            c1, c2 = s, o
            self.store_triple((c1, RDFS.subClassOf, c2))
            self.store_triple((c2, RDFS.subClassOf, c1))

        # RULE scm-op and RULE scm-dp folded together
        # There is a bit of a cheating here: 'Property' is not, strictly speaking, in the rule set!
        elif p == RDF.type and (
            o == OWL.ObjectProperty or o == OWL.DatatypeProperty or o == RDF.Property
        ):
            pp = s
            self.store_triple((pp, RDFS.subPropertyOf, pp))
            self.store_triple((pp, OWL.equivalentProperty, pp))

        # RULE scm-spo
        # RULE scm-eqp2
        elif p == RDFS.subPropertyOf and s != o:
            p1, p2 = s, o
            # Optimize out the trivial identity case (set elsewhere already)
            # RULE scm-spo
            if p1 != p2:
                for p3 in self.graph.objects(p2, RDFS.subPropertyOf):
                    if p1 != p3:
                        self.store_triple((p1, RDFS.subPropertyOf, p3))

            # RULE scm-eqp2
            if (p2, RDFS.subPropertyOf, p1) in self.graph:
                self.store_triple((p1, OWL.equivalentProperty, p2))

        # RULE scm-eqp
        # Optimize out the trivial identity case (set elsewhere already)
        elif p == OWL.equivalentProperty and s != o:
            p1, p2 = s, o
            self.store_triple((p1, RDFS.subPropertyOf, p2))
            self.store_triple((p2, RDFS.subPropertyOf, p1))

        # RULES scm-dom1 and scm-dom2
        elif p == RDFS.domain:
            # RULE scm-dom1
            pp, c1 = s, o
            for _x, _y, c2 in self.graph.triples((c1, RDFS.subClassOf, None)):
                if c1 != c2:
                    self.store_triple((pp, RDFS.domain, c2))
            # RULE scm-dom1
            p2, c = s, o
            for p1, _x, _y in self.graph.triples((None, RDFS.subPropertyOf, p2)):
                if p1 != p2:
                    self.store_triple((p1, RDFS.domain, c))

        # RULES scm-rng1 and scm-rng2
        elif p == RDFS.range:
            # RULE scm-rng1
            pp, c1 = s, o
            for _x, _y, c2 in self.graph.triples((c1, RDFS.subClassOf, None)):
                if c1 != c2:
                    self.store_triple((pp, RDFS.range, c2))
            # RULE scm-rng1
            p2, c = s, o
            for p1, _x, _y in self.graph.triples((None, RDFS.subPropertyOf, p2)):
                if p1 != p2:
                    self.store_triple((p1, RDFS.range, c))

        # RULE scm-hv
        elif p == OWL.hasValue:
            c1, i = s, o
            for p1 in self.graph.objects(c1, OWL.onProperty):
                for c2 in self.graph.subjects(OWL.hasValue, i):
                    for p2 in self.graph.objects(c2, OWL.onProperty):
                        if (p1, RDFS.subPropertyOf, p2) in self.graph:
                            self.store_triple((c1, RDFS.subClassOf, c2))

        # RULES scm-svf1 and scm-svf2
        elif p == OWL.someValuesFrom:
            # RULE scm-svf1
            c1, y1 = s, o
            for pp in self.graph.objects(c1, OWL.onProperty):
                for c2 in self.graph.subjects(OWL.onProperty, pp):
                    for y2 in self.graph.objects(c2, OWL.someValuesFrom):
                        if (y1, RDFS.subClassOf, y2) in self.graph:
                            self.store_triple((c1, RDFS.subClassOf, c2))

            # RULE scm-svf2
            c1, y = s, o
            for p1 in self.graph.objects(c1, OWL.onProperty):
                for c2 in self.graph.subjects(OWL.someValuesFrom, y):
                    for p2 in self.graph.objects(c2, OWL.onProperty):
                        if (p1, RDFS.subPropertyOf, p2) in self.graph:
                            self.store_triple((c1, RDFS.subClassOf, c2))

        # RULES scm-avf1 and scm-avf2
        elif p == OWL.allValuesFrom:
            # RULE scm-avf1
            c1, y1 = s, o
            for pp in self.graph.objects(c1, OWL.onProperty):
                for c2 in self.graph.subjects(OWL.onProperty, pp):
                    for y2 in self.graph.objects(c2, OWL.allValuesFrom):
                        if (y1, RDFS.subClassOf, y2) in self.graph:
                            self.store_triple((c1, RDFS.subClassOf, c2))

            # RULE scm-avf2
            c1, y = s, o
            for p1 in self.graph.objects(c1, OWL.onProperty):
                for c2 in self.graph.subjects(OWL.allValuesFrom, y):
                    for p2 in self.graph.objects(c2, OWL.onProperty):
                        if (p1, RDFS.subPropertyOf, p2) in self.graph:
                            self.store_triple((c2, RDFS.subClassOf, c1))

        # RULE scm-int
        elif p == OWL.intersectionOf:
            c, x = s, o
            for ci in self._list(x):
                self.store_triple((c, RDFS.subClassOf, ci))

        # RULE scm-uni
        elif p == OWL.unionOf:
            c, x = s, o
            for ci in self._list(x):
                self.store_triple((ci, RDFS.subClassOf, c))
