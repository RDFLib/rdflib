.. _persisting_n3_terms:

===========================
Persisting Notation 3 Terms
===========================

Using N3 Syntax for Persistence
-------------------------------
Blank Nodes, Literals, URI References, and Variables can be distinguished in persistence by relying on Notation 3 syntax convention. 

All URI References can be expanded and persisted as:

.. code-block:: text

    <..URI..>

All Literals can be expanded and persisted as:

.. code-block:: text

    "..value.."@lang or "..value.."^^dtype_uri

.. note:: ``@lang`` is a language tag and ``^^dtype_uri`` is the URI of a data type associated with the Literal

Blank Nodes can be expanded and persisted as:

.. code-block:: text

    _:Id 

.. note:: where Id is an identifier as determined by skolemization. Skolemization is a syntactic transformation routinely used in automatic inference systems in which existential variables are replaced by 'new' functions - function names not used elsewhere - applied to any enclosing universal variables. In RDF, Skolemization amounts to replacing every blank node in a graph by a 'new' name, i.e. a URI reference which is guaranteed to not occur anywhere else. In effect, it gives 'arbitrary' names to the anonymous entities whose existence was asserted by the use of blank nodes: the arbitrariness of the names ensures that nothing can be inferred that would not follow from the bare assertion of existence represented by the blank node. (Using a literal would not do. Literals are never 'new' in the required sense.)

Variables can be persisted as they appear in their serialization ``(?varName)`` - since they only need be unique within their scope (the context of their associated statements)

These syntactic conventions can facilitate term round-tripping.

Variables by Scope
------------------
Would an interface be needed in order to facilitate a quick way to aggregate all the variables in a scope (given by a formula identifier)? An interface such as:

.. code-block:: python

    def variables(formula_identifier)

The Need to Skolemize Formula Identifiers
-----------------------------------------
It would seem reasonable to assume that a formula-aware store would assign Blank Node identifiers as names of formulae that appear in a N3 serialization. So for instance, the following bit of N3:

.. code-block:: text

    {?x a :N3Programmer} => {?x :has :Migrane}

Could be interpreted as the assertion of the following statement:

.. code-block:: text

    _:a log:implies _:b

However, how are ``_:a`` and ``_:b`` distinguished from other Blank Nodes? A formula-aware store would be expected to persist the first set of statements as quoted statements in a formula named ``_:a`` and the second set as quoted statements in a formula named ``_:b``, but it would not be cost-effective for a serializer to have to query the store for all statements in a context named ``_:a`` in order to determine if ``_:a`` was associated with a formula (so that it could be serialized properly).

Relying on ``log:Formula`` Membership
-------------------------------------

The store could rely on explicit ``log:Formula`` membership (via ``rdf:type`` statements) to model the distinction of Blank Nodes associated with formulae. However, would these statements be expected from an N3 parser or known implicitly by the store? i.e., would all such Blank Nodes match the following pattern:

.. code-block:: text

    ?formula rdf:type log:Formula

Relying on an Explicit Interface
--------------------------------
A formula-aware store could also support the persistence of this distinction by implementing a method that returns an iterator over all the formulae in the store:

.. code-block:: python

    def formulae(triple=None)

This function would return all the Blank Node identifiers assigned to formulae or just those that contain statements matching the given triple pattern and would be the way a serializer determines if a term refers to a formula (in order to properly serializer it).

How much would such an interface reduce the need to model formulae terms as first class objects (perhaps to be returned by the :meth:`~rdflib.Graph.triple` function)? Would it be more useful for the :class:`~rdflib.Graph` (or the store itself) to return a Context object in place of a formula term (using the formulae interface to make this determination)?

Conversely, would these interfaces (variables and formulae) be considered optimizations only since you have the distinction by the kinds of terms triples returns (which would be expanded to include variables and formulae)?

Persisting Formula Identifiers
------------------------------
This is the most straight forward way to maintain this distinction - without relying on extra interfaces. Formula identifiers could be persisted distinctly from other terms by using the following notation:

.. code-block:: text

    {_:bnode} or {<.. URI ..>}

This would facilitate their persistence round-trip - same as the other terms that rely on N3 syntax to distinguish between each other.

