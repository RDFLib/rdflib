from rdflib.term import Namespace

RDFNS = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

# Syntax names
RDF = RDFNS["RDF"]
Description = RDFNS["Description"]
ID = RDFNS["ID"]
about = RDFNS["about"]
parseType = RDFNS["parseType"]
resource = RDFNS["resource"]
li = RDFNS["li"]
nodeID = RDFNS["nodeID"]
datatype = RDFNS["datatype"]

# RDF Classes
Seq = RDFNS["Seq"]
Bag = RDFNS["Bag"]
Alt = RDFNS["Alt"]
Statement = RDFNS["Statement"]
Property = RDFNS["Property"]
XMLLiteral = RDFNS["XMLLiteral"]
List = RDFNS["List"]

# RDF Properties
subject = RDFNS["subject"]
predicate = RDFNS["predicate"]
object = RDFNS["object"]
type = RDFNS["type"]
value = RDFNS["value"]
first = RDFNS["first"]
rest = RDFNS["rest"]
# and _n where n is a non-negative integer

# RDF Resources
nil = RDFNS["nil"]
