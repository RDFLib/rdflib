from codecs import ignore_errors
from rdflib.graph import Graph
from rdflib.term import URIRef

DATA_1 = """<http://example.com#C> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class>.
<http://example.com#B> <http://www.w3.org/2000/01/rdf-schema#subClassOf> _:fIYNVPxd4.
<http://example.com#B> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://example.com#A>.
http://example.com#B <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class>.
<http://example.com#p1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty>.
<http://example.com#A <http://www.w3.org/2002/07/owl#unionOf> _:fIYNVPxd3.\t\n
<http://example.com#A> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class>.
_: <http:www.w3.org/2002/07/owl#allValuesFrom> "karish".?
_:fIYNVPxd4 <http://www.w3.org/2002/07/owl#onProperty> "<http://example.com#p1>". 
_:fIYNVPxd4 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Restriction>.*&^%$#@!
_:fIYNVPxd3 <http://www.w3.org/1999/02/22-rdf-syntax-ns#first> <http://example.com#B>.
_:fIYNVPxd3 <http://www.w3.org/1999/02/22-rdf-syntax-ns#rest> <http://www.w3.org/1999/02/22-rdf-syntax-ns#nil>.
"""

DATA_2 = """
<http://example.org/#ThreeMemberList> <http://www.w3.org/1999/02/22-rdf-syntax-ns#first> <http://example.org/#p> .
<http://example.org/#ThreeMemberList> <http://www.w3.org/1999/02/22-rdf-syntax-ns#rest> _:list2 \t
_:list2 <http://www.w3.org/1999/02/22-rdf-syntax-ns#first> "false" defgvcsxa
_:list2 <http://www.w3.org/1999/02/22-rdf-syntax-ns#rest> _:
_:list3 <http://www.w3.org/1999/02/22-rdf-syntax-ns#first> <http://example.org/#r> .
_:list3 <http://www.w3.org/1999/02/22-rdf-syntax-ns#rest> <http://www.w3.org/1999/02/22-rdf-syntax-ns#nil> .
"""


class Test_NT_Parsing:
    def test_nt_1(self):
        ignore_errors = True
        g = Graph().parse(data=DATA_1, format="nt", ignore_errors = ignore_errors)
        if ignore_errors:
            assert len(g) == 9
        assert False

    def test_nt_2(self):
        ignore_errors = True
        g = Graph().parse(data=DATA_2, format="nt", ignore_errors = ignore_errors)
        if ignore_errors:
            assert len(g) == 5
        assert False
