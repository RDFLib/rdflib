.. _gettingstarted:

===========================
Getting started with rdflib
===========================

Introduction to parsing RDF into rdflib graphs
----------------------------------------------

Reading an NT file
^^^^^^^^^^^^^^^^^^

RDF data has various syntaxes (``xml``, ``n3``, ``ntriples``, ``trix``, etc) that you might want to read. The simplest format is ``ntriples``. Create the file :file:`demo.nt` in the current directory with these two lines:

.. code-block:: text

    <http://bigasterisk.com/foaf.rdf#drewp> \
    <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> \
    <http://xmlns.com/foaf/0.1/Person> .
    <http://bigasterisk.com/foaf.rdf#drewp> \
    <http://example.com/says> \
    "Hello world" .

In an interactive python interpreter, try this:

.. code-block:: pycon

    >>> from rdflib.graph import Graph
    >>> g = Graph()
    >>> g.parse("demo.nt", format="nt")
    <Graph identifier=HCbubHJy0 (<class 'rdflib.graph.Graph'>)>
    >>> len(g)
    2
    >>> import pprint
    >>> for stmt in g:
    ...     pprint.pprint(stmt)
    ... 
    (rdflib.term.URIRef('http://bigasterisk.com/foaf.rdf#drewp'),
     rdflib.term.URIRef('http://example.com/says'),
     rdflib.term.Literal(u'Hello world'))
    (rdflib.term.URIRef('http://bigasterisk.com/foaf.rdf#drewp'),
     rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
     rdflib.term.URIRef('http://xmlns.com/foaf/0.1/Person'))

The final lines show how ``rdflib`` represents the two statements in the file. The statements themselves are just length-3 tuples; and the subjects, predicates, and objects are all rdflib types.

Reading remote graphs
^^^^^^^^^^^^^^^^^^^^^

Reading graphs from the net is just as easy:

.. code-block:: pycon

    >>> g.parse("http://bigasterisk.com/foaf.rdf")
    >>> len(g)
    42

The format defaults to ``xml``, which is the common format for .rdf files you'll find on the net.

See also

.. module rdflib.graph
.. automethod:: rdflib.graph.Graph.parse
    :noindex:

Plugin parsers for rdflib
-------------------------

.. autoclass::  rdflib.plugins.parsers.rdfxml.RDFXMLParser

.. module:: rdflib.plugins.parsers.rdfa
.. autoclass::  rdflib.plugins.parsers.rdfa.RDFaParser

.. module:: rdflib.plugins.parsers.rdfxml
.. autoclass::  rdflib.plugins.parsers.rdfxml.RDFXMLParser

.. module:: rdflib.plugins.parsers.notation3
.. autoclass::  rdflib.plugins.parsers.notation3.N3Parser

.. module:: rdflib.plugins.parsers.nt
.. autoclass::  rdflib.plugins.parsers.nt.NTParser

.. module:: rdflib.plugins.parsers.trix
.. autoclass::  rdflib.plugins.parsers.trix.TriXParser

Introduction to using SPARQL to query an rdflib graph
-----------------------------------------------------

Create an Rdflib Graph
^^^^^^^^^^^^^^^^^^^^^^

You might parse some files into a new graph (_`Introduction to parsing RDF into rdflib graphs`) or open an on-disk rdflib store.

.. code-block:: python

    from rdflib.graph import Graph
    g = Graph()
    g.parse("http://bigasterisk.com/foaf.rdf")
    g.parse("http://www.w3.org/People/Berners-Lee/card.rdf")

LiveJournal produces FOAF data for their users, but they seem to use ``foaf:member_name`` for a person's full name. For this demo, I made ``foaf:name`` act as a synonym for ``foaf:member_name`` (a poor man's one-way ``owl:equivalentProperty``):

.. code-block:: python

    from rdflib.namespace import Namespace
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    g.parse("http://danbri.livejournal.com/data/foaf") 
    [g.add((s, FOAF['name'], n)) for s,_,n in g.triples((None, FOAF['member_name'], None))]

Run a Query
^^^^^^^^^^^

The ``rdflib`` package concentrates on providing the core RDF types and interfaces for working with RDF. As indicated in the introduction, the package defines a plugin interface (for parsers, stores, and serializers) that other packages can use to implement parsers, stores, and serializers that will plug into the ``rdflib`` package.

In order to perform SPARQL queries, you need to install the companion ``rdfextras`` package which includes a SPARQL plugin implementation:

.. code-block:: bash
    
    $ easy_install rdfextras

In order to use the SPARQL plugin in your code, the plugin must first be registered. This binds the the imported SPARQL query processor implementation to the :meth:`rdflib.graph.Graph.query` method, which can then be passed a SPARQL query (a string). When called, the :meth:`~rdflib.graph.Graph.query` method returns a SPARQLQuery object whose ``result`` attribute is a list of results.

Continuing the example...

.. code-block:: python

    import rdflib
    from rdflib import plugin

    plugin.register(
        'sparql', rdflib.query.Processor,
        'rdfextras.sparql.processor', 'Processor')
    plugin.register(
        'sparql', rdflib.query.Result,
        'rdfextras.sparql.query', 'SPARQLQueryResult')

    qres = g.query(
        """SELECT DISTINCT ?aname ?bname
           WHERE {
              ?a foaf:knows ?b .
              ?a foaf:name ?aname .
              ?b foaf:name ?bname .
           }""",
        initNs=dict(
            foaf=Namespace("http://xmlns.com/foaf/0.1/")))
    
    for row in qres.result:
        print "%s knows %s" % row

The results are tuples of values in the same order as your SELECT arguments.

.. code-block:: text

    Timothy Berners-Lee knows Edd Dumbill
    Timothy Berners-Lee knows Jennifer Golbeck
    Timothy Berners-Lee knows Nicholas Gibbins
    Timothy Berners-Lee knows Nigel Shadbolt
    Dan Brickley knows binzac
    Timothy Berners-Lee knows Eric Miller
    Drew Perttula knows David McClosky
    Timothy Berners-Lee knows Dan Connolly
    ...

Namespaces
^^^^^^^^^^
The :meth:`~rdflib.graph.Graph.parse` :keyword:`initNs` argument is a dictionary of namespaces to be expanded in the query string. In a large program, it is common to use the same ``dict`` for every single query. You might even hack your graph instance so that the ``initNs`` arg is already filled in.


In order to use an empty prefix (e.g. ``?a :knows ?b``), use a ``BASE`` directive in the SPARQL query to set a default namespace:

.. code-block:: text

    BASE <http://xmlns.com/foaf/0.1/>

Bindings
^^^^^^^^

As with SQL queries, it is common to run the same SPARQL query many times with only a few terms changing each time. rdflib calls this ``initBindings``:

.. code-block:: python

    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    ns = dict(foaf=FOAF)
    drew = URIRef('http://bigasterisk.com/foaf.rdf#drewp')
    for row in g.query("""SELECT ?name 
                          WHERE { ?p foaf:name ?name }""", 
                       initNs=ns, initBindings={'p' : drew}):
        print row

Output:

.. code-block:: python

    (rdflib.Literal('Drew Perttula', language=None, datatype=None),)


Store operations
----------------

Example code to create a Sleepycat (``bsddb`` or ``bsddb3``) triple store, add some triples, and serialize the resulting graph. Finally, close the graph and
remove the database files that were created.

.. code-block:: python

    import rdflib
    from rdflib.graph import ConjunctiveGraph as Graph
    from rdflib import plugin
    from rdflib.store import Store, NO_STORE, VALID_STORE
    from rdflib.namespace import Namespace
    from rdflib.term import Literal
    from rdflib.term import URIRef
    from tempfile import mkdtemp

    default_graph_uri = "http://rdflib.net/rdfstore"
    configString = "/var/tmp/rdfstore"

    # Get the Sleepycat plugin. 
    store = plugin.get('Sleepycat', Store)('rdfstore')
    
    # Open previously created store, or create it if it doesn't exist yet
    graph = Graph(store="Sleepycat", 
                  identifier = URIRef(default_graph_uri))
    path = mkdtemp()
    rt = graph.open(path, create=False)
    if rt == NO_STORE:
        # There is no underlying Sleepycat infrastructure, create it
        graph.open(path, create=True)
    else:
        assert rt == VALID_STORE, "The underlying store is corrupt"

    print "Triples in graph before add: ", len(graph)

    # Now we'll add some triples to the graph & commit the changes
    rdflib = Namespace('http://rdflib.net/test/')
    graph.bind("test", "http://rdflib.net/test/")
    
    graph.add((rdflib['pic:1'], rdflib['name'], Literal('Jane & Bob')))
    graph.add((rdflib['pic:2'], rdflib['name'], Literal('Squirrel in Tree')))
    graph.commit()

    print "Triples in graph after add: ", len(graph)

    # display the graph in RDF/XML
    print graph.serialize()
    
    graph.close()
    
    # Clean up the mkdtemp spoor to remove the Sleepycat database files...
    import os
    for f in os.listdir(path): 
        os.unlink(path+'/'+f)
    os.rmdir(path)

The output will appear as follows:

.. code-block:: text

    Triples in graph before add:  0
    Triples in graph after add:  2
    <?xml version="1.0" encoding="UTF-8"?>
    <rdf:RDF
       xmlns="http://rdflib.net/test/"
       xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    >
      <rdf:Description rdf:about="http://rdflib.net/test/pic:1">
        <name>Jane &amp; Bob</name>
      </rdf:Description>
      <rdf:Description rdf:about="http://rdflib.net/test/pic:2">
        <name>Squirrel in Tree</name>
      </rdf:Description>
    </rdf:RDF>
