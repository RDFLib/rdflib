import unittest

#quick = False
quick = True

from test.identifier_equality import *

from test.store import *

from test.graph import *
from test.triple_store import *
from test.context import *

# # Graph no longer has the type checking at the moment. Do we want to
# # put it back? Should we?
# #
# # from test.type_check import * 

from test.parser import *
if not quick:
    from test.parser_rdfcore import *

from test.rdf import * # how does this manage to be 9 tests?

from test.n3 import *
from test.nt import *

from test.util import *
from test.seq import SeqTestCase

if not quick:
    from test.store_performace import *

from test.rules import *


if __name__ == "__main__":
    unittest.main()   
