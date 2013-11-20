import rdflib
from rdflib.plugins.parsers.notation3 import BadSyntax

import nose.tools

# Test for https://github.com/RDFLib/rdflib/issues/336
# and https://github.com/RDFLib/rdflib/issues/345


# stripped-down culprit:
'''\
@prefix fs: <http://freesurfer.net/fswiki/terms/> .
@prefix prov: <http://www.w3.org/ns/prov#> .

<http://nidm.nidash.org/iri/82b79326488911e3b2fb14109fcf6ae7>
        a fs:stat_header,
        prov:Entity ;
    fs:mrisurf.c-cvs_version
        "$Id: mrisurf.c,v 1.693.2.2 2011/04/27 19:21:05 nicks Exp $" .
'''


def test_ns_localname_roundtrip():

    XNS = rdflib.Namespace('http://example.net/fs')

    g = rdflib.Graph()
    g.bind('xns', str(XNS))
    g.add((
        rdflib.URIRef('http://example.com/thingy'),
        XNS['lowecase.xxx-xxx_xxx'],  # <- not round trippable
        rdflib.Literal("Junk")))
    turtledump = g.serialize(format="turtle").decode('utf-8')
    xmldump = g.serialize().decode('utf-8')
    g1 = rdflib.Graph()

    g1.parse(data=xmldump)

    g1.parse(data=turtledump, format="turtle")



if __name__ == '__main__':
    import nose
    import sys
    nose.main(defaultTest=sys.argv[0])
