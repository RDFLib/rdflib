from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    from testcontainers.core.container import DockerContainer

    from rdflib.contrib.graphdb import GraphDBClient
    from rdflib.contrib.graphdb.models import AuthenticatedUser


@pytest.mark.testcontainer
def test_login_returns_authenticated_user(client: GraphDBClient):
    """Test that login() returns an AuthenticatedUser with a valid GDB token."""
    result = client.login("admin", "admin")

    assert isinstance(result, AuthenticatedUser)
    assert result.username == "admin"
    assert result.authorities is not None
    assert "ROLE_ADMIN" in result.authorities
    assert result.token.startswith("GDB ")
    assert "." in result.token  # Token has format: GDB base64.signature


@pytest.mark.testcontainer
def test_gdb_token_can_authenticate_requests(graphdb_container: DockerContainer):
    """Test that a GDB token can be used to authenticate requests with security enabled."""
    port = graphdb_container.get_exposed_port(7200)
    base_url = f"http://localhost:{port}/"

    with GraphDBClient(base_url, auth=("admin", "admin")) as admin_client:
        admin_client.security.enabled = True

        try:
            authenticated_user = admin_client.login("admin", "admin")

            with GraphDBClient(base_url, auth=authenticated_user.token) as token_client:
                security_status = token_client.security.enabled
                assert security_status is True

                repos = token_client.repositories.list()
                assert isinstance(repos, list)
        finally:
            admin_client.security.enabled = False
