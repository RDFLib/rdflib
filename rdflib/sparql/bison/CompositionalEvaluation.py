# -*- coding: utf-8 -*-
"""
This module implements (with sparql-p) compositional forms and semantics as outlined in
the pair of Jorge P´erez et. al papers:

- Semantics of SPARQL                (http://ing.utalca.cl/~jperez/papers/sparql_semantics.pdf)
- Semantics and Complexity of SPARQL (http://arxiv.org/abs/cs.DB/0605124)

It also implements rewrite rules expressed in the SPARQL Algebra:

- http://www.w3.org/TR/rdf-sparql-query/#sparqlAlgebra

Compositional Semantics (Jorge P. et. al syntax)

== Definition 3.5 (Compatible Mappings) == 
Two mappings μ1 : V → T and μ2 : V → T are compatibles if for every ?X ∈ dom(μ1) ∩ dom(μ2) it is the case
that μ1(?X) = μ2(?X), i.e. when μ1 ∪ μ2 is also a mapping.

== Definition 3.7 (Set of Mappings and Operations) ==

Omega1 and Omega2 are sets of mappings

I.   Omega1 ⋉ Omega2          = {μ1 ∪ μ2 | μ1 ∈ Omega1, μ2 ∈ Omega2 are compatible mappings } 
II.  Omega1 ∪ Omega2           = {μ | μ1 ∈ Omega1 or μ2 ∈ Omega2 }
III. Omega1 \ Omega2           = {μ1 ∈ Omega1 | for all μ′ ∈ Omega2, μ and μ′ are not compatible }
IV.  LeftJoin1(Omega1, Omega2) = ( Omega1 ⋉ Omega2 ) ∪ ( Omega1 \ Omega2 ) 

NOTE: sparql-p implements the notion of compatible mappings with the 'clash' attribute
defined on instances of _SPARQLNode (in the evaluation expansion tree)   

An RDF dataset is a set D = {G0, <u1,G1>,... <un,Gn>}

where G0, . . . ,Gn are RDF graphs, u1, . . . , un are IRIs, and n ≥ 0.

NOTE: A SPARQL RDF dataset is equivalent to an RDFLib ConjunctiveGraph so we introduce
a function rdflibDS(D) which returns the ConjunctiveGraph instance associated
with the dataset D

Every dataset D is equipped with a function dD such that
dD(u) = G if u,Gi ∈ D and dD(u) = ∅ otherwise

Let D be an RDF dataset and G an RDF graph in D

== Definition 3.9 (Graph Pattern Evaluation): ==

[[.]](D,G) Is the notation used to indicate the evaluation
of a graph pattern.  

I.  [[(P1 AND P2)]](D,G)   = [[P1]](D,G) ⋉ [[P2]](D,G)
II. [[(P1 UNION P2)]](D,G) = [[P1]](D,G) ∪ [[P2]](D,G)
III.[[(P1 OPT P2)]](D,G)   = LeftJoin1([[P1]](D,G),[[P2]](D,G))  
IV. If u ∈ I, then 
      [[(u GRAPH P)]](D,G)  = [[P]](D,dD(u))
    if ?X ∈ V , then
      [[(?X GRAPH P)]](D,G) =
        [[P]](D,G) ⋉ { ?X -> rdflibDS(D).contexts(P) }
V. [[(P FILTER R)]](D,G) = {μ ∈ [[P]](D,G) | μ |= R}.

NOTE: RDFLib's ConjunctiveGraph.contexts method is used to append bindings
for GRAPH variables.  The FILTER semantics are implemented 'natively'
in sparql-p by python functions 

(http://dev.w3.org/cvsweb/2004/PythonLib-IH/Doc/sparqlDesc.html?rev=1.11#Constraini)

== Equivalence with SPARQL  Algebra (*from* DAWG SPARQL Algebra *to* Jorge.P et. al forms) ==

merge(μ1,μ2)             = μ1 ∪ μ2
Join(Omega1,Omega2)      = Filter(R,Omega1 ⋉ Omega2)
Filter(R,Omega)          = [[(P FILTER R)]](D,G)
Diff(Omega1,Omega2,R)    = (Omega1 \ Omega2) ∪ {μ | μ in Omega1 ⋉ Omega2 and *not* μ |= R} 
Union(Omega1,Omega2)     = Omega1 ∪ Omega2 

#LeftJoin(Omega1,Omega2,R)= Filter(R,Join(Omega1,Omega2)) ∪ Diff(Omega1,Omega2,R)

== Graph Pattern rewrites and reductions ==

[[{t1, t2, . . . , tn}]]D = [[({t1} AND {t2} AND · · · AND {tn})]]D

Proposition 3.13

The above proposition implies that it is equivalent to consider basic
graph patterns or triple patterns as the base case when defining SPARQL general graph patterns.    

== BGP reduction and Disjunctive Normal Forms or Union-Free BGP ==

Step 5 of http://www.w3.org/TR/rdf-sparql-query/#convertGraphPattern
    
Replace Join({}, A) by A
Replace Join(A, {}) by A

=== Disjunctive Normal Form of SPARQL Patterns ==

See: http://en.wikipedia.org/wiki/Disjunctive_normal_form

From Proposition 1 of 'Semantics and Complexity of SPARQL'

I.  (P1 AND (P2 UNION P3)) ≡ ((P1 AND P2) UNION (P1 AND P3))
II. (P1 OPT (P2 UNION P3)) ≡ ((P1 OPT P2) UNION (P1 OPT P3))
III.((P1 UNION P2) OPT P3) ≡ ((P1 OPT P3) UNION (P2 OPT P3)) 
IV. ((P1 UNION P2) FILTER R) ≡ ((P1 FILTER R) UNION (P2 FILTER R)) 

The application of the above equivalences permits to translate any graph pattern
into an equivalent one of the form:

P1 UNION P2 UNION P3 UNION ... UNION P

NOTE: sprarql-p SPARQL.query API is geared for evaluation of SPARQL patterns already in DNF:
 - http://dev.w3.org/cvsweb/~checkout~/2004/PythonLib-IH/Doc/Attic/pythondoc-sparql.html?rev=1.5&content-type=text/html;%20charset=iso-8859-1#sparql.SPARQL.query-method

"""
from GraphPattern import ParsedAlternativeGraphPattern,ParsedOptionalGraphPattern, ParsedGroupGraphPattern, ParsedGraphGraphPattern
from PreProcessor import *
from Resource import *
from rdflib import URIRef,Variable,BNode, Literal, plugin, RDF
from rdflib.sparql.Unbound import Unbound
from QName import *
from Expression import *
from rdflib.sparql.graphPattern import BasicGraphPattern