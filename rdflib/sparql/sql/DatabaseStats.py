# -*- coding: utf-8 -*-

from __future__ import generators

import rdflib
from rdflib.graph import ConjunctiveGraph
from rdflib import plugin
from rdflib.store import Store, NO_STORE, VALID_STORE
from rdflib.namespace import Namespace
from rdflib.term import Literal, URIRef
from types import TupleType
import time
#from rdflib.store.FOPLRelationalModel.QuadSlot import *

import os.path
import cPickle

#NOTE: adjust this array to change which histogram sizes are generated (and 
#need to modify histogram formulas/constant value in QueryCostEstimator to be
# from this list; ideally this should only be one value here)
histogramSizes =  [800]

def OpenGraph(storeType, configStr, graphUri, storeName='rdfstore'):   
    # Get the mysql plugin. You may have to install the python mysql libraries
    store = plugin.get(storeType, Store)(storeName,debug=False,perfLog=True)
    
    # Open previously created store, or create it if it doesn't exist yet
    rt = store.open(configStr, create=False)
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

def GetCachedStats(graph, cacheFolder, alwaysGen=False, genMissing=True, doJoins=False):
    fileName = os.path.join(cacheFolder, graph.store.identifier + "-" + str(normalizeValue(graph.store.configuration, "L"))) + ".cache"
    version = "0.1"
    genStats = genMissing
    stats = LoadCachedStats(fileName, version)
    
    if stats != None:
        genStats = alwaysGen
    
    if genStats:
        print 'Generating data statistics...'
        startTime = time.time()
        stats = GetDatabaseStats(graph, stats, doJoins) # update stats
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

def LoadCachedStats(fileName, version="0.1"):
    if os.path.exists(fileName):
        print 'Reloading data statistics from cache file...',
        # reload previous created data stats cache file
        f = open(fileName, 'r')
        loadVersion = cPickle.load(f)
        if (version == loadVersion):
            startTime = time.time()
            stats = cPickle.load(f)
            #genStats = alwaysGen #False
            f.close()
            print ' done in %s s' % (time.time()-startTime)
            return stats
        else:
            f.close()
            print 'Saved statistics in wrong version! Must be re-generated.'
            os.remove(fileName)
            return None
    else:
        print 'Cache file not found: %s'%(fileName)
        return None

def GetDatabaseStats(store, stats=None, doJoins=False):
    print 'Gathering statistics...'
    startTime = time.time()
    
    if stats is None:
        stats = dict()
    stats['triples'] = 0
    
    stats['cacheName']  = store.identifier + "-" + str(normalizeValue(store.configuration, "L"))
    stats['storeName']  = store.identifier
    stats['internedId'] = store._internedId
    stats['config']     = store.configuration    
    
    tables = dict(type = store.aboxAssertions,
                  lit = store.literalProperties,
                  rel = store.binaryRelations,
                  all = store._internedId + '_all')
    realTables = dict(type = store.aboxAssertions,
                      lit = store.literalProperties,
                      rel = store.binaryRelations)    
    
    cursor = store._db.cursor()
    
    # distinct num. of subjects, predicates, & objects (NOTE: we always want these!)
    statStartTime = time.time()
    stats['subjects'] = CountDistint(cursor, tables['all'], 'subject')   
    stats['predicates'] = CountDistint(cursor, tables['all'], 'predicate') 
    stats['objects'] = CountDistint(cursor, tables['all'], 'object')
    stats['distTime'] = time.time()-statStartTime
    
    if not stats.has_key('colDistTime'):
        stats['colDistTime'] = 0
    
    stats['(%s,?,?)_patTime' % (SUBJECT)] = 0
    stats['(?,%s,?)_patTime' % (PREDICATE)] = 0
    stats['(?,?,%s)_patTime' % (OBJECT)] = 0
    stats['(%s,%s,?)_patTime' % (SUBJECT, PREDICATE)] = 0
    stats['(?,%s,%s)_patTime' % (PREDICATE, OBJECT)] = 0
    stats['(%s,?,%s)_patTime' % (SUBJECT, OBJECT)] = 0
                
    tableType = 'lit'
    for h in histogramSizes:
        if not stats.has_key(tableType + '_pat') or  not stats[tableType + '_pat'].has_key('(%sh%s,?,?)' % (SUBJECT, h)):
            stats['(%sh%s,?,?)_patTime' % (SUBJECT, h)] = 0
            stats['(?,?,%sh%s)_patTime' % (OBJECT,h)] = 0        
            stats['(?,%s,%sh%s)_patTime' % (PREDICATE, OBJECT, h)] = 0             
    
    for tableType in ['lit', 'rel', 'type']:
        
        table = tables[tableType]

        # Statistics on ENTIRE DATABASE (completely unspecified triple pattern)

        # total # triples (NOTE: we always want these!)
        if not stats.has_key(tableType + '_triples'):
            cursor.execute(""" SELECT COUNT(*) FROM %s """ % table) 
            triples = cursor.fetchone()[0]
            stats[tableType + '_triples'] = triples
        
            print '  Processing table %s: %s triples...' %(tableType,triples)
        stats['triples'] += stats[tableType + '_triples']
        
        # distinct num. of subjects, predicates, & objects
        if not stats.has_key(tableType + '_subjects'):
            statStartTime = time.time()
            stats[tableType + '_subjects'] = CountDistint(cursor, table, table.columnNames[SUBJECT])
            stats[tableType + '_predicates'] = CountDistint(cursor, table, table.columnNames[PREDICATE])
            stats[tableType + '_objects'] = CountDistint(cursor, table, table.columnNames[OBJECT])
            stats[tableType + '_distTime'] = time.time()-statStartTime
            
        # subject/object counts for predicates (NOTE: used for greedy ordering algorithm; some cost formulas; always want)
        #if not stats.has_key(tableType + '_colDist'):
        statStartTime = time.time()
        stats[tableType + '_colDist'] = {}
        stats[tableType + '_colDist']['obj_for_pred'] = CountDistinctForColumn(cursor, table, PREDICATE, OBJECT)       
        stats[tableType + '_colDist']['sub_for_pred'] = CountDistinctForColumn(cursor, table, PREDICATE, SUBJECT)
        stats[tableType + '_colDistTime'] = time.time()-statStartTime
        stats['colDistTime'] += stats[tableType + '_colDistTime']

        # triple pattern occurrence counts (NOTE: takes too much space to store all of these! Choose wisely)
        if not stats.has_key(tableType + '_pat'):
            stats[tableType + '_pat'] = {}
        
        if not stats[tableType + '_pat'].has_key('(%s,?,?)' % (SUBJECT)):
            statStartTime = time.time()
            stats[tableType + '_pat']['(%s,?,?)' % (SUBJECT)] = CountTriples(cursor, table, [SUBJECT], [PREDICATE,OBJECT]) # may be useful if lots of queries asking for everything about a particular subject (but only if you are joining the object, etc.); suggest histogram or even average
            stats[tableType + '_pat']['(?,%s,?)' % (PREDICATE)] = CountTriples(cursor, table, [PREDICATE], [SUBJECT,OBJECT]) #NOTE: always wnat this!! Small and very useful!
            stats[tableType + '_pat']['(?,?,%s)' % (OBJECT)] = CountTriples(cursor, table, [OBJECT], [SUBJECT,PREDICATE]) 
            stats[tableType + '_pat']['(%s,%s,?)' % (SUBJECT, PREDICATE)] = CountTriples(cursor, table, [SUBJECT,PREDICATE], [OBJECT])  # if wanted, suggest histogram
            stats[tableType + '_pat']['(?,%s,%s)' % (PREDICATE, OBJECT)] = CountTriples(cursor, table, [PREDICATE, OBJECT], [SUBJECT]) #NOTE: 2nd most useful; but needs ~ 1/3T space; suggest histogram instead
#            stats[tableType + '_pat']['(%s,?,%s)' % (SUBJECT, OBJECT)] = CountTriples(cursor, table, [SUBJECT, OBJECT], [PREDICATE]) #NOTE: basically useless!
            stats[tableType + '_patTime'] = time.time()-statStartTime
        
            stats['(%s,?,?)_patTime' % (SUBJECT)] += stats[tableType + '_pat']['(%s,?,?)' % (SUBJECT)]['countTime']
            stats['(?,%s,?)_patTime' % (PREDICATE)] += stats[tableType + '_pat']['(?,%s,?)' % (PREDICATE)]['countTime']
            stats['(?,?,%s)_patTime' % (OBJECT)] += stats[tableType + '_pat']['(?,?,%s)' % (OBJECT)]['countTime']
            stats['(%s,%s,?)_patTime' % (SUBJECT, PREDICATE)] += stats[tableType + '_pat']['(%s,%s,?)' % (SUBJECT, PREDICATE)]['countTime']
            stats['(?,%s,%s)_patTime' % (PREDICATE, OBJECT)] += stats[tableType + '_pat']['(?,%s,%s)' % (PREDICATE, OBJECT)]['countTime']
            stats['(%s,?,%s)_patTime' % (SUBJECT, OBJECT)] += stats[tableType + '_pat']['(%s,?,%s)' % (SUBJECT, OBJECT)]['countTime']
        
        # histograms (class(s),-,-), (-,-,class(o)), (-,p,class(o))
        for h in histogramSizes:
            if not stats[tableType + '_pat'].has_key('(%sh%s,?,?)' % (SUBJECT, h)):
                #NOTE: if using real value for a particular triple pattern, then disable the histogram version
                #NOTE: can move these out of the loop and put in different histogram sizes for each type of triple pattern (& modify in the formulas)
                stats[tableType + '_pat']['(%sh%s,?,?)' % (SUBJECT, h)] = CountTriples(cursor, table, [SUBJECT], [PREDICATE,OBJECT], [SUBJECT], h)
                stats['(%sh%s,?,?)_patTime' % (SUBJECT, h)] += stats[tableType + '_pat']['(%sh%s,?,?)' % (SUBJECT, h)]['countTime']
                stats[tableType + '_pat']['(?,?,%sh%s)' % (OBJECT, h)] = CountTriples(cursor, table, [OBJECT], [SUBJECT,PREDICATE], [OBJECT], h)
                stats['(?,?,%sh%s)_patTime' % (OBJECT,h)] += stats[tableType + '_pat']['(?,?,%sh%s)' % (OBJECT, h)]['countTime']        
                stats[tableType + '_pat']['(?,%s,%sh%s)' % (PREDICATE, OBJECT, h)] = CountTriples(cursor, table, [PREDICATE, OBJECT], [SUBJECT], [OBJECT], h)
                stats['(?,%s,%sh%s)_patTime' % (PREDICATE, OBJECT, h)] += stats[tableType + '_pat']['(?,%s,%sh%s)' % (PREDICATE, OBJECT, h)]['countTime']            
                #NOTE: may want to add a subject-predicate histogram here (if using the pattern frequently)

    # predicate co-occurrence
    if False:#doJoins:
        # Note: this is very expensive and only used by Stocker WWW2008 method! (i.e. we don't need them)
        if not stats.has_key('joinTime'):
            statStartTime = time.time()
            stats['join_s-s'] = PredicateJoinCount(cursor, realTables, SUBJECT, SUBJECT)
            stats['join_s-o'] = PredicateJoinCount(cursor, realTables, SUBJECT, OBJECT)
            stats['join_o-s'] = PredicateJoinCount(cursor, realTables, OBJECT, SUBJECT)
            stats['join_o-o'] = PredicateJoinCount(cursor, realTables, OBJECT, OBJECT)
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
        for (objCount,) in cursor.fetchall():
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
    
def CountTriples(cursor, table, specifiedColumns, variableColumns, hashColumns=[], hashBuckets=200):
    d = {}
    statStartTime = time.time()
    
    specCols = []
    hardCodedSpecCols = []
    varCols = []
    #hardCodedVarCols = [] # not needed
    indexPos = {}
    distinctCount = []
        
    for i in specifiedColumns:
        if table.columnNames[i] != None:
            indexPos[i] = ('spec',len(specCols))
            
            if not i in hashColumns:        
                specCols.append(table.columnNames[i])  # use all values of this variable column
                if len(hashColumns) > 0:
                    distinctCount.append(table.columnNames[i])                                  
            else:
                # use k hash buckets as a string histogram
                specCols.append("MOD(%s,%s)"%(table.columnNames[i],hashBuckets))
                distinctCount.append(table.columnNames[i])              
        else:
            indexPos[i] = ('hard',len(hardCodedSpecCols))
            hardCodedSpecCols.append(normalizeValue(table.hardCodedResultFields[i],'U')) #BE: assuming this will only be the case for a URI (i.e. for rdf:Type)
    for i in variableColumns:
        indexPos[i] = ('var', -1)
        if table.columnNames[i] != None:    
             varCols.append(table.columnNames[i])
        #else
        #    hardCodedVarCols.append(normalizeValue(table.hardCodedResultFields[i],'U') #BE: assuming this will only be the case for a URI (i.e. for rdf:Type)
        
    distinctClause = ""
    if len(distinctCount) > 0:
        distinctClause = " COUNT(DISTINCT %s) AS distinctCount,"%(",".join(distinctCount))
        
    #Assumes column lists in (s,p,o) order
    if len(specCols) == 0:
        cursor.execute(""" 
            SELECT COUNT(*) AS tripleCount
            FROM %s;""" % (table))        
    if len(specCols) == 1: 
        cursor.execute(""" 
            SELECT %s AS givenCol, %s COUNT(*) AS tripleCount
            FROM %s
            GROUP BY %s;""" % (specCols[0], distinctClause, table, specCols[0]))
#        for (givenCol,tripleCount) in cursor.fetchall():
#            d['%s=%s'%(specCols[0],givenCol) ] = tripleCount        
    elif len(specCols) == 2:
        cursor.execute(""" 
            SELECT %s AS givenCol1, %s AS givenCol2, %s COUNT(*) AS tripleCount
            FROM %s
            GROUP BY %s, %s;""" % (specCols[0], specCols[1], distinctClause, table, specCols[0], specCols[1]))
#        for (givenCol,tripleCount) in cursor.fetchall():
#            d['%s_triples_%s=%s'%(table,givenCols[0],givenCol) ] = tripleCount
    elif len(specCols) == 3:
        cursor.execute(""" 
            SELECT %s AS givenCol1, %s AS givenCol2, %s AS givenCol3, %s COUNT(*) AS tripleCount
            FROM %s
            GROUP BY %s, %s, %s;""" % (specCols[0], specCols[1], specCols[2], distinctClause, table, specCols[0], specCols[1], specCols[2]))
                
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
        if len(distinctCount) > 0: 
            # for histograms, also get the # distinct values in the bucket
            d[','.join(key)+'dist'] = t[len(t)-2]
 
    names = []        
    for i in (SUBJECT,PREDICATE,OBJECT,CONTEXT):            
        if indexPos.has_key(i):
            (type,pos) = indexPos[i]
            if type == 'var':
                names.append('?')
            elif type == 'spec' or type == 'hard':
                names.append(str(i))                
       
    d['countTime'] = time.time()-statStartTime
       
    if len(distinctCount) < 1: 
        print '    Entries for triple pattern (%s) index: %s' % (','.join(names), len(d))
    else:
        print '    Entries for histogram triple pattern (%s) index: %s (%s counts)' % (','.join(names), (len(d)-1)/2, len(d)-1)
    return d
    
def PredicateJoinCount(cursor, realTables, joinField1, joinField2):
    d = {}
            
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
    
def Stats2CSV(stats, cacheFolder, short=True):
    print 'Writing stats to CSV file...',
    startTime = time.time()

    basicValues = ['triples', 'subjects', 'predicates', 'objects',
                   'lit_triples', 'lit_subjects','lit_predicates', 'lit_objects',
                   'rel_triples', 'rel_subjects','rel_predicates', 'rel_objects',
                   'type_triples', 'type_subjects','type_predicates', 'type_objects',
                   'distTime', 'colDistTime',
                   'lit_distTime', 'lit_colDistTime', 'lit_patTime',
                   'rel_distTime', 'rel_colDistTime', 'rel_patTime',
                   'type_distTime', 'type_colDistTime', 'type_patTime',
                   '(%s,?,?)_patTime' % (SUBJECT),
                   '(?,%s,?)_patTime' % (PREDICATE),
                   '(?,?,%s)_patTime' % (OBJECT),
                   '(%s,%s,?)_patTime' % (SUBJECT, PREDICATE),
                   '(?,%s,%s)_patTime' % (PREDICATE, OBJECT),
                   '(%s,?,%s)_patTime' % (SUBJECT, OBJECT),
                                  
                   '(%sh%s,?,?)_patTime' % (SUBJECT, 100),
                   '(?,?,%sh%s)_patTime' % (OBJECT,100),
                   '(?,%s,%sh%s)_patTime' % (PREDICATE, OBJECT, 100),
                   '(%sh%s,?,?)_patTime' % (SUBJECT, 200),
                   '(?,?,%sh%s)_patTime' % (OBJECT,200),
                   '(?,%s,%sh%s)_patTime' % (PREDICATE, OBJECT, 200),
                   '(%sh%s,?,?)_patTime' % (SUBJECT, 400),
                   '(?,?,%sh%s)_patTime' % (OBJECT,400),
                   '(?,%s,%sh%s)_patTime' % (PREDICATE, OBJECT, 400),
                   '(%sh%s,?,?)_patTime' % (SUBJECT, 800),
                   '(?,?,%sh%s)_patTime' % (OBJECT,800),
                   '(?,%s,%sh%s)_patTime' % (PREDICATE, OBJECT, 800),

                   'joinTime',
                   'elapsedTime']
    
    tables = ['lit', 'rel', 'type']  
    
    joins = ['s-s', 's-o', 'o-s', 'o-o']  
    
    filename = os.path.join(cacheFolder,stats['cacheName']) + ".cache.txt" 
    
    if os.path.exists(filename):
        os.remove(filename) # remove old version of file
    
    w = CSVWriter()
    
    w.Open(None, filename)
    w.WriteLine("-----------------------")
    w.WriteLine('Basic Stats')
    w.WriteLine("-----------------------")
    w.Close()  
      
#    w.Open(basicValues,filename)
#    w.WriteEntry(stats)
#    w.Close()
    w.Open(['Name','Value'], filename)
    for n in basicValues:
        if stats.has_key(n):
            w.WriteListEntry([n,stats[n]])
    w.Close()
    
    for tableType in tables:
        for s in stats[tableType + '_colDist']:
            w.Open(None, filename)
            w.WriteLine("-----------------------")
            w.WriteLine("%s_colDist: %s\t%s"%(tableType, s, len(stats[tableType + '_colDist'][s])))
            w.WriteLine("-----------------------")
            w.Close()  

            if not short:
                w.Open(['ColValue','DistValues'], filename)
                for k in stats[tableType + '_colDist'][s]:
                    w.WriteListEntry([k,stats[tableType + '_colDist'][s][k]])            
                w.Close()        
    
    for tableType in tables:
        for s in stats[tableType + '_pat']:
            
            if s.find('h') == -1:
                continue # hack: only show histograms 
                        
            w.Open(None, filename)
            w.WriteLine("-----------------------")
            w.WriteLine("%s_pat: %s\t%s" % (tableType, s, len(stats[tableType + '_pat'][s])-1))
            w.WriteLine("-----------------------")
            w.Close()  

            if not short:
                w.Open(['Pattern','Count'], filename)
                for tp in stats[tableType + '_pat'][s]:
                    w.WriteListEntry([tp,stats[tableType + '_pat'][s][tp]])            
                w.Close()    
           
    for join in joins:
        if not stats.has_key('join_' + join):
            continue
        w.Open(None, filename)
        w.WriteLine("-----------------------")
        w.WriteLine("join_%s\t%s" % (join, len(stats['join_' + join])))
        w.WriteLine("-----------------------")
        w.Close()  

        if not short:
            w.Open(['Pred1','Pred2','Count'], filename)
            for (pred1,pred2) in stats['join_' + join]:
                w.WriteListEntry([pred1,pred2,stats['join_' + join][(pred1,pred2)]])
            w.Close()
                
    print ' done in %s s' % (time.time()-startTime)
  
def Key2Dict(k):
    d = {}
    for pair in k.split(','):
        v = pair.split('=')
        if len(v) < 2:
            return None
        d[int(v[0])] = long(v[1])
    return d      

def HistClass(r, buckets):
    return r % buckets

def TableSum(stats, tables, postFix, key1, key2=None):
    s = 0
    if key2 is None:
        for t in tables:
            s += stats[t + postFix][key1]
    else:
        for t in tables:
            s += stats[t + postFix][key1][key2]
    return s

def AddError(errorData, method, actual, estimate):
    
    if not errorData.has_key(method):
        e = (0,0)
    else:
        e = errorData[method]
        
    errAmount = abs(actual - estimate)   
    # update sums used to calculate mean absolute error and mean squared error 
    errorData[method] = (e[0]+errAmount,e[1]+errAmount*errAmount)        

def WriteErrorResults(w, error, cnt):
    for method in sorted(error):
        print "  %s: MeanErr=%s, MeanSqErr=%s, Cnt=%s" % (method, error[method][0] / float(cnt), error[method][1] / float(cnt), cnt)
        w.WriteListEntry([method, 0, error[method][0] / float(cnt), error[method][1] / float(cnt), cnt])

def CalculateEstimationAccuracy(stats, filename):

    w = CSVWriter()
    w.Open(['Name','Space(Counts)','AvgErr','MeanSqErr','Triples'], filename)
        
    tables = ['lit', 'rel', 'type']
    T = stats['triples']
    DistinctSub = stats['subjects']
    #T = stats['lit_triples'] + stats['rel_triples'] + stats['type_triples']
    #DistinctSub = max(stats['lit_subjects'],stats['rel_subjects'],stats['type_subjects']) #TODO: fix this to get the real distinct # subjects! 
                
    # Columns estimates from [Stocker, 2008]:
    # sel(s) = 1/Distinct(Subject)
    # sel(p) = Size(?,p,?)/T
    # sel(o,p) = Size(?,p,class(c))/Size(?,p,?)
    # sel(o), p not bound = Sum_p{sel(o,p)}
    #                        = Sum_p{Size(?,p,class(o))}/T
        
    print "(s,-,-) Patterns" 
    error = {}
    # 1) (s,?,?) actual
    AddError(error, '(s,-,-)-Actual', 0, 0)
    #w.WriteListEntry(['(s,-,-)-Actual',stats['subjects'],0,0])
    # 2) (s,?,?) estimated as: Size(class(s),?,?)/DistinctClass(class(s))
    # 3) (s,?,?) estimated as: sel(s)*T [Stocker, 2008]
    #                         = T/Distinct(Subject) 
    cnt = 0
    statStartTime = time.time()
    for t in tables:
        for key in stats[t + '_pat']['(%s,?,?)' % (SUBJECT)]:
            cnt += 1
            actual = stats[t + '_pat']['(%s,?,?)' % (SUBJECT)][key]
            d = Key2Dict(key)
            if d is None:
                continue
            s = d[SUBJECT]
            # 2)
            for h in histogramSizes:
                histKey = '%s=%s'%(SUBJECT,HistClass(s,h))
                estimate = stats[t + '_pat']['(%sh%s,?,?)' % (SUBJECT,h)][histKey] / stats[t + '_pat']['(%sh%s,?,?)' % (SUBJECT,h)][histKey + 'dist']
                AddError(error, '(s,-,-)-Hist%s'%(h), actual, estimate)
            # 3)
            estimate = T/DistinctSub
            AddError(error, '(s,-,-)-Stocker', actual, estimate)            
    print "  Elapsed time: %s s"%(time.time()-statStartTime)
    WriteErrorResults(w, error, cnt)    
    
    predicates = []
    print "(-,p,-) Patterns"
    error = {}
    # (?,p,?) actual [Stocker, 2008]
    AddError(error, '(-,p,-)-Actual', 0, 0)
    cnt = 0
    statStartTime = time.time()
    for t in tables:
        for key in stats[t + '_pat']['(?,%s,?)' % (PREDICATE)]:
            cnt += 1
            actual = stats[t + '_pat']['(?,%s,?)' % (PREDICATE)][key]
            d = Key2Dict(key)
            if d is None:
                continue
            predicates.append(d[PREDICATE])
    print "  Elapsed time: %s s"%(time.time()-statStartTime)
    WriteErrorResults(w, error, cnt)    
    
        
    print "(-,-,o) Patterns"
    error = {}
    # 1) (?,?,o) actual    
    AddError(error, '(-,-,o)-Actual', 0, 0)
    # 2) (?,?,o) estimated as: Size(?,?,class(o))/DistinctClass(class(o)) 
    # 3) (?,?,o) estimated as: sel(o)*T [Stocker, 2008]
    #                        = Sum_p{Size(?,p,class(o)}
    # 4) (?,?,o) estimated as: Sum_p{Size(?,p,class(o)}/Sum_p{DistinctClass(p,class(o))}
    # 5) (?,?,o) estimated as: Sum_p{Size(?,p,o)}
    cnt = 0
    statStartTime = time.time()
    for t in tables:
        for key in stats[t + '_pat']['(?,?,%s)' % (OBJECT)]:
            cnt += 1
            actual = stats[t + '_pat']['(?,?,%s)' % (OBJECT)][key]
            d = Key2Dict(key)
            if d is None:
                continue
            o = d[OBJECT]
            
            for h in histogramSizes:
                # 2)
                histKey = '%s=%s'%(OBJECT,HistClass(o,h))
                estimate2 = stats[t + '_pat']['(?,?,%sh%s)' % (OBJECT,h)][histKey] / stats[t + '_pat']['(?,?,%sh%s)' % (OBJECT,h)][histKey + 'dist']
                AddError(error, '(-,-,o)-oDist-Hist%s'%(h), actual, estimate2)
                
                poSum = 0
                distSum = 0
                for p in predicates:
                    poHistKey = '%s=%s,%s=%s'%(PREDICATE, p, OBJECT, HistClass(o,h))
                    if not stats[t + '_pat']['(?,%s,%sh%s)' % (PREDICATE,OBJECT,h)].has_key(poHistKey):
                        continue
                    poSum += stats[t + '_pat']['(?,%s,%sh%s)' % (PREDICATE,OBJECT,h)][poHistKey]
                    distSum += stats[t + '_pat']['(?,%s,%sh%s)' % (PREDICATE,OBJECT,h)][poHistKey + 'dist']
                # 3)
                AddError(error, '(-,-,o)-Stocker-Hist%s'%(h), actual, poSum)
                # 4)
                if distSum > 0:
                    estimate4 = poSum/distSum
                else:
                    estimate4 = 0
                AddError(error, '(-,-,o)-poSumDistSum-Hist%s'%(h), actual, estimate4)
                
            # 5)
            sum5 = 0
            for p in predicates:
                poKey = '%s=%s&%s=%s'%(PREDICATE, p, OBJECT, o)
                if not stats[t + '_pat']['(?,%s,%s)' % (PREDICATE,OBJECT)].has_key(poKey):
                    continue
                sum5 += stats[t + '_pat']['(?,%s,%s)' % (PREDICATE,OBJECT)][poKey]
            AddError(error, '(-,-,o)-poSum', actual, sum5)            
                        
    print "  Elapsed time: %s s"%(time.time()-statStartTime)
    WriteErrorResults(w, error, cnt)    
    
    
    print "(-,p,o) Patterns"
    error = {}
    # 1) (?,p,o) actual    
    AddError(error, '(-,p,o)-Actual', 0, 0)
    # 2) (?,p,o) estimated as: Size(?,p,class(o))/DistinctClass(p,class(o))    
    # 3) (?,p,o) estimated as: sel(p)*sel(o,p)*T [Stocker, 2008]
    #                         = Size(?,p,class(o))
    # 4) (?,p,o) estimated as: min{Size(?,p,?)/DistinctObj(p), DistinctSub(p)}  
    # 5) (?,p,o) estimated as: (Size(?,p,?)/T * Size(?,?,o)/T)*T [Independent]
    cnt = 0
    statStartTime = time.time()
    for t in tables:
        for key in stats[t + '_pat']['(?,%s,%s)' % (PREDICATE,OBJECT)]:
            cnt += 1
            actual = stats[t + '_pat']['(?,%s,%s)' % (PREDICATE,OBJECT)][key]
            d = Key2Dict(key)
            if d is None:
                continue
            p = d[PREDICATE]
            o = d[OBJECT]
            for h in histogramSizes:
                # 2)
                histKey = '%s=%s,%s=%s'%(PREDICATE, p, OBJECT, HistClass(o,h))
                if not stats[t + '_pat']['(?,%s,%sh%s)' % (PREDICATE,OBJECT,h)].has_key(histKey):
                    continue
                estimate2 = stats[t + '_pat']['(?,%s,%sh%s)' % (PREDICATE,OBJECT,h)][histKey] / stats[t + '_pat']['(?,%s,%sh%s)' % (PREDICATE,OBJECT,h)][histKey + 'dist']
                AddError(error, '(-,p,o)-poDist-Hist%s'%(h), actual, estimate2)                            
                # 3)
                estimate3 = stats[t + '_pat']['(?,%s,%sh%s)' % (PREDICATE,OBJECT,h)][histKey]
                AddError(error, '(-,p,o)-Stocker-Hist%s'%(h), actual, estimate3)
            # 4)
            pKey = '%s=%s'%(PREDICATE, p)
            #if t != 'type':
            estimate4 = min(stats[t + '_pat']['(?,%s,?)' % (PREDICATE)][pKey]/stats[t + '_colDist']['obj_for_pred'][p], stats[t + '_colDist']['sub_for_pred'][p])
            #else: #TODO: remove hack after regenerating data
            #    estimate4 = min(stats[t + '_pat']['(?,%s,?)' % (PREDICATE)][pKey]/stats[t + '_colDist']['obj_for_pred'][p][0], stats[t + '_colDist']['sub_for_pred'][p][0])
            AddError(error, '(-,p,o)-pDistCol', actual, estimate4)            
            # 5)            
            oKey = '%s=%s'%(OBJECT, o)
            estimate5 = ((stats[t + '_pat']['(?,%s,?)' % (PREDICATE)][pKey]/T) * (stats[t + '_pat']['(?,?,%s)' % (OBJECT)][oKey]/T))*T
            AddError(error, '(-,p,o)-Independant', actual, estimate5)            
        
    print "  Elapsed time: %s s"%(time.time()-statStartTime)
    WriteErrorResults(w, error, cnt)    
        
        
    print "(s,p,-) Patterns"
    error = {}
    # 1) (s,p,?) actual
    AddError(error, '(s,p,-)-Actual', 0, 0)
    # 2) (s,p,?) estimated as: sel(s)*sel(p)*T [Stocker, 2008]
    #                        = Size(?,p,?)/Distinct(Subject)
    # 3) (s,p,?) estiamted as: min{Size(?,p,?)/DistinctSub(p),DistinctObj(p)}
    # 4) (s,p,?) estimated as: (Size(s,?,?)/T * Size(?,p,?)/T)*T [Independent]
    #TODO: estimate using Size(class(s),?,?) ???
    cnt = 0
    statStartTime = time.time()
    for t in tables:
        for key in stats[t + '_pat']['(%s,%s,?)' % (SUBJECT,PREDICATE)]:
            cnt += 1
            actual = stats[t + '_pat']['(%s,%s,?)' % (SUBJECT,PREDICATE)][key]
            d = Key2Dict(key)
            if d is None:
                continue
            s = d[SUBJECT]
            p = d[PREDICATE]
            # 2)
            pKey = '%s=%s'%(PREDICATE, p)
            estimate2 = stats[t + '_pat']['(?,%s,?)' % (PREDICATE)][pKey]/DistinctSub
            AddError(error, '(s,p,-)-Stocker', actual, estimate2)            
            # 3)
            #if t != 'type':
            estimate3 = min(stats[t + '_pat']['(?,%s,?)' % (PREDICATE)][pKey]/stats[t + '_colDist']['sub_for_pred'][p], stats[t + '_colDist']['obj_for_pred'][p])
            #else: #TODO: remove hack after regenerating data
            #    estimate3 = min(stats[t + '_pat']['(?,%s,?)' % (PREDICATE)][pKey]/stats[t + '_colDist']['sub_for_pred'][p][0], stats[t + '_colDist']['obj_for_pred'][p][0])
                
            AddError(error, '(s,p,-)-pDistCol', actual, estimate3)            
            # 4)
            sKey = '%s=%s'%(SUBJECT, s)
            estimate4 = ((stats[t + '_pat']['(?,%s,?)' % (PREDICATE)][pKey]/T) * (stats[t + '_pat']['(%s,?,?)' % (SUBJECT)][sKey]/T))*T
            AddError(error, '(s,p,-)-Independant', actual, estimate4)            

    print "  Elapsed time: %s s"%(time.time()-statStartTime)
    WriteErrorResults(w, error, cnt)    
    
    print "(s,-,o) Patterns"
    error = {}
    # 1) (s,?,o) actual
    AddError(error, '(s,-,o)-Actual', 0, 0)
    # 2) (s,?,o) estimated as: sel(s)*sel(o)*T [Stocker, 2008] 
    #                        = Sum_p{Size(?,p,class(o))}/Distinct(Subject)
    # 3) (s,?,o) estimated as: (Size(s,?,?)/T * Size(?,?,o)/T)*T [Independent] 
    cnt = 0
    statStartTime = time.time()
    for t in tables:
        for key in stats[t + '_pat']['(%s,?,%s)' % (SUBJECT,OBJECT)]:
            cnt += 1
            actual = stats[t + '_pat']['(%s,?,%s)' % (SUBJECT,OBJECT)][key]
            d = Key2Dict(key)
            if d is None:
                continue
            s = d[SUBJECT]
            o = d[OBJECT]
            # 2)
            for h in histogramSizes:            
                poSum = 0
                for p in predicates:
                    poHistKey = '%s=%s,%s=%s'%(PREDICATE, p, OBJECT, HistClass(o,h))
                    if not stats[t + '_pat']['(?,%s,%sh%s)' % (PREDICATE,OBJECT,h)].has_key(poHistKey):
                        continue;
                    poSum += stats[t + '_pat']['(?,%s,%sh%s)' % (PREDICATE,OBJECT,h)][poHistKey]
                AddError(error, '(s,-,o)-Stocker-Hist%s'%(h), actual, poSum/DistinctSub)            
            # 3)
            sKey = '%s=%s'%(SUBJECT, s)
            oKey = '%s=%s'%(OBJECT, o)
            estimate3 = ((stats[t + '_pat']['(?,?,%s)' % (OBJECT)][oKey]/T) * (stats[t + '_pat']['(%s,?,?)' % (SUBJECT)][sKey]/T))*T
            AddError(error, '(s,-,o)-Independant', actual, estimate3)            
                        
    print "  Elapsed time: %s s"%(time.time()-statStartTime)
    WriteErrorResults(w, error, cnt)    
    
    
    w.Close()
    print "Done."

class CSVWriter(object):
    
    def __init__(self):
        self.f = None
        self.Columns = None

    def Open(self,columns, filename):
        self.Columns = columns
        self.f = open(filename,'a')
        # header
        if self.Columns != None:
            for k in self.Columns:
                self.f.write(k + '\t')
            self.f.write('\n')
            self.f.flush()
    
    def WriteLine(self,line):
        self.f.write(line + '\n')
        self.f.flush()
    
    def WriteListEntry(self,list):
        for k in list:
            if k != None:
                val = str(k).replace('\n',' ').replace('\t', ' ')
            else:
                val = ''
            self.f.write(val + '\t')
        self.f.write('\n')
        self.f.flush()       
    
    def Write(self,list):
        # write data rows
        for d in list:
            self.WriteEntry(d)
    
    def WriteEntry(self,d):
        for k in self.Columns:
            if d.has_key(k):
                val = str(d[k]).replace('\n',' ').replace('\t', ' ')
            else:
                val = ''
            self.f.write(val + '\t')
        self.f.write('\n')
        self.f.flush()
     
    
    def Close(self):        
        self.f.close()
        self.f = None
        
def WriteAllResults(filename, columns, list):
    w = CSVWriter()
    w.Open(columns, filename)    
    w.Write(list)            
    w.Close()
    
