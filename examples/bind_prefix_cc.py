"""
Prefix.cc is a community curated prefix map. By using `bind_namespace="cc"`,
you can set a namespace manager or graph to dynamically load prefixes from
this resource.
"""

import rdflib

graph = rdflib.Graph(bind_namespaces="cc")
assert graph.qname("http://purl.obolibrary.org/obo/GO_0032571") == "go:0032571"
