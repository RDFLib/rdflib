import rdflib
from nose import SkipTest
from nose.tools import assert_raises

data = '''<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:http="http://www.w3.org/2011/http#">

    <http:HeaderElement rdf:about="#he0">
        <http:params>
            <http:Parameter rdf:about="#param0_0" />
            <http:Parameter rdf:about="#param0_1" />
        </http:params>
    </http:HeaderElement>

</rdf:RDF>
'''

data2 = '''<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns="http://www.example.org/meeting_organization#">

    <rdf:Description about="http://meetings.example.com/cal#m1">
        <Location rdf:parseType="Resource">
            <zip xmlns="http://www.another.example.org/geographical#">02139</zip>
            <lat xmlns="http://www.another.example.org/geographical#">14.124425</lat>
        </Location>
    </rdf:Description>
</rdf:RDF>
'''

def test_broken_rdfxml():
    #import ipdb; ipdb.set_trace()
    def p():
        rdflib.Graph().parse(data=data)

    assert_raises(Exception, p)

def test_parsetype_resource():
    g = rdflib.Graph().parse(data=data2)
    print(g.serialize(format='n3'))

if __name__ == '__main__':
    test_broken_rdfxml()
    test_parsetype_resource()
