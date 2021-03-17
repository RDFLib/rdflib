.. _intro_to_parsing:

======================
Loading and saving RDF
======================

Reading an n-triples file
--------------------------

RDF data has various syntaxes (``xml``, ``n3``, ``ntriples``,
``trix``, ``JSON-LD``, etc) that you might want to read. The simplest format is
``ntriples``, a line-based format. Create the file :file:`demo.nt` in
the current directory with these two lines:

.. code-block:: Turtle

    <http://bigasterisk.com/foaf.rdf#drewp> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
    <http://bigasterisk.com/foaf.rdf#drewp> <http://example.com/says> "Hello world" .

You need to tell RDFLib what format to parse, use the ``format``
keyword-parameter to :meth:`~rdflib.graph.Graph.parse`, you can pass
either a mime-type or the name (a :doc:`list of available parsers
<plugin_parsers>` is available).  If you are not sure what format your
file will be, you can use :func:`rdflib.util.guess_format` which will
guess based on the file extension.

In an interactive python interpreter, try this:

.. code-block:: python

    from rdflib import Graph

    g = Graph()
    g.parse("demo.nt", format="nt")

    print(len(g)) # prints 2

    import pprint
    for stmt in g:
        pprint.pprint(stmt)

    # prints :
    (rdflib.term.URIRef('http://bigasterisk.com/foaf.rdf#drewp'),
     rdflib.term.URIRef('http://example.com/says'),
     rdflib.term.Literal('Hello world'))
    (rdflib.term.URIRef('http://bigasterisk.com/foaf.rdf#drewp'),
     rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
     rdflib.term.URIRef('http://xmlns.com/foaf/0.1/Person'))

The final lines show how RDFLib represents the two statements in the
file. The statements themselves are just length-3 tuples; and the
subjects, predicates, and objects are all rdflib types.

Reading remote graphs
---------------------

Reading graphs from the net is just as easy:

.. code-block:: python

    g.parse("http://bigasterisk.com/foaf.rdf")
    print(len(g))
    # prints 42

The format defaults to ``xml``, which is the common format for .rdf
files you'll find on the net.

RDFLib will also happily read RDF from any file-like object,
i.e. anything with a ``.read()`` method.


Saving RDF
----------

To store a graph in a file use the :func:`rdflib.Graph.serialize` function:

.. code-block:: python

    g.parse("http://bigasterisk.com/foaf.rdf")
    with open("foaf.n3", "wb") as f:
        g.serialize(f, format="n3")