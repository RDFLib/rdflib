from rdflib import Dataset, Graph, Literal, URIRef


def main():
    # example for adding a quad
    ds = Dataset()
    g = Graph(identifier=URIRef("http://graph-a"))
    ds.add_graph(g)
    triple = (URIRef("http://subj-a"), URIRef("http://pred-a"), Literal("obj-a"))
    ds.get_context(g.identifier).add(triple)
    result = ds.serialize(format="patch", operation="add")
    print("Add Quad Patch:")
    print(result)

    # alternate example for adding a quad
    ds = Dataset()
    quad = (
        URIRef("http://subj-a"),
        URIRef("http://pred-a"),
        Literal("obj-a"),
        Graph(identifier=URIRef("http://graph-a")),
    )
    ds.add(quad)
    result = ds.serialize(format="patch", operation="add")
    print("Add Quad Patch:")
    print(result)

    # example for adding a triple
    ds = Dataset()
    ds.add(triple)
    result = ds.serialize(format="patch", operation="add")
    print("\nAdd Triple Patch:")
    print(result)

    # Example for diff quads
    quad_1 = (
        URIRef("http://subj-a"),
        URIRef("http://pred-a"),
        Literal("obj-a"),
        Graph(identifier=URIRef("http://graph-a")),
    )
    quad_2 = (
        URIRef("http://subj-b"),
        URIRef("http://pred-b"),
        Literal("obj-b"),
        Graph(identifier=URIRef("http://graph-b")),
    )
    quad_3 = (
        URIRef("http://subj-c"),
        URIRef("http://pred-c"),
        Literal("obj-c"),
        Graph(identifier=URIRef("http://graph-c")),
    )
    ds1 = Dataset()
    ds2 = Dataset()
    ds1.addN([quad_1, quad_2])
    ds2.addN([quad_2, quad_3])
    result = ds1.serialize(format="patch", target=ds2)
    print("Diff Quad Patch:")
    print(result)


if __name__ == "__main__":
    main()
