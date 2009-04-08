import rdflib
from rdflib.Graph import ConjunctiveGraph
from rdflib import plugin
from rdflib.store import Store, NO_STORE, VALID_STORE

try:
    import MySQLdb
except ImportError:
    import warnings
    warnings.warn("MySQLdb is not installed")
    __test__=False

def FixViewsString(configStr, storeName='rdfstore'):
    # Get the mysql plugin. You may have to install the python mysql libraries
    store = plugin.get('MySQL', Store)(storeName,debug=False,perfLog=True)
    
    # Open previously created store, or create it if it doesn't exist yet
    rt = store.open(configStr,create=False)
    if rt == NO_STORE:
        #There is no underlying MySQL infrastructure, create it
        #store.open(configStr,create=True)
        
        #TODO: could create store & load appropriate data here
        assert False, "'%s' store '%s' not found using config string '%s!'" % (storeType, storeName, configStr) 
    else:
        assert rt == VALID_STORE,"There underlying store is corrupted"
        
    #There is a store, use it; use ConjunctiveGraph to see everything!
    graph = ConjunctiveGraph(store, identifier = URIRef(graphUri))
    
    FixViewsGraph(graph)    

def FixViewsGraph(graph):
    FixViews(graph.store._db.cursor(), graph.store._internedId)

def FixViews(cursor, storeInteredId):
    print "Fixing view %s_all."%(storeInteredId)
    
    cursor.execute("""ALTER view %(store)s_all as select subject as subject, subject_term
as subject_term, predicate as predicate, predicate_term as
predicate_term, object as object, 'L' as object_term, context as
context, context_term as context_term, data_type, language from
%(store)s_literalProperties
 union all
select subject as subject, subject_term as subject_term, predicate as
predicate, predicate_term as predicate_term, object as object,
object_term as object_term, context as context, context_term as
context_term, NULL as data_type, NULL as language from
%(store)s_relations
 union all
select member as subject, member_term as subject_term,
CONVERT('3732454415692939113', UNSIGNED INTEGER) as predicate, 'U' as predicate_term, class as
object, class_term as object_term, context as context, context_term as
context_term, NULL as data_type, NULL as language from
%(store)s_associativeBox"""%dict(store=storeInteredId))
    
    print "Fixing view %s_relation_or_associativeBox."%(storeInteredId)
    
    cursor.execute("""ALTER view %(store)s_relation_or_associativeBox as select * from
%(store)s_relations
 union all
select member as subject, member_term as subject_term,
CONVERT('3732454415692939113', UNSIGNED INTEGER) as predicate, 'U' as predicate_term, class as
object, class_term as object_term, context as context, context_term as
context_term from %(store)s_associativeBox"""%dict(store=storeInteredId))
        
    cursor.close()
    
    print "Done."
    
    
if __name__ == '__main__':
   from optparse import OptionParser
   usage = '''usage: %prog [options] configStr storeName'''
   op = OptionParser(usage=usage)
   #op.add_option('--buildOWL',action="store_true",default=True,
   #    help = 'Build OWL from components')
   #op.add_option('--sql',action='store_true',default=False, dest='sql', help='Generate SQL from SPARQL.')
   (options, args) = op.parse_args()
   FixViewsString(args[0], args[1], options)


