# -*- coding: utf-8 -*-
# try:
#     from graphviz import Digraph
# except ModuleNotFoundError:
#     raise ModuleNotFoundError("Graphviz module not found.")
from graphviz import Digraph

from rdflib import URIRef, Literal
from rdflib.term import BNode


def visualize_graph(g, filename, shortMode=False, format1="pdf"):
    """
    Code used to visualize the graph
    """
    dot = Digraph()  # Create a dot digraph
    dot.format = format1
    classQuery = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?s where { {?s a rdfs:Class} UNION {?s a owl:Class} UNION {?s rdfs:subclass ?x}}"""  # Query to exactly class and subclass
    literalQuery = """SELECT ?o WHERE { ?s ?p ?o. FILTER isLiteral(?o) }"""  # Query to extract literals
    tripleQuery = """SELECT ?s ?p ?o WHERE{?s ?p ?o}"""  # Query to get all the literals

    nodes = {}  # All the nodes in the graph
    count = 1  # Assign name to nodes
    for classes in g.query(classQuery):  # Get all the classes using the query
        nodes[classes[0]] = (
            "class",
            count,
            g.compute_qname(classes[0], generate=True)[2],
        )  # Save all the nodes related data
        count += 1

    for literal in g.query(literalQuery):  # Get all the literal using the query
        nodes[literal[0]] = (
            "literal",
            count,
            literal[0],
        )  # Save all the nodes related data
        count += 1

    for queryReturn in g.query(tripleQuery):  # Extract all the triples
        if queryReturn[0] not in nodes:  # If not in nodes add it to node
            if type(queryReturn[0]) == BNode:  # If node is blank node
                nodes[queryReturn[0]] = (
                    "blank",
                    count,
                    queryReturn[0],
                )  # Add blank node in the query
                count += 1
            else:
                nodes[queryReturn[0]] = (
                    "normal",
                    count,
                    g.compute_qname(queryReturn[0], generate=True)[2],
                )  # Add node in the query
                count += 1

        # if queryReturn[1] not in nodes: --- Currently not used ---
        #     nodes[queryReturn[1]] = ("normal",count)
        #     count += 1

        if queryReturn[2] not in nodes:  # If not in nodes add it to node
            if type(queryReturn[2]) == BNode:  # If node is blank node
                nodes[queryReturn[2]] = (
                    "blank",
                    count,
                    queryReturn[2],
                )  # Add blank node in the query
                count += 1
            else:
                try:
                    nodes[queryReturn[2]] = (
                        "normal",
                        count,
                        g.compute_qname(queryReturn[2], generate=True)[2],
                    )  # Add node in the query
                    count += 1
                except ValueError:
                    pass

    shapeDict = {
        "literal": "rectangle",
        "class": "ellipse",
        "blank": "ellipse",
        "normal": "ellipse",
    }  # Type of nodes in graph
    colorDict = {
        "literal": "#ADD8E6",
        "class": "orange",
        "normal": "orange",
        "blank": "#E3FF00",
    }  # Nodes color in graph

    if shortMode:  # If there in short node
        for node in nodes:  # For nodes in graph
            dot.node(
                str(nodes[node][1]),
                label=nodes[node][2],
                tooltip=node,
                shape=shapeDict[nodes[node][0]],
                style="filled",
                fillcolor=colorDict[nodes[node][0]],
            )  # Add short name nodes in the dot graph

        for queryReturn in g.query(tripleQuery):  # For each triple
            dot.edge(
                str(nodes[queryReturn[0]][1]),
                str(nodes[queryReturn[2]][1]),
                tooltip=queryReturn[1],
                label=str(g.compute_qname(queryReturn[1], generate=True)[2]),
            )  # Add edges in dot graph
    else:
        for node in nodes:  # For nodes in graph
            dot.node(
                str(nodes[node][1]),
                label=node,
                tooltip=node,
                shape=shapeDict[nodes[node][0]],
                style="filled",
                fillcolor=colorDict[nodes[node][0]],
            )  # Add nodes in the dot graph

        for queryReturn in g.query(tripleQuery):  # For each triple
            dot.edge(
                str(nodes[queryReturn[0]][1]),
                str(nodes[queryReturn[2]][1]),
                tooltip=queryReturn[1],
                label=queryReturn[1],
            )  # Add edges in dot graph

    dot.render(filename, view=True)  # Render graph


def check_path_between(g, node1, node2):
    """Code to check path between any two node can be used to find relation between nodes"""
    if isinstance(node1, Literal) and isinstance(node2, Literal):
        queryCheck = (
            "ASK { " + str(node1) + " ((<>|!<>)|^(<>|!<>))* " + str(node2) + " }"
        )  # Check path between node and literal
        for i in g.query(queryCheck):
            return i
    elif isinstance(node1, Literal) and isinstance(node2, URIRef):
        queryCheck = (
            "ASK { " + str(node1) + " ((<>|!<>)|^(<>|!<>))* <" + str(node2) + "> }"
        )  # Check path between node and node
        for i in g.query(queryCheck):
            return i
    elif isinstance(node1, URIRef) and isinstance(node2, Literal):
        queryCheck = (
            "ASK { <" + str(node1) + "> ((<>|!<>)|^(<>|!<>))* " + str(node2) + " }"
        )  # Check path between literal and node
        for i in g.query(queryCheck):
            return i
    elif isinstance(node1, URIRef) and isinstance(node2, URIRef):
        queryCheck = (
            "ASK { <" + str(node1) + "> ((<>|!<>)|^(<>|!<>))* <" + str(node2) + "> }"
        )  # Check path between literal and literal
        for i in g.query(queryCheck):
            return i


def get_properties_path(g, node1, node2):
    """Code to get properties in the path of 2 nodes"""
    if check_path_between(g, node1, node2):  # Query to retrieve property path
        queryProperties = (
            """ SELECT ?temp ?prop ?temp2 WHERE{
                            {
                                <"""
            + str(node1)
            + """> (<>|!<>)* ?temp .
                                ?temp ?prop ?temp2 .
                                ?temp2 (<>|!<>)* <"""
            + str(node2)
            + """>
                            }
                            UNION
                            {
                                <"""
            + str(node1)
            + """> (<>|!<>)* ?temp.
                                ?temp ?prop ?temp2 .
                                ?temp2 (<>|!<>)* ?temp3 .
                                <"""
            + str(node2)
            + """> (<>|!<>)* ?temp4.
                                ?temp4 ?prop2 ?temp5 .
                                ?temp5 (<>|!<>)* ?temp3
                            }
                            UNION
                            {
                                <"""
            + str(node2)
            + """> (<>|!<>)* ?temp.
                                ?temp ?prop ?temp2 .
                                ?temp2 (<>|!<>)* ?temp3 .
                                <"""
            + str(node1)
            + """> (<>|!<>)* ?temp4.
                                ?temp4 ?prop2 ?temp5 .
                                ?temp5 (<>|!<>)* ?temp3
                            }
                            UNION
                            {
                                ?temp3 (<>|!<>)* ?temp.
                                ?temp ?prop ?temp2 .
                                ?temp2 (<>|!<>)* <"""
            + str(node1)
            + """>.
                                ?temp3 (<>|!<>)* ?temp4.
                                ?temp4 ?prop2 ?temp5 .
                                ?temp5 (<>|!<>)* <"""
            + str(node2)
            + """>
                            }
                            UNION
                            {
                                ?temp3 (<>|!<>)* ?temp.
                                ?temp ?prop ?temp2 .
                                ?temp2 (<>|!<>)* <"""
            + str(node2)
            + """>.
                                ?temp3 (<>|!<>)* ?temp4.
                                ?temp4 ?prop2 ?temp5 .
                                ?temp5 (<>|!<>)* <"""
            + str(node1)
            + """>
                            }
                            UNION
                            {
                                <"""
            + str(node2)
            + """> (<>|!<>)* ?temp .
                                ?temp ?prop ?temp2 .
                                ?temp2 (<>|!<>)* <"""
            + str(node1)
            + """>
                            }
                           }"""
        )
        listProperties = []
        for i in g.query(queryProperties):  # For all the properties add to list
            listProperties += [i]

        return set(listProperties)  # Retun properties set to remove duplicates
    else:
        return set([])


def show_properties_path(g, node1, node2, filename, shortMode=False, format1="pdf"):
    """Code used to visualize the path between nodes in the graph"""
    dot = Digraph()  # Create a dot digraph
    dot.format = format1
    classQuery = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?s where { {?s a rdfs:Class} UNION {?s a owl:Class} UNION {?s rdfs:subclass ?x}}"""  # Query to exactly class and subclass
    literalQuery = """SELECT ?o WHERE { ?s ?p ?o. FILTER isLiteral(?o) }"""  # Query to extract literals
    tripleQuery = """SELECT ?s ?p ?o WHERE{?s ?p ?o}"""  # Query to get all the literals

    nodes = {}  # All the nodes in the graph
    count = 1  # Assign name to nodes
    for classes in g.query(classQuery):  # Get all the classes using the query
        nodes[classes[0]] = (
            "class",
            count,
            g.compute_qname(classes[0], generate=True)[2],
        )  # Save all the nodes related data
        count += 1

    for literal in g.query(literalQuery):  # Get all the literal using the query
        nodes[literal[0]] = (
            "literal",
            count,
            literal[0],
        )  # Save all the nodes related data
        count += 1

    for queryReturn in g.query(tripleQuery):  # Extract all the triples
        if queryReturn[0] not in nodes:  # If not in nodes add it to node
            if type(queryReturn[0]) == BNode:  # If node is blank node
                nodes[queryReturn[0]] = (
                    "blank",
                    count,
                    queryReturn[0],
                )  # Add blank node in the query
                count += 1
            else:
                nodes[queryReturn[0]] = (
                    "normal",
                    count,
                    g.compute_qname(queryReturn[0], generate=True)[2],
                )  # Add node in the query
                count += 1

        # if queryReturn[1] not in nodes: --- Currently not used ---
        #     nodes[queryReturn[1]] = ("normal",count)
        #     count += 1
        if queryReturn[2] not in nodes:  # If not in nodes add it to node
            if type(queryReturn[2]) == BNode:  # If node is blank node
                nodes[queryReturn[2]] = (
                    "blank",
                    count,
                    queryReturn[2],
                )  # Add blank node in the query
                count += 1
            else:
                nodes[queryReturn[2]] = (
                    "normal",
                    count,
                    g.compute_qname(queryReturn[2], generate=True)[2],
                )  # Add node in the query
                count += 1

    shapeDict = {
        "literal": "rectangle",
        "class": "ellipse",
        "blank": "ellipse",
        "normal": "ellipse",
    }  # Type of nodes in graph
    colorDict = {
        "literal": "#ADD8E6",
        "class": "orange",
        "normal": "orange",
        "blank": "#E3FF00",
    }  # Nodes color in graph

    listNodes = get_properties_path(g, node1, node2)  # Retrieve all the paths
    if shortMode:  # If there in short node
        for node in nodes:  # For nodes in graph
            dot.node(
                str(nodes[node][1]),
                label=nodes[node][2],
                tooltip=node,
                shape=shapeDict[nodes[node][0]],
                style="filled",
                fillcolor=colorDict[nodes[node][0]],
            )  # Add short name nodes in the dot graph

        for queryReturn in g.query(tripleQuery):  # For each triple
            if queryReturn not in listNodes:  # If not in list to avoid duplicates
                dot.edge(
                    str(nodes[queryReturn[0]][1]),
                    str(nodes[queryReturn[2]][1]),
                    tooltip=queryReturn[1],
                    label=str(g.compute_qname(queryReturn[1], generate=True)[2]),
                )  # Add edges in dot graph

        for edge in listNodes:
            dot.edge(
                str(nodes[edge[0]][1]),
                str(nodes[edge[2]][1]),
                color="red",
                tooltip=edge[1],
                label=str(g.compute_qname(edge[1], generate=True)[2]),
            )  # Add edges in dot graph
    else:
        for node in nodes:  # For nodes in graph
            dot.node(
                str(nodes[node][1]),
                label=node,
                tooltip=node,
                shape=shapeDict[nodes[node][0]],
                style="filled",
                fillcolor=colorDict[nodes[node][0]],
            )  # Add nodes in the dot graph

        for queryReturn in g.query(tripleQuery):  # For each triple
            if queryReturn not in listNodes:  # If not in list to avoid duplicates
                dot.edge(
                    str(nodes[queryReturn[0]][1]),
                    str(nodes[queryReturn[2]][1]),
                    tooltip=queryReturn[1],
                    label=queryReturn[1],
                )  # Add edges in dot graph

        for edge in listNodes:
            dot.edge(
                str(nodes[edge[0]][1]),
                str(nodes[edge[2]][1]),
                color="red",
                tooltip=edge[1],
                label=edge[1],
            )  # Add edges in dot graph

    dot.render(filename, view=True)  # Render graph
