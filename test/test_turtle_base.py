import os
from rdflib.graph import Graph
from rdflib.term import URIRef

turtle = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
@prefix xsd: <http://www.w3.org/2001/XMLSchema#>.
@base <http://example.org/schemas/vehicles>.

:MotorVehicle a rdfs:Class.

:PassengerVehicle a rdfs:Class;
   rdfs:subClassOf :MotorVehicle.

:Truck a rdfs:Class;
   rdfs:subClassOf :MotorVehicle.
    
:Van a rdfs:Class;
   rdfs:subClassOf :MotorVehicle.

:MiniVan a rdfs:Class;
   rdfs:subClassOf :Van;
   rdfs:subClassOf :PassengerVehicle.

:Person a rdfs:Class.

xsd:integer a rdfs:Datatype.

:registeredTo a rdf:Property;
   rdfs:domain :MotorVehicle;
   rdfs:range  :Person.
    
:rearSeatLegRoom a rdf:Property;
   rdfs:domain :MotorVehicle;
   rdfs:range xsd:integer.

:driver a rdf:Property;
   rdfs:domain :MotorVehicle.

:primaryDriver a rdf:Property;
   rdfs:subPropertyOf :driver.
"""

turtle_without_base = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
@prefix xsd: <http://www.w3.org/2001/XMLSchema#>.

:MotorVehicle a rdfs:Class.

:PassengerVehicle a rdfs:Class;
   rdfs:subClassOf :MotorVehicle.

:Truck a rdfs:Class;
   rdfs:subClassOf :MotorVehicle.
    
:Van a rdfs:Class;
   rdfs:subClassOf :MotorVehicle.

:MiniVan a rdfs:Class;
   rdfs:subClassOf :Van;
   rdfs:subClassOf :PassengerVehicle.

:Person a rdfs:Class.

xsd:integer a rdfs:Datatype.

:registeredTo a rdf:Property;
   rdfs:domain :MotorVehicle;
   rdfs:range  :Person.
    
:rearSeatLegRoom a rdf:Property;
   rdfs:domain :MotorVehicle;
   rdfs:range xsd:integer.

:driver a rdf:Property;
   rdfs:domain :MotorVehicle.

:primaryDriver a rdf:Property;
   rdfs:subPropertyOf :driver.
"""


def test_base():
    """Test parsing turtle file with @base"""
    g = Graph()
    g.parse(data=turtle, format='turtle')
    print(len(g))
    target_predicate = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    target_object = URIRef("http://www.w3.org/2000/01/rdf-schema#Class")
    subjects = list(g.subjects(predicate=target_predicate, object=target_object))
    assert len(subjects)
    for subject in subjects:
        assert "http://example.org/schemas/vehicles" in subject.toPython()


def test_without_base():
    """Test parsing turtle file without @base"""
    g = Graph()
    g.parse(data=turtle_without_base, format='turtle')
    print(len(g))
    target_predicate = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    target_object = URIRef("http://www.w3.org/2000/01/rdf-schema#Class")
    subjects = list(g.subjects(predicate=target_predicate, object=target_object))
    assert len(subjects)
    current_dir = os.getcwd()
    for subject in subjects:
        assert current_dir in subject.toPython()
    
