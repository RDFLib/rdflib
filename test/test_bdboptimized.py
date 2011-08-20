import logging

_logger = logging.getLogger(__name__)

from test import test_graph
from test import test_context


class BDBOptimizedGraphTestCase(test_graph.GraphTestCase):
    store_name = "BDBOptimized"
    non_core = True
    bsddb = True

class BDBOptimizedStoreTestCase(test_context.ContextTestCase):
    store = "BDBOptimized"
    non_core = True
    bsddb = True
