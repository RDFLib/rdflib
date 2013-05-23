
"""

Iteration and update conflict with set based IOMemory store

https://github.com/RDFLib/rdflib/issues/286

"""

from rdflib.store import Store
from rdflib import plugin

from rdflib import Graph, Literal, Namespace

def test_concurrent1(): 
    dns = Namespace(u"http://www.example.com/")

    store = plugin.get("IOMemory", Store)()
    g1 = Graph(store=store)

    g1.add((dns.Name, dns.prop, Literal(u"test")))
    g1.add((dns.Name, dns.prop, Literal(u"test2")))
    g1.add((dns.Name, dns.prop, Literal(u"test3")))

    n = len(g1)
    i = 0

    for t in g1.triples((None, None, None)):
        i+=1
        # next line causes problems because it adds a new Subject that needs
        # to be indexed  in __subjectIndex dictionary in IOMemory Store.
        # which invalidates the iterator used to iterate over g1
        g1.add(t)

    assert i == n

def test_concurrent2(): 
    dns = Namespace(u"http://www.example.com/")

    store = plugin.get("IOMemory", Store)()
    g1 = Graph(store=store)
    g2 = Graph(store=store)

    g1.add((dns.Name, dns.prop, Literal(u"test")))
    g1.add((dns.Name, dns.prop, Literal(u"test2")))
    g1.add((dns.Name, dns.prop, Literal(u"test3")))

    n = len(g1)
    i = 0

    for t in g1.triples((None, None, None)):
        i+=1
        g2.add(t)
        # next line causes problems because it adds a new Subject that needs
        # to be indexed  in __subjectIndex dictionary in IOMemory Store.
        # which invalidates the iterator used to iterate over g1
        g2.add((dns.Name1, dns.prop1, Literal(u"test")))
        g2.add((dns.Name1, dns.prop, Literal(u"test")))
        g2.add((dns.Name, dns.prop, Literal(u"test4")))

    assert i == n

if __name__ == '__main__':
    test_concurrent1()
    test_concurrent2()
