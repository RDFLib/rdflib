import platform
import rdflib
from nose.exc import SkipTest
from rdflib.py3compat import b
if platform.system == 'Java':
    raise SkipTest("Skipped test, unicode issues in Jython")


def test_issue_130():
    raise SkipTest("Remote content change - skip for now")
    g = rdflib.Graph()
    try:
        g.parse(location="http://linked-data.ru/example")
    except:
        raise SkipTest('Test data URL unparseable')
    if len(g) == 0:
        raise SkipTest('Test data URL empty of content')
    assert b('rdf:about="http://semanticfuture.net/linked-data/example/#company"') in g.serialize(), g.serialize()
