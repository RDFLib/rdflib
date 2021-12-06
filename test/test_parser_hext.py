import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.absolute()))
from rdflib import Dataset


def test_small_string():
    s = """
        ["http://example.com/s01", "http://example.com/a", "http://example.com/Type1", "", "", ""]
        ["http://example.com/s01", "http://example.com/label", "This is a Label", "http://www.w3.org/2001/XMLSchema#string", "en", ""]
        ["http://example.com/s01", "http://example.com/comment", "This is a comment", "http://www.w3.org/2001/XMLSchema#string", "", ""]
        ["http://example.com/s01", "http://example.com/creationDate", "2021-12-01", "http://www.w3.org/2001/XMLSchema#date", "", ""]
        ["http://example.com/s01", "http://example.com/creationTime", "2021-12-01T12:13:00", "http://www.w3.org/2001/XMLSchema#dateTime", "", ""]
        ["http://example.com/s01", "http://example.com/age", 42, "http://www.w3.org/2001/XMLSchema#integer", "", ""]
        ["http://example.com/s01", "http://example.com/trueFalse", false, "http://www.w3.org/2001/XMLSchema#boolean", "", ""]
        ["http://example.com/s01", "http://example.com/op1", "http://example.com/o1", "", "", ""]
        ["http://example.com/s01", "http://example.com/op1", "http://example.com/o2", "", "", ""]
        ["http://example.com/s01", "http://example.com/op2", "http://example.com/o3", "", "", ""]
        """
    d = Dataset().parse(data=s, format="hext")
    assert len(d) == 10


def test_small_file():
    d = Dataset().parse(Path(__file__).parent / "test_parser_hext_01.ndjson", format="hext")
    assert len(d) == 10


if __name__ == "__main__":
    test_small_string()
    test_small_file()
