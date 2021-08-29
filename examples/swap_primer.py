"""
This is a simple primer using some of the
example stuff in the Primer on N3:

http://www.w3.org/2000/10/swap/Primer
"""

from rdflib import ConjunctiveGraph, Namespace, Literal
from rdflib.namespace import OWL, DC

if __name__ == "__main__":

    # Firstly, it doesn't have to be so complex.
    # Here we create a "Graph" of our work.
    # Think of it as a blank piece of graph paper!

    primer = ConjunctiveGraph()
    myNS = Namespace("https://example.com/")

    primer.add((myNS.pat, myNS.knows, myNS.jo))
    # or:
    primer.add((myNS["pat"], myNS["age"], Literal(24)))

    # Now, with just that, lets see how the system
    # recorded *way* too many details about what
    # you just asserted as fact.

    from pprint import pprint

    print("All the things in the Graph:")
    pprint(list(primer))

    # just think .whatever((s, p, o))
    # here we report on what we know

    print("==================")

    print("Subjects:")
    pprint(list(primer.subjects()))
    print("Predicates:")
    pprint(list(primer.predicates()))
    print("Objects:")
    pprint(list(primer.objects()))

    print("==================")
    # and other things that make sense

    print("What we know about pat:")
    pprint(list(primer.predicate_objects(myNS.pat)))

    print("Who is what age?")
    pprint(list(primer.subject_objects(myNS.age)))

    print("==================")
    print("==================")

    # Okay, so lets now work with a bigger
    # dataset from the example, and start
    # with a fresh new graph.

    del primer
    primer = ConjunctiveGraph()

    # Lets start with a verbatim string straight from the primer text:

    mySource = """
    @prefix : <https://example.com/> .
    @prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix owl:  <http://www.w3.org/2002/07/owl#> .
    @prefix dc:  <http://purl.org/dc/elements/1.1/> .
    @prefix foo: <http://www.w3.org/2000/10/swap/Primer#>.
    @prefix swap: <http://www.w3.org/2000/10/swap/>.

    <> dc:title
      "Primer - Getting into the Semantic Web and RDF using N3".

    :pat    :knows          :jo .
    :pat    :age            24 .
    :al     :is_child_of    :pat .

    :pat    :child          :al, :chaz, :mo ;
            :age            24 ;
            :eyecolor       "blue" .


    :Person a rdfs:Class .

    :Pat a :Person .

    :Woman a rdfs:Class; rdfs:subClassOf :Person .

    :sister a rdf:Property .

    :sister rdfs:domain :Person ;
            rdfs:range :Woman .

    :Woman = foo:FemaleAdult .
    :Title a rdf:Property; = dc:title .
    """  # --- End of primer code

    # To make this go easier to spit back out...
    # technically, we already created a namespace
    # with the object init (and it added some namespaces as well)
    # By default, your main namespace is the URI of your
    # current working directory, so lets make that simpler:

    primer.bind("owl", OWL)
    primer.bind("dc", DC)
    primer.bind("swap", "http://www.w3.org/2000/10/swap/")

    # Lets load it up!

    primer.parse(data=mySource, format="n3")

    # Now you can query, either directly straight into a list:

    print()
    print("Printing bigger example's triples:")
    for i in [(x, y, z) for x, y, z in primer]:
        print(i)

    # or spit it back out (mostly) the way we created it:

    print()
    print("Printing bigger example as N3:")
    print(primer.serialize(format="n3"))

    # for more insight into things already done, lets see the namespaces

    print()
    print("Printing bigger example's namespaces:")
    for n in list(primer.namespaces()):
        print(n)

    # lets ask something about the data, using a SPARQL query

    print()
    print("Who are pat's children?")
    q = "SELECT ?child WHERE { :pat :child ?child }"
    for r in primer.query(q):
        print(r)
