.. _rdflib_howto: rdflib HOW-TO

=============
rdflib HOW-TO
=============

Merging graphs
--------------

    A merge of a set of RDF graphs is defined as follows. If the graphs in the set have no blank nodes in common, then the union of the graphs is a merge; if they do share blank nodes, then it is the union of a set of graphs that is obtained by replacing the graphs in the set by equivalent graphs that share no blank nodes. This is often described by saying that the blank nodes have been 'standardized apart'. It is easy to see that any two merges are equivalent, so we will refer to the merge, following the convention on equivalent graphs. Using the convention on equivalent graphs and identity, any graph in the original set is considered to be a subgraph of the merge.

    One does not, in general, obtain the merge of a set of graphs by concatenating their corresponding N-Triples documents and constructing the graph described by the merged document. If some of the documents use the same node identifiers, the merged document will describe a graph in which some of the blank nodes have been 'accidentally' identified. To merge N-Triples documents it is necessary to check if the same nodeID is used in two or more documents, and to replace it with a distinct nodeID in each of them, before merging the documents. Similar cautions apply to merging graphs described by RDF/XML documents which contain nodeIDs

*(copied directly from http://www.w3.org/TR/rdf-mt/#graphdefs)*

.. code-block:: pycon

    """
    Tutorial 9 - demonstrate graph operations

    (not really quite graph operations since rdflib cannot merge models like 
    Jena, but this examples shows you can load two different RDF files and 
    rdflib will merge the two together into one model)

    Copyright (C) 2005 Sylvia Wong <sylvia at whileloop dot org>

    This program is free software; you can redistribute it and/or modify it 
    under the terms of the GNU General Public License as published by the 
    Free Software Foundation; either version 2 of the License, or (at your 
    option) any later version.

    This program is distributed in the hope that it will be useful, but 
    WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
    General Public License for more details.

    You should have received a copy of the GNU General Public License along 
    with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
    """

    >>> data1 = """\
    ... @prefix vCard: <http://www.w3.org/2001/vcard-rdf/3.0#> .
    ... 
    ... <http://somewhere/JohnSmith/> vCard:FN "John Smith";
    ...     vCard:N [ vCard:Family "Smith";
    ...             vCard:Given "John" ] .
    ... """
    >>> data2 = """\
    ... @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    ... @prefix vCard: <http://www.w3.org/2001/vcard-rdf/3.0#> .
    ... 
    ... <http://somewhere/JohnSmith/> vCard:EMAIL [ a vCard:internet;
    ...             rdf:value "John@somewhere.com" ];
    ...     vCard:FN "John Smith" .
    ... """
    >>> from rdflib import Graph
    >>> store = Graph()
    >>> store.parse(data=data1, format="n3") #doctest :ellipsis
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> store.parse(data=data2, format="n3") #doctest :ellipsis
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> print(store.serialize(format="n3"))
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix vCard: <http://www.w3.org/2001/vcard-rdf/3.0#> .

    <http://somewhere/JohnSmith/> vCard:EMAIL [ a vCard:internet;
                rdf:value "John@somewhere.com" ];
        vCard:FN "John Smith";
        vCard:N [ vCard:Family "Smith";
                vCard:Given "John" ] .

(edited for inclusion in rdflib documentation)

How to use transitive traversal methods
----------------------------------------

How to use the `transitive_objects` and `transitive_subjects` graph methods

.. automethod:: rdflib.graph.Graph.transitive_subjects
    :noindex:
.. automethod:: rdflib.graph.Graph.transitive_objects
    :noindex:

Formal definition
^^^^^^^^^^^^^^^^^^

The :meth:`~rdflib.graph.Graph.transitive_objects` method finds all nodes such that there is a path from subject to one of those nodes using only the predicate property in the triples. The :meth:`~rdflib.graph.Graph.transitive_subjects` method is similar; it finds all nodes such that there is a path from the node to the object using only the predicate property.

Informal description, with an example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In brief, :meth:`~rdflib.graph.Graph.transitive_objects` walks forward in a graph using a particular property, and :meth:`~rdflib.graph.Graph.transitive_subjects` walks backward. A good example uses a property ``ex:parent``, the semantics of which are biological parentage. The :meth:`~rdflib.graph.Graph.transitive_objects` method would get all the ancestors of a particular person (all nodes such that there is a parent path between the person and the object). The :meth:`~rdflib.graph.Graph.transitive_subjects` method would get all the descendants of a particular person (all nodes such that there is a parent path between the node and the person). So, say that your URI is ``ex:person``. 

The following code would get all of your (known) ancestors, and then get all the (known) descendants of your maternal grandmother:

.. code-block:: python

    from rdflib import ConjunctiveGraph, URIRef
 
    person = URIRef('ex:person')
    dad = URIRef('ex:d')
    mom = URIRef('ex:m')
    momOfDad = URIRef('ex:gm0')
    momOfMom = URIRef('ex:gm1')
    dadOfDad = URIRef('ex:gf0')
    dadOfMom = URIRef('ex:gf1')
 
    parent = URIRef('ex:parent')
 
    g = ConjunctiveGraph()
    g.add((person, parent, dad))
    g.add((person, parent, mom))
    g.add((dad, parent, momOfDad))
    g.add((dad, parent, dadOfDad))
    g.add((mom, parent, momOfMom))
    g.add((mom, parent, dadOfMom))
 
    print "Parents, forward from `ex:person`:"
    for i in g.transitive_objects(person, parent):
        print i
 
    print "Parents, *backward* from `ex:gm1`:"
    for i in g.transitive_subjects(parent, momOfMom):
        print i
      
.. warning:: The :meth:`transitive_objects` method has the start node as the *first* argument, but the :meth:`transitive_subjects` method has the start node as the *second* argument.

User-defined transitive closures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: rdflib.graph.Graph.transitiveClosure
    :noindex:

