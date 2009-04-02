# import os, sys, string
import unittest

from rdflib.graph import Graph
from rdflib.term import URIRef


DATA=\
"""<http://example.com#C> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class>.
<http://example.com#B> <http://www.w3.org/2000/01/rdf-schema#subClassOf> _:fIYNVPxd4.
<http://example.com#B> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://example.com#A>.
<http://example.com#B> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class>.
<http://example.com#p1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty>.
<http://example.com#A> <http://www.w3.org/2002/07/owl#unionOf> _:fIYNVPxd3.
<http://example.com#A> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class>.
_:fIYNVPxd4 <http://www.w3.org/2002/07/owl#allValuesFrom> <http://example.com#C>.
_:fIYNVPxd4 <http://www.w3.org/2002/07/owl#onProperty> <http://example.com#p1>.
_:fIYNVPxd4 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Restriction>.
_:fIYNVPxd3 <http://www.w3.org/1999/02/22-rdf-syntax-ns#first> <http://example.com#B>.
_:fIYNVPxd3 <http://www.w3.org/1999/02/22-rdf-syntax-ns#rest> <http://www.w3.org/1999/02/22-rdf-syntax-ns#nil>.
"""

def main():
    unittest.main()

class OWLCollectionTest(unittest.TestCase):

    def testCollectionRDFXML(self):
        g=Graph().parse(data=DATA, format='nt')
        g.namespace_manager.bind('owl',URIRef('http://www.w3.org/2002/07/owl#'))
        print g.serialize(format='pretty-xml')

if __name__ == '__main__':
    main()
