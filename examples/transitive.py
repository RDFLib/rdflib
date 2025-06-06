"""
An example illustrating how to use the
[`Graph.transitive_subjects`][rdflib.graph.Graph.transitive_subjects] and
[`Graph.transitive_objects`][rdflib.graph.Graph.transitive_objects] graph methods

## Formal definition


The [`Graph.transitive_objects`][rdflib.graph.Graph.transitive_objects] method finds all
nodes such that there is a path from subject to one of those nodes
using only the predicate property in the triples. The
[`Graph.transitive_subjects`][rdflib.graph.Graph.transitive_subjects] method is similar; it
finds all nodes such that there is a path from the node to the object
using only the predicate property.

## Informal description, with an example

In brief, [`Graph.transitive_objects`][rdflib.graph.Graph.transitive_objects] walks forward
in a graph using a particular property, and
[`Graph.transitive_subjects`][rdflib.graph.Graph.transitive_subjects] walks backward. A good
example uses a property `ex:parent`, the semantics of which are
biological parentage. The
[`Graph.transitive_objects`][rdflib.graph.Graph.transitive_objects] method would get all
the ancestors of a particular person (all nodes such that there is a
parent path between the person and the object). The
[`Graph.transitive_subjects`][rdflib.graph.Graph.transitive_subjects] method would get all
the descendants of a particular person (all nodes such that there is a
parent path between the node and the person). So, say that your URI is
`ex:person`.

This example would get all of your (known) ancestors, and then get all
the (known) descendants of your maternal grandmother.

!!! warning "Important note on arguments"

    The [`Graph.transitive_objects`][rdflib.graph.Graph.transitive_objects] method has the start node
    as the *first* argument, but the [`Graph.transitive_subjects`][rdflib.graph.Graph.transitive_subjects]
    method has the start node as the *second* argument.

## User-defined transitive closures

The method [`Graph.transitiveClosure`][rdflib.graph.Graph.transitiveClosure] returns
transtive closures of user-defined functions.
"""

if __name__ == "__main__":
    from rdflib import ConjunctiveGraph, URIRef

    person = URIRef("ex:person")
    dad = URIRef("ex:d")
    mom = URIRef("ex:m")
    momOfDad = URIRef("ex:gm0")  # noqa: N816
    momOfMom = URIRef("ex:gm1")  # noqa: N816
    dadOfDad = URIRef("ex:gf0")  # noqa: N816
    dadOfMom = URIRef("ex:gf1")  # noqa: N816

    parent = URIRef("ex:parent")

    g = ConjunctiveGraph()
    g.add((person, parent, dad))
    g.add((person, parent, mom))
    g.add((dad, parent, momOfDad))
    g.add((dad, parent, dadOfDad))
    g.add((mom, parent, momOfMom))
    g.add((mom, parent, dadOfMom))

    print("Parents, forward from `ex:person`:")
    for i in g.transitive_objects(person, parent):
        print(i)

    print("Parents, *backward* from `ex:gm1`:")
    for i in g.transitive_subjects(parent, momOfMom):
        print(i)
