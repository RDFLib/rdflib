"""

This is a simple primer using some of the
example stuff in the Primer on N3:

http://www.w3.org/2000/10/swap/Primer

"""

# Load up RDFLib

from rdflib import ConjunctiveGraph, Namespace, Literal
from rdflib.namespace import OWL, DC

if __name__=='__main__':

    # Firstly, it doesn't have to be so complex.
    # Here we create a "Graph" of our work.
    # Think of it as a blank piece of graph paper!

    primer = ConjunctiveGraph()
    myNS = Namespace('#')

    primer.add((myNS.pat, myNS.knows, myNS.jo))
    # or:
    primer.add((myNS['pat'], myNS['age'], Literal(24)))


    # Now, with just that, lets see how the system
    # recorded *way* too many details about what
    # you just asserted as fact.
    #

    from pprint import pprint
    pprint(list(primer))


    # just think .whatever((s, p, o))
    # here we report on what we know

    pprint(list(primer.subjects()))
    pprint(list(primer.predicates()))
    pprint(list(primer.objects()))

    # and other things that make sense

    # what do we know about pat?
    pprint(list(primer.predicate_objects(myNS.pat)))

    # who is what age?
    pprint(list(primer.subject_objects(myNS.age)))



    # Okay, so lets now work with a bigger
    # dataset from the example, and start
    # with a fresh new graph.


    primer = ConjunctiveGraph()


    # Lets start with a verbatim string straight from the primer text:

    mySource = """


    @prefix : <http://www.w3.org/2000/10/swap/Primer#>.
    @prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix owl:  <http://www.w3.org/2002/07/owl#> .
    @prefix dc:  <http://purl.org/dc/elements/1.1/> .
    @prefix foo: <http://www.w3.org/2000/10/swap/Primer#>.
    @prefix swap: <http://www.w3.org/2000/10/swap/>.

    <> dc:title
      "Primer - Getting into the Semantic Web and RDF using N3".

    <#pat> <#knows> <#jo> .
    <#pat> <#age> 24 .
    <#al> is <#child> of <#pat> .

    <#pat> <#child>  <#al>, <#chaz>, <#mo> ;
           <#age>    24 ;
           <#eyecolor> "blue" .


    :Person a rdfs:Class.

    :Pat a :Person.

    :Woman a rdfs:Class; rdfs:subClassOf :Person .

    :sister a rdf:Property.

    :sister rdfs:domain :Person;
            rdfs:range :Woman.

    :Woman = foo:FemaleAdult .
    :Title a rdf:Property; = dc:title .



    """ # --- End of primer code

    # To make this go easier to spit back out...
    # technically, we already created a namespace
    # with the object init (and it added some namespaces as well)
    # By default, your main namespace is the URI of your
    # current working directory, so lets make that simpler:

    myNS = Namespace('http://www.w3.org/2000/10/swap/Primer#')
    primer.bind('', myNS)
    primer.bind('owl', OWL)
    primer.bind('dc', DC)
    primer.bind('swap', 'http://www.w3.org/2000/10/swap/')

    # Lets load it up!

    primer.parse(data=mySource, format='n3')


    # Now you can query, either directly straight into a list:

    [(x, y, z) for x, y, z in primer]

    # or spit it back out (mostly) the way we created it:

    print(primer.serialize(format='n3'))

    # for more insight into things already done, lets see the namespaces

    list(primer.namespaces())

    # lets ask something about the data

    list(primer.objects(myNS.pat, myNS.child))
