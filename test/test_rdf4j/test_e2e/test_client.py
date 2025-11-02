import pytest

from rdflib.contrib.rdf4j import RDF4JClient
from rdflib.contrib.rdf4j.exceptions import RDF4JUnsupportedProtocolError


@pytest.mark.testcontainer
def test_client_close_method(client: RDF4JClient):
    client.close()
    assert client._http_client.is_closed


@pytest.mark.testcontainer
def test_client_protocol(client: RDF4JClient):
    assert client.protocol >= 12


@pytest.mark.testcontainer
def test_client_protocol_error(monkeypatch):
    monkeypatch.setattr(RDF4JClient, "protocol", 11)
    with pytest.raises(RDF4JUnsupportedProtocolError):
        RDF4JClient("http://example.com/")
