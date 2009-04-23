#!/usr/bin/env python
"""
sparqler.py - Run SPARQL queries against an existing RDF store.

Copyright 2007 John L. Clark

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 2 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.

If you do not have a copy of the GNU General Public License, you may obtain
one from <http://www.gnu.org/licenses/>.
"""

import sys
from rdflib.sparql.bison.Query import Prolog
from rdflib import plugin, util
from rdflib.namespace import Namespace, RDF, RDFS
from rdflib.term import URIRef, BNode, Variable, Literal
from rdflib.store import Store
from rdflib.sparql.parser import parse
from rdflib.graph import ConjunctiveGraph, Graph
from rdflib.sparql.sql.RelationalAlgebra import RdfSqlBuilder, ParseQuery, DEFAULT_OPT_FLAGS
from rdflib.sparql.sql.RdfSqlBuilder import *

OWL_NS=Namespace('http://www.w3.org/2002/07/owl#')

OWL_PROPERTIES_QUERY=\
"""
SELECT ?literalProperty ?resourceProperty
WHERE {
    { ?literalProperty a owl:DatatypeProperty }
                    UNION
    { ?resourceProperty a ?propType 
      FILTER( 
        ?propType = owl:ObjectProperty || 
        ?propType = owl:TransitiveProperty ||
        ?propType = owl:SymmetricProperty ||
        ?propType = owl:InverseFunctionalProperty )  }
}"""

RDFS_NS=Namespace('http://www.w3.org/2000/01/rdf-schema#')

RDFS_PROPERTIES_QUERY=\
"""
SELECT ?literalProperty ?resourceProperty
WHERE {
    { ?literalProperty rdfs:range rdfs:Literal }
                    UNION
    { ?resourceProperty rdfs:range ?range .
      ?range owl:disjointWith rdfs:Literal . }
}"""

def print_set(intro, aSet, stream=sys.stderr):
  print >> stream, intro + ', a set of size %s:' % len(aSet)
  for el in aSet:
    print >> stream, ' ', el

def prepQuery(queryString,ontGraph):
    query=parse(queryString)
    if ontGraph:
        if not query.prolog:
            query.prolog = Prolog(None, [])
            query.prolog.prefixBindings.update(dict(ontGraph.namespace_manager.namespaces()))
        else:
            for prefix, nsInst in ontGraph.namespace_manager.namespaces():
                if prefix not in query.prolog.prefixBindings:
                    query.prolog.prefixBindings[prefix] = nsInst
        print "Bindings picked up ", query.prolog.prefixBindings
    return query

def main():
    from optparse import OptionParser
    usage = '''usage: %prog [options] \\
    <DB connection string> <DB table identifier> <SPARQL query string>'''
    op = OptionParser(usage=usage)
    op.add_option('-s', '--storeKind',
                  metavar='STORE', help='Use this type of DB')
    op.add_option('--owl',
      help='Owl file used to help identify literal and resource properties')
    op.add_option('--rdfs',
      help='RDFS file used to help identify literal and resource properties')
    op.add_option('-d', '--debug', action='store_true',
                  help='Enable (store-level) debugging')
    op.add_option('--sparqlDebug', action='store_true',
                  help='Enable (SPARQL evaluation) debugging')  
    op.add_option('--file', default=None,
                  help='File to load SPARQL from')    
    op.add_option('--render', action='store_true',default=False,
                  help='Render a SPARQL snippet')    
    op.add_option('--flatten', action='store_true',default=False,
                  help='Used with --render to determine if the SQL should be flattened or not')    
    op.add_option('-l', '--literal',
                  action='append', dest='literal_properties',
                  metavar='URI',
                  help='Add URI to the list of literal properties')
    op.add_option('-p', '--profile',action='store_true',
                  help='Enable profiling statistics')
    op.add_option('--originalSPARQL',action='store_true',default=False,
                  help='Bypass SPARQL-to-SQL method?')    
    op.add_option('-r', '--resource',
                  action='append', dest='resource_properties',
                  metavar='URI',
                  help='Add URI to the list of resource properties')
    op.add_option('--inMemorySQL', action='store_true',default=False,
      help="Force in memory SPARQL evaluation?")    
  
    op.set_defaults(debug=False, storeKind='MySQL')
    (options, args) = op.parse_args()

    if len(args) <2 :
      op.error(
        'You need to provide a connection string ' +
        '\n(of the form "user=...,password=...,db=...,host=..."), ' +
        '\na table identifier, and a query string.')

    from rdflib.sparql import Algebra
    Algebra.DAWG_DATASET_COMPLIANCE = False
    if len(args)==3:
        connection, identifier, query = args
    else:
        connection, identifier = args
    store = plugin.get(options.storeKind, Store)(identifier)
    ontGraph=None
    if options.owl:
        ontGraph=Graph().parse(options.owl)
    elif options.rdfs:
        ontGraph=Graph().parse(options.rdfs)
    if options.storeKind == 'MySQL' and options.owl:
        for litProp,resProp in ontGraph.query(OWL_PROPERTIES_QUERY,
                                              initNs={u'owl':OWL_NS}):
            if litProp:
                store.literal_properties.add(litProp)
            if resProp: 
                store.resource_properties.add(resProp)
        if options.debug:
            print "literalProperties: ", litProp
            print "resourceProperties: ", resProp
    if options.storeKind == 'MySQL' and options.rdfs:
        for litProp,resProp in ontGraph.query(RDFS_PROPERTIES_QUERY,
                                              initNs={u'owl':OWL_NS}):
            if litProp:
                store.literal_properties.add(litProp)
            if resProp: 
                store.resource_properties.add(resProp)
        if options.debug:
            print "literalProperties: ", litProp
            print "resourceProperties: ", resProp
    rt = store.open(connection, create=False)
    dataset = ConjunctiveGraph(store)
    if options.inMemorySQL:
        dataset.store.originalInMemorySQL = True
  
    if options.literal_properties:
        store.literal_properties.update(
            [URIRef(el) for el in options.literal_properties])
    if options.resource_properties:
        store.resource_properties.update(
            [URIRef(el) for el in options.resource_properties])
    if options.debug:
        print_set('literal_properties', store.literal_properties)
        print_set('resource_properties', store.resource_properties)
        store.debug = True
    if options.profile:
        import hotshot, hotshot.stats
        prof = hotshot.Profile("sparqler.prof")
        res = prof.runcall(dataset.query,query,DEBUG=options.sparqlDebug)
        prof.close()
        stats = hotshot.stats.load("sparqler.prof")
        stats.strip_dirs()
        stats.sort_stats('time', 'calls')
        print "==="*20
        stats.print_stats(20)
        print "==="*20  
    if options.originalSPARQL:
        dataset.store.originalInMemorySQL = True
    if options.render:
        flags=DEFAULT_OPT_FLAGS.copy()
        if options.flatten:
            flags[OPT_FLATTEN]=False
        sb = RdfSqlBuilder(Graph(store), optimizations=flags)
        if options.file:
            query=prepQuery(open(options.file).read(),ontGraph)
            res = dataset.query(query,DEBUG=True)
            print res
        else:
            query = prepQuery(query,ontGraph)
            root = ParseQuery(query,sb)
            print repr(root)
            root.GenSql(sb)        
            sql = sb.Sql()
            print sql
        return
    else:
        flags=DEFAULT_OPT_FLAGS.copy()
        if options.flatten:
            flags[OPT_FLATTEN]=False
        dataset.store.optimizations = flags
        if options.file:
            query=prepQuery(open(options.file).read(),ontGraph)
            res = dataset.query(query,DEBUG=options.sparqlDebug)
        else:
            query=prepQuery(query,ontGraph)
            res = dataset.query(query,DEBUG=options.sparqlDebug,initNs=ontGraph and dict(ontGraph.namespace_manager.namespaces()) or {})
    print res.serialize(format='xml')

if __name__ == '__main__':
    main()
