import logging

_logger = logging.getLogger(__name__)

from test.graph import GraphTestCase

try:
    from rdflib.store.Sleepycat import Sleepycat
    class SleepycatGraphTestCase(GraphTestCase):
        store_name = "Sleepycat"
except ImportError, e:
    _logger.warning("Can not test Sleepycat store: %s" % e)


from test.context import ContextTestCase

try:
    from rdflib.store.Sleepycat import Sleepycat
    class SleepycatStoreTestCase(ContextTestCase):
        store = "Sleepycat"
except ImportError, e:
    _logger.warning("Can not test Sleepycat store: %s" % e)


#class Sleepycat(PychinkoTestCase):
#    backend = 'Sleepycat'

