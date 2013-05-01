import unittest
try:
  from pydot import Dot
except ImportError:
  from nose import SkipTest
  raise SkipTest('pydot required but not installed')
from StringIO import StringIO
from rdflib.extras.utils import graphutils
from rdflib.graph import Graph

n3source = """\
@prefix : <http://www.w3.org/2000/10/swap/Primer#>.
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix dc:  <http://purl.org/dc/elements/1.1/> .
@prefix foo: <http://www.w3.org/2000/10/swap/Primer#>.
@prefix swap: <http://www.w3.org/2000/10/swap/>.

<> dc:title
  "Primer - Getting into the Semantic Web and RDF using N3".

<#pat> <#knows> <#jo> .
<#pat> <#age> 24 .
<#al> is <#child> of <#pat> .

<#pat> <#child>  <#al>, <#chaz>, <#mo> ;
       <#age>    24 ;
       <#eyecolor> "blue" .

:Person a rdfs:Class.

:Pat a :Person.

:Woman a rdfs:Class; rdfs:subClassOf :Person .

:sister a rdf:Property.

:sister rdfs:domain :Person; 
        rdfs:range :Woman.

:Woman = foo:FemaleAdult .
:Title a rdf:Property; = dc:title .

""" # --- End of primer code

class TestUtilN3toDot(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()
        self.graph.parse(StringIO(n3source), format="n3")
        self.dot = Dot()

    def test_util_graph_to_dot(self):
        res = graphutils.graph_to_dot(self.graph, self.dot)
        res = self.dot.to_string()
        self.assert_('swap/Primer#Person' in res, res)

if __name__ == "__main__":
    unittest.main()
