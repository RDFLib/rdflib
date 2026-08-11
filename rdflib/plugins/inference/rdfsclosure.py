#
"""
This module is brute force implementation of the RDFS semantics on the top of RDFLib (with some caveats, see in the
introductory text).


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

from itertools import product
from typing import Union

from rdflib import Graph, Literal
from rdflib.namespace import RDF, RDFS
from rdflib.plugins.inference.axiomatictriples import (
    RDFS_Axiomatic_Triples,
    RDFS_D_Axiomatic_Triples,
)
from rdflib.plugins.inference.closure import Core

######################################################################################################

# ruff: noqa: N801 N806

# mypy: disable_error_code = "valid-type, union-attr"


# RDFS Semantics class
# noinspection PyPep8Naming
class RDFS_Semantics(Core):
    """
    RDFS Semantics class, ie, implementation of the RDFS closure graph.

    .. note:: Note that the module does *not* implement the so called Datatype entailment rules, simply because the
        underlying RDFLib does not implement the datatypes (ie, RDFLib will not make the literal "1.00" and "1.00000"
        identical, although even with all the ambiguities on datatypes, this I{should} be made equal...).

        Also, the so-called extensional entailment rules (Section 7.3.1 in the RDF Semantics document) have not been
        implemented either.

    The comments and references to the various rule follow the names as used in the `RDF Semantics document`_.

    .. _RDF Semantics document: http://www.w3.org/TR/rdf-mt/

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

    def add_axioms(self):
        """
        Add axioms
        """
        for t in RDFS_Axiomatic_Triples:
            self.destination.add(t)
        for i in range(1, self.IMaxNum + 1):
            ci = RDF[("_%d" % i)]
            self.destination.add((ci, RDF.type, RDF.Property))
            self.destination.add((ci, RDFS.domain, RDFS.Resource))
            self.destination.add((ci, RDFS.range, RDFS.Resource))
            self.destination.add((ci, RDF.type, RDFS.ContainerMembershipProperty))

    def add_d_axioms(self):
        """
        This is not really complete, because it just uses the comparison possibilities that RDFLib provides.
        """
        # #1
        literals = (lt for lt in self._literals() if lt.datatype is not None)
        for lt in literals:
            self.destination.add((lt, RDF.type, lt.datatype))

        for t in RDFS_D_Axiomatic_Triples:
            self.destination.add(t)

    @staticmethod
    def _literals_same_as(lt1, lt2):
        if lt1.value is not None and lt2.value is not None:
            return lt1.value == lt2.value
        elif lt1.datatype is not None and lt2.datatype is not None:
            return lt1.__eq__(lt2)
        return False

    # noinspection PyBroadException
    def one_time_rules(self):
        """
        Some of the rules in the rule set are axiomatic in nature, meaning that they really have to be added only
        once, there is no reason to add these in a cycle. These are performed by this method that is invoked only once
        at the beginning of the process.

        In this case this is related to a 'hidden' same as rules on literals with identical values (though different
        lexical values).
        """
        # There is also a hidden sameAs rule in RDF Semantics: if a literal appears in a triple, and another one has
        # the same value, then the triple should be duplicated with the other value.
        literals = self._literals()
        items = (
            (lt1, lt2)
            for lt1, lt2 in product(literals, literals)
            if (lt1 is lt2) or self._literals_same_as(lt1, lt2)
        )
        for lt1, lt2 in items:
            # In OWL, this line is simply stating a sameAs for the
            # corresponding literals, and then let the usual rules take
            # effect. In RDFS this is not possible, so the sameAs rule is,
            # essentially replicated...
            for s, p, o in self.graph.triples((None, None, lt1)):
                self.destination.add((s, p, lt2))

    def rules(self, t, cycle_num):
        """
        Go through the RDFS entailment rules rdf1, rdfs4-rdfs12, by extending the graph.

        :param t: A triple (in the form of a tuple).
        :type t: tuple

        :param cycle_num: Which cycle are we in, starting with 1. Can be used for some (though minor) optimization.
        :type cycle_num: int
        """
        s, p, o = t
        # rdf1
        self.store_triple((p, RDF.type, RDF.Property))
        # rdfs4a
        if cycle_num == 1:
            self.store_triple((s, RDF.type, RDFS.Resource))
        # rdfs4b
        if cycle_num == 1:
            self.store_triple((o, RDF.type, RDFS.Resource))
        if p == RDFS.domain:
            # rdfs2
            for uuu, Y, yyy in self.graph.triples((None, s, None)):
                self.store_triple((uuu, RDF.type, o))
        if p == RDFS.range:
            # rdfs3
            for uuu, Y, vvv in self.graph.triples((None, s, None)):
                self.store_triple((vvv, RDF.type, o))
        if p == RDFS.subPropertyOf:
            # rdfs5
            for Z, Y, xxx in self.graph.triples((o, RDFS.subPropertyOf, None)):
                self.store_triple((s, RDFS.subPropertyOf, xxx))
            # rdfs7
            for zzz, Z, www in self.graph.triples((None, s, None)):
                self.store_triple((zzz, o, www))
        if p == RDF.type and o == RDF.Property:
            # rdfs6
            self.store_triple((s, RDFS.subPropertyOf, s))
        if p == RDF.type and o == RDFS.Class:
            # rdfs8
            self.store_triple((s, RDFS.subClassOf, RDFS.Resource))
            # rdfs10
            self.store_triple((s, RDFS.subClassOf, s))
        if p == RDFS.subClassOf:
            # rdfs9
            for vvv, Y, Z in self.graph.triples((None, RDF.type, s)):
                self.store_triple((vvv, RDF.type, o))
            # rdfs11
            for Z, Y, xxx in self.graph.triples((o, RDFS.subClassOf, None)):
                self.store_triple((s, RDFS.subClassOf, xxx))
        if p == RDF.type and o == RDFS.ContainerMembershipProperty:
            # rdfs12
            self.store_triple((s, RDFS.subPropertyOf, RDFS.member))
        if p == RDF.type and o == RDFS.Datatype:
            self.store_triple((s, RDFS.subClassOf, RDFS.Literal))

    def _literals(self):
        """
        Get all literals defined in the graph.
        """
        return set(
            o
            for s, p, o in self.graph.triples((None, None, None))
            if isinstance(o, Literal)
        )
