import unittest

from test.identifier_equality import *
from test.triple_store import *
from test.type_check import *
from test.graph import *

# you must export your PYTHONPATH to point to a Z3 installation to get this to work!, like:
# export PYTHONPATH="export PYTHONPATH="/home/michel/dev/Zope3Trunk/src"
try:
    import persistent
    from test.zodb import *
except ImportError:
    pass

#from test.rdf import *
#from test.parser import *

if __name__ == "__main__":
    unittest.main()   
