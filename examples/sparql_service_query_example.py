from rdflib import Graph

if __name__ == "__main__":
    g = Graph()
    g.bind("dbp", "https://dbpedia.org/")
    qres = g.query(
        """
        SELECT ?s
            WHERE {
                SERVICE dbp:sparql {
                    ?s a ?o .
                }
            }
        LIMIT 3
        """
    )
    for row in qres:
        print(row.s)
