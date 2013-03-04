from rdflib.graph import ConjunctiveGraph
from rdflib.term import Identifier, URIRef
from rdflib.parser import StringInputSource
from os import path


DATA = u"""
<http://example.org/record/1> a <http://xmlns.com/foaf/0.1/Document> .
"""

PUBLIC_ID = u"http://example.org/record/1"


def test_graph_ids():
    def check(kws):
        cg = ConjunctiveGraph()
        cg.parse(**kws)

        for g in cg.contexts():
            gid = g.identifier
            assert isinstance(gid, Identifier)

    yield check, dict(data=DATA, publicID=PUBLIC_ID, format="turtle")

    source = StringInputSource(DATA.encode('utf8'))
    source.setPublicId(PUBLIC_ID)
    yield check, dict(source=source, format='turtle')


if __name__ == '__main__':
    import nose
    nose.main(defaultTest=__name__)
