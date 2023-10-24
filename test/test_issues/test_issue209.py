import threading

import rdflib


def make_node():
    i = 0
    while i < 9999:
        i += 1
        rdflib.term.BNode()


def test_bnode_id_gen_in_thread():
    """
    Test a random seed in a thread.
    """
    th = threading.Thread(target=make_node)
    th.daemon = True
    th.start()
    make_node()
