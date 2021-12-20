# Work log

##  Cannot enumerate dataset graphs #758 

Extant issue `test_sparqlstore_readonly`

##  Clarify confusion around type of context element in ConjunctiveGraphs and context aware stores #167

Appears to be resolved, see `test_issue_167`

##  Clarify respective use cases of Store.add vs. Store.addN, and correct use of Graph.parse #357 

###  pchampin commented on 20 Feb 2014

The respective use cases between Store.add and Store.addN are not really clear. More precisely, when some one has several triples to write to a store (not necessarily many, nor necessarily available as an iterable), is it

- (a) acceptable to use multiple calls to Store.add, or
- (b) should one avoid that and absolutely use Store.addN?

This needs clarification because currently the answer is "it depends on the store"; more precisely "IOMemory" and "Sleepycat" answer (a), as they have a rather efficient add method, while SPARQLUpdateStore or the SqlAlchemy plugin answer (b), since they make a single query to the underlying store for each call to add.

There is a rather serious consequence to this lack of clarity, in the use of Graph.parse. All parsers in rdflib.plugins use add rather than addN. As a consequence, it might be very inefficient to write:

```py
# g is a Graph
g.parse(filename, format=f)
```

depending on the underlying store of g. For "add-inefficient" stores, one has to write:

```py
data = rdflib.Graph() # in memory graph
data.parse(filename, format=f)
g += data  # uses addN
```

---

###  mwatts15 commented on 31 Aug 2019

As an active user of RDFLib, I don't see that there's much "clarification" needed. The choice between addN and add is as @gromgull describes, but it is, ultimately, up to the application using RDFLib to decide whether batching is appropriate based on their application needs.

Batching add into addN is pretty trivial, but we can save users the effort of doing it themselves. I've made a [context manager and wrapper for Graph](https://github.com/mwatts15/rdflib/commit/48cd7df77e71d8382847872fe7a3371477828df4) that does this.

---

###  pchampin commented on 31 Aug 2019

@mwatts15

> The choice between addN and add is (...) ultimately, up to the application using RDFLib

Well, not when they are using graph.parse, which makes this choice for them...

> I've made a context manager and wrapper for Graph that does this.

That's a great idea :)

### <<<<< Added to Cookbook recipes >>>>>>>


##  CLEAR DEFAULT statement erases named graphs #1275

Extant issue, see `test_clear_default`



test_cg_parse_of_datasets


##  ConjunctiveGraph doesn't handle parsing datasets with default graphs properly #436 

test_ds_capable_parse

###  nicholascar commented 3 days ago

This issue is still a problem in RDFlib 6.0.2. The workaround of `publicID=cg.default_context.identifier` does _work_ but is indeed unintuitive.

We really do need to be able to say:

```py
cg = Dataset()
cg.parse("some-quads-file.trig")   # RDF file type worked out by guess_format()
```

... and then have the default_context == whatever the Trig file said the default graph was.


##  Dataset.graph should not allow adding random graphs to the store #698

###  gromgull commented on 24 Jan 2017

A combination of this:

https://github.com/RDFLib/rdflib/blob/master/rdflib/graph.py#L1356

and this:

https://github.com/RDFLib/rdflib/blob/master/rdflib/graph.py#L1628-L1630

means you can pass an existing graph into the dataset. This will then be added directly.

But there is no guarantee this new graph has the same store, and the triples will not be copied over.

This is chaos, but wasn't flagged earlier since it's chaos all the way down :) #167


>>>>>>>>>> May be chaos but there _is_ Dataset.add_graph(), so it might as well be properly functional.

###  mgberg commented on 23 Jan 2020 •

To clarify, if I were to run

```py
import rdflib
from rdflib.namespace import FOAF
foaf = rdflib.Graph(identifier=FOAF)
foaf.parse("http://xmlns.com/foaf/spec/index.rdf", format="xml")
ds = rdflib.Dataset()
ds.add_graph(foaf)
```

Am I correct in assuming that expected behavior is that len(foaf) should equal len(ds) (when in fact len(ds) is 0)?

It does now: test_issue_698_len_ds


##  Given a Graph, can it be used as default graph for a Dataset? #319 

###  uholzer commented on 1 Aug 2013

Imagine, you are given a Graph, maybe created with Graph() or maybe backed by some arbitrary store. Maybe, for some reason you need a Dataset and you want your Graph to be the default graph of this Dataset. The Dataset should not and will not need to contain any other graphs.

Is there a straightforward way to achieve this without copying all triples? As far as I know, Dataset needs a context_aware and graph_aware store, so it is not possible to just create a Dataset backed by the same store. Graham Klyne is interested in this because he wants to provide a SPARQL endpoint for a given rdflib.Graph, but my implementation of a SPARQL endpoint requires a Dataset. I don't really like to implement support for plain graphs, so I wonder whether there is a simple solution.

Also, I wonder whether it would be useful to have a true union of several graphs backed by different stores.

###  gromgull commented on 2 Aug 2013

There is no way to do it currently, but it would be easy enough to add.

In most cases, the underlying store WILL be context_aware, since most of our stores are, but even if it isn't, we could implement a special "single graph dataset" that will throw an exception if you try to get any other graphs?

And actually, the DataSet is very similar to a graph, how would your endpoint implementation break if just handed a graph?

For the actual SPARQL calls, I made an effort to work with both ConjunctiveGraph and DataSet (or rather, with graph_aware and not graph_aware stores) for the bits that require graphs, and even with a non context-aware graph/store for everything else.

The true-union of graphs from different stores is easy to do naively and with poor performance, and probably impossible to make really scalable (if you have 1000 graphs ... ) It's probably another issue though :)

##  uholzer commented on 10 Aug 2013

There is a discrepancy between Graph and Dataset (note that the parsed triple is missing from the serialization):

```pycon
>>> ds = rdflib.Dataset()
>>> ds.parse(data='<a> <b> <c>.', format='turtle')
>>> print(ds.serialize(format='turtle'))
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

>>> for c in ds.contexts(): print c
... 
[a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'IOMemory']].
<urn:x-rdflib:default> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'IOMemory'].
```

It is clear to me why this happens. ConjunctiveGraph parses into a fresh graph and Dataset inherits this behaviour. For ConjunctiveGraphs one does not observe the above, because the default is the union and hence contains the fresh graph.

Is this behaviour intended? (It doesn't bother me much, I just wanted to note it.)

##  iherman commented on 11 Aug 2013

Well...

One would have to look at the turtle parser behaviour to understand what is going on. But it also a RDFLib design decision.

Formally, a turtle file returns a graph. Not a dataset; a graph.

Which means that the situation below is unclear at a certain level: what happens if one parses a turtle file (ie a graph) into a dataset.

I guess the obvious answer is that it should be parsed into the default graph, but either the turtle parser is modified to do that explicitly in case or a Dataset, or an extra trick should be done in the Dataset object.

And, of course, any modification to the turtle file should be done to all other parsers, which is a bit of a pain (though may be a much cleaner solution!).

#  Inconsistent parse format default #1244 

## ashleysommer commented on 5 Feb •

We recently changed the Graph.parse() method's format parameter to default of turtle instead of XML. This is because turtle is now a much more popular file format for Graph data.

However we overlooked that the ConjunctiveGraph and Dataset classes each have their own overloaded parse() method, and they still use 'xml' as the default format if none is given.

The simple thing to do would be simply replace "xml" with "turtle" on those too, but looking closer that may not be wise. Because ConjuctiveGraph and Dataset are both multi-graph containers and Turtle is not multi-graph capable. So usually when you are doing ConjunctiveGraph.parse() you will not be expecting a turtle file, but more likely .trig or .jsonld.

Should we change the default format on these to something else, or leave it on XML?

##  white-gecko commented on 5 Feb

I think trig would be good

>>>>>>>>>>>>>>>>>>>>>>>>>>  FIXED 

#  ConjunctiveGraph doesn't handle parsing datasets with default graphs properly #436 

##  niklasl commented on 22 Nov 2014

When ConjunctiveGraph.parse is called, it wraps its underlying store in a regular Graph instance. This causes problems for parsers of datasets, e.g. NQuads, TriG and JSON-LD.

Specifically, the triples in the default graph of a dataset haphazardly end up in bnode-named contexts.

Example:

``` python
from rdflib import ConjunctiveGraph

cg = ConjunctiveGraph()
cg.parse(format="nquads", data=u"""
<http://example.org/a> <http://example.org/ns#label> "A" .
<http://example.org/b> <http://example.org/ns#label> "B" <http://example.org/b/> .
""")
assert len(cg.default_context) == 1  # fails
```

While I've attempted to overcome this by using the underlying `graph.store` in these parsers, they cannot access the `default_context` of ConjunctiveGraph through this store. It is there in the underlying store, but its identifier is inaccessible to the parser without further changes to the parse method of ConjunctiveGraph.

This becomes tricky because the contract for ConjunctiveGraph:s parse method is:

```
    Parse source adding the resulting triples to its own context
    (sub graph of this graph).

    See :meth:`rdflib.graph.Graph.parse` for documentation on arguments.

    :Returns:

    The graph into which the source was parsed. In the case of n3
    it returns the root context.
```

I am not sure how we can change this behaviour, since client code may rely on this. We could either add a new method, e.g. `parse_dataset`, or a flag. That would not be obvious to all users though, and somehow I would like to change the behaviour to handle datasets as well. It is always possible to get/create a named graph from a conjunctive graph and parse data into that.

I have gotten further by adding `publicID=cg.default_context.identifier` to the parse invocation. This causes the TriG parser to behave properly (and it is easy to adapt the nquads parser to work from there on). But I am not sure if this is a wise solution to the problem.

I'll mull more on this given time, but it would be good to have more people consider a proper revision of the parsing mechanism for datasets.

This underlies the problems described in #432 and #433 (and is related #428).

(Obviously, this in turn causes the serializers for the same formats to emit unexpected bnode-named graphs when data has been read through these parsers.)

##  niklasl commented on 4 Aug 2016

It might make sense that one should simply parse into the `default_context` of a `ConjunctiveGraph` or `Dataset`, like:

``` py
import rdflib
cg = rdflib.ConjunctiveGraph()
cg.default_context.parse(data=data, format='trig')
print(cg.serialize(format='trig'))
```

By doing it like this (along with a bunch of fairly recent fixes on RDFLib master), this could be considered good enough. It doesn't seem intuitive though.

Leaving this open in case we want to redesign the parsing of datasets to make this more obvious.

##  niklasl commented on 4 Aug 2016

## jpmccu commented on 16 Feb 2017

Fixed issue #682.


##  jpmccu commented on 17 Feb 2017

The current error (in Py3) seems to expect IsomorphicGraph to be hashable:

...
  File "/home/travis/build/RDFLib/rdflib/rdflib/plugins/memory.py", line 254, in add
    self.__all_contexts.add(context)
TypeError: unhashable type: 'IsomorphicGraph'

T
##  joernhees commented on 17 Feb 2017

aaaahaaa:

https://docs.python.org/3/reference/datamodel.html#object.__hash__

    A class that overrides __eq__() and does not define __hash__() will have its __hash__() implicitly set to None. When the __hash__() method of a class is None, instances of the class will raise an appropriate TypeError when a program attempts to retrieve their hash value, and will also be correctly identified as unhashable when checking isinstance(obj, collections.Hashable).
here would be no change by telling users to parse into default_context, that just seems unintuitive.

I'd say leave this open (but for 5.0.0 maybe?) since it is about changing the parsing usage/behaviour when parsing dataset syntaxes (nquads, trig, json-ld and trix). The current wiring of graphs, contexts and underlying stores could really do with such an overhaul.

##  nicholascar [commented 10 days ago](https://github.com/RDFLib/rdflib/issues/436#issuecomment-987435414)


This issue is still a problem in RDFlib 6.0.2. The workaround of publicID=cg.default_context.identifier does _work_ but is indeed unintuitive.

We really do need to be able to say:

```py
from rdflib import Dataset

cg = Dataset()
cg.parse("some-quads-file.trig")   # RDF file type worked out by guess_format()
```

... and then have the default_context == whatever the Trig file said the default graph was.


#  remove __hash__ from mutable classes such as Graph #719 

##  joernhees commented on 20 Feb 2017

see discussion in #718 : `IOMemory` by default uses `hash(graph)` to hash its `identifier` to then create hashed quads... all of this happens in light of "hashing a graph" meaning that its triples are hashed in a cryptographically reliable way...

maybe we should just not define `__hash__` for mutable things such as Graph...

##  jpmccu commented on 21 Feb 2017

We could make an immutable graph class that fixes that. Maybe IsomorphicGraph would also be immutable.

##  Added test for Issue #682 and fixed. #718 

## jpmccu commented on 16 Feb 2017

Fixed issue #682.

##  jpmccu commented on 17 Feb 2017

The current error (in Py3) seems to expect IsomorphicGraph to be hashable:

```
...
  File "/home/travis/build/RDFLib/rdflib/rdflib/plugins/memory.py", line 254, in add
    self.__all_contexts.add(context)
TypeError: unhashable type: 'IsomorphicGraph'
```

##  joernhees commented on 17 Feb 2017

aaaahaaa:

https://docs.python.org/3/reference/datamodel.html#object.__hash__

    A class that overrides __eq__() and does not define __hash__() will have its __hash__() implicitly set to None. When the __hash__() method of a class is None, instances of the class will raise an appropriate TypeError when a program attempts to retrieve their hash value, and will also be correctly identified as unhashable when checking isinstance(obj, collections.Hashable).

##  joernhees commented on 17 Feb 2017

@jimmccusker tests pass, but i'm not entirely sure [f72b51a](https://github.com/RDFLib/rdflib/commit/f72b51aebcbc5d7d0650f94e5f0b9bcec8c597cc) is the way to go... the store uses the hash as context (quads), so changing it as new triples are added is bad bad bad... however, hashing the full `IsomorphicGraph` should probably have something to do with its content?!? luckily we also have an `IsomorphicGraph.internal_hash`

##  jpmccu commented on 17 Feb 2017 •

Right, that's the thing. `__hash__` is supposed to be invariant. What does `set` do? It's hashable, but variant. Since RDF graphs are supposed to be sets of triples (or quads), maybe we can look there for guidance.


##  gromgull commented on 17 Feb 2017

Python sets are NOT hashable, precisely because they are mutable. That's why there is "FrozenSet", this thing has to copy all the triples into a new object that is unchangable. OR make a "FrozenGraph" subclass, that does not allow writes, and hopes the underlying store is not changed during the operation of checking isomorphism.

##  jpmccu commented on 17 Feb 2017

Then that argues that Graphs shouldn't be hashable either. For some reason, there seems to be a use case in Python 3 where graphs are expected to be hashable, but not in Python 2.7.

## joernhees commented on 20 Feb 2017

hmm, not sure we're not getting hung up here on the alternative fact that IOMemory internally hashes the graph's identifier to transform triples into quads... i'm leaning toward hitting that the merge button and be done with this for now, but maybe we should add a cleanup issue to remove the `__hash__` from all mutable things and make IOMemory explicitly hash the identifier?

#  Store query and update methods queryGraph parameter does not support ConjunctiveGraph and Dataset #1396 

##  Tpt commented on 29 Aug

The `query` and `update` methods of the `Store` abstract class allows to overide rdflib default SPARQL evaluator.

They both provide a `queryGraph` parameter to provide the default graph identifier.

However this parameter is not helpful enough to allow a proper implementation of SPARQL evaluation if the Store is used inside of a `ConjunctiveGraph` (for `update`) or a `Dataset` (both `query` and `update`).

Problems:

1. With `query` and `Dataset`.
`Dataset(store="MyCustomStore").update("INSERT DATA {}")` will call the underlying `MyCustomStore` with the parameter `queryGraph=BNode("abcde")` with `BNode("abcde")` the dataset `identifier` instead of `queryGraph=URI("urn:x-rdflib:default")` that identifies the default graph and is used by the basic triple insertion and deletion method. With this parameter the `Store` query evaluator will query the `_:abcde` graph even if the triples are by default added in the default graph identified by `<urn:x-rdflib:default>`.

2. With `update` and `ConjunctiveGraph`.
`ConjunctiveGraph(store="MyCustomStore").update("INSERT DATA {}")` will call the underlying `MyCustomStore` with the parameter `queryGraph="__UNION__"`. With only this information the underlying store does not know what is the identifier of the `ConjunctiveDataset` default graph in which the triples should be added if the update contains an `INSERT` or a `LOAD` action.

3. With `update` and `Dataset`.
 Similarly to the `query` method the `queryGraph` parameter is set to the Dataset `identifier` and not `URI("urn:x-rdflib:default")` so the update is evaluated against the `_:abcde` graph even if triples are by default added to the default graph (`<urn:x-rdflib:default>`) by the `add` method.

A possible solution might be to:
1. Set `queryGraph` to `URI("urn:x-rdflib:default")` for `Dataset` `query` and `update`.
2. Add a new parameter `updateGraph` to the `update` method. It would keep the same value as `queryGraph` if the update is called from a `Graph` or a `Dataset` and to the `ConjunctiveGraph` `identifier` if the update is called from a `ConjunctiveGraph`.

#  TypeError (input parameter) when not providing context for Graph.triples() #899

## themmes commented on 21 Feb 2019

I could not find this error in the issues yet, following the docs it should be possible "If triple pattern does not provide a context, all contexts will be searched.".

Example

```py
import rdflib
graph = rdflib.Graph()
graph.triples()
```

##  mwatts15 commented on 11 Oct 2019 •

The documentation for this method is misleading and incomplete. Both should be resolved in the next release.

In any case `rdflib.graph.Graph::triples()` only accepts a triple pattern, but the sub-class method `rdflib.graph.ConjunctiveGraph::triples()` accepts either a quad with the context (i.e., named graph identifier) as the fourth member or a context keyword param. See this [doc](https://rdflib.readthedocs.io/en/latest/intro_to_graphs.html#basic-triple-matching) (from the latest development version) for more some examples for Graph.

##  sanyam19106 commented on 28 May 2020 •

if you can use

```py
import rdflib
graph = rdflib.Graph()
graph.triples(())
```

It gives no error beacuse you are not give any triple so take if default.
