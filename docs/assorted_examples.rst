.. _assorted_examples:

=================
Assorted examples
=================

Foaf Smushing  
=============

Filter a graph by normalizing all foaf:Persons into URIs based on their ``mbox_sha1sum``.

Suppose I got two FOAF documents each talking about the same person (according to ``mbox_sha1sum``) but they each used a :class:`rdflib.term.BNode` for the subject. For this demo I've combined those two documents into one file:

demo.n3
-------

.. code-block:: n3

    @prefix foaf: <http://xmlns.com/foaf/0.1/> .

    ## from one document
    :p0 a foaf:Person;
      foaf:mbox_sha1sum "65b983bb397fb71849da910996741752ace8369b";
      foaf:nick "mortenf";
      foaf:weblog <http://www.wasab.dk/morten/blog/archives/author/mortenf/> .

    ## from another document
    :p1 a foaf:Person;
        foaf:mbox_sha1sum "65b983bb397fb71849da910996741752ace8369b";
        foaf:nick "mortenf";
        foaf:homepage <http://www.wasab.dk/morten/>;
        foaf:interest <http://en.wikipedia.org/wiki/Atom_(standard)> .

Now I'll use rdflib to transform all the incoming FOAF data to new data that lies about the subjects. It might be easier to do some queries on this resulting graph, although you wouldn't want to actually publish the result anywhere since it loses some information about FOAF people who really had a meaningful URI.

fold_sha1.py
------------

.. code-block:: python

    """filter a graph by changing every subject with a foaf:mbox_sha1sum
    into a new subject whose URI is based on the sha1sum. This new graph
    might be easier to do some operations on.
    """

    from rdflib.graph import Graph
    from rdflib import Namespace

    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    STABLE = Namespace("http://example.com/person/mbox_sha1sum/")

    g = Graph()
    g.parse("demo.n3", format="n3")

    newURI = {} # old subject : stable uri
    for s,p,o in g.triples((None, FOAF['mbox_sha1sum'], None)):
        newURI[s] = STABLE[o]


    out = Graph()
    out.bind('foaf', FOAF)

    for s,p,o in g:
        s = newURI.get(s, s)
        o = newURI.get(o, o) # might be linked to another person
        out.add((s,p,o))

    print out.serialize(format="n3")

Output 
------
note how all of the data has come together under one subject:

.. code-block:: n3

    @prefix _5: <http://example.com/person/mbox_sha1sum/65>.
    @prefix foaf: <http://xmlns.com/foaf/0.1/>.
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.

     _5:b983bb397fb71849da910996741752ace8369b a foaf:Person;
         foaf:homepage <http://www.wasab.dk/morten/>;
         foaf:interest <http://en.wikipedia.org/wiki/Atom_(standard)>;
         foaf:mbox_sha1sum "65b983bb397fb71849da910996741752ace8369b";
         foaf:nick "mortenf";
         foaf:weblog <http://www.wasab.dk/morten/blog/archives/author/mortenf/>. 

An advantage of this approach over other methods for collapsing BNodes is that I can incrementally process new FOAF documents as they come in without having to access my ever-growing archive. Even if another "65b983bb397fb71849da910996741752ace8369b" document comes in next year, I would still give it the same stable subject URI that merges with my existing data.

