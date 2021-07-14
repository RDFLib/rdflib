from rdflib.term import URIRef
from rdflib.namespace import DefinedNamespace, Namespace


class XSD(DefinedNamespace):
    """
    W3C XML Schema Definition Language (XSD) 1.1 Part 2: Datatypes
    
    Generated from: ../schemas/datatypes.xsd
    Date: 2020-05-26 14:21:14.993677
    
    The schema corresponding to this document is normative,
      with respect to the syntactic constraints it expresses in the
      XML Schema language.  The documentation (within <documentation>
      elements) below, is not normative, but rather highlights important
      aspects of the W3C Recommendation of which this is a part
    
    First the built-in primitive datatypes.  These definitions are for
      information only, the real built-in definitions are magic.
    
    For each built-in datatype in this schema (both primitive and
      derived) can be uniquely addressed via a URI constructed
      as follows:
        1) the base URI is the URI of the XML Schema namespace
        2) the fragment identifier is the name of the datatype

      For example, to address the int datatype, the URI is:

        http://www.w3.org/2001/XMLSchema#int

      Additionally, each facet definition element can be uniquely
      addressed via a URI constructed as follows:
        1) the base URI is the URI of the XML Schema namespace
        2) the fragment identifier is the name of the facet

      For example, to address the maxInclusive facet, the URI is:

        http://www.w3.org/2001/XMLSchema#maxInclusive

      Additionally, each facet usage in a built-in datatype definition
      can be uniquely addressed via a URI constructed as follows:
        1) the base URI is the URI of the XML Schema namespace
        2) the fragment identifier is the name of the datatype, followed
           by a period (".") followed by the name of the facet

      For example, to address the usage of the maxInclusive facet in
      the definition of int, the URI is:

        http://www.w3.org/2001/XMLSchema#int.maxInclusive
    
    Now the derived primitive types
    """
    _fail = True

    ENTITIES: URIRef        # see: http://www.w3.org/TR/xmlschema-2/#ENTITIES
    ENTITY: URIRef          # see: http://www.w3.org/TR/xmlschema-2/#ENTITY
    ID: URIRef              # see: http://www.w3.org/TR/xmlschema-2/#ID
    IDREF: URIRef           # see: http://www.w3.org/TR/xmlschema-2/#IDREF
    IDREFS: URIRef          # see: http://www.w3.org/TR/xmlschema-2/#IDREFS
    NCName: URIRef          # see: http://www.w3.org/TR/xmlschema-2/#NCName
    NMTOKEN: URIRef         # see: http://www.w3.org/TR/xmlschema-2/#NMTOKEN
    NMTOKENS: URIRef        # see: http://www.w3.org/TR/xmlschema-2/#NMTOKENS
    NOTATION: URIRef        # see: http://www.w3.org/TR/xmlschema-2/#NOTATIONNOTATION cannot be used directly in a schema; rather a type
    Name: URIRef            # see: http://www.w3.org/TR/xmlschema-2/#Name
    QName: URIRef           # see: http://www.w3.org/TR/xmlschema-2/#QName
    anyURI: URIRef          # see: http://www.w3.org/TR/xmlschema-2/#anyURI
    base64Binary: URIRef    # see: http://www.w3.org/TR/xmlschema-2/#base64Binary
    boolean: URIRef         # see: http://www.w3.org/TR/xmlschema-2/#boolean
    byte: URIRef            # see: http://www.w3.org/TR/xmlschema-2/#byte
    date: URIRef            # see: http://www.w3.org/TR/xmlschema-2/#date
    dateTime: URIRef        # see: http://www.w3.org/TR/xmlschema-2/#dateTime
    decimal: URIRef         # see: http://www.w3.org/TR/xmlschema-2/#decimal
    double: URIRef          # see: http://www.w3.org/TR/xmlschema-2/#double
    duration: URIRef        # see: http://www.w3.org/TR/xmlschema-2/#duration
    float: URIRef           # see: http://www.w3.org/TR/xmlschema-2/#float
    gDay: URIRef            # see: http://www.w3.org/TR/xmlschema-2/#gDay
    gMonth: URIRef          # see: http://www.w3.org/TR/xmlschema-2/#gMonth
    gMonthDay: URIRef       # see: http://www.w3.org/TR/xmlschema-2/#gMonthDay
    gYear: URIRef           # see: http://www.w3.org/TR/xmlschema-2/#gYear
    gYearMonth: URIRef      # see: http://www.w3.org/TR/xmlschema-2/#gYearMonth
    hexBinary: URIRef       # see: http://www.w3.org/TR/xmlschema-2/#binary
    int: URIRef             # see: http://www.w3.org/TR/xmlschema-2/#int
    integer: URIRef         # see: http://www.w3.org/TR/xmlschema-2/#integer
    language: URIRef        # see: http://www.w3.org/TR/xmlschema-2/#language
    long: URIRef            # see: http://www.w3.org/TR/xmlschema-2/#long
    negativeInteger: URIRef  # see: http://www.w3.org/TR/xmlschema-2/#negativeInteger
    nonNegativeInteger: URIRef  # see: http://www.w3.org/TR/xmlschema-2/#nonNegativeInteger
    nonPositiveInteger: URIRef  # see: http://www.w3.org/TR/xmlschema-2/#nonPositiveInteger
    normalizedString: URIRef  # see: http://www.w3.org/TR/xmlschema-2/#normalizedString
    positiveInteger: URIRef  # see: http://www.w3.org/TR/xmlschema-2/#positiveInteger
    short: URIRef           # see: http://www.w3.org/TR/xmlschema-2/#short
    string: URIRef          # see: http://www.w3.org/TR/xmlschema-2/#string
    time: URIRef            # see: http://www.w3.org/TR/xmlschema-2/#time
    token: URIRef           # see: http://www.w3.org/TR/xmlschema-2/#token
    unsignedByte: URIRef    # see: http://www.w3.org/TR/xmlschema-2/#unsignedByte
    unsignedInt: URIRef     # see: http://www.w3.org/TR/xmlschema-2/#unsignedInt
    unsignedLong: URIRef    # see: http://www.w3.org/TR/xmlschema-2/#unsignedLong
    unsignedShort: URIRef   # see: http://www.w3.org/TR/xmlschema-2/#unsignedShort
    
    _NS = Namespace("http://www.w3.org/2001/XMLSchema#")
