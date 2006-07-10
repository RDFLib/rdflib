import unittest, inspect
import rdflib

quick = True
verbose = False

from test.identifier_equality import *

from test.graph import *
from test.graph2_2 import *

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

from test.rdf import * # how does this manage to be 9 tests?

from test.n3 import *
from test.n3_quoting import *
from test.nt import *

from test.util import *
from test.seq import SeqTestCase

from test.store_performace import *

from test.rules import *

import test.rdfa

from test.events import *

if __name__ == "__main__":

    test.rdfa.main()

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

