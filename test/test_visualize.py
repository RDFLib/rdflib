from rdflib import Graph,URIRef
from rdflib.visualizeGraph import visualizeGraph

graphData = """@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix juice: <http://www.juice.org/>.
@prefix xsd: <http://www.w3.org/2001/XMLSchema#>.

juice:Fruit rdf:type rdfs:Class.

juice:Apple rdf:type juice:Fruit;
			rdfs:label "Apple".

juice:FruitJuice rdf:type rdfs:Class.

juice:MixedFruitJuice rdfs:subClassOf juice:FruitJuice.


juice:juiceMadeOf rdf:Type rdf:property.

juice:juiceMadeOfFruit rdfs:subProperty juice:juiceMadeOf;
					   rdfs:domain juice:FruitJuice;
					   rdfs:range juice:Fruit.
					   
juice:costOfJuice rdf:type rdf:property;
				  rdfs:domain juice:FruitJuice;
				  rdfs:range "25"^^xsd:unsignedInt.

juice:Banana rdf:type juice:fruit;
			 rdfs:label "Banana".
			 
juice:Orange rdf:type juice:fruit;
			 rdfs:label "Orange".
			 
juice:Pineapple rdf:type juice:fruit;
				rdfs:label "Pineapple".
				
juice:Watermelon rdf:type juice:fruit;
				 rdfs:label "Watermelon".
				 
juice:Pomegranate rdf:type juice:fruit;
				  rdfs:label "Pomegranate".

juice:OrangeJuice rdf:type juice:FruitJuice;
				  rdfs:label "OrangeJuice";
				  juice:juiceMadeOf [ juice:fruitType juice:Orange;juice:quantity "3"^^xsd:unsignedInt],[juice:item "Salt";juice:quantity "1 tbs"].

juice:Mixed1 rdf:type juice:MixedFruitJuice;
			 juice:juiceMadeOfFruit juice:Banana,juice:Orange,juice:Pineapple,juice:Watermelon .

juice:Mixed2 rdf:type juice:MixedFruitJuice;
			 juice:juiceMadeOf [juice:fruitType juice:Orange;juice:quantity "2"^^xsd:unsignedInt],[juice:fruitType juice:Pomegranate;juice:quantity "1"^^xsd:unsignedInt],[juice:fruitType juice:Pineapple;juice:quantity "1"^^xsd:unsignedInt]."""

g = Graph() # Create a graph
g.parse(data=graphData, format='ttl')
# visualizeGraph(g,"Hello",shortMode = True,format1="png")  -- uncomment this to run the test code