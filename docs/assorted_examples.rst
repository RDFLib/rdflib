.. _assorted_examples:

=================
Assorted examples
=================

Conjunctive Graphs
==================

.. code-block:: python

    from rdflib import Namespace, BNode, Literal, URIRef
    from rdflib.graph import Graph, ConjunctiveGraph
    from rdflib.plugins.memory import IOMemory

    ns = Namespace("http://love.com#")

    mary = URIRef("http://love.com/lovers/mary#")
    john = URIRef("http://love.com/lovers/john#")

    cmary=URIRef("http://love.com/lovers/mary#")
    cjohn=URIRef("http://love.com/lovers/john#")

    store = IOMemory()

    g = ConjunctiveGraph(store=store)
    g.bind("love",ns)

    gmary = Graph(store=store, identifier=cmary)

    gmary.add((mary, ns['hasName'], Literal("Mary")))
    gmary.add((mary, ns['loves'], john))

    gjohn = Graph(store=store, identifier=cjohn)
    gjohn.add((john, ns['hasName'], Literal("John")))

    #enumerate contexts
    for c in g.contexts():
        print "-- %s " % c

    #separate graphs
    print gjohn.serialize(format='n3')
    print "==================="
    print gmary.serialize(format='n3')
    print "==================="

    #full graph
    print g.serialize(format='n3')

Two-finger exercises
====================

.. code-block:: python

    import logging

    # Configure how we want rdflib logger to log messages
    _logger = logging.getLogger("rdflib")
    _logger.setLevel(logging.DEBUG)
    _hdlr = logging.StreamHandler()
    _hdlr.setFormatter(logging.Formatter('%(name)s %(levelname)s: %(message)s'))
    _logger.addHandler(_hdlr)

    from rdflib.graph import Graph
    from rdflib import URIRef, Literal, BNode, Namespace
    from rdflib import RDF

    store = Graph()

    # Bind a few prefix, namespace pairs.
    store.bind("dc", "http://http://purl.org/dc/elements/1.1/")
    store.bind("foaf", "http://xmlns.com/foaf/0.1/")

    # Create a namespace object for the Friend of a friend namespace.
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")

    # Create an identifier to use as the subject for Donna.
    donna = BNode()

    # Add triples using store's add method.
    store.add((donna, RDF.type, FOAF["Person"]))
    store.add((donna, FOAF["nick"], Literal("donna", lang="foo")))
    store.add((donna, FOAF["name"], Literal("Donna Fales")))

    # Iterate over triples in store and print them out.
    print "--- printing raw triples ---"
    for s, p, o in store:
        print s, p, o

    # For each foaf:Person in the store print out its mbox property.
    print "--- printing mboxes ---"
    for person in store.subjects(RDF.type, FOAF["Person"]):
        for mbox in store.objects(person, FOAF["mbox"]):
            print mbox

    # Serialize the store as RDF/XML to the file foaf.rdf.
    store.serialize("foaf.rdf", format="pretty-xml", max_depth=3)

    # Let's show off the serializers

    print "RDF Serializations:"

    # Serialize as XML
    print "--- start: rdf-xml ---"
    print store.serialize(format="pretty-xml")
    print "--- end: rdf-xml ---\n"

    # Serialize as NTriples
    print "--- start: ntriples ---"
    print store.serialize(format="nt")
    print "--- end: ntriples ---\n"




Update namespace
================

.. code-block:: python

    #OLD = "http://www.mindswap.org/2004/terrorOnt.owl#"
    #OLD = "http://wang-desktop/TerrorOrgInstances#"
    OLD = "http://localhost/"
    NEW = "http://profilesinterror.mindswap.org/"

    graph.bind("terror", "http://counterterror.mindswap.org/2005/terrorism.owl#")
    graph.bind("terror_old", "http://www.mindswap.org/2004/terrorOnt.owl#")
    graph.bind("tech", "http://www.mindswap.org/~glapizco/technical.owl#")
    graph.bind("wang-desk", "http://wang-desktop/TerrorOrgInstances#")
    graph.bind("foaf", 'http://xmlns.com/foaf/0.1/')
    graph.bind("dc", 'http://purl.org/dc/elements/1.1/')


    REDFOOT = graph.namespace("http://redfoot.net/2005/redfoot#")

    for cid, _, source in graph.triples((None, REDFOOT.source, None)):
        if source:
            print "updating %s" % source
            try:
                context = graph.get_context(cid)

                for s, p, o in context:
                    context.remove((s, p, o))
                    if isinstance(s, URIRef) and OLD in s:
                        s = URIRef(s.replace(OLD, NEW))
                    if isinstance(p, URIRef) and OLD in p:
                        p = URIRef(p.replace(OLD, NEW))
                    if isinstance(o, URIRef) and OLD in o:
                        o = URIRef(o.replace(OLD, NEW))
                    context.add((s, p, o))

                context.save(source, format="pretty-xml")
            except Exception, e:
                print e


SPARQL query
============

.. code-block:: python

    from rdflib import Literal, ConjunctiveGraph, Namespace, BNode, URIRef

    import rdflib
    from rdflib import plugin

    plugin.register(
        'sparql', rdflib.query.Processor,
        'rdfextras.sparql.processor', 'Processor')
    plugin.register(
        'sparql', rdflib.query.Result,
        'rdfextras.sparql.query', 'SPARQLQueryResult')

    DC = Namespace(u"http://purl.org/dc/elements/1.1/")
    FOAF = Namespace(u"http://xmlns.com/foaf/0.1/")

    graph = ConjunctiveGraph()
    s = BNode()
    graph.add((s, FOAF['givenName'], Literal('Alice')))
    b = BNode()
    graph.add((b, FOAF['givenName'], Literal('Bob')))
    graph.add((b, DC['date'], Literal("2005-04-04T04:04:04Z")))
 
    print graph.query("""PREFIX foaf: <http://xmlns.com/foaf/0.1/>
      PREFIX dc:  <http://purl.org/dc/elements/1.1/>
      PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
      SELECT ?name
      WHERE { ?x foaf:givenName  ?name .
                      OPTIONAL { ?x dc:date ?date } .
                      FILTER ( bound(?date) ) }""").serialize('python')


Data reading exercise
=====================

.. code-block:: python

    #!/usr/bin/env python
    # -*- coding: utf-8 -*-

    """Demo script to show the different ways to read information 
    from an RDF file using rdflib, as found at http://rdflib.net/.

    The tree main methods are:
    1. Simple lookup in a list of triplets (SimpleLookup),
    2. SPARQL query, created with rdflib.sparql.* objects (CustomSparql),
    3. SPARQL query, created with bison (BisonSparql).

    The main function reads a file, xfn-example.rdf, and displays all resource 
    pairs with a symmetrical "xfn:met" relation (e.g. A met B and B met A)
    Uses the rdfs:label of the resources to display the name.

    This demo file has been tested with the following versions of RDFlib:
      rdflib 2.0.6 -- unsupported (since it has no "Graph" modules)
      rdflib 2.1.3 -- methods 1, and 2 work fine
      rdflib 2.1.4 -- methods 1, and 2 work fine
      rdflib 2.2.3 -- methods 1, and 2 work fine
      rdflib 2.3.0 -- methods 1, and 2 work fine
      rdflib 2.3.1 -- methods 1, and 2 work fine
      rdflib 2.3.2 -- methods 1, and 2 work fine
      rdflib 2.3.3 -- methods 1, 2, and 3 work fine
      rdflib 2.4.0 -- methods 1, 2, and 3 work fine (but function call for method 2 was changed)
    """

    __copyright__ = "rdflibdemo written by Freek Dijkstra, Universiteit van Amsterdam, april 2007, contributed to the public domain (feel free to attribute me, but it's not needed)."

    import os
    import sys
    import distutils.version
    # semi-standard modules
    try:
        import rdflib
    except ImportError:
        raise ImportError("Module rdflib is not available. It can be downloaded from http://rdflib.net/\n")
    if distutils.version.StrictVersion(rdflib.__version__) < "3.0.0":
        raise ImportError("The installed version of rdflib, %s, is too old. 2.1 or higher is required" % rdflib.__version__)
    from rdflib.graph import Graph
    from rdflib.sparql.sparqlGraph  import SPARQLGraph
    from rdflib.sparql.graphPattern import GraphPattern
    if distutils.version.StrictVersion(rdflib.__version__) > "2.3.2":
        from rdflib.sparql.bison import Parse   # available in 2.3.3 and up
    if distutils.version.StrictVersion(rdflib.__version__) > "2.3.9":
        from rdflib.sparql import Query         # available in 2.4.0 and up




    def SimpleLookup(graph):
        """
        Extracts information form a rdflib Graph object 
        using a simple list lookup. E.g.:
        result = list(graph.subject_objects(self.xfn["met"])):
        """
        assert(isinstance(graph, Graph))
        xfn  = rdflib.Namespace("http://gmpg.org/xfn/1#")
        rdf  = rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        rdfs = rdflib.Namespace("http://www.w3.org/2000/01/rdf-schema#")
        meetings = []
        # Get a list of (subject, object) tuples in the graph with the xfn:met predicate
        relations = list(graph.subject_objects(xfn["met"]))
        for (person, peer) in relations:
            if not (peer, person) in relations:
                # person says he/she has met peer, but peer doesn't say he/she has met person. Skip.
                continue
            # since we're processing (person, peer), we can skip (peer, person) later
            relations.remove((peer, person))
            personname = list(graph.objects(person, rdfs["label"]))
            if len(personname) == 0:
                continue    # skip persons with no name
            peername = list(graph.objects(peer, rdfs["label"]))
            if len(peername) == 0:
                continue    # skip peers with no name
            personname = list(graph.objects(person, rdfs["label"]))
            # Add the name of the person and peer to list of people who've met.
            meetings.append((personname[0], peername[0]))
    
        # Print the results
        print "Simple Lookup (%d meetings found)" % len(meetings)
        print 40*"-"
        for (person, peer) in meetings:
            print "%s and %s have met" % (person, peer)
        print


    def CustomSparql(graph):
        """
        Extracts information form a rdflib Graph object 
        using a SPARQL query, put together using GraphPattern objects. E.g.:
        select = ("?ifA","?ifB")
        where = GraphPattern([("?ifA", xfn["met"], "?ifB")])
        result = graph.query(select,where)
        See http://dev.w3.org/cvsweb/~checkout~/2004/PythonLib-IH/Doc/sparqlDesc.html for more information.
        """
        assert(isinstance(graph, Graph))
        xfn  = rdflib.Namespace("http://gmpg.org/xfn/1#")
        rdf  = rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        rdfs = rdflib.Namespace("http://www.w3.org/2000/01/rdf-schema#")
        select = ("?personname","?peername")
        where = GraphPattern([
                ("?person", xfn["met"],    "?peer"),
                ("?peer",   xfn["met"],    "?person"),
                ("?person", rdfs["label"], "?personname"),
                ("?peer",   rdfs["label"], "?peername"),
                ])
        # Create a SPARQLGraph wrapper object out of the normal Graph
        sparqlGrph = SPARQLGraph(graph)
        # Make the query
        if distutils.version.StrictVersion(rdflib.__version__) <= "2.3.9":
            relations = sparqlGrph.query(select, where)
        else:
            # graph.query() function was changed in RDFlib 2.4.0
            bindings = { u"xfn": xfn, u"rdf": rdf, u"rdfs": rdfs }
            relations = Query.query(sparqlGrph, select, where, initialBindings=bindings)
    
        for (person, peer) in relations:
            # since we're processing (person, peer), we can skip (peer, person) later
            relations.remove((peer, person))
    
        # Print the results
        print "Manual formatted SPARQL query (%d meetings found)" % len(relations)
        print 40*"-"
        for (person, peer) in relations:
            print "%s and %s have met" % (person, peer)
        print


    def BisonSparql(graph):
        """
        Extracts information form a rdflib Graph object 
        using a SPARQL query, parsed by the bison parser in RDFlib.
        graphpattern = Parse('SELECT ?ifA ?ifB WHERE { ?ifA xfn:met ?ifB . ?ifB xfn:met ?ifA }')
        result = graph.query(graphpattern, initNs=bindings)
        """
        assert(isinstance(graph, Graph))
        if distutils.version.StrictVersion(rdflib.__version__) <= "2.3.2":
            print "Skipping Bison SPARQL query (requires RDFlib 2.3.3 or higher; version %s detected)" % (rdflib.__version__)
            print
            return
        xfn  = rdflib.Namespace("http://gmpg.org/xfn/1#")
        rdf  = rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        rdfs = rdflib.Namespace("http://www.w3.org/2000/01/rdf-schema#")
        bindings = { u"xfn": xfn, u"rdf": rdf, u"rdfs": rdfs }
        query = Parse('SELECT ?personname ?peername WHERE \
            { ?person xfn:met ?peer . ?peer xfn:met ?person . \
            ?person rdfs:label ?personname . ?peer rdfs:label ?peername }')
        # Make the query, and serialize the result as python objects (as opposed to for example XML)
        relations = graph.query(query, initNs=bindings).serialize('python')
        for (person, peer) in relations:
            # since we're processing (person, peer), we can skip (peer, person) later
            relations.remove((peer, person))
    
        # Print the results
        print "Bison SPARQL query (%d meetings found)" % len(relations)
        print 40*"-"
        for (person, peer) in relations:
            print "%s and %s have met" % (person, peer)
        print

    def ReadFile(filename="xfn-example.rdf"):
        """Read a RDF and returns the objects in a rdflib Graph object"""
        graph = Graph()
        print "Read RDF data from %s" % filename
        print
        graph.parse(filename)
        return graph

    if __name__=="__main__":
        print "RDFlib version %s detected" % rdflib.__version__
        print
        graph = ReadFile()
        SimpleLookup(graph)
        CustomSparql(graph)
        BisonSparql(graph)

Example Foaf Smushing  
=====================

Filter a graph by normalizing all foaf persons into URIs based on their mbox_sha1sum.

Suppose I got two FOAF documents each talking about the same person (according to mbox_sha1sum) but they each used a BNode for the subject. For this demo I've combined those two documents into one file:

demo.n3
-------

.. code-block:: n3

    @prefix foaf: <http://xmlns.com/foaf/0.1/> .

    ## from one document
    :p0 a foaf:Person;
      foaf:mbox_sha1sum "65b983bb397fb71849da910996741752ace8369b";
      foaf:nick "mortenf";
      foaf:weblog <http://www.wasab.dk/morten/blog/archives/author/mortenf/> .

    ## from another document
    :p1 a foaf:Person;
        foaf:mbox_sha1sum "65b983bb397fb71849da910996741752ace8369b";
        foaf:nick "mortenf";
        foaf:homepage <http://www.wasab.dk/morten/>;
        foaf:interest <http://en.wikipedia.org/wiki/Atom_(standard)> .

Now I'll use rdflib to transform all the incoming FOAF data to new data that lies about the subjects. It might be easier to do some queries on this resulting graph, although you wouldn't want to actually publish the result anywhere since it loses some information about FOAF people who really had a meaningful URI.

fold_sha1.py
------------

.. code-block:: python

    """filter a graph by changing every subject with a foaf:mbox_sha1sum
    into a new subject whose URI is based on the sha1sum. This new graph
    might be easier to do some operations on.
    """

    from rdflib.graph import Graph
    from rdflib import Namespace

    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    STABLE = Namespace("http://example.com/person/mbox_sha1sum/")

    g = Graph()
    g.parse("demo.n3", format="n3")

    newURI = {} # old subject : stable uri
    for s,p,o in g.triples((None, FOAF['mbox_sha1sum'], None)):
        newURI[s] = STABLE[o]


    out = Graph()
    out.bind('foaf', FOAF)

    for s,p,o in g:
        s = newURI.get(s, s)
        o = newURI.get(o, o) # might be linked to another person
        out.add((s,p,o))

    print out.serialize(format="n3")

Output 
------
note how all of the data has come together under one subject:

.. code-block:: n3

    @prefix _5: <http://example.com/person/mbox_sha1sum/65>.
    @prefix foaf: <http://xmlns.com/foaf/0.1/>.
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.

     _5:b983bb397fb71849da910996741752ace8369b a foaf:Person;
         foaf:homepage <http://www.wasab.dk/morten/>;
         foaf:interest <http://en.wikipedia.org/wiki/Atom_(standard)>;
         foaf:mbox_sha1sum "65b983bb397fb71849da910996741752ace8369b";
         foaf:nick "mortenf";
         foaf:weblog <http://www.wasab.dk/morten/blog/archives/author/mortenf/>. 

An advantage of this approach over other methods for collapsing BNodes is that I can incrementally process new FOAF documents as they come in without having to access my ever-growing archive. Even if another "65b983bb397fb71849da910996741752ace8369b" document comes in next year, I would still give it the same stable subject URI that merges with my existing data.

Transitive traversal
====================

How to use the `transitive_objects` and `transitive_subjects` graph methods

Formal definition
-----------------
The :meth:`~rdflib.graph.Graph.transitive_objects` method finds all nodes such that there is a path from subject to one of those nodes using only the predicate property in the triples. The :meth:`~rdflib.graph.Graph.transitive_subjects` method is similar; it finds all nodes such that there is a path from the node to the object using only the predicate property.

Informal description, with an example
-------------------------------------
In brief, :meth:`~rdflib.graph.Graph.transitive_objects` walks forward in a graph using a particular property, and :meth:`~rdflib.graph.Graph.transitive_subjects` walks backward. A good example uses a property ``ex:parent``, the semantics of which are biological parentage. The :meth:`~rdflib.graph.Graph.transitive_objects` method would get all the ancestors of a particular person (all nodes such that there is a parent path between the person and the object). The :meth:`~rdflib.graph.Graph.transitive_subjects` method would get all the descendants of a particular person (all nodes such that there is a parent path between the node and the person). So, say that your URI is ``ex:person``. 

The following code would get all of your (known) ancestors, and then get all the (known) descendants of your maternal grandmother:

.. code-block:: python

    from rdflib import ConjunctiveGraph, URIRef
 
    person = URIRef('ex:person')
    dad = URIRef('ex:d')
    mom = URIRef('ex:m')
    momOfDad = URIRef('ex:gm0')
    momOfMom = URIRef('ex:gm1')
    dadOfDad = URIRef('ex:gf0')
    dadOfMom = URIRef('ex:gf1')
 
    parent = URIRef('ex:parent')
 
    g = ConjunctiveGraph()
    g.add((person, parent, dad))
    g.add((person, parent, mom))
    g.add((dad, parent, momOfDad))
    g.add((dad, parent, dadOfDad))
    g.add((mom, parent, momOfMom))
    g.add((mom, parent, dadOfMom))
 
    print "Parents, forward from `ex:person`:"
    for i in g.transitive_objects(person, parent):
        print i
 
    print "Parents, *backward* from `ex:gm1`:"
    for i in g.transitive_subjects(parent, momOfMom):
        print i
      
.. warning:: The :meth:`transitive_objects` method has the start node as the *first* argument, but the :meth:`transitive_subjects` method has the start node as the *second* argument.

film.py
=======

.. code-block:: python

    #!/usr/bin/env python
    """ film.py: a simple tool to manage your movies review
    Simon Rozet, http://atonie.org/

    @@ :
    - manage directors and writers
    - manage actors
    - handle non IMDB uri
    - markdown support in comment

    --
    Usage:
        film.py whoami "John Doe <john@doe.org>"
            Initialize the store and set your name and email.
        film.py whoami
            Tell you who you are
        film.py http://www.imdb.com/title/tt0105236/
            Review the movie "Reservoir Dogs"
    """
    import datetime, os, sys, re, time, imdb
    from rdflib import BNode, ConjunctiveGraph, URIRef, Literal, Namespace, RDF

    #storefn = os.path.expanduser('~/movies.n3')
    storefn = '/home/simon/codes/film.dev/movies.n3'
    storeuri = 'file://'+storefn
    title = 'Movies viewed by %s'

    r_who = re.compile('^(.*?) <([a-z0-9_-]+(\.[a-z0-9_-]+)*@[a-z0-9_-]+(\.[a-z0-9_-]+)+)>$')

    DC = Namespace('http://purl.org/dc/elements/1.1/')
    FOAF = Namespace('http://xmlns.com/foaf/0.1/')
    IMDB = Namespace('http://www.csd.abdn.ac.uk/~ggrimnes/dev/imdb/IMDB#')
    REV = Namespace('http://purl.org/stuff/rev#')

    class Store:
        def __init__(self):
            self.graph = ConjunctiveGraph()
            if os.path.exists(storefn):
                self.graph.load(storeuri, format='n3')
            self.graph.bind('dc', 'http://purl.org/dc/elements/1.1/')
            self.graph.bind('foaf', 'http://xmlns.com/foaf/0.1/')
            self.graph.bind('imdb', 'http://www.csd.abdn.ac.uk/~ggrimnes/dev/imdb/IMDB#')
            self.graph.bind('rev', 'http://purl.org/stuff/rev#')
        
        def save(self):
            self.graph.serialize(storeuri, format='n3')
        
        def who(self, who=None):
            if who is not None:
                name, email = (r_who.match(who).group(1), r_who.match(who).group(2))
                self.graph.add((URIRef(storeuri), DC['title'], Literal(title % name)))
                self.graph.add((URIRef(storeuri+'#author'), RDF.type, FOAF['Person']))
                self.graph.add((URIRef(storeuri+'#author'), FOAF['name'], Literal(name)))
                self.graph.add((URIRef(storeuri+'#author'), FOAF['mbox'], Literal(email)))
                self.save()
            else:
                return self.graph.objects(URIRef(storeuri+'#author'), FOAF['name'])
            
        def new_movie(self, movie):
            movieuri = URIRef('http://www.imdb.com/title/tt%s/' % movie.movieID)
            self.graph.add((movieuri, RDF.type, IMDB['Movie']))
            self.graph.add((movieuri, DC['title'], Literal(movie['title'])))
            self.graph.add((movieuri, IMDB['year'], Literal(int(movie['year']))))
            self.save()
        
        def new_review(self, movie, date, rating, comment=None):
            review = BNode() # @@ humanize the identifier (something like #rev-$date)
            movieuri = URIRef('http://www.imdb.com/title/tt%s/' % movie.movieID)
            self.graph.add((movieuri, REV['hasReview'], URIRef('%s#%s' % (storeuri, review))))
            self.graph.add((review, RDF.type, REV['Review']))
            self.graph.add((review, DC['date'], Literal(date)))
            self.graph.add((review, REV['maxRating'], Literal(5)))
            self.graph.add((review, REV['minRating'], Literal(0)))
            self.graph.add((review, REV['reviewer'], URIRef(storeuri+'#author')))
            self.graph.add((review, REV['rating'], Literal(rating)))
            print comment
            if comment is not None:
                self.graph.add((review, REV['text'], Literal(comment)))
            self.save()

        def movie_is_in(self, uri):
            return (URIRef(uri), RDF.type, IMDB['Movie']) in self.graph
            
    def help():
        print __doc__.split('--')[1]

    def main(argv=None):
        if not argv:
            argv = sys.argv
        s = Store()
        if argv[1] in ('help', '--help', 'h', '-h'):
            help()
        elif argv[1] == 'whoami':
            if os.path.exists(storefn):
                print list(s.who())[0]
            else:
                s.who(argv[2])
        elif argv[1].startswith('http://www.imdb.com/title/tt'):
            if s.movie_is_in(argv[1]):
                raise
            else:
                i = imdb.IMDb()
                movie = i.get_movie(argv[1][len('http://www.imdb.com/title/tt'):-1])
                print '%s (%s)' % (movie['title'].encode('utf-8'), movie['year'].encode('utf-8'))
                for director in movie['director']:
                    print 'directed by: %s' % director['name'].encode('utf-8')
                for writer in movie['writer']:
                    print 'writed by: %s' % writer['name'].encode('utf-8')
                s.new_movie(movie)
                rating = None
                while not rating or (rating > 5 or rating <= 0):
                    try:
                        rating = int(raw_input('Rating (on five): '))
                    except ValueError:
                        rating = None
                date = None
                while not date:
                    try:
                        i = raw_input('Review date (YYYY-MM-DD): ')
                        date = datetime.datetime(*time.strptime(i, '%Y-%m-%d')[:6])
                    except:
                        date = None
                comment = raw_input('Comment: ')
                s.new_review(movie, date, rating, comment)
        else:
            help()
    
    if __name__ == '__main__':
        main()

