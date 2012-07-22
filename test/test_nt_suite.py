import os
import traceback
import logging

log = logging.getLogger(__name__)


"""
Basic code for loading all NT files in test/nt folder
The actual tests are done in test_roundtrip
"""

def _get_test_files_formats():
    for f in os.listdir('test/nt'):
        fpath = "test/nt/"+f
        if f.endswith('.rdf'):
            yield fpath, 'xml'
        elif f.endswith('.nt'):
            yield fpath, 'nt'

def all_nt_files():
    skiptests = [        
        # illegal literal as subject
        'test/nt/literals-01.nt', 
        'test/nt/keywords-08.nt',
        'test/nt/paths-04.nt',
        'test/nt/numeric-01.nt',
        'test/nt/numeric-02.nt',
        'test/nt/numeric-03.nt',
        'test/nt/numeric-04.nt',
        'test/nt/numeric-05.nt',

        # illegal variables
        'test/nt/formulae-01.nt',
        'test/nt/formulae-02.nt',
        'test/nt/formulae-03.nt',
        'test/nt/formulae-05.nt',
        'test/nt/formulae-06.nt',
        'test/nt/formulae-10.nt',

        # illegal bnode as predicate
        'test/nt/paths-06.nt', 
        'test/nt/anons-02.nt',
        'test/nt/anons-03.nt', 
        'test/nt/qname-01.nt',
        'test/nt/lists-06.nt',
        ]
    [
        'test/nt/literals-02.nt', # this should work
        'test/nt/literals-05.nt', # this should work
        'test/nt/rdflibtest05.nt', # this should work
        ]
    for fpath, fmt in _get_test_files_formats():
        if fpath in skiptests:
            log.debug("Skipping %s, known issue" % fpath)
        else:
            yield fpath, fmt

