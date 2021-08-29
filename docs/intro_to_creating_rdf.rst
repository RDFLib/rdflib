.. _intro_to_creating_rdf: 

====================
Creating RDF triples
====================

Creating Nodes
--------------

RDF data is a graph where the nodes are URI references, Blank Nodes or Literals. In RDFLib, these node types are
represented by the classes :class:`~rdflib.term.URIRef`, :class:`~rdflib.term.BNode`, and :class:`~rdflib.term.Literal`.
``URIRefs`` and ``BNodes`` can both be thought of as resources, such a person, a company, a website, etc.

* A ``BNode`` is a node where the exact URI is not known - usually a node with identity only in relation to other nodes.
* A ``URIRef`` is a node where the exact URI is known. In addition to representing some subjects and predicates in RDF graphs, ``URIRef``\s are always used to represent properties/predicates
* ``Literals`` represent object values, such as a name, a date, a number, etc. The most common literal values are XML data types, e.g. string, int... but custom types can be declared too

Nodes can be created by the constructors of the node classes:

.. code-block:: python

   from rdflib import URIRef, BNode, Literal

   bob = URIRef("http://example.org/people/Bob")
   linda = BNode()  # a GUID is generated

   name = Literal("Bob")  # passing a string
   age = Literal(24)  # passing a python int
   height = Literal(76.5)  # passing a python float

Literals can be created from Python objects, this creates ``data-typed literals``. For the details on the mapping see
:ref:`rdflibliterals`.

For creating many ``URIRefs`` in the same ``namespace``, i.e. URIs with the same prefix, RDFLib has the
:class:`rdflib.namespace.Namespace` class

::

   from rdflib import Namespace

   n = Namespace("http://example.org/people/")

   n.bob  # == rdflib.term.URIRef("http://example.org/people/bob")
   n.eve  # == rdflib.term.URIRef("http://example.org/people/eve")


This is very useful for schemas where all properties and classes have the same URI prefix. RDFLib defines Namespaces for
some common RDF/OWL schemas, including most W3C ones:

.. code-block:: python

    from rdflib.namespace import CSVW, DC, DCAT, DCTERMS, DOAP, FOAF, ODRL2, ORG, OWL, \
                               PROF, PROV, RDF, RDFS, SDO, SH, SKOS, SOSA, SSN, TIME, \
                               VOID, XMLNS, XSD

    RDF.type
    # == rdflib.term.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")

    FOAF.knows
    # == rdflib.term.URIRef("http://xmlns.com/foaf/0.1/knows")

    PROF.isProfileOf
    # == rdflib.term.URIRef("http://www.w3.org/ns/dx/prof/isProfileOf")

    SOSA.Sensor
    # == rdflib.term.URIRef("http://www.w3.org/ns/sosa/Sensor")


Adding Triples to a graph
-------------------------

We already saw in :doc:`intro_to_parsing`, how triples can be added from files and online locations with with the
:meth:`~rdflib.graph.Graph.parse` function.

Triples can also be added within Python code directly, using the :meth:`~rdflib.graph.Graph.add` function:

.. automethod:: rdflib.graph.Graph.add
    :noindex:

:meth:`~rdflib.graph.Graph.add` takes a 3-tuple (a "triple") of RDFLib nodes. Using the nodes and
namespaces we defined previously:

.. code-block:: python

    from rdflib import Graph, URIRef, Literal, BNode
    from rdflib.namespace import FOAF, RDF

    g = Graph()
    g.bind("foaf", FOAF)

    bob = URIRef("http://example.org/people/Bob")
    linda = BNode()  # a GUID is generated

    name = Literal("Bob")
    age = Literal(24)

    g.add((bob, RDF.type, FOAF.Person))
    g.add((bob, FOAF.name, name))
    g.add((bob, FOAF.age, age))
    g.add((bob, FOAF.knows, linda))
    g.add((linda, RDF.type, FOAF.Person))
    g.add((linda, FOAF.name, Literal("Linda")))

    print(g.serialize())


outputs: 

.. code-block:: Turtle

    @prefix foaf: <http://xmlns.com/foaf/0.1/> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    <http://example.org/people/Bob> a foaf:Person ;
        foaf:age 24 ;
        foaf:knows [ a foaf:Person ;
                foaf:name "Linda" ] ;
        foaf:name "Bob" .

For some properties, only one value per resource makes sense (i.e they are *functional properties*, or have a
max-cardinality of 1). The :meth:`~rdflib.graph.Graph.set` method is useful for this:

.. code-block:: python

    from rdflib import Graph, URIRef, Literal
    from rdflib.namespace import FOAF

    g = Graph()
    bob = URIRef("http://example.org/people/Bob")

    g.add((bob, FOAF.age, Literal(42)))
    print(f"Bob is {g.value(bob, FOAF.age)}")
    # prints: Bob is 42

    g.set((bob, FOAF.age, Literal(43)))  # replaces 42 set above
    print(f"Bob is now {g.value(bob, FOAF.age)}")
    # prints: Bob is now 43


:meth:`rdflib.graph.Graph.value` is the matching query method. It will return a single value for a property, optionally
raising an exception if there are more.

You can also add triples by combining entire graphs, see :ref:`graph-setops`.


Removing Triples
----------------

Similarly, triples can be removed by a call to :meth:`~rdflib.graph.Graph.remove`:

.. automethod:: rdflib.graph.Graph.remove
    :noindex:

When removing, it is possible to leave parts of the triple unspecified (i.e. passing ``None``), this will remove all
matching triples:

.. code-block:: python

    g.remove((bob, None, None))  # remove all triples about bob


An example
----------

LiveJournal produces FOAF data for their users, but they seem to use
``foaf:member_name`` for a person's full name but ``foaf:member_name``
isn't in FOAF's namespace and perhaps they should have used ``foaf:name``

To retrieve some LiveJournal data, add a ``foaf:name`` for every
``foaf:member_name`` and then remove the ``foaf:member_name`` values to
ensure the data actually aligns with other FOAF data, we could do this:

.. code-block:: python

    from rdflib import Graph
    from rdflib.namespace import FOAF

    g = Graph()
    # get the data
    g.parse("http://danbri.livejournal.com/data/foaf")

    # for every foaf:member_name, add foaf:name and remove foaf:member_name
    for s, p, o in g.triples((None, FOAF['member_name'], None)):
        g.add((s, FOAF['name'], o))
        g.remove((s, FOAF['member_name'], o))

.. note:: Since rdflib 5.0.0, using ``foaf:member_name`` is somewhat prevented in RDFlib since FOAF is declared
    as a :meth:`~rdflib.namespace.ClosedNamespace` class instance that has a closed set of members and
    ``foaf:member_name`` isn't one of them! If LiveJournal had used RDFlib 5.0.0, an error would have been raised for
    ``foaf:member_name`` when the triple was created.


Creating Containers & Collections
---------------------------------
There are two convenience classes for RDF Containers & Collections which you can use instead of declaring each
triple of a Containers or a Collections individually:

    * :meth:`~rdflib.container.Container` (also ``Bag``, ``Seq`` & ``Alt``) and
    * :meth:`~rdflib.collection.Collection`

See their documentation for how.
