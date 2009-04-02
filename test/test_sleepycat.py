import logging

_logger = logging.getLogger(__name__)

from test import test_graph
from test import test_context


class SleepycatGraphTestCase(test_graph.GraphTestCase):
    store_name = "Sleepycat"
    non_core = True
    bsddb = True

class SleepycatStoreTestCase(test_context.ContextTestCase):
    store = "Sleepycat"
    non_core = True
    bsddb = True
