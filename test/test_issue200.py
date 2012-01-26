#!/usr/bin/env python

import os
import rdflib
import unittest
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

import platform
if platform.system() == 'Java':
    from nose import SkipTest
    raise SkipTest('No os.pipe() in Jython, skipping')

# Adapted from http://icodesnip.com/snippet/python/simple-universally-unique-id-uuid-or-guid
def bnode_uuid():
    """
    Generates a uuid on behalf of Python 2.4
    """
    import random, time, socket
    t = long( time.time() * 1000.0 )
    r = long( random.random()*100000000000000000L )
    try:
        a = socket.gethostbyname( socket.gethostname() )
    except:
        # if we can't get a network address, just imagine one
        a = random.random()*100000000000000000L
    data = str(t)+' '+str(r)+' '+str(a)
    data = md5(data.encode('ascii')).hexdigest()
    yield data


class TestRandomSeedInFork(unittest.TestCase):
    def test_same_bnodeid_sequence_in_fork(self):
        """Demonstrates that with os.fork(), the child process produces 
        the same sequence of BNode ids as does the parent process.
        """
        r, w = os.pipe() # these are file descriptors, not file objects
        pid = os.fork()
        if pid:
            pb1 = rdflib.term.BNode()
            os.close(w) # use os.close() to close a file descriptor
            r = os.fdopen(r) # turn r into a file object
            txt = r.read()
            os.waitpid(pid, 0) # make sure the child process gets cleaned up
        else:
            os.close(r)
            w = os.fdopen(w, 'w')
            cb = rdflib.term.BNode()
            w.write(cb)
            w.close()
            os._exit(0)
        assert txt == str(pb1), "Test now obsolete, random seed working"

    def test_random_not_reseeded_in_fork(self):
        """Demonstrates ineffectiveness of reseeding Python's random.
        """
        r, w = os.pipe() # these are file descriptors, not file objects
        pid = os.fork()
        if pid:
            pb1 = rdflib.term.BNode()
            os.close(w) # use os.close() to close a file descriptor
            r = os.fdopen(r) # turn r into a file object
            txt = r.read()
            os.waitpid(pid, 0) # make sure the child process gets cleaned up
        else:
            os.close(r)
            import random, time
            try: 
                preseed = os.urandom(16) 
            except NotImplementedError: 
                preseed = '' 
            # Have doubts about this. random.seed will just hash the string 
            random.seed('%s%s%s' % (preseed, os.getpid(), time.time())) 
            del preseed 
            w = os.fdopen(w, 'w')
            cb = rdflib.term.BNode()
            w.write(cb)
            w.close()
            os._exit(0)
        assert txt == str(pb1), "Reseeding worked, this test is obsolete"

    def test_bnode_uuid_differs_in_fork(self):
        """Demonstrates that with os.fork(), the child process produces 
        a sequence of BNode ids that differs from the sequence produced
        by the parent process.
        """
        r, w = os.pipe() # these are file descriptors, not file objects
        pid = os.fork()
        if pid:
            pb1 = rdflib.term.BNode(_sn_gen=bnode_uuid(), _prefix="")
            os.close(w) # use os.close() to close a file descriptor
            r = os.fdopen(r) # turn r into a file object
            txt = r.read()
            os.waitpid(pid, 0) # make sure the child process gets cleaned up
        else:
            os.close(r)
            w = os.fdopen(w, 'w')
            cb = rdflib.term.BNode(_sn_gen=bnode_uuid(), _prefix="")
            w.write(cb)
            w.close()
            os._exit(0)
        assert txt != str(pb1), "Parent process BNode id: " + \
                                "%s, child process BNode id: %s" % (
                                    txt, str(pb1))


if __name__ == "__main__":
    unittest.main()
