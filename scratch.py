from rdflib import Graph

nt = '<http://example.com> <http://example.com> "http://example.com [some remark]" .'
graph = Graph().parse(data=nt, format="nt").de_skolemize()
