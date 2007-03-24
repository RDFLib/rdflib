#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
This test runner uses Nose for test discovery and running. It uses the argument
spec of Nose, but with some options pre-set.

See <http://code.google.com/p/python-nose/> for details.

If ``coverage.py`` is placed in $PYTHONPATH, it can be used to create coverage
information (using the built-in coverage plugin of Nose) if the default
option "--with-coverage" is supplied (which also enables some additional
coverage options).

See <http://nedbatchelder.com/code/modules/coverage.html> for details.

Note that this runner is just a convenience script. You can use ``nosetests``
directly if it's on $PATH, with the difference that you have to supply the
options pre-set here manually.
"""


NOSE_ARGS = [
        '--where=./',
        '--with-doctest',
        '--doctest-extension=.doctest',
        '--doctest-tests',
    ]

COVERAGE_EXTRA_ARGS = [
        '--cover-package=rdflib',
        '--cover-inclusive',
    ]

DEFAULT_ATTRS = ['!slowtest', '!unstable', '!non_standard_dep']

DEFAULT_DIRS = ['test', 'rdflib']


if __name__ == '__main__':

    from sys import argv, exit, stderr
    try: import nose
    except ImportError:
        print >>stderr, """\
    Requires Nose. Try:

        $ sudo easy_install nose

    Exiting. """; exit(1)


    if '--with-coverage' in argv:
        try: import coverage
        except ImportError:
            print >>stderr, "No coverage module found, skipping code coverage."
            argv.remove('--with-coverage')
        else:
            NOSE_ARGS += COVERAGE_EXTRA_ARGS


    if True not in [a.startswith('-a') or a.startswith('--attr=') for a in argv]:
        argv.append('--attr=' + ','.join(DEFAULT_ATTRS))

    if not [a for a in argv[1:] if not a.startswith('-')]:
        argv += DEFAULT_DIRS # since nose doesn't look here by default..


    finalArgs = argv + NOSE_ARGS
    print "Running nose with:", " ".join(finalArgs[1:])
    nose.run(argv=finalArgs)


# TODO: anything from the following we've left behind?
old_run_tests = """
import logging

_logger = logging.getLogger()
_logger.setLevel(logging.ERROR)
_formatter = logging.Formatter('%(name)s %(levelname)s %(message)s')
_handler = logging.StreamHandler()
_handler.setFormatter(_formatter)
_logger.addHandler(_handler)

import unittest, inspect
import rdflib

quick = True
verbose = True

from test.IdentifierEquality import IdentifierEquality
from test.sparql.QueryTestCase import QueryTestCase

from test.graph import *

from test.triple_store import *
from test.context import *

# # Graph no longer has the type checking at the moment. Do we want to
# # put it back? Should we?
# #
# # from test.type_check import *

from test.parser import *

if not quick:
    from test import parser_rdfcore
    if verbose:
        parser_rdfcore.verbose = 1
    from test.parser_rdfcore import *

    from test.Sleepycat import *

from test.rdf import * # how does this manage to be 9 tests?

from test.n3 import *
from test.n3_quoting import *
from test.nt import *

from test.util import *
from test.seq import SeqTestCase

#from test.store_performace import *

from test.rules import *

from test.n3Test import *

from test.JSON import JSON

import test.rdfa

from test.events import *

def run():
    # TODO: Fix failed test and comment back in.
    # test.rdfa.main()

    if verbose:
        ts = unittest.makeSuite
        tests = [
            c for c in vars().values()
            if inspect.isclass(c)
                and not isinstance(c, rdflib.Namespace)
                and issubclass(c, unittest.TestCase)
        ]
        suite = unittest.TestSuite(map(ts, tests))
        unittest.TextTestRunner(verbosity=2).run(suite)
    else:
        unittest.main()

"""
