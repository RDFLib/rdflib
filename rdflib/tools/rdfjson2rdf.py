import json
from rdflib.term import URIRef
from rdflib.term import BNode, Literal
from rdflib import graph

#function called recursivelt to go through all the elements in json
def getrdffromjsontriple(js, g, array):

    for i in js:

        if isinstance(js[i], dict):
            array1 = []

            for k in array:
                array1.append(k)

            if "_:" in i:
                if BNode(i[2:]) not in array1:
                    array1.append(BNode(i[2:]))

            else:
                if URIRef(i) not in array1:
                    array1.append(URIRef(i))

            getrdffromjsontriple(js[i], g, array1)

        elif isinstance(js[i], list):

            for j in range(len(js[i])):
                if isinstance(js[i][j], dict):
                    array1 = []

                    for k in array:
                        array1.append(k)

                    if URIRef(i) not in array1:
                        array1.append(URIRef(i))

                    getrdffromjsontriple(js[i][j],g,array1)

        elif isinstance(js[i], str):

            if "type" in js:
                if js["type"] == "uri":
                    if len(array) == 2:
                        g.add((array[0], array[1], URIRef(js["value"])))

                elif js["type"] == "bnode":
                    if len(array) == 2:
                        g.add((array[0], array[1], BNode(js["value"][2:])))

                elif js["type"] == "literal":
                    if len(array) == 2:
                        if "lang" in js:
                            g.add((array[0], array[1], Literal(js["value"],js["lang"])))

                        elif "datatype" in js:
                            g.add((array[0], array[1], Literal(js["value"], datatype = js["datatype"])))

                        else:
                            g.add((array[0], array[1], Literal(js["value"])))

            return
    return

# function to be called when you want to convert a rdf-json file to a rdf graph
#it takes a rdfjson file as input and return a rdf graph
#example available in the examples folder
def getrdffromjson(filename):

    g = graph.Graph()

    f1 = open(filename, "r")
    s = f1.read()
    f1.close()

    js = json.loads(s)#loading the content of file into json
    getrdffromjsontriple(js, g, [])


    return g