from rdflib import Graph,URIRef

#This contains a dummy triple which is no interest but sometime this may be required
graphData = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix juice: <http://www.juice.org/>.
@prefix xsd: <http://www.w3.org/2001/XMLSchema#>.
@prefix dummy: <http://www.unusedPrefix.org/>.

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
				  rdfs:range "25".

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

"""

g = Graph() # Create a graph
g.parse(data=graphData, format='ttl')
print("Graph with extra prefix : \n"+g.serialize(format="ttl",allPrefix = True).decode("utf8"))
g.removeUnusedPrefix() # Call this function to remove the unused prefix premanently unbind 
print("\nGraph without extra prefix : \n"+g.serialize(format="ttl",allPrefix = True).decode("utf8")) 