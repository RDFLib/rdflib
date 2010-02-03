# -*- coding: utf-8 -*-

from __future__ import generators

import rdflib
from rdflib.Graph import ConjunctiveGraph
from rdflib import plugin
from rdflib.store import Store, NO_STORE, VALID_STORE
from rdflib import Namespace
from rdflib import Literal
from rdflib import URIRef
import time
from rdflib.store.FOPLRelationalModel.QuadSlot import *

import os.path
import cPickle

from CSVWriter import CSVWriter, WriteAllResults
#from QueryRunner import OpenGraph

defaultGraphUri = "http://www.risukun.com/picweb.rdf#context"
defaultConfigString = "host=localhost,user=semdb,password=semdb,db=rdfstore"

def OpenGraph(storeType, configStr, graphUri, storeName='rdfstore'):   
    # Get the mysql plugin. You may have to install the python mysql libraries
    store = plugin.get(storeType, Store)(storeName,debug=False,perfLog=True)
    
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
    
    print "    Triples in graph: ", len(graph)
    return graph

def GetCachedStats(graph, cacheFolder):
    fileName = os.path.join(cacheFolder, graph.store.identifier + "-" + str(normalizeValue(graph.store.configuration, "L"))) + ".cache"
    version = "0.1"
    genStats = True
    
    if os.path.exists(fileName):
        print 'Reloading data statistics from cache file...',
        # reload previous created data stats cache file
        f = open(fileName, 'r')
        loadVersion = cPickle.load(f)
        if (version == loadVersion):
            startTime = time.time()
            stats = cPickle.load(f)
            genStats = False
            f.close()
            print ' done in %s s' % (time.time()-startTime)
        else:
            f.close()
            print 'Saved statistics in wrong version! Must be re-generated.'
            os.remove(fileName)
    
    if genStats:
        print 'Generating data statistics...'
        startTime = time.time()
        stats = GetDatabaseStats(graph)
        print ' done in %s s' % (time.time()-startTime)
        
        # save stats to disk
        print 'Saving data statistics...',
        startTime = time.time()
        f = open(fileName, 'w')
        cPickle.dump(version, f)
        cPickle.dump(stats, f)
        f.close()
        #print ' done in %s s' % (time.time()-startTime)
        
    return stats    

def GetDatabaseStats(graph):
    print 'Gathering statistics...'
    startTime = time.time()
    
    stats = dict()
    stats['triples'] = 0 #len(graph) #ISSUE: len(graph) only gives count for default graph???
    
    stats['cacheName'] = graph.store.identifier + "-" + str(normalizeValue(graph.store.configuration, "L"))
    stats['storeName'] = graph.store.identifier
    stats['internedId'] = graph.store._internedId
    stats['config'] = graph.store.configuration    
    
    tables = dict(type = graph.store.aboxAssertions,
                  lit = graph.store.literalProperties,
                  rel = graph.store.binaryRelations,
                  all = graph.store._internedId + '_all')
    realTables = dict(type = graph.store.aboxAssertions,
                  lit = graph.store.literalProperties,
                  rel = graph.store.binaryRelations)    
    # columnNames[OBJECT]
    
    cursor = graph.store._db.cursor()
    
    # distinct num. of subjects, predicates, & objects
    tableType = 'all'
    statStartTime = time.time()
    stats['subjects'] = CountDistint(cursor, tables[tableType], 'subject')
    stats['predicates'] = CountDistint(cursor, tables[tableType], 'predicate')
    stats['objects'] = CountDistint(cursor, tables[tableType], 'object')
    stats['distTime'] = time.time()-statStartTime
    
    for tableType in ['lit', 'rel', 'type']:
        
        table = tables[tableType]

        # total # triples
        cursor.execute(""" SELECT COUNT(*) FROM %s """ % table) 
        triples = cursor.fetchone()[0]
        stats[tableType + '_triples'] = triples
        stats['triples'] = stats['triples'] + triples
        
        print '  Processing table %s: %s triples...' %(tableType,triples)
        
        # distinct num. of subjects, predicates, & objects
        statStartTime = time.time()
        stats[tableType + '_subjects'] = CountDistint(cursor, table, table.columnNames[SUBJECT])
        stats[tableType + '_predicates'] = CountDistint(cursor, table, table.columnNames[PREDICATE])
        stats[tableType + '_objects'] = CountDistint(cursor, table, table.columnNames[OBJECT])
        stats[tableType + '_distTime'] = time.time()-statStartTime
        
        # subject/object counts for predicates
        statStartTime = time.time()
        stats[tableType + '_colDist'] = {}
        stats[tableType + '_colDist']['obj_for_pred'] = CountDistinctForColumn(cursor, table, PREDICATE, OBJECT)       
        stats[tableType + '_colDist']['sub_for_pred'] = CountDistinctForColumn(cursor, table, PREDICATE, SUBJECT)
        stats[tableType + '_colDistTime'] = time.time()-statStartTime

        # triple pattern occurrence counts
        statStartTime = time.time()
        stats[tableType + '_pat'] = {}
        stats[tableType + '_pat']['(%s,?,?)' % (SUBJECT)] = CountTriples(cursor, table, [SUBJECT], [PREDICATE,OBJECT])
        stats[tableType + '_pat']['(?,%s,?)' % (PREDICATE)] = CountTriples(cursor, table, [PREDICATE], [SUBJECT,OBJECT])
        stats[tableType + '_pat']['(?,?,%s)' % (OBJECT)] = CountTriples(cursor, table, [OBJECT], [SUBJECT,PREDICATE])
        stats[tableType + '_pat']['(%s,%s,?)' % (SUBJECT, PREDICATE)] = CountTriples(cursor, table, [SUBJECT,PREDICATE], [OBJECT])
        stats[tableType + '_pat']['(?,%s,%s)' % (PREDICATE, OBJECT)] = CountTriples(cursor, table, [PREDICATE, OBJECT], [SUBJECT])
        stats[tableType + '_pat']['(%s,?,%s)' % (SUBJECT, OBJECT)] = CountTriples(cursor, table, [SUBJECT, OBJECT], [PREDICATE])
        stats[tableType + '_patTime'] = time.time()-statStartTime

    # predicate co-occurrence
    statStartTime = time.time()
#    stats['join_s-s'] = PredicateJoinCount(cursor, graph, realTables, SUBJECT, SUBJECT)
#    stats['join_s-o'] = PredicateJoinCount(cursor, graph, realTables, SUBJECT, OBJECT)
#    stats['join_o-s'] = PredicateJoinCount(cursor, graph, realTables, OBJECT, SUBJECT)
#    stats['join_o-o'] = PredicateJoinCount(cursor, graph, realTables, OBJECT, OBJECT)
    stats['joinTime'] = time.time()-statStartTime

    cursor.close()

    endTime = time.time()-startTime
    print 'Statistics gathered in %s ms' % (endTime)
    stats['elapsedTime'] = endTime
    
    return stats
    
    
def CountDistint(cursor, table, colName):
    if colName == None:
        count = 1 # hard-coded columns should have only 1 value! 
    else:
        cursor.execute(""" SELECT COUNT(DISTINCT %s) FROM %s """ % (colName, table)) 
        count = cursor.fetchone()[0]
    print '    Distinct values in column %s: %s' % (colName,count)
    return count
    
def CountDistinctForColumn(cursor, table, mainColumn, countColumn):
    d = {}

    if table.columnNames[mainColumn] == None:
        pred = table.hardCodedResultFields[mainColumn]
        predInt = normalizeValue(pred,'U') #BE: assuming this will only be the case for a URI (i.e. for rdf:Type)
        cursor.execute(""" 
            SELECT COUNT(DISTINCT %s) AS objCount
            FROM %s;""" % (table.columnNames[countColumn], table))
        for (objCount) in cursor.fetchall():
            d[predInt] = objCount
    else: 
        cursor.execute(""" 
            SELECT %s AS pred, COUNT(DISTINCT %s) AS objCount
            FROM %s
            GROUP BY %s;""" % (table.columnNames[mainColumn], table.columnNames[countColumn], table, table.columnNames[mainColumn]))
        for (pred,objCount) in cursor.fetchall():
            d[pred] = objCount
    
    print '    Distinct value entries in %s for column %s: %s' % (countColumn, mainColumn, len(d))    
    return d
    
def CountTriples(cursor, table, specifiedColumns, variableColumns):
    d = {}
    
    specCols = []
    hardCodedSpecCols = []
    varCols = []
    #hardCodedVarCols = [] # not needed
    indexPos = {}
        
    for i in specifiedColumns:
        if table.columnNames[i] != None:
            indexPos[i] = ('spec',len(specCols))
            specCols.append(table.columnNames[i])
        else:
            indexPos[i] = ('hard',len(hardCodedSpecCols))
            hardCodedSpecCols.append(normalizeValue(table.hardCodedResultFields[i],'U')) #BE: assuming this will only be the case for a URI (i.e. for rdf:Type)
    for i in variableColumns:
        indexPos[i] = ('var', -1)
        if table.columnNames[i] != None:
            varCols.append(table.columnNames[i])
        #else
        #    hardCodedVarCols.append(normalizeValue(table.hardCodedResultFields[i],'U') #BE: assuming this will only be the case for a URI (i.e. for rdf:Type)
        
    #Assumes column lists in (s,p,o) order
    if len(specCols) == 0:
        cursor.execute(""" 
            SELECT COUNT(*) AS tripleCount
            FROM %s;""" % (table))        
    if len(specCols) == 1: 
        cursor.execute(""" 
            SELECT %s AS givenCol, COUNT(*) AS tripleCount
            FROM %s
            GROUP BY %s;""" % (specCols[0], table, specCols[0]))
#        for (givenCol,tripleCount) in cursor.fetchall():
#            d['%s=%s'%(specCols[0],givenCol) ] = tripleCount        
    elif len(specCols) == 2:
        cursor.execute(""" 
            SELECT %s AS givenCol1, %s AS givenCol2, COUNT(*) AS tripleCount
            FROM %s
            GROUP BY %s, %s;""" % (specCols[0], specCols[1], table, specCols[0], specCols[1]))
#        for (givenCol,tripleCount) in cursor.fetchall():
#            d['%s_triples_%s=%s'%(table,givenCols[0],givenCol) ] = tripleCount
    elif len(specCols) == 3:
        cursor.execute(""" 
            SELECT %s AS givenCol1, %s AS givenCol2, %s AS givenCol3 COUNT(*) AS tripleCount
            FROM %s
            GROUP BY %s, %s, %s;""" % (specCols[0], specCols[1], specCols[2], table, specCols[0], specCols[1], specCols[2]))
                
    for t in cursor.fetchall():
        key = []
        for i in (SUBJECT,PREDICATE,OBJECT,CONTEXT):  
            if indexPos.has_key(i):
                (type,pos) = indexPos[i]
                if type == 'spec':
                    key.append('%s=%s'%(i,t[pos]))
                elif type == 'hard':
                    key.append('%s=%s'%(i,hardCodedSpecCols[pos]))
        d[','.join(key)] = t[len(t)-1]
 
    names = []        
    for i in (SUBJECT,PREDICATE,OBJECT,CONTEXT):            
        if indexPos.has_key(i):
            (type,pos) = indexPos[i]
            if type == 'var':
                names.append('?')
            elif type == 'spec' or type == 'hard':
                names.append(str(i))                
       
    print '    Entries for triple pattern (%s) index: %s' % (','.join(names), len(d)) 
    return d
    
def PredicateJoinCount(cursor, graph, realTables, joinField1, joinField2):
    d = {}
    #predField = 'predicate' 
    #tableName = graph.store._internedId + '_all'
            
    for table1 in realTables:
        t1 = realTables[table1]
        if t1.columnNames[PREDICATE] == None:
            predStr = t1.hardCodedResultFields[PREDICATE]
            pred1 = normalizeValue(predStr,'U') #BE: assuming this will only be the case for a URI (i.e. for rdf:Type)
        else:
            pred1 = "t1.%s"%(t1.columnNames[PREDICATE])
            
        for table2 in realTables:            
            t2 = realTables[table2]
            if t2.columnNames[PREDICATE] == None:
                predStr = t2.hardCodedResultFields[PREDICATE]
                pred2 = normalizeValue(predStr,'U') #BE: assuming this will only be the case for a URI (i.e. for rdf:Type)
            else:
                pred2 = "t2.%s"%(t2.columnNames[PREDICATE])

            cursor.execute("""
                SELECT %s AS pred1, %s AS pred2, COUNT(*) as tupleCount
                FROM %s t1, %s t2
                WHERE t1.%s = t2.%s
                GROUP BY pred1, pred2
            """%(pred1, pred2, 
                 t1, t2, 
                 t1.columnNames[joinField1], t2.columnNames[joinField2]))
            for (p1,p2,tupleCount) in cursor.fetchall():
                d[(p1,p2)] = tupleCount

    print '    Entries for join type (%s-%s) index: %s' % (joinField1, joinField2, len(d)) 
    return d
    
def Stats2CSV(stats, cacheFolder):
    print 'Writing stats to CSV file...',
    startTime = time.time()

    basicValues = ['triples', 'subjects', 'predicates', 'objects',
                   'lit_triples', 'lit_subjects','lit_predicates', 'lit_objects',
                   'rel_triples', 'rel_subjects','rel_predicates', 'rel_objects',
                   'type_triples', 'type_subjects','type_predicates', 'type_objects',
                   'distTime',
                   'lit_distTime', 'lit_colDistTime', 'lit_patTime',
                   'rel_distTime', 'rel_colDistTime', 'rel_patTime',
                   'type_distTime', 'type_colDistTime', 'type_patTime',
                   'joinTime',
                   'elapsedTime']
    
    tables = ['lit', 'rel', 'type']  
    
    joins = ['s-s', 's-o', 'o-s', 'o-o']  
    
    filename = os.path.join(cacheFolder,stats['cacheName']) + ".cache.txt" # graph.store._internedId + "-" + normalizeValue(graph.store.configuration, "L") + ".cache.txt"
    
    if os.path.exists(filename):
        os.remove(filename) # remove old version of file
    
    w = CSVWriter()
    
    w.Open(None, filename)
    w.WriteLine("-----------------------")
    w.WriteLine('Basic Stats')
    w.WriteLine("-----------------------")
    w.Close()  
      
    w.Open(basicValues,filename)
    w.WriteEntry(stats)
    w.Close()
    
    for tableType in tables:
        for s in stats[tableType + '_colDist']:
            w.Open(None, filename)
            w.WriteLine("-----------------------")
            w.WriteLine("%s_colDist: %s\t%s"%(tableType, s, len(stats[tableType + '_colDist'][s])))
            w.WriteLine("-----------------------")
            w.Close()  

            w.Open(['ColValue','DistValues'], filename)
            for k in stats[tableType + '_colDist'][s]:
                w.WriteListEntry([k,stats[tableType + '_colDist'][s][k]])            
            w.Close()        
    
    for tableType in tables:
        for s in stats[tableType + '_pat']:
            w.Open(None, filename)
            w.WriteLine("-----------------------")
            w.WriteLine("%s_pat: %s\t%s" % (tableType, s, len(stats[tableType + '_pat'][s])))
            w.WriteLine("-----------------------")
            w.Close()  

            w.Open(['Pattern','Count'], filename)
            for tp in stats[tableType + '_pat'][s]:
                w.WriteListEntry([k,stats[tableType + '_pat'][s][tp]])            
            w.Close()    
           
    for join in joins:
        if not stats.has_key('join_' + join):
            continue
        w.Open(None, filename)
        w.WriteLine("-----------------------")
        w.WriteLine("join_%s\t%s" % (join, len(stats['join_' + join])))
        w.WriteLine("-----------------------")
        w.Close()  

        w.Open(['Pred1','Pred2','Count'], filename)
        for (pred1,pred2) in stats['join_' + join]:
            w.WriteListEntry([pred1,pred2,stats['join_' + join][(pred1,pred2)]])
        w.Close()
                
    print ' done in %s s' % (time.time()-startTime)
                
# GetDatabaseStats(OpenGraph('MySQL', defaultConfigString, defaultGraphUri, 'rdfstore'))
# GetDatabaseStats(OpenGraph('MySQL', defaultConfigString + "1", defaultGraphUri, 'rdfstore'))
