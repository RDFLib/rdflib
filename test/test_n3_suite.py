import os
import sys
import logging

log = logging.getLogger(__name__)

try:
    from .testutils import check_serialize_parse
except:
    from test.testutils import check_serialize_parse


def _get_test_files_formats():
    skiptests = [
    ]
    for f in os.listdir('test/n3'):
        if f not in skiptests:
            fpath = "test/n3/" + f
            if f.endswith('.rdf'):
                yield fpath, 'xml'
            elif f.endswith('.n3'):
                yield fpath, 'n3'

def all_n3_files():
    skiptests = [
        'test/n3/example-lots_of_graphs.n3',  # the issue here seems to be with QuotedGraph, should this work?
        # 'test/n3/n3-writer-test-30.n3', # this reveals the broken xml qname handling
    ]
    for fpath, fmt in _get_test_files_formats():
        if fpath in skiptests:
            log.debug("Skipping %s, known issue" % fpath)
        else:
            yield fpath, fmt

def test_n3_writing():
    for fpath, fmt in _get_test_files_formats():
        yield check_serialize_parse, fpath, fmt, 'n3'


if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_serialize_parse(sys.argv[1], 'n3', 'n3', True)
        sys.exit()
    else:
        import nose
        nose.main(defaultTest=__name__)
