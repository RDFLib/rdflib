from rdflib import URIRef, Literal,  Graph, Dataset

def trig_export_test():
    graphs = [(URIRef("urn:tg1"),"A"), (URIRef("urn:tg2"), "B")]
    ds = Dataset()
    for i, n in graphs:
        g = ds.graph(i)
        a = URIRef("urn:{}#S".format(n))
        b = URIRef("urn:{}#p".format(n))
        c = Literal('c')
        g.add((a,b,c))


    # this generated two graphs, with a differnet namespace for the URIs inside.
    # this tests that the prefix for each internal ns is different

    data = ds.serialize(format='trig')
    print data
    assert False


if __name__ == '__main__':
    trig_export_test()
