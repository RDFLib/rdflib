#
"""
Lists of XSD datatypes and their mutual relationships

**Requires**: `RDFLib`_, 7.5.0 and higher.

.. _RDFLib: https://github.com/RDFLib/rdflib

**License**: This software is available for use under the `W3C Software License`_.

.. _W3C Software License: http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231

**Organization**: `World Wide Web Consortium`_

.. _World Wide Web Consortium: http://www.w3.org

**Author**: `Ivan Herman`_

.. _Ivan Herman: http://www.w3.org/People/Ivan/

"""
__author__ = "Ivan Herman"
__contact__ = "Ivan Herman, ivan@w3.org"
__license__ = "W3C® SOFTWARE NOTICE AND LICENSE, http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231"

from rdflib.namespace import RDF, RDFS, XSD

# The basic XSD types used everywhere; this means not the complete set of day/month types
_Common_XSD_Datatypes = [
    XSD.integer,
    XSD.decimal,
    XSD.nonNegativeInteger,
    XSD.nonPositiveInteger,
    XSD.negativeInteger,
    XSD.positiveInteger,
    XSD.long,
    XSD.int,
    XSD.short,
    XSD.byte,
    XSD.unsignedLong,
    XSD.unsignedInt,
    XSD.unsignedShort,
    XSD.unsignedByte,
    XSD.float,
    XSD.double,
    XSD.string,
    XSD.normalizedString,
    XSD.token,
    XSD.language,
    XSD.Name,
    XSD.NCName,
    XSD.NMTOKEN,
    XSD.boolean,
    XSD.hexBinary,
    XSD.base64Binary,
    XSD.anyURI,
    XSD.dateTimeStamp,
    XSD.dateTime,
    XSD.time,
    XSD.date,
    RDFS.Literal,
    RDF.XMLLiteral,
    RDF.HTML,
    RDF.langString,
]

# RDFS Datatypes: the basic ones plus the complete set of day/month ones
RDFS_Datatypes = _Common_XSD_Datatypes + [
    XSD.gYearMonth,
    XSD.gMonthDay,
    XSD.gYear,
    XSD.gDay,
    XSD.gMonth,
]

# OWL RL Datatypes: the basic ones plus plain literal
OWL_RL_Datatypes = _Common_XSD_Datatypes + [RDF.PlainLiteral]

# XSD Datatype subsumptions
_Common_Datatype_Subsumptions = {
    XSD.dateTimeStamp: [XSD.dateTime],
    XSD.integer: [XSD.decimal],
    XSD.long: [XSD.integer, XSD.decimal],
    XSD.int: [XSD.long, XSD.integer, XSD.decimal],
    XSD.short: [
        XSD.int,
        XSD.long,
        XSD.integer,
        XSD.decimal,
    ],
    XSD.byte: [
        XSD.short,
        XSD.int,
        XSD.long,
        XSD.integer,
        XSD.decimal,
    ],
    XSD.nonNegativeInteger: [XSD.integer, XSD.decimal],
    XSD.positiveInteger: [
        XSD.nonNegativeInteger,
        XSD.integer,
        XSD.decimal,
    ],
    XSD.unsignedLong: [
        XSD.nonNegativeInteger,
        XSD.integer,
        XSD.decimal,
    ],
    XSD.unsignedInt: [
        XSD.unsignedLong,
        XSD.nonNegativeInteger,
        XSD.integer,
        XSD.decimal,
    ],
    XSD.unsignedShort: [
        XSD.unsignedInt,
        XSD.unsignedLong,
        XSD.nonNegativeInteger,
        XSD.integer,
        XSD.decimal,
    ],
    XSD.unsignedByte: [
        XSD.unsignedShort,
        XSD.unsignedInt,
        XSD.unsignedLong,
        XSD.nonNegativeInteger,
        XSD.integer,
        XSD.decimal,
    ],
    XSD.nonPositiveInteger: [XSD.integer, XSD.decimal],
    XSD.negativeInteger: [
        XSD.nonPositiveInteger,
        XSD.integer,
        XSD.decimal,
    ],
    XSD.normalizedString: [XSD.string],
    XSD.token: [XSD.normalizedString, XSD.string],
    XSD.language: [XSD.token, XSD.normalizedString, XSD.string],
    XSD.Name: [XSD.token, XSD.normalizedString, XSD.string],
    XSD.NCName: [
        XSD.Name,
        XSD.token,
        XSD.normalizedString,
        XSD.string,
    ],
    XSD.NMTOKEN: [
        XSD.Name,
        XSD.token,
        XSD.normalizedString,
        XSD.string,
    ],
}

# RDFS Datatype subsumptions: at the moment, there is no extra to XSD
RDFS_Datatype_Subsumptions = _Common_Datatype_Subsumptions

# OWL Datatype subsumptions: at the moment, there is no extra to XSD
OWL_Datatype_Subsumptions = _Common_Datatype_Subsumptions
