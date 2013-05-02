
"""

Query using graph.query

Result is iterable over the result rows

The variable bindings can be access 
as attributes of the row objects 
For variable names that are not valid python identifiers, 
dict access (i.e. with row[var] /  __getitem__) is also possible. 

result.vars contains the variables

"""

import rdflib

g = rdflib.Graph()
g.load("foaf.rdf")

for row in g.query(
        'select ?s where { [] <http://xmlns.com/foaf/0.1/knows> ?s .}'):
    print row.s 
    # or row["s"]
    # or row[rdflib.Variable("s")]
    
