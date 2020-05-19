# from graphviz import Digraph # This code is commenented because rdflib doesnot contain graphviz
from rdflib import graph
from rdflib.term import BNode

def visualizeGraph(g,filename,shortMode = False,format1="pdf"):
    """ Code used to visualize the graph """
    dot = Digraph() # Create a dot digraph
    dot.format = format1
    classQuery = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?s where { {?s a rdfs:Class} UNION {?s a owl:Class} UNION {?s rdfs:subclass ?x}}""" # Query to exactly class and subclass
    literalQuery = """SELECT ?o WHERE { ?s ?p ?o. FILTER isLiteral(?o) }""" # Query to extract literals
    tripleQuery = """SELECT ?s ?p ?o WHERE{?s ?p ?o}""" # Query to get all the literals
    
    nodes = {} # All the nodes in the graph
    count = 1 # Assign name to nodes 
    for classes in g.query(classQuery): # Get all the classes using the query
        nodes[classes[0]] = ("class",count,g.compute_qname(classes[0],generate=True)[2]) # Save all the nodes related data
        count += 1

    for literal in g.query(literalQuery): # Get all the literal using the query
        nodes[literal[0]] = ("literal",count,literal[0])# Save all the nodes related data
        count += 1

    for queryReturn in g.query(tripleQuery): # Extract all the triples
        if queryReturn[0] not in nodes: # If not in nodes add it to node
            if type(queryReturn[0]) == BNode: # If node is blank node
                nodes[queryReturn[0]] = ("blank",count,queryReturn[0]) # Add blank node in the query
                count += 1
            else:
                nodes[queryReturn[0]] = ("normal",count,g.compute_qname(queryReturn[0],generate=True)[2]) # Add node in the query
                count += 1
            
        # if queryReturn[1] not in nodes: --- Currently not used ---
        #     nodes[queryReturn[1]] = ("normal",count)
        #     count += 1
        if queryReturn[2] not in nodes: # If not in nodes add it to node
            if type(queryReturn[2]) == BNode: # If node is blank node
                nodes[queryReturn[2]] = ("blank",count,queryReturn[2]) # Add blank node in the query
                count += 1
            else:
                nodes[queryReturn[2]] = ("normal",count,g.compute_qname(queryReturn[2],generate=True)[2]) # Add node in the query
                count += 1
                
    shapeDict = {"literal":"rectangle","class":"ellipse","blank":"ellipse","normal":"ellipse"} # Type of nodes in graph
    colorDict = {"literal":"#ADD8E6","class":"orange","normal":"orange","blank":"#E3FF00"} # Nodes color in graph 

    if shortMode: # If there in short node
        for node in nodes: # For nodes in graph
            dot.node(str(nodes[node][1]),label=nodes[node][2],tooltip=node,shape=shapeDict[nodes[node][0]],style="filled", fillcolor=colorDict[nodes[node][0]]) # Add short name nodes in the dot graph

        for queryReturn in g.query(tripleQuery): #For each triple
            dot.edge(str(nodes[queryReturn[0]][1]),str(nodes[queryReturn[2]][1]),tooltip=queryReturn[1],label=str(g.compute_qname(queryReturn[1],generate=True)[2])) # Add edges in dot graph
    else:
        for node in nodes: # For nodes in graph
            dot.node(str(nodes[node][1]),label=node,tooltip=node,shape=shapeDict[nodes[node][0]],style="filled", fillcolor=colorDict[nodes[node][0]]) # Add nodes in the dot graph

        for queryReturn in g.query(tripleQuery): #For each triple
            dot.edge(str(nodes[queryReturn[0]][1]),str(nodes[queryReturn[2]][1]),tooltip=queryReturn[1],label=queryReturn[1]) # Add edges in dot graph

    dot.render(filename,view=True) # Render graph
