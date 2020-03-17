import unittest

from rdflib.graph import BatchAddGraph


class TestBatchAddGraph(unittest.TestCase):
    def test_add_less_than_batchsize(self):
        pass

    def test_add_more_than_batchsize(self):
        pass

    def test_negative_batchsize_denied(self):
        pass

    def test_zero_batchsize_denied(self):
        pass

    def test_one_batchsize_denied(self):
        pass

    def test_add_quad_for_non_conjunctive_fail(self):
        pass

    def test_add_quad_for_non_conjunctive_pass_on_context_matches(self):
        pass

    def test_no_addN_on_exception(self):
        '''
        Even if we've added triples so far, it may be that attempting to add the last
        batch is the cause of our exception, so we don't want to attempt again
        '''

    def test_batch_has_graph_added_to_triples(self):
        pass

    def test_batch_does_not_add_graph_to_quads(self):
        pass
