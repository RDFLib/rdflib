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
    'initial_color_count', 
    'adjacent_nodes', 
    'initial_coloring_runtime', 
    'triple_count', 
    'graph_digest',
    'to_hash_runtime',
    'canonicalize_triples_runtime',
    ]     

def bioportal_benchmark(apikey, output_file):
    metadata = Namespace("http://data.bioontology.org/metadata/")
    url = 'http://data.bioontology.org/ontologies?apikey=%s'%apikey
    ontology_graph = Graph()
    print url
    ontology_list_json = urlopen(url).read()
    print ontology_list_json[:1000]
    ontology_graph.parse(StringIO(unicode(ontology_list_json)), format="json-ld")
    ontologies = ontology_graph.query(bioportal_query)
    w = open(output_file, 'w')
    writer = csv.DictWriter(w,stat_cols)
    writer.writeheader()
    for ontology, title, download in ontologies:
        stats = defaultdict(str)
        stats.update({
            "id":ontology,
            "ontology": title,
            "download_url": download
        })
        print title, download
        try:
            og = Graph()
            og.load(download+"?apikey=%s"%apikey)
            ig = to_isomorphic(og)
            graph_digest = ig.graph_digest(stats)
            writer.writerow(stats)
            w.flush()
        except Exception as e:
            print e

if __name__ == '__main__':
    bioportal_benchmark(sys.argv[1], sys.argv[2])