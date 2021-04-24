.. _intro_to_parsing:

======================
Loading and saving RDF
======================

Reading RDF files
-----------------

RDF data can be represented using various syntaxes (``turtle``, ``rdf/xml``, ``n3``, ``n-triples``,
``trix``, ``JSON-LD``, etc.). The simplest format is
``ntriples``, which is a triple-per-line format.

Create the file :file:`demo.nt` in the current directory with these two lines in it:

.. code-block:: Turtle

    <http://example.com/drewp> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
    <http://example.com/drewp> <http://example.com/says> "Hello World" .

On line 1 this file says "drewp is a FOAF Person:. On line 2 it says "drep says "Hello World"".

RDFLib can guess what format the file is by the file ending (".nt" is commonly used for n-triples) so you can just use
:meth:`~rdflib.graph.Graph.parse` to read in the file. If the file had a non-standard RDF file ending, you could set the
keyword-parameter ``format`` to specify either an Internet Media Type or the format name (a :doc:`list of available
parsers <plugin_parsers>` is available).

In an interactive python interpreter, try this:

.. code-block:: python

    from rdflib import Graph

    g = Graph()
    g.parse("demo.nt")

    print(len(g))
    # prints: 2

    import pprint
    for stmt in g:
        pprint.pprint(stmt)
    # prints:
    # (rdflib.term.URIRef('http://example.com/drewp'),
    #  rdflib.term.URIRef('http://example.com/says'),
    #  rdflib.term.Literal('Hello World'))
    # (rdflib.term.URIRef('http://example.com/drewp'),
    #  rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
    #  rdflib.term.URIRef('http://xmlns.com/foaf/0.1/Person'))

The final lines show how RDFLib represents the two statements in the
file: the statements themselves are just length-3 tuples ("triples") and the
subjects, predicates, and objects of the triples are all rdflib types.

Reading remote RDF
------------------

Reading graphs from the Internet is easy:

.. code-block:: python

    from rdflib import Graph

    g = Graph()
    g.parse("http://www.w3.org/People/Berners-Lee/card")
    print(len(g))
    # prints: 86

:func:`rdflib.Graph.parse` can process local files, remote data via a URL, as in this example, or RDF data in a string
(using the ``data`` parameter).


Saving RDF
----------

To store a graph in a file, use the :func:`rdflib.Graph.serialize` function:

.. code-block:: python

    from rdflib import Graph

    g = Graph()
    g.parse("http://www.w3.org/People/Berners-Lee/card")
    g.serialize(destination="tbl.ttl")

This parses data from http://www.w3.org/People/Berners-Lee/card and stores it in a file ``tbl.ttl`` in this directory
using the turtle format as a default.

To read the same data and to save it in a varable ``v`` a string in the RDF/XML format, do this:

.. code-block:: python

    from rdflib import Graph

    g = Graph()
    g.parse("http://www.w3.org/People/Berners-Lee/card")
    v = g.serialize(format="xml")


Working with multi-graphs
-------------------------

To read and query multi-graphs, that is RDF data that is context-aware, you need to use rdflib's
:class:`rdflib.ConjunctiveGraph` or :class:`rdflib.Dataset` class. These are extensions to :class:`rdflib.Graph` that
know all about quads (triples + graph IDs).

If you had this multi-graph data file (in the ``trig`` format, using new-style ``PREFIX`` statement (not the older
``@prefix``):

.. code-block:: Turtle

    PREFIX eg: <http://example.com/person/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>

    eg:graph-1 {
        eg:drewp a foaf:Person .
        eg:drewp eg:says "Hello World" .
    }

    eg:graph-2 {
        eg:nick a foaf:Person .
        eg:nick eg:says "Hi World" .
    }

You could parse the file and query it like this:

.. code-block:: python

    from rdflib import Dataset
    from rdflib.namespace import RDF

    g = Dataset()
    g.parse("demo.trig")

    for s, p, o, g in g.quads((None, RDF.type, None, None)):
        print(s, g)

This will print out:

.. code-block::

    http://example.com/person/drewp http://example.com/person/graph-1
    http://example.com/person/nick http://example.com/person/graph-2
