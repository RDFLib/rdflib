#!/usr/bin/env python

'''
This benchmark will produce graph digests for all of the 
downloadable ontologies available in Bioportal.
'''

from rdflib import *
from rdflib.compare import to_isomorphic
import sys, csv
from urllib import *
from io import StringIO
from collections import defaultdict

from multiprocessing import *
from Queue import Empty

bioportal_query = '''
PREFIX metadata: <http://data.bioontology.org/metadata/>

select distinct ?ontology ?title ?download where {
    ?ontology a metadata:Ontology;
              metadata:omvname ?title;
              metadata:links ?links.
    ?links metadata:Ontology ?download.
    filter(regex(?download, "/download"))
} 
'''

stat_cols = [
    'id',
    'ontology',
    'download_url',
    'tree_depth', 
    'color_count', 
    'individuations', 
    'prunings',
    'initial_color_count', 
    'adjacent_nodes', 
    'initial_coloring_runtime', 
    'triple_count', 
    'graph_digest',
    'to_hash_runtime',
    'canonicalize_triples_runtime',
    'error',
    ]     

def bioportal_benchmark(apikey, output_file, threads):
    metadata = Namespace("http://data.bioontology.org/metadata/")
    url = 'http://data.bioontology.org/ontologies?apikey=%s'%apikey
    ontology_graph = Graph()
    print url
    ontology_list_json = urlopen(url).read()
    ontology_graph.parse(StringIO(unicode(ontology_list_json)), format="json-ld")
    ontologies = ontology_graph.query(bioportal_query)
    w = open(output_file, 'w')
    writer = csv.DictWriter(w,stat_cols)
    writer.writeheader()
    tasks = Queue()
    finished_tasks = Queue()
    task_count = len(ontologies)
    def worker(q,finished_tasks):
        try:
            while True:
                stats = q.get()
                print stats['ontology'], stats['download_url']
                try:
                    og = Graph()
                    og.load(stats['download_url']+"?apikey=%s"%apikey)
                    ig = to_isomorphic(og)
                    graph_digest = ig.graph_digest(stats)
                except Exception as e:
                    print e
                    stats['error'] = str(e)
                    finished_tasks.put(stats)
        except Empty:
            pass
    for i in range(int(threads)):
        print "Starting worker", i
        t = Process(target=worker, args=[tasks,finished_tasks])
        t.daemon = True
        t.start()
    for ontology, title, download in ontologies:
        stats = defaultdict(str)
        stats.update({
            "id":ontology,
            "ontology": title,
            "download_url": download
        })
        tasks.put(stats)
    tasks.close()
    written_tasks = 0
    while written_tasks < task_count:
        stats = finished_tasks.get()
        print "Writing", stats['ontology']
        writer.writerow(stats)
        w.flush()
        written_tasks += 1

if __name__ == '__main__':
    bioportal_benchmark(sys.argv[1], sys.argv[2], sys.argv[3])
