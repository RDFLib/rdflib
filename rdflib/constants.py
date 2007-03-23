"""
Deprecated. Use rdflib.RDF and rdflib.RDFS instead.
"""

import warnings 

warnings.warn("Use rdflib.RDF and rdflib.RDFS instead.", DeprecationWarning, stacklevel=2)


from rdflib import RDF as _RDF
from rdflib import RDFS as _RDFS

RDFNS = _RDF.RDFNS

# Syntax names
RDF = _RDF.RDF
DESCRIPTION = _RDF.Description
ID = _RDF.ID
ABOUT = _RDF.about
PARSE_TYPE = _RDF.parseType
RESOURCE = _RDF.resource
LI = _RDF.li
NODE_ID = _RDF.nodeID
DATATYPE = _RDF.datatype

# RDF Classes
SEQ = _RDF.Seq
BAG = _RDF.Bag
ALT = _RDF.Alt
STATEMENT = _RDF.Statement
PROPERTY = _RDF.Property
XMLLiteral = _RDF.XMLLiteral
LIST = _RDF.List

# RDF Properties
SUBJECT = _RDF.subject
PREDICATE = _RDF.predicate
OBJECT = _RDF.object
TYPE = _RDF.type
VALUE = _RDF.value
FIRST = _RDF.first
REST = _RDF.rest
# and _n where n is a non-negative integer

# RDF Resources
NIL = _RDF.nil


# SCHEMA
RDFSNS = _RDFS.RDFSNS

RDFS_CLASS = _RDFS.Class
RDFS_RESOURCE = _RDFS.Resource
RDFS_SUBCLASSOF = _RDFS.subClassOf
RDFS_SUBPROPERTYOF = _RDFS.subPropertyOf
RDFS_ISDEFINEDBY = _RDFS.isDefinedBy
RDFS_LABEL = _RDFS.label
RDFS_COMMENT = _RDFS.comment
RDFS_RANGE = _RDFS.range
RDFS_DOMAIN = _RDFS.domain
RDFS_LITERAL = _RDFS.Literal
RDFS_CONTAINER = _RDFS.Container
RDFS_SEEALSO = _RDFS.seeAlso
