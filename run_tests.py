import unittest

from test.identifier_equality import *
from test.triple_store import *
from test.type_check import *
from test.graph import *

try:
    import persistent
    from test.zodb import *
except ImportError:
    pass

#from test.rdf import *
#from test.parser import *

if __name__ == "__main__":
    unittest.main()   
