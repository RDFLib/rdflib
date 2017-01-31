# -*- coding: utf-8 -*-
import re
import sys
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

try:
    from uuid import uuid4
except ImportError:
    def uuid4():
        """
        Generates a uuid on behalf of Python 2.4
        """
        import random
        import os
        import time
        import socket
        try:
            preseed = os.urandom(16)
        except NotImplementedError:
            preseed = ''
        # Have doubts about this. random.seed will just hash the string
        random.seed('%s%s%s' % (preseed, os.getpid(), time.time()))
        del preseed
        t = int( time.time() * 1000.0 )
        r = int( random.random()*100000000000000000 )
        try:
            a = socket.gethostbyname( socket.gethostname() )
        except:
            # if we can't get a network address, just imagine one
            a = random.random()*100000000000000000
        strdata = str(t)+' '+str(r)+' '+str(a)
        data = md5(strdata.encode('ascii')).hexdigest()
        yield data

# Adapted from http://icodesnip.com/snippet/python/simple-universally-unique-id-uuid-or-guid
def bnode_uuid():
    yield uuid4()


def is_ncname(value):
    """
    BNode identifiers must be valid NCNames.

    From the `W3C RDF Syntax doc <http://www.w3.org/TR/REC-rdf-syntax/#section-blank-nodeid-event>`_

    "The value is a function of the value of the ``identifier`` accessor.
    The string value begins with "_:" and the entire value MUST match
    the `N-Triples nodeID <http://www.w3.org/TR/2004/REC-rdf-testcases-20040210/#nodeID>`_ production".

    The nodeID production is specified to be a `name <http://www.w3.org/TR/2004/REC-rdf-testcases-20040210/#name>`_

        name    ::= [A-Za-z][A-Za-z0-9]*

    >>> assert is_ncname('') == False
    >>> assert is_ncname('999') == False
    >>> assert is_ncname('x') == True
    >>> assert is_ncname(u'x') == True
    >>> assert is_ncname(u'Michèle') == True

    However, vanilla uuid4s are not necessarily NCNames:

    >>> assert is_ncname('6fa459ea-ee8a-3ca4-894e-db77e160355e') == False

    So this has to be finessed with an appropriate prefix ...

    >>> assert is_ncname("urn:uuid:"+str(uuid4())) == True
    >>> from rdflib import BNode
    >>> assert is_ncname(BNode(_sn_gen=bnode_uuid, _prefix="urn:uuid:")) == True
    """
    ncnameexp = re.compile('[A-Za-z][A-Za-z0-9]*')
    if ncnameexp.match(value):
        return True
    else:
        return False

if __name__ == '__main__':
    import doctest
    doctest.testmod()
