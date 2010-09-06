.. _univrdfstore:

===============================
A Universal RDF Store Interface
===============================

This document attempts to summarize some fundamental components of an RDF store. The motivation is to outline a standard set of interfaces for providing the support needed to persist an `RDF Graph`_ in a way that is universal and not tied to any specific implementation.

For the most part, the interface adheres to the core RDF model and uses terminology that is consistent with the RDF Model specifications. However, this suggested interface also extends an RDF store with additional requirements necessary to facilitate those aspects of `Notation 3`_ that go beyond the RDF model to provide a framework for `First Order Predicate Logic`_ processing and persistence.

..  _RDF Graph: http://www.w3.org/TR/rdf-concepts/#dfn-rdf-graph
..  _Notation 3: http://www.w3.org/2000/10/swap/Primer
..  _First Order Predicate Logic: http://en.wikipedia.org/wiki/First-order_predicate_logic

Terminology
===========

.. topic:: **Context**

    A named, unordered set of statements (that could also be called a sub-graph). The ``named graph`` `literature`__ and `ontology`__ are relevant to this concept. The term ``context`` could be thought of as either the sub-graph itself or the relationship between an RDF triple and a sub-graph in which it is found (this latter is how the term context is used in the `Notation 3 Design Issues page`_).

    It is worth noting that the concept of logically grouping `triples`__ within an addressable 'set' or 'subgraph' is just barely beyond the scope of the RDF model. The RDF model defines a graph to be an arbitrary collection of triples and the semantics of these triples --- but doesn't give guidance on how to address such arbitrary collections in a consistent manner. Although a collection of triples can be thought of as a resource itself, the association between a triple and the collection (of which it is a part) is not covered. `Public RDF`_ is an example of an attempt to formally model this relationship - and includes one other unrelated extension: Articulated Text

..  __: http://www.w3.org/2004/03/trix/
..  __: http://metacognition.info/Triclops/?xslt=Triclops.xslt&query=type(list(rdfs:Class,owl:Class,rdf:Property))&queryType=Graph&remoteGraph=http://www.w3.org/2004/03/trix/rdfg-1/
.. __: http://www.w3.org/TR/rdf-concepts/#section-triples
..  _Notation 3 Design Issues page: http://www.w3.org/DesignIssues/Notation3.html
..  _Public RDF: http://laurentszyster.be/blog/public-rdf/

.. topic:: **Conjunctive Graph**

    This refers to the 'top-level' Graph. It is the aggregation of all the contexts within it and is also the appropriate, absolute boundary for `closed world assumptions`__ / models. This distinction is the low-hanging fruit of RDF along the path to the semantic web and most of its value is in (corporate/enterprise) real-world problems:

    .. pull-quote::
    
        There are at least two situations where the closed world assumption is used. The first is where it is assumed that a knowledge base contains all relevant facts. This is common in corporate databases. That is, the information it contains is assumed to be complete 
    
    From a store perspective, closed world assumptions also provide the benefit of better query response times, due to the explicit closed world boundaries. Closed world boundaries can be made transparent by federated queries that assume each :class:`ConjunctiveGraph` is a section of a larger, unbounded universe. So a closed world assumption does not preclude you from an open world assumption.

    For the sake of persistence, Conjunctive Graphs must be distinguished by identifiers (which may not necessarily be RDF `identifiers`__ or may be an RDF identifier normalized - SHA1/MD5 perhaps - for database naming purposes) that could be referenced to indicate conjunctive queries (queries made across the entire conjunctive graph) or appear as nodes in asserted statements. In this latter case, such statements could be interpreted as being made about the entire 'known' universe. For example:

    .. code-block:: xml

        <urn:uuid:conjunctive-graph-foo> rdf:type :ConjunctiveGraph
        <urn:uuid:conjunctive-graph-foo> rdf:type log:Truth
        <urn:uuid:conjunctive-graph-foo> :persistedBy :MySQL

..  __: http://cs.wwc.edu/~aabyan/Logic/CWA.html
..  __: http://www.w3.org/2002/07/rdf-identifer-terminology/

.. topic:: **Quoted Statement**

    A statement that isn't asserted but is referred to in some manner. Most often, this happens when we want to make a statement about another statement (or set of statements) without necessarily saying these quoted statements (are true). For example:

    .. code-block:: text

        Chimezie said "higher-order statements are complicated"

    Which can be written (in N3) as:

    .. code-block:: text

        :chimezie :said {:higherOrderStatements rdf:type :complicated}

.. topic:: **Formula**

    A context whose statements are quoted or hypothetical.

    Context quoting can be thought of as very similar to `reification`__. The main difference is that quoted statements are not asserted or considered as statements of truth about the universe and can be referenced as a group: a hypothetical RDF Graph

..  __: http://www.w3.org/TR/rdf-mt/#Reif

.. topic:: **Universal Quantifiers / Variables**

    (relevant references):

        * OWL `Definition`__ of `SWRL`__.
        * SWRL/RuleML `Variable`__

..  __: http://www.w3.org/Submission/SWRL/swrl.owl
..  __: http://www.w3.org/Submission/SWRL/
..  __: http://www.w3.org/Submission/SWRL/#owls_Variable

.. topic:: **Terms**

    Terms are the kinds of objects that can appear in a quoted/asserted triple. 
    
    This includes those that are core to RDF:

        * Blank Nodes
        * URI References
        * Literals (which consist of a literal value, datatype and language tag)

    Those that extend the RDF model into N3:

        * Formulae
        * Universal Quantifications (Variables)

    And those that are primarily for matching against 'Nodes' in the underlying Graph:

        * REGEX Expressions
        * Date Ranges
        * Numerical Ranges

.. topic:: **Nodes**

    Nodes are a subset of the Terms that the underlying store actually persists. The set of such Terms depends on whether or not the store is formula-aware. Stores that aren't formula-aware would only persist those terms core to the RDF Model, and those that are formula-aware would be able to persist the N3 extensions as well. However, utility terms that only serve the purpose for matching nodes by term-patterns probably will only be terms and not nodes.

    The set of nodes of an RDF graph is the set of subjects and objects of triples in the graph.

.. topic:: **Context-aware**

    An RDF store capable of storing statements within contexts is considered context-aware. Essentially, such a store is able to partition the RDF model it represents into individual, named, and addressable sub-graphs.

.. topic:: **Formula-aware**

    An RDF store capable of distinguishing between statements that are asserted and statements that are quoted is considered formula-aware.

    Such a store is responsible for maintaining this separation and ensuring that queries against the entire model (the aggregation of all the contexts - specified by not limiting a 'query' to a specifically name context) do not include quoted statements. Also, it is responsible for distinguishing universal quantifiers (variables).

    .. note:: These 2 additional concepts (formulae and variables) must be thought of as core extensions and distinguishable from the other terms of a triple (for the sake of the persistence round trip - at the very least). It's worth noting that the 'scope' of universal quantifiers (variables) and existential quantifiers (BNodes) is the formula (or context - to be specific) in which their statements reside. Beyond this, a Formula-aware store behaves the same as a Context-aware store.

.. topic:: **Conjunctive Query**

    Any query that doesn't limit the store to search within a named context only. Such a query expects a context-aware store to search the entire asserted universe (the conjunctive graph). A formula-aware store is expected not to include quoted statements when matching such a query.

.. topic:: **N3 Round Trip**

    This refers to the requirements on a formula-aware RDF store's persistence mechanism necessary for it to be properly populated by a N3 parser and rendered as syntax by a N3 serializer.

.. topic:: **Transactional Store**

    An RDF store capable of providing transactional integrity to the RDF operations performed on it.

Interpreting Syntax
===================

The following `Notation 3 document`__:

.. code-block:: text

    { ?x a :N3Programmer } => { ?x :has [a :Migraine] }

Could cause the following statements to be asserted in the store:

.. code-block:: text

    _:a log:implies _:b

This statement would be asserted in the partition associated with quoted statements (in a formula named ``_:a``)

.. code-block:: text

    ?x rdf:type :N3Programmer

Finally, these statements would be asserted in the same partition (in a formula named ``_:b``)

.. code-block:: text

    ?x :has _:c

    _:c rdf:type :Migraine

..  __: http://metacognition.info/Triclops/?xslt=Triclops.xslt&query=log:N3Document&queryType=Triple&remoteGraph=http://www.w3.org/2000/10/swap/log#

Formulae and Variables as Terms
===============================
Formulae and variables are distinguishable from URI references, Literals, and BNodes by the following syntax:

.. code-block:: text

    { .. } - Formula ?x - Variable

They must also be distinguishable in persistence to ensure they can be round-tripped. 

.. note:: There are a number of other issues regarding the `persisting of N3 terms <persisting_n3_terms.html>`_.

Database Management
===================

An RDF store should provide standard interfaces for the management of database connections. Such interfaces are standard to most database management systems (Oracle, MySQL, Berkeley DB, Postgres, etc..)

The following methods are defined to provide this capability (see below for description of the *configuration* string):

.. automethod:: rdflib.store.Store.open
                :noindex:

.. automethod:: rdflib.store.Store.close
                :noindex:

.. automethod:: rdflib.store.Store.destroy
                :noindex:

The *configuration* string is understood by the store implementation and represents all the parameters needed to locate an individual instance of a store. This could be similar to an ODBC string or in fact be an ODBC string, if the connection protocol to the underlying database is ODBC.

The :meth:`~rdflib.graph.Graph.open` function needs to fail intelligently in order to clearly express that a store (identified by the given configuration string) already exists or that there is no store (at the location specified by the configuration string) depending on the value of :keyword:`create`.

Triple Interfaces
=================
An RDF store could provide a standard set of interfaces for the manipulation, management, and/or retrieval of its contained triples (asserted or quoted):

.. module:: rdflib.store

.. automethod:: rdflib.store.Store.add
    :noindex:

.. automethod:: rdflib.store.Store.remove
    :noindex:

.. automethod:: rdflib.store.Store.triples 
    :noindex:

    .. note:: The :meth:`~rdflib.store.Store.triples` method can be thought of as the primary mechanism for producing triples with nodes that match the corresponding terms in the ``(s, p, o)`` term pattern provided. The term pattern ``(None, None, None)`` matches *all* nodes.

.. automethod:: rdflib.store.Store.__len__
                :noindex:

Formula / Context Interfaces
============================

These interfaces work on contexts and formulae (for stores that are formula-aware) interchangeably.

.. automethod:: rdflib.graph.ConjunctiveGraph.contexts
                :noindex:

.. automethod:: rdflib.graph.ConjunctiveGraph.remove_context
                :noindex:

Interface Test Cases
====================

Basic 
-------------------------

Tests parsing, triple patterns, triple pattern removes, size, contextual removes

Source Graph
^^^^^^^^^^^^^

.. code-block:: text

    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> . 
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> . 
    @prefix : <http://test/> . 
    {:a :b :c; a :foo} => {:a :d :c} . 
    _:foo a rdfs:Class . 
    :a :d :c .

Test code
^^^^^^^^^

.. code-block:: python

    implies = URIRef("http://www.w3.org/2000/10/swap/log#implies") 
    a = URIRef('http://test/a') 
    b = URIRef('http://test/b')  
    c = URIRef('http://test/c') 
    d = URIRef('http://test/d') 
    for s,p,o in g.triples((None,implies,None)): 
        formulaA = s 
        formulaB = o 

        #contexts test 
        assert len(list(g.contexts()))==3 

        #contexts (with triple) test 
        assert len(list(g.contexts((a,d,c))))==2 

        #triples test cases 
        assert type(list(g.triples((None,RDF.type,RDFS.Class)))[0][0]) == BNode 
        assert len(list(g.triples((None,implies,None))))==1 
        assert len(list(g.triples((None,RDF.type,None))))==3 
        assert len(list(g.triples((None,RDF.type,None),formulaA)))==1 
        assert len(list(g.triples((None,None,None),formulaA)))==2  
        assert len(list(g.triples((None,None,None),formulaB)))==1 
        assert len(list(g.triples((None,None,None))))==5 
        assert len(list(g.triples((None,URIRef('http://test/d'),None),formulaB)))==1 
        assert len(list(g.triples((None,URIRef('http://test/d'),None))))==1 

        #Remove test cases 
        g.remove((None,implies,None)) 
        assert len(list(g.triples((None,implies,None))))==0 
        assert len(list(g.triples((None,None,None),formulaA)))==2 
        assert len(list(g.triples((None,None,None),formulaB)))==1 
        g.remove((None,b,None),formulaA) 
        assert len(list(g.triples((None,None,None),formulaA)))==1 
        g.remove((None,RDF.type,None),formulaA) 
        assert len(list(g.triples((None,None,None),formulaA)))==0 
        g.remove((None,RDF.type,RDFS.Class)) 

        #remove_context tests 
        formulaBContext=Context(g,formulaB) 
        g.remove_context(formulaB) 
        assert len(list(g.triples((None,RDF.type,None))))==2 
        assert len(g)==3 assert len(formulaBContext)==0 
        g.remove((None,None,None)) 
        assert len(g)==0
    

Formula and Variables Test
--------------------------

Source Graph
^^^^^^^^^^^^

.. code-block:: text

    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> . 
    @prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> . 
    @prefix : <http://test/> . 
    {?x a rdfs:Class} => {?x a :Klass} .

Test Code
^^^^^^^^^

.. code-block:: python

    implies = URIRef("http://www.w3.org/2000/10/swap/log#implies") 
    klass = URIRef('http://test/Klass') 
    for s,p,o in g.triples((None,implies,None)): 
        formulaA = s 
        formulaB = o 
        assert type(formulaA) == Formula 
        assert type(formulaB) == Formula 
        for s,p,o in g.triples((None,RDF.type,RDFS.Class)),formulaA): 
            assert type(s) == Variable 
        for s,p,o in g.triples((None,RDF.type,klass)),formulaB): 
            assert type(s) == Variable 

Transactional Tests
-------------------

To be instantiated.

Additional Terms to Model
=========================
These are a list of additional kinds of RDF terms (all of which are special Literals)

    * RegExLiteral - a REGEX string which can be used in any term slot in order to match by applying the Regular Expression to statements in the underlying graph.
    * Date (could provide some utility functions for date manipulation / serialization, etc..)
    * DateRange

Namespace Management Interfaces
===============================

The following namespace management interfaces (defined in Graph) could be implemented in the RDF store. Currently, they exist as stub methods of :class:`~rdflib.store.Store` and are defined in the store subclasses (e.g. :class:`~rdflib.store.IOMemory`):

.. automethod:: rdflib.store.Store.bind
                :noindex:

.. automethod:: rdflib.store.Store.prefix
                :noindex:

.. automethod:: rdflib.store.Store.namespace
                :noindex:

.. automethod:: rdflib.store.Store.namespaces
                :noindex:

Open issues
===========
Does the Store interface need to have an identifier property or can we keep that at the Graph level?

The Store implementation needs a mechanism to distinguish between triples (quoted or asserted) in ConjunctiveGraphs (which are mutually exclusive universes in systems that make closed world assumptions - and queried separately). This is the separation that the store identifier provides. This is different from the name of a context within a ConjunctiveGraph (or the default context of a conjunctive graph). I tried to diagram the logical separation of ConjunctiveGraphs, SubGraphs and QuotedGraphs in this diagram

.. image:: _static/ContextHierarchy.png

An identifier of ``None`` can be used to indicate the store (aka `all contexts`) in methods such as :meth:`~rdflib.store.Store.triples`, :meth:`~rdflib.store.Store.__len__`, etc. This works as long as we're only dealing with one Conjunctive Graph at a time -- which may not always be the case.

Is there any value in persisting terms that lie outside N3 (RegExLiteral, Date, etc..)?

Potentially, not sure yet.

Should a conjunctive query always return quads instead of triples? It would seem so, since knowing the context that produced a triple match is an essential aspect of query construction / optimization. Or if having the triples function yield/produce different length tuples is problematic, could an additional - and slightly redundant - interface be introduced?:

.. automethod:: rdflib.graph.ConjunctiveGraph.quads
                :noindex:

Stores that weren't context-aware could simply return ``None`` as the 4th item in the produced/yielded tuples or simply not support this interface.

