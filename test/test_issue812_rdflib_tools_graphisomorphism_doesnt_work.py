from rdflib import Graph, URIRef
from rdflib.tools.graphisomorphism import IsomorphicTestableGraph


michel = URIRef("urn:michel")
tarek = URIRef("urn:tarek")
likes = URIRef("urn:likes")
pizza = URIRef("urn:pizza")
cheese = URIRef("urn:cheese")


def test_issue812_rdflib_tools_graphisomorphism_doesnt_work():

    """
    python ../../rdflib/tools/graphisomorphism.py --format=n3 input1.n3 input2.n3
    Traceback (most recent call last):
      File "../../rdflib/tools/graphisomorphism.py", line 113, in <module>
        main()
      File "../../rdflib/tools/graphisomorphism.py", line 102, in main
        graph2FName[graph] = fn
    TypeError: unhashable type: 'IsomorphicTestableGraph'
    """

    """
    diff --git a/rdflib/tools/graphisomorphism.py b/rdflib/tools/graphisomorphism.py
    index fbb31c0e..792ee371 100644
    --- a/rdflib/tools/graphisomorphism.py
    +++ b/rdflib/tools/graphisomorphism.py
    @@ -95,17 +95,20 @@ def main():
         if options.stdin:
             graph = IsomorphicTestableGraph().parse(sys.stdin, format=options.inputFormat)
             graphs.append(graph)
    -        graph2FName[graph] = "(STDIN)"
    +        graph2FName[graph.identifier] = "(STDIN)"
         for fn in args:
             graph = IsomorphicTestableGraph().parse(fn, format=options.inputFormat)
             graphs.append(graph)
    -        graph2FName[graph] = fn
    +        graph2FName[graph.identifier] = fn
         checked = set()
         for graph1, graph2 in combinations(graphs, 2):
    -        if (graph1, graph2) not in checked and (graph2, graph1) not in checked:
    +        if (graph1.identifier, graph2.identifier) not in checked and (
    +            graph2.identifier,
    +            graph1.identifier,
    +        ) not in checked:
                 assert graph1 == graph2, "%s != %s" % (
    -                graph2FName[graph1],
    -                graph2FName[graph2],
    +                graph2FName[graph1.identifier],
    +                graph2FName[graph2.identifier],
                 )
     
     

    """

    g1 = Graph()
    g1.add((michel, likes, pizza))
    g1.add((michel, likes, pizza))
    g1.add((tarek, likes, cheese))
    g1.add((tarek, likes, michel))
    g1.add((tarek, likes, pizza))

    g2 = Graph()
    g2.add((tarek, likes, pizza))
    g2.add((tarek, likes, cheese))
    g2.add((tarek, likes, michel))
    g2.add((michel, likes, pizza))
    g2.add((michel, likes, pizza))

    input1 = g1.serialize(format="ttl")

    input2 = g2.serialize(format="ttl")

    graph1 = IsomorphicTestableGraph().parse(data=input1, format="ttl")

    graph2 = IsomorphicTestableGraph().parse(data=input2, format="ttl")

    assert graph1 == graph2

    g2.add((michel, likes, tarek))

    input2 = g2.serialize(format="ttl")

    graph1 = IsomorphicTestableGraph().parse(data=input1, format="ttl")

    graph2 = IsomorphicTestableGraph().parse(data=input2, format="ttl")

    assert graph1 != graph2
