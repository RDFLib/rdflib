from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb import GraphDBClient
    from rdflib.contrib.graphdb.models import FreeAccessSettings


@pytest.mark.testcontainer
def test_graphdb_free_access_get_details(client: GraphDBClient):
    settings = client.security.get_free_access_details()

    assert isinstance(settings, FreeAccessSettings)
    assert isinstance(settings.enabled, bool)
    assert isinstance(settings.authorities, list)
    assert isinstance(settings.appSettings, dict)


@pytest.mark.testcontainer
def test_graphdb_free_access_update_and_restore(client: GraphDBClient):
    initial_settings = client.security.get_free_access_details()

    updated_settings = FreeAccessSettings(
        enabled=not initial_settings.enabled,
        authorities=initial_settings.authorities,
        appSettings=initial_settings.appSettings,
    )
    client.security.set_free_access_details(updated_settings)

    updated_response = client.security.get_free_access_details()
    assert updated_response.enabled == updated_settings.enabled

    client.security.set_free_access_details(initial_settings)
