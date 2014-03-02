import rdflib
from nose.tools import assert_raises

data='''<?xml version="1.0" encoding="utf-8"?>
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



def test_broken_rdfxml():
    #import ipdb; ipdb.set_trace()

    def p():
        g = rdflib.Graph().parse(data=data)

    assert_raises(Exception, p)
