import rdflib
graph_data = "data.ttl"
shape_data = "Shape.ttl"



def test_981():
    data = rdflib.Graph().parse(location=graph_data)
    shape = rdflib.Graph().parse(location=shape_data)
    assert data!=None
    assert shape!=None
if __name__ == "__main__":
    test_981()
