import sys

import time
import bz2
import rdflib

import os
import os.path
import re

import random
from datetime import datetime
import isodate

DATE_FROM = '2008-03-21T00:00:00'
DATE_TO = '2008-05-21T00:00:00'


def randdate():
    start = isodate.parse_datetime(DATE_FROM).toordinal()
    end = isodate.parse_datetime(DATE_TO).toordinal()

    d = datetime.fromordinal(random.randint(start, end))
    return '"%s"^^<%s>' % (isodate.datetime_isoformat(d), rdflib.XSD.dateTime)


def rand(l):
    return lambda: random.sample(l, 1)[0]


def readuris(f):
    return [rdflib.URIRef(x.strip()).n3() for x in file(f)]


def readwords(f):
    return [x.strip() for x in file(f)]


def timequery(graph, querytemplate, transform, K=20):
    res = []
    for x in range(K):
        query = querytemplate
        for k, v in transform.iteritems():
            query = query.replace('%%%s%%' % k, v())

        # print query
        res.append(len(graph.query(query)))
    return res

if __name__ == '__main__':

    start = time.time()
    D = {
        'CountryURI': rand(readuris('countries.txt')),
        'Dictionary1': rand(readwords('titlewords.txt')),
        'OfferURI': rand(readuris('offers.txt')),
        'ProductFeatureURI': rand(readuris('productfeatures.txt')),
        'ProductPropertyNumericValue': lambda: str(random.randint(1, 500)),
        'ProductTypeURI': rand(readuris('producttypes.txt')),
        'ProductURI': rand(readuris('products.txt')),
        'ReviewURI': rand(readuris('reviews.txt')),
        'CurrentDate': randdate
    }
    print 'Reading resource lists in %.2fs' % (time.time() - start)

    g = rdflib.Graph()
    start = time.time()
    g.load(bz2.BZ2File("40k_data.nt.bz2"), format='nt')
    print "Loaded %d triples in %.2fs" % (len(g), time.time() - start)

    for qn in os.listdir('queries/explore'):
        if re.search('query[0-9]*.txt', qn):

            if len(sys.argv) > 1 and sys.argv[1] not in qn:
                continue

            q = os.path.join('queries/explore', qn)
            query = file(q).read()
            if 'DESCRIBE' in query:
                continue
            desc = q.replace('.txt', 'desc.txt')
            transform = {}
            for l in file(desc):
                if l.strip() == '':
                    continue
                k, v = l.strip().split('=')
                if v in D:
                    transform[k] = D[v]

            # print 'Running ',q
            start = time.time()
            rows = timequery(g, query, transform)

            print "%s %s %.2fs" % (qn, rows, time.time() - start)
