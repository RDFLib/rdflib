import os
import sys
import logging
import unittest
from rdflib.graph import ConjunctiveGraph
log = logging.getLogger(__name__)

try: 
    from testutils import check_serialize_parse
except:
    from test.testutils import check_serialize_parse

def _get_test_files_formats():
    for f in os.listdir('test/nt'):
        fpath = "test/nt/"+f
        if f.endswith('.rdf'):
            yield fpath, 'xml'
        elif f.endswith('.nt'):
            yield fpath, 'nt'

def test_all_nt_serialize():
    skiptests = [
        'test/nt/anons-02.nt',
        'test/nt/anons-03.nt',
        'test/nt/formulae-01.nt',
        'test/nt/formulae-02.nt',
        'test/nt/formulae-03.nt',
        'test/nt/formulae-05.nt',
        'test/nt/formulae-06.nt',
        'test/nt/formulae-10.nt',
        'test/nt/keywords-08.nt',
        'test/nt/lists-06.nt',
        'test/nt/literals-01.nt',
        'test/nt/literals-02.nt',
        'test/nt/literals-04.nt',
        'test/nt/literals-05.nt',
        'test/nt/numeric-01.nt',
        'test/nt/numeric-02.nt',
        'test/nt/numeric-03.nt',
        'test/nt/numeric-04.nt',
        'test/nt/numeric-05.nt',
        'test/nt/paths-04.nt',
        'test/nt/paths-06.nt',
        'test/nt/qname-01.nt',
        'test/nt/rdflibtest05.nt',
        ]
    for fpath, fmt in _get_test_files_formats():
        if fpath in skiptests:
            log.debug("Skipping %s, known issue" % fpath)
        else:
            yield fpath, fmt


if __name__ == "__main__":
    class TestNTWriting(unittest.TestCase):
        def testWriting(self):
            for fpath, fmt in test_all_nt_serialize():
                check_serialize_parse(fpath, fmt, 'nt')
    if len(sys.argv) > 1:
        check_serialize_parse(sys.argv[1], "nt", "nt", True)
        sys.exit()
    else:
        unittest.main()

