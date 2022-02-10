from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class WGS(DefinedNamespace):
    """
    Basic Geo (WGS84 lat/long) Vocabulary

    The HTML Specification for the vocabulary can be found
    `here <https://www.w3.org/2003/01/geo/>`.
    """

    _NS = Namespace("https://www.w3.org/2003/01/geo/wgs84_pos#")

    # http://www.w3.org/2000/01/rdf-schema#Datatype
    SpatialThing: URIRef
    Point: URIRef

    # http://www.w3.org/2002/07/owl#DatatypeProperty
    alt: URIRef

    # NOTE: this is not in the official vocabulary, but it is used by dbpedia
    # and will commonly be treated as a de-facto term. It's range appears to be
    # a structured string literal. E.g.,
    # > _:something geo:geometry "POINT(-76.348335266113 39.536666870117)"
    geometry: URIRef

    lat: URIRef  # http://www.w3.org/2003/01/geo/wgs84_pos#lat
    lat_long: URIRef
    location: URIRef
    long: URIRef
