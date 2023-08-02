"""
Prefix.cc is a community curated prefix map. By using `bind_namespace="cc"`,
you can set a namespace manager or graph to dynamically load prefixes from
this resource.
"""

import rdflib

graph = rdflib.Graph(bind_namespaces="cc")

# The Gene Ontology is a biomedical ontology describing
# biological processes, cellular locations, and cellular components.
# It is typically abbreviated with the prefix "go" and uses PURLs
# issued by the Open Biological and Biomedical Ontologies Foundry.
prefix_map = {prefix: str(ns) for prefix, ns in graph.namespaces()}
assert "go" in prefix_map
assert prefix_map["go"] == "http://purl.obolibrary.org/obo/GO_"
assert graph.qname("http://purl.obolibrary.org/obo/GO_0032571") == "go:0032571"
