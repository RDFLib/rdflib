import os

import pytest

import rdflib


@pytest.mark.skipif(
    condition=(os.name == "nt"),
    reason="No os.fork() and/or os.pipe() on this platform, skipping",
)
def test_bnode_id_differs_in_fork():
    """Checks that os.fork()ed child processes produce a
    different sequence of BNode ids from the parent process.
    """
    r, w = os.pipe()  # these are file descriptors, not file objects
    pid = os.fork()
    if pid:
        pb1 = rdflib.term.BNode()
        os.close(w)  # use os.close() to close a file descriptor
        r = os.fdopen(r)  # turn r into a file object
        txt = r.read()
        os.waitpid(pid, 0)  # make sure the child process gets cleaned up
        r.close()
    else:
        os.close(r)
        w = os.fdopen(w, "w")
        cb = rdflib.term.BNode()
        w.write(cb)
        w.close()
        os._exit(0)
    assert txt != str(
        pb1
    ), "Parent process BNode id: " + "%s, child process BNode id: %s" % (
        txt,
        str(pb1),
    )
