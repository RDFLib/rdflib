import os
import sys
import unittest
try:
    maketrans = str.maketrans
except AttributeError:
    from string import maketrans
import rdflib

"""
SWAP N3 parser test suite
"""

rdf = rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = rdflib.Namespace("http://www.w3.org/2000/01/rdf-schema#")
xsd = rdflib.Namespace("http://www.w3.org/2001/XMLSchema#")
owl = rdflib.Namespace("http://www.w3.org/2002/07/owl#")
test = rdflib.Namespace("http://www.w3.org/2000/10/swap/test.n3#")
n3test = rdflib.Namespace("http://www.w3.org/2004/11/n3test#")
rdft = rdflib.Namespace("http://www.w3.org/2000/10/rdf-tests/rdfcore/testSchema#")
triage = rdflib.Namespace("http://www.w3.org/2000/10/swap/test/triage#")
mf = rdflib.Namespace("http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#")
qt = rdflib.Namespace("http://www.w3.org/2001/sw/DataAccess/tests/test-query#")


# class TestSWAPN3(unittest.TestCase):
#     """SWAP 2000/10/n3 tests"""

#     def setUp(self):

#     def test_foo(self):
#         """footest"""
#         self.graph.parse(os.getcwd()+'/test/swap-n3/n3-rdf.tests', format="n3")
#         tfiles = []
#         for tst in self.graph.subjects():
#             files = [str(tfile).replace('http://www.w3.org/2000/10/', 'file://'+os.getcwd()+'/test/swap-n3/')
#                         for tfile in self.graph.objects(tst, rdflib.URIRef("http://www.w3.org/2004/11/n3test#inputDocument")) if tfile.endswith('n3')]
#             tfiles += files
#         for tfile in tfiles:
#             self.graph.parse(tfile, format="n3")

from nose.exc import SkipTest

skiptests = [
    'syntax_neg_single_quote',
    'syntax_neg_literal_predicate',
    'syntax_this_quantifiers',
    'syntax_trailing_semicolon',
    'syntax_neg_thisadoc',
    'syntax_equals1',
    'syntax_equals2',
    'syntax_this_rules',
    'syntax_neg_keywords3',
    'syntax_zero_objects',
    'syntax_neg_formula_predicate',
    'syntax_zero_predicates',
    # 'syntax_qvars1',
    # 'syntax_qvars2',
    # 'contexts',
    'syntax_too_nested'
]
class Envelope(object):
    def __init__(self, n, f):
        self.name = n
        self.file = f
    def __repr__(self):
        return self.name

def generictest(e):
    """Documentation"""
    if e.skip:
        raise SkipTest("%s skipped, known issue" % e.name)
    g = rdflib.Graph()
    for i in [rdf, rdfs, xsd, owl, test, n3test, rdft, triage, mf, qt]:
        g.bind(str(i), i)
    g.parse(e.file, format="n3")

def dir_to_uri(directory, sep=os.path.sep):
    '''
    Convert a local path to a File URI.
    
    >>> dir_to_uri('c:\\\\temp\\\\foo\\\\file.txt', sep='\\\\')
    'file:///c:/temp/foo/file.txt'
    
    >>> dir_to_uri('/tmp/foo/file.txt', sep='/')
    'file:///tmp/foo/file.txt'
    '''
    items = directory.split(sep)
    path = '/'.join(items)
    if path.startswith('/'):
        path = path[1:]
    return 'file:///%s' % (path,)

def test_cases():
    from copy import deepcopy
    g = rdflib.Graph()
    swap_dir = os.path.join(os.getcwd(), 'test', 'swap-n3')
    g.parse(os.path.join(swap_dir, 'n3-rdf.tests'), format="n3")
    g.parse(os.path.join(swap_dir, 'n3-full.tests'), format="n3")
    tfiles = []
    swap_dir_uri = dir_to_uri(swap_dir) + '/'
    for tst in g.subjects():
        files = [str(tfile).replace('http://www.w3.org/2000/10/', swap_dir_uri)
                    for tfile in g.objects(tst, rdflib.URIRef("http://www.w3.org/2004/11/n3test#inputDocument")) if tfile.endswith('n3')]
        tfiles += files
    for tfile in set(tfiles):
        gname = tfile.split('/swap-n3/swap/test/')[1][:-3].translate(maketrans('-/','__'))
        e = Envelope(gname, tfile)
        if gname in skiptests:
            e.skip = True 
        else:
            e.skip = False
        # e.skip = True
        if sys.version_info[:2] == (2,4):
            import pickle
            gjt = pickle.dumps(generictest)
            gt = pickle.loads(gjt)
        else:
            gt = deepcopy(generictest)
        gt.__doc__ = tfile
        yield gt, e


if __name__ == "__main__":
    test_cases()
    # unittest.main()


"""
Interesting failure in Python 2.4 ...

======================================================================
ERROR: Failure: TypeError (function() takes at least 2 arguments (0 given))
----------------------------------------------------------------------
Traceback (most recent call last):
  File ".../python2.4/site-packages/nose/loader.py", line 231, in generate
    for test in g():
  File ".../rdflib/test/test_swap_n3.py", line 95, in test_cases
    gt = deepcopy(generictest)
  File "/usr/local/python2.4/lib/python2.4/copy.py", line 204, in deepcopy
    y = _reconstruct(x, rv, 1, memo)
  File "/usr/local/python2.4/lib/python2.4/copy.py", line 336, in _reconstruct
    y = callable(*args)
  File "...py24/lib/python2.4/copy_reg.py", line 92, in __newobj__
    return cls.__new__(cls, *args)
TypeError: function() takes at least 2 arguments (0 given)

"""
