import rdflib
import unittest
import threading


def makeNode():
    i = 0
    while i < 9999:
        i += 1
        rdflib.term.BNode()


class TestRandomSeedInThread(unittest.TestCase):

    def test_bnode_id_gen_in_thread(self):
        """
        """
        th = threading.Thread(target=makeNode)
        th.daemon = True
        th.start()
        makeNode()


if __name__ == "__main__":
    unittest.main()
