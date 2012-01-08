import logging

_logger = logging.getLogger(__name__)

from test import test_graph
from test import test_context
from nose import SkipTest
import sys


class SleepycatGraphTestCase(test_graph.GraphTestCase):
    store_name = "Sleepycat"
    non_core = True
    bsddb = True

class SleepycatStoreTestCase(test_context.ContextTestCase):
    store = "Sleepycat"
    non_core = True
    bsddb = True

if sys.version_info >= (3,):
    try:
        import bsddb3
    except ImportError:
        raise SkipTest('bsddb3 not installed')
else:
    try:
        import bsddb
    except ImportError:
        raise SkipTest('bsddb not installed')
