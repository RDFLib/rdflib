from rdflib import Dataset


def main():
    # RDF patch data
    add_patch = """
    TX .
    A _:bn1 <http://example.org/predicate1> "object1" .
    A _:bn1 <http://example.org/predicate2> "object2" .
    TC .
    """

    delete_patch = """
    TX .
    D _:bn1 <http://example.org/predicate1> "object1" .
    TC .
    """

    ds = Dataset()

    # Apply add patch
    ds.parse(data=add_patch, format="patch")
    print("After add patch:")
    for triple in ds:
        print(triple)

    # Apply delete patch
    ds.parse(data=delete_patch, format="patch")
    print("After delete patch:")
    for triple in ds:
        print(triple)


if __name__ == "__main__":
    main()
