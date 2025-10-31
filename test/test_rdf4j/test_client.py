from rdflib.rdf4j import RDF4JClient


def test_client_close_method(client: RDF4JClient):
    client.close()
    assert client._http_client.is_closed
