import os
import sys
import unittest

try: 
    from testutils import check_serialize_parse
except:
    from test.testutils import check_serialize_parse

def _get_test_files_formats():
    skiptests = [
        'strquot.n3',
    ]
    for f in os.listdir('test/n3'):
        if f not in skiptests:
            fpath = "test/n3/"+f
            if f.endswith('.rdf'):
                yield fpath, 'xml'
            elif f.endswith('.n3'):
                yield fpath, 'n3'


if __name__ == "__main__":
    class TestN3Writing(unittest.TestCase):
        def testWriting(self):
            for fpath, fmt in _get_test_files_formats():
                check_serialize_parse(fpath, fmt, 'n3')
    if len(sys.argv) > 1:
        check_serialize_parse(sys.argv[1], 'n3','n3', True)
        sys.exit()
    else:
        unittest.main()

