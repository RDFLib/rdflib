.. _graphs_bnodes:

====================================
Graphs, Named Graphs and Blank Nodes
====================================

Vin's question
==============

Clarifying the query more precisely:

.. code-block:: pycon

    >>> from rdflib.graph import Graph, ConjunctiveGraph
    >>> from rdflib import URIRef

[1]

.. code-block:: pycon

    >>> graph = Graph('MySQL', identifier = URIRef('http://www.example.com'))
    >>> graph.identifier
    rdflib.URIRef('http://www.example.com')

[2]

.. code-block:: pycon

    >>> graph1 = ConjunctiveGraph('MySQL', identifier = URIRef('http://www.example.com'))
    >>> graph1.identifier
    rdflib.BNode('VLjQILCh3')

[3]

.. code-block:: pycon

    >>> graph1 = ConjunctiveGraph('MySQL', identifier = URIRef('http://www.example.com'))
    >>> graph1.identifier
    rdflib.BNode('VLjQILCh4')

In [1] when I mention the Graph identifier, the return is a persistent
URIRef (i.e. it can be used out of the current model as well) which
gives me a unique name for the graph and now I am free to use it in
other model as well - maybe it can be used for merging graphs. 

Whereas in [2] and [3], when I mention Graph identifier the return is a
BNode which changes value every time we invoke it (and hence BNodes
have local scope and are not good for using outside the model). 

My query was simply to know why the Model "identifier" is giving BNode in
[2] comparing to a persistent URI in case [1]?  In ConjunctiveGraph,
identifier is inherited from the Graph class.

The discourse
=============

This sparql-dev discussion airs some of the issues ...

0016: Nuutti Kotivuori
----------------------
http://lists.w3.org/Archives/Public/public-sparql-dev/2006JulSep/0016.html

This isn't exactly a SPARQL question, but it is very closely
related. I will first outline the question context.

Assume an RDF statement store, which has a mechanism for tracking
statement origin (scope, context, graph, source whatever). Many of the
statements have a distinct origin, or source graph, they were imported
from. But there are also those which either seemingly have no origin,
or the origin is not known. The origin of these statements have to be
handled somehow. We'll come to the specific choices later on.

This statement store offers a SPARQL query interface into it. The
facilities for querying named graphs in SPARQL would obviously be used
to query the different origins in the store. But there are two things
to decide. First, how should statements without an origin be accessed
in SPARQL? There are several choices on this, which I will outline
below. And related to the first one, second, what should the default
graph be for the queries if none is given explicitly.

I will list a few possibilities and mention the problems and benefits
that seem to result from them as a basis for discussion.

 1. Unknown origin is a distinct node, but separate from all uris,
    blank nodes or literals. The default graph for the query is the
    graph of the unknown origin nodes.

    - Separation of identifier spaces, no fear of any overlap. The
      graph of statements with unknown origin is separate from any
      named graph.

    - Since there is no way to represent the unknown origin in SPARQL
      syntax, the default graph is the only way to access the nodes in
      that graph.

    - The nodes in the unknown origin graph are not matched by any
      graph query, since the name of the graph could not be returned
      reasonably. That is:

      .. code-block:: sparql
      
          SELECT ?g ?s ?o ?p
          WHERE { GRAPH ?g { ?s ?p ?o } }

      cannot return ?g for the unknown origin graph.

 2. Unknown origin is a distinct node, as above. The default graph is
    the RDF merge of all graphs in the store, including the statements
    with an unknown origin.

    - The problems above.

    - In addition, there is no way to select nodes that explicitly
      have an unknown origin. (Or is there? Could one match all the
      statements for which there is no graph with the same statement? 
      In any case, this would be quite contorted.)

 3. Unknown origin is represented by a distinct blank node; that is,
    every statement has it's own blank node as the graph name, which
    is not shared with any of the other statements. The default graph
    is the RDF merge of all graphs in the store, including the
    statements with an unknown origin.

    - This is probably closest to accurate modelling of the
      situation. We know every statement has an origin, we just don't
      know what it is - a situation commonly modelled with a blank
      node. Also, we don't know which statements might share an
      origin, so until we know better, we make them all distinct.

    - The origin of the statements is nicely queryable with SPARQL
      queries and every statement has an origin, even if unknown.

    - Queries which specify several statements from a single graph
      will not match the statements with unknown origins as it cannot
      be confirmed that they would be from the same graph.

    - There is no way to match the origin of a single statement as
      there is no way to match a certain blank node explicitly. The
      current SPARQL treats it as an open variable(?).

    - There is no way to explicitly match statements that have an
      unknown origin, since the origins are just distinct blank nodes.

    - Possibly hard to implement, because of the number of distinct
      blank nodes.

 4. Unknown origin is represented by a singleton blank node; that is,
    every statement with an unknown origin shares one single blank
    node as the graph name. The default graph is the RDF merge of all
    graphs in the store.

    - Lumps all statements with an unknown origin under a single named
      graph. Queries which match several statements from a single
      graph will match statement sets from unknown origin as well.

    - The origin of the statements is nicely queryable with SPARQL
      queries and every statement has an origin, even if unknown.

    - There is no way to explicitly match statements that have an
      unknown origin, since the origin is a single blank node. If the
      application provided a magic type for this blank node (_:x a
      rdfx:UnknownOrigin), this could be matched with:

      .. code-block:: sparql

          SELECT ?s ?o ?p
          WHERE { ?g a rdfx:UnknownOrigin .
                  GRAPH ?g { ?s ?o ?p } }

      But this again is quite contorted. (The same could be applied to
      the third case as well, but the implementation of that would be
      really tricky to be effecient.)

 5. Unknown origin is represented by a singleton blank node as
    above. The default graph is the singleton blank node of unknown
    origin.

    - Mostly as above, but in the common case, explictly matching
      statements that have an unknown origin would be easy in just
      matching the statements from the default graph.

 6. Unknown origin is represented by a well known URI that is shared
    universally. The default graph is the RDF merge of all graphs in
    the store.

    - Somewhat incorrectly asserts that the statements have a certain
      origin, even though we don't know the origin.

    - The origin of the statements is nicely queryable with SPARQL.

    - Statements with an unknown origin can be easily explicitly
      matched by comparing them against the well known URI.

    - Assigns a special meaning to an URI.

    - Hard to coordinate with a number of people implementing similar
      solutions if not standardized.

Some other variants of the above were omitted, since their problems
and benefits are easily reasoned.

On irc, 'chimenzie' outlined the problem as such:

17:35 chimezie:#swig => Hmm.. well, seems like what is missing is a good 
      definition of a 'name for nodes that don't have an explicit context'
17:36 chimezie:#swig => or rather 'a name for the context of nodes that aren't 
      assigned to a context explicitely'

So, I'm out for some input on what might be the sanest route to
through this.

TIA,
-- Naked

0018: Richard Cyganiak
----------------------

http://lists.w3.org/Archives/Public/public-sparql-dev/2006JulSep/0018.html

Hi Nuutti,

Without having thought through all the consequences ...

Some of your options are not really possible with named graphs  
because graphs need to be *named*, that is, the name *must* be a URI  
and not a blank node. Blank nodes are always scoped to a single  
graph, and using blank nodes as graph labels would make it impossible  
to refer to a named graph from the outside world. This excludes #3  
and #4.

In SPARQL, the default graph is structurally and syntactically  
handled so differently from the other graphs that I wouldn't consider  
using it for the same kind of data. That is, I tend to reserve the  
default graph for metadata or the merge of all named graphs. This  
excludes #1 and #5.

#6 has the problem of re-using a single URI for many different things  
-- the statements of unknown origin in Alice's store, *and* the  
statements of unknown origin in Bob's store. While workable, this is  
not an elegant solution.

I would suggest that Alice and Bob each mint a new URI for the graph  
containing the statements of unknown origin *in their own store*. Or  
mint a new URI to hold each individual statement, or anything in  
between. Since the owner of a URI gets to say what the meaning of the  
URI is, they can declare that this chunk of URI space is reserved for  
this purpose (assuming Alice and Bob each own a chunk of URI space).

I wonder why you discounted this solution?

I also question the existence of "statements without a known origin".  
They surely didn't just pop up magically inside your triple store,  
eh? I guess it's more like "statements whose origin I don't want to  
model".


0020: Chimezie Ogbuji
---------------------

http://lists.w3.org/Archives/Public/public-sparql-dev/2006JulSep/0020.html

On Wed, 13 Sep 2006, Richard Cyganiak wrote:

.. code-block:: text

    > Hi Nuutti,
    >
    > Without having thought through all the consequences ...
    >
    > Some of your options are not really possible with named graphs because graphs 
    > need to be *named*, that is, the name *must* be a URI and not a blank node.

I don't agree.  What's the source of this assertion? I think the core 
issue here is that there is *no* concensus formalism for named graphs WRT RDF, yet SPARQL is dependent 
on an RDF model that supports named graphs.  If there is one, please 
point me to it, because I ran across the same problem when constructing 
programming APIs for named graphs.  The only formalism I know of is Graham Kyle, John McCarthy's work [1].

.. code-block:: text

    > Blank nodes are always scoped to a single graph, and using blank nodes as 
    > graph labels would make it impossible to refer to a named graph from the 
    > outside world. This excludes #3 and #4.

Well, Blank nodes used within a graph can't be referred to 
directly but they can still be matched by SPARQL - doesn't make them any 
less useful.  The problem isn't the use of Blank nodes for graph names but
a the lack of a mechanism [2] to match the graph name(s) associated with a 
node.  Given how closely coupled SPARQL is with (admittedly informal) 
named graph semantics, I would expect to be able to answer questions such as:

"What are the graph names in which all the statements about <someIRI> are 
asserted?"

Assuming I could answer this question, then graph labels that are blank 
nodes become as accessible as blank nodes asserted *within* a graph and it 
becomes a question of what is the appropriate use for a bnode as a graph 
label?

If BNodes are used for existential assertions about nodes, why wouldn't 
they be used as existential assertions about graphs? And if there is 
some semantic consequence, it furthers the argument that the formalisms 
for named graphs should be well articulated before they are tightly integrated into a query language.

.. code-block:: text

    > I would suggest that Alice and Bob each mint a new URI for the graph 
    > containing the statements of unknown origin *in their own store*. Or mint a 
    > new URI to hold each individual statement, or anything in between. Since the 
    > owner of a URI gets to say what the meaning of the URI is, they can declare 
    > that this chunk of URI space is reserved for this purpose (assuming Alice and 
    > Bob each own a chunk of URI space).
    >
    > I wonder why you discounted this solution?

I don't think it's an elegant solution when we already have the means 
(within 'vanilla' RDF Model Theory) to express 
existential assertions - which is exactly the scenario here.

If a graph label is nothing but a name associated with a set of graphs, 
why should it not behave the same as the name associated with a node 
within a graph?

.. code-block:: text

    > I also question the existence of "statements without a known origin". They 
    > surely didn't just pop up magically inside your triple store, eh? I guess 
    > it's more like "statements whose origin I don't want to model".

How different is this from "nodes whose names I don't care to maintain / 
model?"

[1] http://ninebynine.org/RDFNotes/UsingContextsWithRDF.html#xtocid-6303976

[2] http://copia.ogbuji.net/blog/2006-07-14/querying-named-rdf-graph-aggregate

0023: Nuutti Kotivuori
----------------------

http://lists.w3.org/Archives/Public/public-sparql-dev/2006JulSep/0023.html

Chimezie Ogbuji wrote:

.. code-block:: text

    > I don't agree.  What's the source of this assertion? I think the
    > core issue here is that there is *no* concensus formalism for named
    > graphs WRT RDF, yet SPARQL is dependent on an RDF model that
    > supports named graphs.  If there is one, please point me to it,
    > because I ran across the same problem when constructing programming
    > APIs for named graphs.  The only formalism I know of is Graham Kyle,
    > John McCarthy's work [1].

Well, one thing which would help me in this is a survey of the
approaches other people have taken when doing these things.

I think I know the situation with Redland librdf, when I read the code
last, but I'm not sure if I'm correct.

I think that in librdf, there are statements explicitly without a
context. In SPARQL queries, the default graph is the merge of all
statements in the store, with or without a context. Queries which
explicitly match the graph in a variable never match statements
without a context. And so there is no easy way to match all the
statements without a context only.

I'd like to know atleast how rdflib and Jena (with whatever extensions
that this requires) solve this issue.

-- Naked

0027: Chimezie Ogbuji
---------------------

http://lists.w3.org/Archives/Public/public-sparql-dev/2006JulSep/0027.html

RDFLib has two API's: a Store API and a Graph API.  Every Graph (there 
are several kinds: QuotedGraphs, ConjunctiveGraphs, Named Graphs, 
AggregateGraphs, ..) is associated with a Store instance and an 
identifier. The identifiers are either a Blank Node or a URI.

All the Store API's take a fourth parameter which is the containing Graph 
(even the :meth:`__len__` method). So, theoretically the Store can choose to 
persist RDF triples in a flat space (i.e., vanilla RDF model) and disregard the fourth parameter or use 
the identifier of the containing graph to partition its persistence space 
accordingly - it can even choose to partition formulae seperately (to 
support N3 persistence) from the kind of Graph passed down to it (it will 
receive QuotedGraph instances as the fourth parameter in this case).

The :meth:`Store.triples` method returns a generator of (s,p,o), graphInst so each 
Store implementation is expected to be able to associate each triple with 
a containing graph (or None if the Store chooses to persist triples in a 
flat space).

The Graph API's do most of the leg work of named graph aggregation. 
:class:`ConjunctiveGraph` is an (unamed) aggregation of all the named graphs within 
the Store.  It has a 'default' graph, whose name is associated with the 
ConjunctiveGraph throughout its life.  All methods work against this 
default graph.  Its constructor can take an identifier to use as the name 
of this 'default' graph or it will assign a BNode.  In practice (at least 
how \*I\* use RDFLib), I instantiate a ConjunctiveGraph if I want to add 
triples to the Store but don't care to mint a URI for the graph (the 
scenario which triggered this thread).  These triples can still be 
addressed.

:class:`ReadOnlyGraphAggregate` is a subset of the :class:`ConjunctiveGraph` where the names 
of the graphs it provides an aggregate view for are passed on in the 
constructor - this is how a SPARQL query with multiple FROM NAMED is 
supported.

:class:`QuotedGraphs` are meant to implement Notation 3 formulae.  They are 
associated with a required identifier that the N3 parser must provide in 
order to maintain consistent formulae identification for scenarios such as 
implication and such.

The default dataset for SPARQL queries is equivalent to the Graph instance 
on which the query is dispatched.  If the :meth:`query` method is called on a 
:class:`ConjunctiveGraph`, the default dataset is the entire Store, if it's a named 
graph it's the named graph.

This setup supports:

- Flat space of triples
- Named Graph partitioning
- Notation 3 persistence

0028: Nuutti Kotivuori
----------------------

http://lists.w3.org/Archives/Public/public-sparql-dev/2006JulSep/0028.html

Chimezie Ogbuji wrote:

.. code-block:: text

    > The Graph API's do most of the leg work of named graph
    > aggregation. ConjunctiveGraph is an (unamed) aggregation of all the
    > named graphs within the Store.  It has a 'default' graph, whose name
    > is associated with the ConjunctiveGraph throughout it's life.  All
    > methods work against this default graph.  Its constructor can take an
    > identifier to use as the name of this 'default' graph or it will
    > assign a BNode.  In practice (at least how *I* use RDFLib), I
    > instanciate a ConjunctiveGraph if I want to add triples to the Store
    > but don't care to mint a URI for the graph (the scenario which
    > triggered this thread).  These triples can still be addressed.

Okay, in the context of this discussion, what RDFLib does is that
every time a ConjunctiveGraph is instantiated, it creates a new blank
node and uses that throughout the life of the ConjunctiveGraph
object. And the default graph is the merge of all graphs in the store.

So triples without an origin will be associated with a blank node,
which is shared between added triples, but distinct between different
ConjunctiveGraph objects. This probably coincides rather nicely with
most usages of the API. Single "sessions" of manipulating nodes will
have the blank node origin shared.

And the possible problems are mostly what was already mentioned
earlier about an approach like this. The blank node identities might
not coincide with the actual separateness of the sources graphs -
making a query which matches several statements out of a single graph
might not be too meaningful for these blank nodes. It is difficult to
query only nodes which have no specific origin. And since the graph
name is a blank node, there is no way to explicitly specify the graph
name to be specific blank node, as the SPARQL syntax doesn't allow
this.

-- Naked

References
----------

Two posts by Pat Hayes, recommended by Andy Seaborne.

http://www.ihmc.us/users/phayes/RDFGraphSyntax.html

http://lists.w3.org/Archives/Public/public-rdf-dawg/2006JulSep/0153.html
