"""

A simple example showing how to use a Sleepycat store to do on-disk
persistence.

"""

from rdflib import ConjunctiveGraph, Namespace, Literal
from rdflib.store import NO_STORE, VALID_STORE

from tempfile import mktemp

if __name__ == '__main__':
    path = mktemp()

    # Open previously created store, or create it if it doesn't exist yet
    graph = ConjunctiveGraph('Sleepycat')

    rt = graph.open(path, create=False)

    if rt == NO_STORE:
        # There is no underlying Sleepycat infrastructure, create it
        graph.open(path, create=True)
    else:
        assert rt == VALID_STORE, 'The underlying store is corrupt'

    print('Triples in graph before add: ', len(graph))

    # Now we'll add some triples to the graph & commit the changes
    rdflib = Namespace('http://rdflib.net/test/')
    graph.bind('test', 'http://rdflib.net/test/')

    graph.add((rdflib['pic:1'], rdflib.name, Literal('Jane & Bob')))
    graph.add((rdflib['pic:2'], rdflib.name, Literal('Squirrel in Tree')))

    print('Triples in graph after add: ', len(graph))

    # display the graph in RDF/XML
    print(graph.serialize(format='n3'))

    # close when done, otherwise sleepycat will leak lock entries.
    graph.close()

    graph = None

    # reopen the graph

    graph = ConjunctiveGraph('Sleepycat')

    graph.open(path, create = False)

    print('Triples still in graph: ', len(graph))

    graph.close()

    # Clean up the temp folder to remove the Sleepycat database files...
    import os
    for f in os.listdir(path):
        os.unlink(path+'/'+f)
    os.rmdir(path)
