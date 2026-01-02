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


@pytest.mark.testcontainer
def test_overwrite_user_updates_admin_user(client: GraphDBClient):
    """Test that overwrite successfully updates the admin user."""
    # Get the current admin user
    original_user = client.users.get("admin")

    # Create an updated user with modified appSettings
    # Note: We must explicitly set password to "admin" because the GET response
    # returns an empty password field, and sending it back would reset the password
    updated_user = User(
        username=original_user.username,
        password="admin",  # Must set explicitly to maintain auth
        dateCreated=original_user.dateCreated,
        grantedAuthorities=original_user.grantedAuthorities,
        appSettings={"test_setting": "test_value"},
        gptThreads=original_user.gptThreads,
    )

    # Overwrite the user
    result = client.users.overwrite("admin", updated_user)
    assert result is None

    # Verify the user was updated
    fetched_user = client.users.get("admin")
    assert fetched_user.appSettings.get("test_setting") == "test_value"

    # Restore original user to clean up (with explicit password)
    restore_user = User(
        username=original_user.username,
        password="admin",  # Must set explicitly to maintain auth
        dateCreated=original_user.dateCreated,
        grantedAuthorities=original_user.grantedAuthorities,
        appSettings=original_user.appSettings,
        gptThreads=original_user.gptThreads,
    )
    client.users.overwrite("admin", restore_user)


@pytest.mark.testcontainer
def test_overwrite_user_preserves_admin_role(client: GraphDBClient):
    """Test that overwrite preserves the admin role when specified."""
    original_user = client.users.get("admin")

    # Overwrite with same authorities
    # Note: Must explicitly set password to "admin" to maintain authentication
    updated_user = User(
        username=original_user.username,
        password="admin",  # Must set explicitly to maintain auth
        dateCreated=original_user.dateCreated,
        grantedAuthorities=original_user.grantedAuthorities,
        appSettings=original_user.appSettings,
        gptThreads=original_user.gptThreads,
    )

    client.users.overwrite("admin", updated_user)

    # Verify admin role is preserved
    fetched_user = client.users.get("admin")
    assert "ROLE_ADMIN" in fetched_user.grantedAuthorities


@pytest.mark.testcontainer
def test_overwrite_user_raises_not_found_for_nonexistent_user(client: GraphDBClient):
    """Test that overwrite raises NotFoundError for a non-existent user."""
    user = User(
        username="nonexistent_user_12345",
        password="password",
        dateCreated=1736234567890,
        grantedAuthorities=["ROLE_USER"],
        appSettings={},
        gptThreads=[],
    )

    with pytest.raises(NotFoundError, match="User not found"):
        client.users.overwrite("nonexistent_user_12345", user)
