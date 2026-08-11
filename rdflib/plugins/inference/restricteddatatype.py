#
"""
Module to datatype restrictions, i.e., data ranges.

The module implements the following aspects of datatype restrictions:

    - a new datatype is created run-time and added to the allowed and accepted datatypes; literals are checked whether they abide to the restrictions
    - the new datatype is defined to be a 'subClass' of the restricted datatype
    - literals of the restricted datatype and that abide to the restrictions defined by the facets are also assigned to be of the new type

The last item is important to handle the following structures::

 ex:RE a owl:Restriction ;
    owl:onProperty ex:p ;
    owl:someValuesFrom [
        a rdfs:Datatype ;
        owl:onDatatype xsd:string ;
        owl:withRestrictions (
            [ xsd:minLength "3"^^xsd:integer ]
            [ xsd:maxLength "6"^^xsd:integer ]
        )
    ]
 .
 ex:q ex:p "abcd"^^xsd:string.

In the case above the system can then infer that :code:`ex:q` is also of type :code:`ex:RE`.

Datatype restrictions are used by the :class:`.OWLRLExtras.OWLRL_Extension` extension class.

The implementation is **not** 100% complete. Some things that an ideal implementation should do are not done yet like:

    - checking whether a facet is of a datatype that is allowed for that facet
    - handling of non-literals in the facets (ie, if the resource is defined to be of type literal, but whose value is defined via a separate :code:`owl:sameAs` somewhere else)

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

import re
from functools import reduce

from rdflib import Graph
from rdflib import Literal as rdflibLiteral
from rdflib.namespace import OWL, RDF, RDFS, XSD
from rdflib.plugins.inference.datatypehandling import AltXSDToPYTHON

# ruff: noqa: E741 F841 N802 N806
# mypy: disable_error_code = "operator, var-annotated, unreachable"

# Constant for datatypes using min, max (inclusive and exclusive):
MIN_MAX = 0
# Constant for datatypes using length, minLength, and maxLength (and nothing else)
LENGTH = 1
# Constant for datatypes using length, minLength, maxLength, and pattern
LENGTH_AND_PATTERN = 2
# Constant for datatypes using length, minLength, maxLength, pattern, and lang range
LENGTH_PATTERN_LRANGE = 3

# Dictionary of all the datatypes, keyed by category
Datatypes_per_facets = {
    MIN_MAX: [
        # OWL.rational,
        # OWL.real,
        XSD.decimal,
        XSD.integer,
        XSD.nonNegativeInteger,
        XSD.nonPositiveInteger,
        XSD.positiveInteger,
        XSD.negativeInteger,
        XSD.long,
        XSD.short,
        XSD.byte,
        XSD.unsignedLong,
        XSD.unsignedInt,
        XSD.unsignedShort,
        XSD.unsignedByte,
        XSD.double,
        XSD.float,
        XSD.dateTime,
        XSD.dateTimeStamp,
        XSD.time,
        XSD.date,
    ],
    LENGTH: [XSD.hexBinary, XSD.base64Binary],
    LENGTH_AND_PATTERN: [
        XSD.anyURI,
        XSD.string,
        XSD.NMTOKEN,
        XSD.Name,
        XSD.NCName,
        XSD.language,
        XSD.normalizedString,
    ],
    LENGTH_PATTERN_LRANGE: [RDF.PlainLiteral],
}

# a simple list containing C{all} datatypes that may have a facet
facetable_datatypes = reduce(lambda x, y: x + y, list(Datatypes_per_facets.values()))

#######################################################################################################


def _lit_to_value(dt, v):
    """
    This method is used to convert a string to a value with facet checking. RDF Literals are converted to
    Python values using this method; if there is a problem, an exception is raised (and caught higher
    up to generate an error message).

    The method is the equivalent of all the methods in the :mod:`.DatatypeHandling` module, and is registered
    to the system run time, as new restricted datatypes are discovered.

    (Technically, the registration is done via a :code:`lambda v: _lit_to_value(self,v)` setting from within a
    :class:`.RestrictedDatatype` instance).

    :param dt: Faceted datatype.
    :type dt: :class:`RestrictedDatatype`

    :param v: Literal to be converted and checked.

    :raise ValueError: Invalid literal value.
    """
    # This may raise an exception...
    value = dt.converter(v)

    # look at the different facet categories and try to find which is
    # is, if any, the one that is of relevant for this literal
    for cat in Datatypes_per_facets:
        if dt.base_type in Datatypes_per_facets[cat]:
            # yep, this is to be checked.
            if not dt.checkValue(value):
                raise ValueError(
                    "Literal value %s does not fit the faceted datatype %s" % (v, dt)
                )
    # got here, everything should be fine
    return value


# noinspection PyPep8Naming,PyShadowingBuiltins
def _lang_range_check(range, lang):
    """
    Implementation of the extended filtering algorithm, as defined in point 3.3.2,
    of U{RFC 4647<http://www.rfc-editor.org/rfc/rfc4647.txt>}, on matching language ranges and language tags.
    Needed to handle the C{rdf:PlainLiteral} datatype.
    @param range: language range
    @param lang: language tag
    @rtype: boolean
    """

    def _match(r, l):
        """Matching of a range and language item: either range is a wildcard or the two are equal
        @param r: language range item
        @param l: language tag item
        @rtype: boolean
        """
        return r == "*" or r == l

    rangeList = range.strip().lower().split("-")
    langList = lang.strip().lower().split("-")
    if not _match(rangeList[0], langList[0]):
        return False

    rI = 1
    rL = 1
    while rI < len(rangeList):
        if rangeList[rI] == "*":
            rI += 1
            continue
        if rL >= len(langList):
            return False
        if _match(rangeList[rI], langList[rL]):
            rI += 1
            rL += 1
            continue
        if len(langList[rL]) == 1:
            return False
        else:
            rL += 1
            continue
    return True


#######################################################################################################


def extract_faceted_datatypes(core, graph: Graph):
    """
    Extractions of restricted (i.e., faceted) datatypes from the graph.

    :param core: The core closure instance that is being handled.
    :type core: :class:`.Closure.Core`

    :param graph: RDFLib graph.
    :type graph: :class:`rdflib.graph.Graph`

    :return: List of :class:`.RestrictedDatatype` instances.
    :rtype: list
    """
    retval = []
    for dtype in graph.subjects(RDF.type, RDFS.Datatype):
        base_type = None
        facets = []
        try:
            base_types = [x for x in graph.objects(dtype, OWL.onDatatype)]
            if len(base_types) > 0:
                if len(base_types) > 1:
                    raise Exception(
                        "Several base datatype for the same restriction %s" % dtype
                    )
                else:
                    base_type = base_types[0]
                    if base_type in facetable_datatypes:
                        rlists = [x for x in graph.objects(dtype, OWL.withRestrictions)]
                        if len(rlists) > 1:
                            raise Exception(
                                "More than one facet lists for the same restriction %s"
                                % dtype
                            )
                        elif len(rlists) > 0:
                            final_facets = []
                            for r in graph.items(rlists[0]):
                                for facet, lit in graph.predicate_objects(r):
                                    if isinstance(lit, rdflibLiteral):
                                        # the python value of the literal should be extracted
                                        # note that this call may lead to an exception, but that is fine,
                                        # it is caught some lines below anyway...
                                        try:
                                            if (
                                                lit.datatype is None
                                                or lit.datatype == XSD.string
                                            ):
                                                final_facets.append((facet, str(lit)))
                                            else:
                                                final_facets.append(
                                                    (
                                                        facet,
                                                        AltXSDToPYTHON[lit.datatype](
                                                            str(lit)
                                                        ),
                                                    )
                                                )
                                        except Exception as msg:
                                            core.add_error(msg)
                                            continue
                                # We do have everything we need:
                            new_datatype = RestrictedDatatype(
                                dtype, base_type, final_facets
                            )
                            retval.append(new_datatype)
        except Exception as msg:
            # import sys
            # print sys.exc_info()
            # print sys.exc_type
            # print sys.exc_value
            # print sys.exc_traceback
            core.add_error(msg)
            continue
    return retval


# noinspection PyPep8Naming
class RestrictedDatatypeCore:
    """
    An 'abstract' superclass for datatype restrictions. The instance variables listed here are
    used in general, without the specificities of the concrete restricted datatype.

    This module defines the :class:`.RestrictedDatatype` class that corresponds to the datatypes and their restrictions
    defined in the OWL 2 standard. Other modules may subclass this class to define new datatypes with restrictions.

    :ivar type_uri: The URI for this datatype.

    :ivar base_type: URI of the datatype that is restricted.

    :ivar toPython: Function to convert a Literal of the specified type to a Python value.
    """

    def __init__(self, type_uri, base_type):
        self.datatype = type_uri
        self.base_type = base_type
        self.toPython = None

    def checkValue(self, value):
        """
        Check whether the (Python) value abides to the constraints defined by the current facets.

        :param value: The value to be checked.
        :rtype: bool
        """
        raise Exception(
            "This class should not be used by itself, only via its subclasses!"
        )


# noinspection PyPep8Naming
class RestrictedDatatype(RestrictedDatatypeCore):
    """
    Implementation of a datatype with facets, ie, datatype with restrictions.

    :param type_uri: URI of the datatype being defined.
    :param base_type: URI of the base datatype, ie, the one being restricted.
    :param facets: List of :code:`(facetURI, value)` pairs.

    :ivar datatype : The URI for this datatype.

    :ivar base_type: URI of the datatype that is restricted.

    :ivar converter: Method to convert a literal of the base type to a Python value (:code:`DatatypeHandling.AltXSDToPYTHON`).

    :ivar minExclusive: Value for the :code`xsd:minExclusive` facet, initialized to :code:`None` and set to the right value if
        a facet is around.
    :ivar minInclusive: Value for the :code:`xsd:minInclusive` facet, initialized to :code:`None` and set to the right value if
        a facet is around.
    :ivar maxExclusive: Value for the :code:`xsd:maxExclusive` facet, initialized to :code:`None` and set to the right value if
        a facet is around.
    :ivar maxInclusive: Value for the :code:`xsd:maxInclusive` facet, initialized to :code:`None` and set to the right value if
        a facet is around.
    :ivar minLength: Value for the :code:`xsd:minLength` facet, initialized to :code:`None` and set to the right value if a facet
        is around.
    :ivar maxLength: Value for the :code:`xsd:maxLength` facet, initialized to :code:`None` and set to the right value if a facet
        is around.
    :ivar length: Value for the :code:`xsd:length` facet, initialized to :code:`None` and set to the right value if a facet is
        around.
    :ivar pattern: Array of patterns for the :code:`xsd:pattern` facet, initialized to :code:`[]` and set to the right value if a
        facet is around.
    :ivar langRange: Array of language ranges for the :code:`rdf:langRange` facet, initialized to :code:`[]` and set to the right
        value if a facet is around.
    :ivar check_methods: List of class methods that are relevant for the given :code:`base_type`.

    :ivar toPython: Function to convert a Literal of the specified type to a Python value. Is defined by :code:`lambda v:
        _lit_to_value(self, v)`, see :py:func:`._lit_to_value`.
    """

    def __init__(self, type_uri, base_type, facets):
        """
        @param type_uri: URI of the datatype being defined
        @param base_type: URI of the base datatype, ie, the one being restricted
        @param facets: array of C{(facetURI, value)} pairs
        """
        RestrictedDatatypeCore.__init__(self, type_uri, base_type)
        if self.base_type not in AltXSDToPYTHON:
            raise Exception("No facet is implemented for datatype %s" % self.base_type)
        self.converter = AltXSDToPYTHON[self.base_type]

        self.minExclusive = None
        self.maxExclusive = None
        self.minInclusive = None
        self.maxInclusive = None
        self.length = None
        self.maxLength = None
        self.minLength = None
        self.pattern = []
        self.langRange = []
        for facet, value in facets:
            if facet == XSD.minInclusive and (
                self.minInclusive is None or self.minInclusive < value
            ):
                self.minInclusive = value
            elif facet == XSD.minExclusive and (
                self.minExclusive is None or self.minExclusive < value
            ):
                self.minExclusive = value
            elif facet == XSD.maxInclusive and (
                self.maxInclusive is None or value < self.maxInclusive
            ):
                self.maxInclusive = value
            elif facet == XSD.maxExclusive and (
                self.maxExclusive is None or value < self.maxExclusive
            ):
                self.maxExclusive = value
            elif facet == RDF.langRange:
                self.langRange.append(value)
            elif facet == XSD.length:
                self.length = value
            elif facet == XSD.maxLength and (
                self.maxLength is None or value < self.maxLength
            ):
                self.maxLength = value
            elif facet == XSD.minLength and (
                self.minLength is None or value > self.minLength
            ):
                self.minLength = value
            elif facet == XSD.pattern:
                self.pattern.append(re.compile(value))

        # Choose the methods that are relevant for this datatype, based on the base type
        facet_to_method = {
            MIN_MAX: [
                RestrictedDatatype._check_max_exclusive,
                RestrictedDatatype._check_min_exclusive,
                RestrictedDatatype._check_max_inclusive,
                RestrictedDatatype._check_min_inclusive,
            ],
            LENGTH: [
                RestrictedDatatype._check_min_length,
                RestrictedDatatype._check_max_length,
                RestrictedDatatype._check_length,
            ],
            LENGTH_AND_PATTERN: [
                RestrictedDatatype._check_min_length,
                RestrictedDatatype._check_max_length,
                RestrictedDatatype._check_length,
                RestrictedDatatype._check_pattern,
            ],
            LENGTH_PATTERN_LRANGE: [
                RestrictedDatatype._check_min_length,
                RestrictedDatatype._check_max_length,
                RestrictedDatatype._check_length,
                RestrictedDatatype._check_lang_range,
            ],
        }
        self.check_methods = []
        for cat in Datatypes_per_facets:
            if self.base_type in Datatypes_per_facets[cat]:
                self.check_methods = facet_to_method[cat]
                break
        self.toPython = lambda v: _lit_to_value(self, v)

    def checkValue(self, value):
        """
        Check whether the (Python) value abides to the constraints defined by the current facets.

        :param value: The value to be checked.
        :rtype: bool
        """
        for method in self.check_methods:
            if not method(self, value):
                return False
        return True

    def _check_min_exclusive(self, value):
        """
        Check  the (python) value against min exclusive facet.
        @param value: the value to be checked
        @rtype: boolean
        """
        if self.minExclusive is not None:
            return self.minExclusive < value
        else:
            return True

    def _check_min_inclusive(self, value):
        """
        Check  the (python) value against min inclusive facet.
        @param value: the value to be checked
        @rtype: boolean
        """
        if self.minInclusive is not None:
            return self.minInclusive <= value
        else:
            return True

    def _check_max_exclusive(self, value):
        """
        Check  the (python) value against max exclusive facet.
        @param value: the value to be checked
        @rtype: boolean
        """
        if self.maxExclusive is not None:
            return value < self.maxExclusive
        else:
            return True

    def _check_max_inclusive(self, value):
        """
        Check  the (python) value against max inclusive facet.
        @param value: the value to be checked
        @rtype: boolean
        """
        if self.maxInclusive is not None:
            return value <= self.maxInclusive
        else:
            return True

    def _check_min_length(self, value):
        """
        Check  the (python) value against minimum length facet.
        @param value: the value to be checked
        @rtype: boolean
        """
        if isinstance(value, rdflibLiteral):
            val = str(value)
        else:
            val = value
        if self.minLength is not None:
            return self.minLength <= len(val)
        else:
            return True

    def _check_max_length(self, value):
        """
        Check  the (python) value against maximum length facet.
        @param value: the value to be checked
        @rtype: boolean
        """
        if isinstance(value, rdflibLiteral):
            val = str(value)
        else:
            val = value
        if self.maxLength is not None:
            return self.maxLength >= len(val)
        else:
            return True

    def _check_length(self, value):
        """
        Check  the (python) value against exact length facet.
        @param value: the value to be checked
        @rtype: boolean
        """
        if isinstance(value, rdflibLiteral):
            val = str(value)
        else:
            val = value
        if self.length is not None:
            return self.length == len(val)
        else:
            return True

    def _check_pattern(self, value):
        """
        Check  the (python) value against array of regular expressions.
        @param value: the value to be checked
        @rtype: boolean
        """
        if isinstance(value, rdflibLiteral):
            val = str(value)
        else:
            val = value
        for p in self.pattern:
            if p.match(val) is None:
                return False
        return True

    def _check_lang_range(self, value):
        """
        Check  the (python) value against array of language ranges.
        @param value: the value to be checked
        @rtype: boolean
        """
        if isinstance(value, rdflibLiteral):
            lang = value.language
        else:
            return False
        for r in self.langRange:
            if not _lang_range_check(r, lang):
                return False
        return True
