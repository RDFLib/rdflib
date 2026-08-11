#
"""
The combined closure: performing *both* the OWL 2 RL and RDFS closures.

The two are very close but there are some rules in RDFS that are not in OWL 2 RL (eg, the axiomatic
triples concerning the container membership properties). Using this closure class the
OWL 2 RL implementation becomes a full extension of RDFS.

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

from typing import Union

from rdflib import Graph
from rdflib.namespace import OWL, RDFS
from rdflib.plugins.inference.owlrl import OWLRL_Semantics
from rdflib.plugins.inference.rdfsclosure import RDFS_Semantics

######################################################################################################

# ruff: noqa: N801


# noinspection PyPep8Naming
class RDFS_OWLRL_Semantics(RDFS_Semantics, OWLRL_Semantics):
    """
    Common subclass of the RDFS and OWL 2 RL semantic classes. All methods simply call back
    to the functions in the superclasses. This may lead to some unnecessary duplication of terms
    and rules, but it is not so bad. Also, the additional identification defined for OWL Full,
    ie, Resource being the same as Thing and OWL and RDFS classes being identical are added to the
    triple store.

    Note that this class is also a possible user extension point: subclasses can be created that
    extend the standard functionality by extending this class. This class *always*} performs RDFS inferences.
    Subclasses have to set the :code:`self.rdfs` flag explicitly to the requested value if that is to be controlled.

    :param graph: The RDF graph to be extended.
    :type graph: :class:`rdflib.Graph`

    :param axioms: Whether (non-datatype) axiomatic triples should be added or not.
    :type axioms: bool

    :param daxioms: Whether datatype axiomatic triples should be added or not.
    :type daxioms: bool

    :param rdfs: Placeholder flag (used in subclassed only, it is always defaulted to True in this class)
    :type rdfs: bool

    :var full_binding_triples: Additional axiom type triples that are added to the combined semantics; these 'bind'
        the RDFS and the OWL worlds together.

    :var rdfs: (bool) Whether RDFS inference is to be performed or not. In this class instance the value is *always*
        :code:`True`, subclasses may explicitly change it at initialization time.
    :type rdfs: bool
    """

    full_binding_triples = [
        (OWL.Thing, OWL.equivalentClass, RDFS.Resource),
        (RDFS.Class, OWL.equivalentClass, OWL.Class),
        (OWL.DataRange, OWL.equivalentClass, RDFS.Datatype),
    ]

    def __init__(
        self,
        graph: Graph,
        axioms,
        daxioms,
        rdfs: bool = True,
        destination: Union[None, Graph] = None,
    ):
        """
        @param graph: the RDF graph to be extended
        @type graph: rdflib.Graph
        @param axioms: whether (non-datatype) axiomatic triples should be added or not
        @type axioms: bool
        @param daxioms: whether datatype axiomatic triples should be added or not
        @type daxioms: bool
        @param rdfs: placeholder flag (used in subclassed only, it is always defaulted to True in this class)
        @type rdfs: boolean
        @param destination: the destination graph to which the results are written. If None, use the source graph.
        @type destination: rdflib.Graph
        """
        OWLRL_Semantics.__init__(
            self, graph, axioms, daxioms, rdfs=rdfs, destination=destination
        )
        RDFS_Semantics.__init__(
            self, graph, axioms, daxioms, rdfs=rdfs, destination=destination
        )
        self.rdfs = True

    # noinspection PyMethodMayBeStatic
    @staticmethod
    def add_new_datatype(
        uri,
        conversion_function,
        datatype_list,
        subsumption_dict=None,
        subsumption_key=None,
        subsumption_list=None,
    ):
        """
        If an extension wants to add new datatypes, this method should be invoked at initialization time.

        :param uri: URI for the new datatypes, like owl_ns["Rational"].

        :param conversion_function: A function converting the lexical representation of the datatype to a Python value,
            possibly raising an exception in case of unsuitable lexical form.

        :param datatype_list: List of datatypes already in use that has to be checked.
        :type datatype_list: list

        :param subsumption_dict: Dictionary of subsumption hierarchies (indexed by the datatype URI-s).
        :type subsumption_dict: dict

        :param subsumption_key: Key in the dictionary, if None, the uri parameter is used.
        :type subsumption_key: str

        :param subsumption_list: List of subsumptions associated to a subsumption key (ie, all datatypes that are
            superclasses of the new datatype).
        :type subsumption_list: list
        """
        from .datatypehandling import AltXSDToPYTHON, use_Alt_lexical_conversions

        if datatype_list:
            datatype_list.append(uri)

        if subsumption_dict and subsumption_list:
            if subsumption_key:
                subsumption_dict[subsumption_key] = subsumption_list
            else:
                subsumption_dict[uri] = subsumption_list

        AltXSDToPYTHON[uri] = conversion_function
        use_Alt_lexical_conversions()

    def post_process(self):
        """
        Do some post-processing step. This method when all processing is done, but before handling possible
        errors (I.e., the method can add its own error messages). By default, this method is empty, subclasses
        can add content to it by overriding it.
        """
        OWLRL_Semantics.post_process(self)

    def rules(self, t, cycle_num):
        """
        :param t: A triple (in the form of a tuple).
        :type t: tuple

        :param cycle_num: Which cycle are we in, starting with 1. This value is forwarded to all local rules; it is
            also used locally to collect the bnodes in the graph.
        :type cycle_num: int
        """
        OWLRL_Semantics.rules(self, t, cycle_num)
        if self.rdfs:
            RDFS_Semantics.rules(self, t, cycle_num)

    def add_axioms(self):
        if self.rdfs:
            RDFS_Semantics.add_axioms(self)
        OWLRL_Semantics.add_axioms(self)

    def add_d_axioms(self):
        if self.rdfs:
            RDFS_Semantics.add_d_axioms(self)
        OWLRL_Semantics.add_d_axioms(self)

    def one_time_rules(self):
        """Adds some extra axioms and calls for the d_axiom part of the OWL Semantics."""
        for t in self.full_binding_triples:
            self.store_triple(t)

        # Note that the RL one time rules include the management of datatype which is a true superset
        # of the rules in RDFS. It is therefore unnecessary to add those even self.rdfs is True.
        OWLRL_Semantics.one_time_rules(self)
