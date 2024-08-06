from rdflib import Dataset, Literal, URIRef

# Example for adding a quad
ds = Dataset()
ds.add(
    (
        URIRef("http://subj-a"),
        URIRef("http://pred-a"),
        Literal("obj-a"),
        URIRef("http://graph-a"),
    )
)
result = ds.serialize(format="patch", operation="add")
print("Add Quad Patch:")
print(result)

# Example for removing a triple
ds = Dataset()
ds.add(
    (
        URIRef("http://subj-a"),
        URIRef("http://pred-a"),
        Literal("obj-a"),
    )
)
result = ds.serialize(format="patch", operation="remove")
print("Delete Triple Patch:")
print(result)

# Example for diff quads
quad_1 = (
    URIRef("http://subj-a"),
    URIRef("http://pred-a"),
    Literal("obj-a"),
    URIRef("http://graph-a"),
)
quad_2 = (
    URIRef("http://subj-b"),
    URIRef("http://pred-b"),
    Literal("obj-b"),
    URIRef("http://graph-b"),
)
quad_3 = (
    URIRef("http://subj-c"),
    URIRef("http://pred-c"),
    Literal("obj-c"),
    URIRef("http://graph-c"),
)
ds1 = Dataset()
ds2 = Dataset()
ds1.addN([quad_1, quad_2])
ds2.addN([quad_2, quad_3])
result = ds1.serialize(format="patch", target=ds2)
print("Diff Quad Patch:")
print(result)
