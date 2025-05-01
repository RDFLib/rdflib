# SPARQL update example

SPARQL Update statements can be applied with [`update()`](rdflib.graph.Graph.update)

```python
from pathlib import Path

import rdflib

EXAMPLES_DIR = Path(__file__).parent

g = rdflib.Graph()

print(f"Initially there are {len(g)} triples in the graph")

g.update(
    """
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX dbpedia: <http://dbpedia.org/resource/>
    INSERT {
        ?s a dbpedia:Human .
    }
    WHERE {
        ?s a foaf:Person .
    }
    """
)

print(f"After the UPDATE, there are {len(g)} triples in the graph")
```
