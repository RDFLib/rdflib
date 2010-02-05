import unittest
import doctest

data = """
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix : <tag:example.org,2007;stuff/> .

:a foaf:knows :b .
:a foaf:knows :c .
:a foaf:knows :d .

:b foaf:knows :a .
:b foaf:knows :c .

:c foaf:knows :a .

"""

query = """
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

select distinct ?person
where {
    ?person foaf:knows ?a .
    ?person foaf:knows ?b .
   filter (?a != ?b) .
}
"""

#g = CG()
from StringIO import StringIO
#g.parse(StringIO(data), format='n3')
#print g.query(q).serialize('json')

from test import test_sparql

def test_leaves():
    return doctest.DocFileSuite("../test/test_sparql/leaves.txt",
                                package="rdflib",
                                optionflags = doctest.ELLIPSIS,
                                globs=locals())


if __name__ == "__main__":
    doctest.testfile("leaves.txt", globs=globals(),
                     optionflags = doctest.ELLIPSIS)
