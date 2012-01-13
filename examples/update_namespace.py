__doc__ = """Undergoing refurbishment"""


# from rdflib import Graph, URIRef
# #OLD = "http://www.mindswap.org/2004/terrorOnt.owl#"
# #OLD = "http://wang-desktop/TerrorOrgInstances#"
# OLD = "http://localhost/"
# NEW = "http://profilesinterror.mindswap.org/"
# graph = Graph()
# graph.bind("terror", "http://counterterror.mindswap.org/2005/terrorism.owl#")
# graph.bind("terror_old", "http://www.mindswap.org/2004/terrorOnt.owl#")
# graph.bind("tech", "http://www.mindswap.org/~glapizco/technical.owl#")
# graph.bind("wang-desk", "http://wang-desktop/TerrorOrgInstances#")
# graph.bind("foaf", 'http://xmlns.com/foaf/0.1/')
# graph.bind("dc", 'http://purl.org/dc/elements/1.1/')


# REDFOOT = graph.namespace("http://redfoot.net/2005/redfoot#")

# for cid, _, source in graph.triples((None, REDFOOT.source, None)):
#     if source:
#         print "updating %s" % source
#         try:
#             context = graph.get_context(cid)

#             for s, p, o in context:
#                 context.remove((s, p, o))
#                 if isinstance(s, URIRef) and OLD in s:
#                     s = URIRef(s.replace(OLD, NEW))
#                 if isinstance(p, URIRef) and OLD in p:
#                     p = URIRef(p.replace(OLD, NEW))
#                 if isinstance(o, URIRef) and OLD in o:
#                     o = URIRef(o.replace(OLD, NEW))
#                 context.add((s, p, o))

#             context.save(source, format="pretty-xml")
#         except Exception, e:
#             print(e)
