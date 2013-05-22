.. _upgrade3to4: Upgrading from RDFLib version 3.X to 4.X

========================================
Upgrading from RDFLib version 3.X to 4.X
========================================

RDFLib version 4.0 introduced a small number of backwards compatible changes that you should know about when porting code from version 3 or earlier.

SPARQL and SPARQLStore are now included in core
-----------------------------------------------

For version 4.0 we've merged the SPARQL implementation from ``rdflib-sparql``, the SPARQL(Update)Store from ``rdflib-sparqlstore`` and miscellaneous utilities from ``rdfextras``. If you used any of these previously, everything you need should now be included. 


Datatyped literals
------------------

We separate lexical and value space operations for datatyped literals. 

This mainly affects the way datatyped literals are compared. Lexical space comparisons are done by default for ``==`` and ``!=``, meaning the exact lexical representation and the exact data-types have to match for literals to be equal. Value space comparisons are also available through the :meth:`rdflib.term.Identifier.eq` and :meth:`rdflib.term.Identifier.neq` methods, ``< > <= >=`` are also done in value space. 

Most things now work in a fairly sane and sensible way, if you do not have existing stores/intermediate stored sorted lists, or hash-dependent something-or-other, you should be good to go. 

Things to watch out for: 

Literals no longer compare equal across data-types with ```==```
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

i.e.

.. code-block:: python

   >>> Literal(2, datatype=XSD.int) == Literal(2, datatype=XSD.float)
   False


But a new method :meth:`rdflib.term.Identifier.eq` on all Nodes has been introduced, which does semantic equality checking, i.e.:

.. code-block:: python

   >>> Literal(2, datatype=XSD.int).eq(Literal(2, datatype=XSD.float))
   True

The ``eq`` method is still limited to what data-types map to the same *value space*, i.e. all numeric types map to numbers and will compare, ``xsd:string`` and ``plain literals`` both map to strings and compare fine, but: 

.. code-block:: python

   >>> Literal(2, datatype=XSD.int).eq(Literal('2'))
   False



Literals will be normalised according to datatype
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you care about the exact lexical representation of a literal, and not just the value. Either set :data:`rdflib.NORMALIZE_LITERALS` to ``False`` before creating your literal, or pass ``normalize=False`` to the Literal constructor

Ordering of literals and nodes has changed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Comparing literals with ``<, >, <=, >=`` now work same as in SPARQL filter expressions. 

Greater-than/less-than ordering comparisons are also done in value space, when compatible datatypes are used.
Incompatible datatypes are ordered by data-type, or by lang-tag.
For other nodes the ordering is ``None < BNode < URIRef < Literal``

Any comparison with non-rdflib Node are ``NotImplemented``
In PY2.X some stable order will be made up by python.
In PY3 this is an error.

Custom mapping of datatypes to python objects 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can add new mappings of datatype URIs to python objects using the :func:`rdflib.term.bind` method. 
This also allows you to specify a constructor for constructing objects from the lexical string representation, and a serialization method for generating a lexical string representation from an object. 



Minor Changes 
--------------

* :class:`rdflib.namespace.Namespace` is no longer a sub-class of :class:`rdflib.term.URIRef` 
  this was changed as it makes no sense for a namespace to be a node in a graph, and was causing numerous bug. Unless you do something very special, you should not notice this change. 

* The identifiers for Graphs are now converted to URIRefs if they are not a :class:`rdflib.term.Node`, i.e. no more graphs with string identifiers. Again, unless you do something quite unusual, you should not notice. 

* String concatenation with URIRefs now returns URIRefs, not strings:: 

  >>> URIRef("http://example.org/people/") + "Bill"
  rdflib.term.URIRef(u'http://example.org/people/Bill')

  This is be convenient, but may cause trouble if you expected a string.
