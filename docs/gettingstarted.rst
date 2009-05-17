.. _gettingstarted:

===========================
Getting started with rdflib
===========================

Introduction to parsing RDF into rdflib graphs
----------------------------------------------

Reading an NT file
^^^^^^^^^^^^^^^^^^

RDF data has various syntaxes (``xml``, ``n3``, ``ntriples``, ``trix``, etc) that you might want to read. The simplest format is ``ntriples``. Create the file :file:`demo.nt` in the current directory with these two lines:

.. code-block:: n3

    <http://bigasterisk.com/foaf.rdf#drewp> \
    <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> \
    <http://xmlns.com/foaf/0.1/Person> .
    <http://bigasterisk.com/foaf.rdf#drewp> \
    <http://example.com/says> \
    "Hello world" .

In an interactive python interpreter, try this:

.. code-block:: python

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

The final lines show how rdflib represents the two statements in the file. The statements themselves are just length-3 tuples; and the subjects, predicates, and objects are all rdflib types.

Reading remote graphs
^^^^^^^^^^^^^^^^^^^^^

Reading graphs from the net is just as easy:

.. code-block:: pycon

    >>> g.parse("http://bigasterisk.com/foaf.rdf")
    >>> len(g)
    42

The format defaults to ``xml``, which is the common format for .rdf files you'll find on the net.

See also

.. automethod:: rdflib.graph.Graph.parse

Other parsers supported by rdflib
---------------------------------

.. automodule:: rdflib.syntax.parsers

.. automodule:: rdflib.syntax.parsers.n3p

.. automodule:: rdflib.syntax.parsers.N3Parser

.. autoclass:: rdflib.syntax.parsers.N3Parser.N3Parser
    :members:

.. automodule:: rdflib.syntax.parsers.NTParser

.. autoclass:: rdflib.syntax.parsers.NTParser.NTParser
    :members:

.. automodule:: rdflib.syntax.parsers.ntriples

.. autoclass:: rdflib.syntax.parsers.ntriples.NTriplesParser
    :members:

.. automodule:: rdflib.syntax.parsers.RDFXMLParser

.. autoclass:: rdflib.syntax.parsers.RDFXMLParser.RDFXMLParser
    :members:

.. automodule:: rdflib.syntax.parsers.TriXParser

.. autoclass:: rdflib.syntax.parsers.TriXParser.TriXParser
    :members:

.. .. automodule:: rdflib.syntax.parsers.RDFaParser
..     :members:
.. 
.. .. autoclass:: rdflib.syntax.parsers.RDFaParser.RDFaParser
..     :members:
.. 

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

.. code-block:: python

    for row in g.query(
            """SELECT ?aname ?bname 
               WHERE { 
                  ?a foaf:knows ?b . 
                  ?a foaf:name ?aname . 
                  ?b foaf:name ?bname . 
               }""", 
            initNs=dict(foaf=Namespace("http://xmlns.com/foaf/0.1/"))):
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
The :meth:`Graph.parse` :keyword:`initNs` argument is a dictionary of namespaces to be expanded in the query string. In a large program, it's common to use the same dict for every single query. You might even hack your graph instance so that the ``initNs`` arg is already filled in.

If someone knows how to use the empty prefix (e.g. "?a :knows ?b"), please write about it here and in the :meth:`Graph.query` docs.

*ewan klein provides the answer, use BASE to set a default namespace ...*

.. code-block:: sparql

    BASE <http://xmlns.com/foaf/0.1/>

Bindings
^^^^^^^^

Just like with SQL queries, it's common to run the same query many times with only a few terms changing. rdflib calls this ``initBindings``:

.. code-block:: python

    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    ns = dict(foaf=FOAF)
    drew = URIRef('http://bigasterisk.com/foaf.rdf#drewp')
    for row in g.query("""SELECT ?name 
                          WHERE { ?p foaf:name ?name }""", 
                       initNs=ns, initBindings={'?p' : drew}):
        print row

Output:

.. code-block:: python

    (rdflib.Literal('Drew Perttula', language=None, datatype=None),)

.. automethod:: rdflib.graph.Graph.query

Store operations
----------------

Example code to create a MySQL triple store, add some triples, and serialize the resulting graph.

.. code-block:: python

    import rdflib
    from rdflib.graph import ConjunctiveGraph as Graph
    from rdflib import plugin
    from rdflib.store import Store, NO_STORE, VALID_STORE
    from rdflib.namespace import Namespace
    from rdflib.term import Literal
    from rdflib.term import URIRef

    default_graph_uri = "http://rdflib.net/rdfstore"
    configString = "host=localhost,user=username,password=password,db=rdfstore"

    # Get the mysql plugin. You may have to install the python mysql libraries
    store = plugin.get('MySQL', Store)('rdfstore')

    # Open previously created store, or create it if it doesn't exist yet
    rt = store.open(configString,create=False)
    if rt == NO_STORE:
        # There is no underlying MySQL infrastructure, create it
        store.open(configString,create=True)
    else:
        assert rt == VALID_STORE,"There underlying store is corrupted"
    
    # There is a store, use it
    graph = Graph(store, identifier = URIRef(default_graph_uri))

    print "Triples in graph before add: ", len(graph)

    # Now we'll add some triples to the graph & commit the changes
    rdflib = Namespace('http://rdflib.net/test/')
    graph.add((rdflib['pic:1'], rdflib['name'], Literal('Jane & Bob')))
    graph.add((rdflib['pic:2'], rdflib['name'], Literal('Squirrel in Tree')))
    graph.commit()

    print "Triples in graph after add: ", len(graph)

    # display the graph in RDF/XML
    print graph.serialize()
