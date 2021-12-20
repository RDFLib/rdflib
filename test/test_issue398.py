from rdflib import (
    logger,
    Graph,
    URIRef,
    Literal,
    RDF,
    RDFS,
    FOAF,
    ConjunctiveGraph,
    plugin,
)
from rdflib.plugin import Store
from rdflib.plugins.stores.memory import Memory, SimpleMemory
from pprint import pformat

# Think about __iadd__, __isub__ etc. for ConjunctiveGraph
# https://github.com/RDFLib/rdflib/issues/225


def test_issue398():
    store = plugin.get("Memory", Store)()
    # store = SimpleMemory()
    store = Memory()
    g1 = Graph(store=store, identifier="http://example.com/graph#1")
    g2 = Graph(store=store, identifier="http://example.com/graph#2")
    g3 = Graph(store=store, identifier="http://example.com/graph#3")

    donna = URIRef("http://example.org/donna")

    g1.addN([(donna, RDF.type, FOAF.Person, g1)])
    g2.addN([(donna, RDF.type, FOAF.Person, g2)])
    g3.addN([(donna, RDF.type, FOAF.Person, g3)])

    # for s, p, o in g1:
    #     logger.debug(f"g1: s {s}, p {p}, o {o}, g1 {g1.identifier}")

    # for s, p, o in g2:
    #     logger.debug(f"g2: s {s}, p {p}, o {o}, g2 {g2.identifier}")

    # for s, p, o in g3:
    #     logger.debug(f"g3: s {s}, p {p}, o {o}, g3 {g3.identifier}")

    logger.debug(f"len(g1) {len(g1)}")

    # Rebind the store to a ConjenctiveGraph (!!!)
    cg = ConjunctiveGraph(store)

    # for s, p, o, c in cg.quads():
    #     logger.debug(f"cg quads: s {s}, p {p}, o {o}, c {c.identifier}")

    for s, p, o, c in cg.quads((None, None, None, g1)):
        logger.debug(f"g1 in g: s {s}, p {p}, o {o}, c {c.identifier}")

    # logger.debug(f"######### donna g1 in g:")

    # for s, p, o, c in g.quads((donna, None, None, g1)):
    #     logger.debug(f"s {s}, p {p}, o {o}, c {c.identifier}")

    # logger.debug(f"####### donna RDF.type g1 in g:")

    # for s, p, o, c in g.quads((donna, RDF.type, None, g1)):
    #     logger.debug(f"s {s}, p {p}, o {o}, c {c.identifier}")

    # logger.debug(f"########### donna RDF.type FOAF.Person g1 in g:")

    # for s, p, o, c in g.quads((donna, RDF.type, FOAF.Person, g1)):
    #     logger.debug(f"s {s}, p {p}, o {o}, c {c.identifier}")


# g1 g2 g3:
# exorg:donna rdf:type foaf:Person <excom:graph#1>.
# exorg:donna rdf:type foaf:Person <excom:graph#2>.
# exorg:donna rdf:type foaf:Person <excom:graph#3>.

# 43 ######## g1 g2 g3:
# 46 s exorg:donna, p rdf:type, o foaf:Person, g1 excom:graph#1
# 49 s exorg:donna, p rdf:type, o foaf:Person, g2 excom:graph#2
# 52 s exorg:donna, p rdf:type, o foaf:Person, g3 excom:graph#3

# 1
# 54 len(g1) 1

# g:
# exorg:donna rdf:type foaf:Person <excom:graph#1>.
# exorg:donna rdf:type foaf:Person <excom:graph#2>.
# exorg:donna rdf:type foaf:Person <excom:graph#3>.

# 58 ########## g:
# 61 s exorg:donna, p rdf:type, o foaf:Person, c excom:graph#1
# 61 s exorg:donna, p rdf:type, o foaf:Person, c excom:graph#2
# 61 s exorg:donna, p rdf:type, o foaf:Person, c excom:graph#3

# g1 in g:
# exorg:donna rdf:type foaf:Person <excom:graph#1>.

# 63 ########## g1 in g:
# 66 s exorg:donna, p rdf:type, o foaf:Person, c excom:graph#1
# 66 s exorg:donna, p rdf:type, o foaf:Person, c excom:graph#2
# 66 s exorg:donna, p rdf:type, o foaf:Person, c excom:graph#3

# donna g1 in g:
# exorg:donna rdf:type foaf:Person <excom:graph#1>.

# 68 ######### donna g1 in g:
# 71 s exorg:donna, p rdf:type, o foaf:Person, c excom:graph#1
# 71 s exorg:donna, p rdf:type, o foaf:Person, c excom:graph#2
# 71 s exorg:donna, p rdf:type, o foaf:Person, c excom:graph#3

# donna RDF.type g1 in g:
# exorg:donna rdf:type foaf:Person <excom:graph#1>.

# 73 ####### donna RDF.type g1 in g:
# 76 s exorg:donna, p rdf:type, o foaf:Person, c excom:graph#1
# 76 s exorg:donna, p rdf:type, o foaf:Person, c excom:graph#2
# 76 s exorg:donna, p rdf:type, o foaf:Person, c excom:graph#3

# donna RDF.type FOAF.Person g1 in g:
# exorg:donna rdf:type foaf:Person <excom:graph#1>.

# 78 ########### donna RDF.type FOAF.Person g1 in g:
# 81 s exorg:donna, p rdf:type, o foaf:Person, c excom:graph#1
# 81 s exorg:donna, p rdf:type, o foaf:Person, c excom:graph#2
# 81 s exorg:donna, p rdf:type, o foaf:Person, c excom:graph#3
