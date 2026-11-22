from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb import GraphDBClient


@pytest.mark.testcontainer
def test_graphdb_security_get_status(client: GraphDBClient):
    """Test getting the current security status."""
    status = client.security.enabled
    assert isinstance(status, bool)


@pytest.mark.testcontainer
def test_graphdb_security_enable(client: GraphDBClient):
    """Test enabling security."""
    # Get initial state
    initial_state = client.security.enabled

    # Enable security
    client.security.enabled = True
    assert client.security.enabled is True

    # Restore initial state
    client.security.enabled = initial_state


@pytest.mark.testcontainer
def test_graphdb_security_disable(client: GraphDBClient):
    """Test disabling security."""
    # Get initial state
    initial_state = client.security.enabled

    # Disable security
    client.security.enabled = False
    assert client.security.enabled is False

    # Restore initial state
    client.security.enabled = initial_state


@pytest.mark.testcontainer
def test_graphdb_security_toggle(client: GraphDBClient):
    """Test toggling security on and off."""
    # Get initial state
    initial_state = client.security.enabled

    # Toggle to opposite state
    client.security.enabled = not initial_state
    assert client.security.enabled == (not initial_state)

    # Toggle back to initial state
    client.security.enabled = initial_state
    assert client.security.enabled == initial_state


@pytest.mark.testcontainer
def test_graphdb_security_invalid_value(client: GraphDBClient):
    """Test that setting security with invalid value raises TypeError."""
    with pytest.raises(TypeError, match="Value must be a boolean"):
        client.security.enabled = "true"  # type: ignore

    with pytest.raises(TypeError, match="Value must be a boolean"):
        client.security.enabled = 1  # type: ignore
