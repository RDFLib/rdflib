from rdflib.plugins.shared.jsonld.util import norm_url


def test_norm_urn():
    assert norm_url("urn:ns:test", "/one") == "urn:ns:test/one"
    assert norm_url("urn:ns:test/path/", "two") == "urn:ns:test/path/two"
    assert norm_url("urn:ns:test/path", "two") == "urn:ns:test/two"
    assert norm_url("urn:ns:test", "three") == "urn:ns:test/three"
    assert norm_url("urn:ns:test/path#", "four") == "urn:ns:test/four"
    assert norm_url("urn:ns:test/path1/path2/", "../path3") == "urn:ns:test/path1/path3"
    assert norm_url("urn:ns:test/path1/path2/", "/path3") == "urn:ns:test/path3"
    assert (
        norm_url("urn:ns:test/path1/path2/", "http://example.com")
        == "http://example.com"
    )
    assert (
        norm_url("urn:ns:test/path1/path2/", "urn:another:test/path")
        == "urn:another:test/path"
    )
    assert norm_url("urn:ns:test/path", "#four") == "urn:ns:test/path#four"
    assert norm_url("urn:ns:test/path/", "#four") == "urn:ns:test/path/#four"
