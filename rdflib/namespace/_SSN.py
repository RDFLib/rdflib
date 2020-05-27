from rdflib.term import URIRef
from rdflib.namespace import DefinedNamespace, Namespace


class SSN(DefinedNamespace):
    """
    Semantic Sensor Network Ontology
    
    This ontology describes sensors, actuators and observations, and related concepts. It does not describe domain
    concepts, time, locations, etc. these are intended to be included from other ontologies via OWL imports.
    
    Generated from: http://www.w3.org/ns/ssn/
    Date: 2020-05-26 14:20:09.068204

    a voaf:Vocabulary
    dcterms:created "2017-04-17"^^xsd:date
    dcterms:license <http://www.opengeospatial.org/ogc/Software>
        <http://www.w3.org/Consortium/Legal/2015/copyright-software-and-document>
    dcterms:rights "Copyright 2017 W3C/OGC."
    vann:preferredNamespacePrefix "ssn"
    vann:preferredNamespaceUri "http://www.w3.org/ns/ssn/"
    rdfs:comment "Please report any errors to the W3C Spatial Data on the Web Working Group via the SDW WG Public
    List public-sdw-wg@w3.org"
    rdfs:seeAlso <https://www.w3.org/2015/spatial/wiki/Semantic_Sensor_Network_Ontology>
    owl:imports sosa:
    owl:versionInfo '''New modular version of the SSN ontology.
    This ontology was originally developed in 2009-2011 by the W3C Semantic Sensor Networks Incubator Group (SSN-
    XG). For more information on the group's activities http://www.w3.org/2005/Incubator/ssn/. The ontology was
    revised and modularized in 2015-2017 by the W3C/OGC Spatial Data on the Web Working Group,
    https://www.w3.org/2015/spatial/wiki/Semantic_Sensor_Network_Ontology.
    In particular, (a) the scope is extended to include actuation and sampling; (b) the core concepts and
    properties are factored out into the SOSA ontology. The SSN ontology imports SOSA and adds formal
    axiomatization consistent with the text definitions in SOSA, and adds classes and properties to accommodate
    the scope of the original SSN ontology. '''
    """
    
    # http://www.w3.org/2002/07/owl#Class
    Deployment: URIRef              # Describes the Deployment of one or more Systems for a particular purpose. Deployment may be done on a Platform.
    Input: URIRef                   # Any information that is provided to a Procedure for its use.
    Output: URIRef                  # Any information that is reported from a Procedure.
    Property: URIRef                # A quality of an entity. An aspect of an entity that is intrinsic to and cannot exist without the entity.
    Stimulus: URIRef                # An event in the real world that 'triggers' the Sensor. The properties associated to the Stimulus may be different to the eventual observed ObservableProperty. It is the event, not the object, that triggers the Sensor.
    System: URIRef                  # System is a unit of abstraction for pieces of infrastructure that implement Procedures. A System may have components, its subsystems, which are other systems.

    # http://www.w3.org/2002/07/owl#FunctionalProperty
    wasOriginatedBy: URIRef         # Relation between an Observation and the Stimulus that originated it.

    # http://www.w3.org/2002/07/owl#ObjectProperty
    deployedOnPlatform: URIRef      # Relation between a Deployment and the Platform on which the Systems are deployed.
    deployedSystem: URIRef          # Relation between a Deployment and a deployed System.
    detects: URIRef                 # A relation from a Sensor to the Stimulus that the Sensor detects. The Stimulus itself will be serving as a proxy for some ObservableProperty.
    forProperty: URIRef             # A relation between some aspect of an entity and a Property.
    hasDeployment: URIRef           # Relation between a System and a Deployment, recording that the System is deployed in that Deployment.
    hasInput: URIRef                # Relation between a Procedure and an Input to it.
    hasOutput: URIRef               # Relation between a Procedure and an Output of it.
    hasProperty: URIRef             # Relation between an entity and a Property of that entity.
    hasSubSystem: URIRef            # Relation between a System and its component parts.
    implementedBy: URIRef           # Relation between a Procedure (an algorithm, procedure or method) and an entity that implements that Procedure in some executable way.
    implements: URIRef              # Relation between an entity that implements a Procedure in some executable way and the Procedure (an algorithm, procedure or method).
    inDeployment: URIRef            # Relation between a Platform and a Deployment, meaning that the deployedSystems of the Deployment are hosted on the Platform.
    isPropertyOf: URIRef            # Relation between a Property and the entity it belongs to.
    isProxyFor: URIRef              # A relation from a Stimulus to the Property that the Stimulus is serving as a proxy for.

    _NS = Namespace("http://www.w3.org/ns/ssn/")
