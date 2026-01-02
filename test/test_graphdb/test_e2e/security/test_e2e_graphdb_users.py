from __future__ import annotations

import pytest

from rdflib.contrib.graphdb.exceptions import NotFoundError
from rdflib.contrib.graphdb.models import User
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb import GraphDBClient


@pytest.mark.testcontainer
def test_get_users_returns_list(client: GraphDBClient):
    """Test that get_users returns a list of users."""
    users = client.users.list()
    assert isinstance(users, list)


@pytest.mark.testcontainer
def test_get_users_contains_admin_user(client: GraphDBClient):
    """Test that get_users includes the default admin user."""
    users = client.users.list()

    # GraphDB always has an admin user by default
    usernames = [user.username for user in users]
    assert "admin" in usernames


@pytest.mark.testcontainer
def test_get_users_returns_user_objects(client: GraphDBClient):
    """Test that get_users returns User dataclass instances."""
    users = client.users.list()

    assert len(users) > 0
    for user in users:
        assert isinstance(user, User)


@pytest.mark.testcontainer
def test_get_users_user_has_required_fields(client: GraphDBClient):
    """Test that returned User objects have all required fields populated."""
    users = client.users.list()

    assert len(users) > 0
    for user in users:
        # Required fields
        assert isinstance(user.username, str)
        assert isinstance(user.password, str)
        assert isinstance(user.dateCreated, int)

        # Optional fields should be normalized to collections
        assert isinstance(user.grantedAuthorities, list)
        assert isinstance(user.appSettings, dict)
        assert isinstance(user.gptThreads, list)


@pytest.mark.testcontainer
def test_get_users_admin_has_admin_role(client: GraphDBClient):
    """Test that the admin user has the ROLE_ADMIN authority."""
    users = client.users.list()

    admin_user = next((u for u in users if u.username == "admin"), None)
    assert admin_user is not None
    assert "ROLE_ADMIN" in admin_user.grantedAuthorities


@pytest.mark.testcontainer
def test_get_user_returns_admin_user(client: GraphDBClient):
    """Test that get returns the admin user."""
    user = client.users.get("admin")
    assert user.username == "admin"


@pytest.mark.testcontainer
def test_get_user_returns_user_object(client: GraphDBClient):
    """Test that get returns a User dataclass instance."""
    user = client.users.get("admin")
    assert isinstance(user, User)


@pytest.mark.testcontainer
def test_get_user_has_required_fields(client: GraphDBClient):
    """Test that the returned User object has all required fields populated."""
    user = client.users.get("admin")

    # Required fields
    assert isinstance(user.username, str)
    assert isinstance(user.password, str)
    assert isinstance(user.dateCreated, int)

    # Optional fields should be normalized to collections
    assert isinstance(user.grantedAuthorities, list)
    assert isinstance(user.appSettings, dict)
    assert isinstance(user.gptThreads, list)


@pytest.mark.testcontainer
def test_get_user_admin_has_admin_role(client: GraphDBClient):
    """Test that the admin user has the ROLE_ADMIN authority."""
    user = client.users.get("admin")
    assert "ROLE_ADMIN" in user.grantedAuthorities


@pytest.mark.testcontainer
def test_get_user_raises_not_found_for_nonexistent_user(client: GraphDBClient):
    """Test that get raises NotFoundError for a non-existent user."""
    with pytest.raises(NotFoundError, match="User not found"):
        client.users.get("nonexistent_user_12345")
