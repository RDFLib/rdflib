from rdflib.Namespace import Namespace

RDFSNS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

Resource = RDFSNS["Resource"]
Class = RDFSNS["Class"]
subClassOf = RDFSNS["subClassOf"]
subPropertyOf = RDFSNS["subPropertyOf"]
comment = RDFSNS["comment"]
label = RDFSNS["label"]
domain = RDFSNS["domain"]
range = RDFSNS["range"]
seeAlso = RDFSNS["seeAlso"]
isDefinedBy = RDFSNS["isDefinedBy"]
Literal = RDFSNS["Literal"]
Container = RDFSNS["Container"]
ContainerMembershipProperty = RDFSNS["ContainerMembershipProperty"]
member = RDFSNS["member"]
Datatype = RDFSNS["Datatype"]

