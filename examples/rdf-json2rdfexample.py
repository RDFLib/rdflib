from rdflib.tools.rdfjson2rdf import getrdffromjson

#replace C:\\Users\hp\PycharmProjects\Sweb\projectrdf.json with your filename
g = getrdffromjson("rdf-json2rdf.json")

#select any format of rdf serealization
print(g.serialize(format="turtle").decode("utf-8"))