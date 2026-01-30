from __future__ import annotations

import pytest

from rdflib.contrib.graphdb.exceptions import BadRequestError, NotFoundError
from rdflib.contrib.graphdb.models import User, UserCreate, UserUpdate
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


@pytest.mark.testcontainer
def test_create_user_creates_new_user(client: GraphDBClient):
    """Test that create successfully creates a new user."""
    username = "test_create_user_12345"
    user = UserCreate(
        username=username,
        password="password123",
        grantedAuthorities=["ROLE_USER"],
        appSettings={},
        gptThreads=[],
    )

    try:
        # Create the user
        result = client.users.create(username, user)
        assert result is None

        # Verify the user was created
        fetched_user = client.users.get(username)
        assert fetched_user.username == username
    finally:
        # Clean up: delete the user
        try:
            # Use overwrite with empty authorities, then delete via the management API
            # Note: GraphDB doesn't have a delete user endpoint in the standard REST API,
            # but the user will be orphaned if not cleaned up. In a real scenario,
            # we'd need admin-level cleanup. For now, we leave it.
            pass
        except Exception:
            pass


@pytest.mark.testcontainer
def test_create_user_returns_user_with_correct_fields(client: GraphDBClient):
    """Test that a created user has the correct fields when retrieved."""
    username = "test_create_fields_12345"
    user = UserCreate(
        username=username,
        password="securepassword",
        grantedAuthorities=["ROLE_USER", "READ_REPO_test-repo"],
        appSettings={"theme": "dark"},
        gptThreads=[],
    )

    try:
        client.users.create(username, user)

        fetched_user = client.users.get(username)

        assert fetched_user.username == username
        assert isinstance(fetched_user.password, str)  # Password is hashed/empty
        assert isinstance(fetched_user.dateCreated, int)
        assert "ROLE_USER" in fetched_user.grantedAuthorities
        assert "READ_REPO_test-repo" in fetched_user.grantedAuthorities
        assert fetched_user.appSettings.get("theme") == "dark"
    finally:
        pass


@pytest.mark.testcontainer
def test_create_user_appears_in_users_list(client: GraphDBClient):
    """Test that a created user appears in the users list."""
    username = "test_create_list_12345"
    user = UserCreate(
        username=username,
        password="password123",
        grantedAuthorities=["ROLE_USER"],
        appSettings={},
        gptThreads=[],
    )

    try:
        client.users.create(username, user)

        users = client.users.list()
        usernames = [u.username for u in users]

        assert username in usernames
    finally:
        pass


@pytest.mark.testcontainer
def test_create_user_raises_bad_request_for_duplicate_user(client: GraphDBClient):
    """Test that create raises BadRequestError when creating a duplicate user."""
    username = "test_create_dup_12345"
    user = UserCreate(
        username=username,
        password="password123",
        grantedAuthorities=["ROLE_USER"],
        appSettings={},
        gptThreads=[],
    )

    try:
        # Create the user first time
        client.users.create(username, user)

        # Try to create the same user again - should fail
        with pytest.raises(BadRequestError):
            client.users.create(username, user)
    finally:
        # Clean up: delete the user
        try:
            client.users.delete(username)
        except Exception:
            pass


@pytest.mark.testcontainer
def test_delete_user_deletes_existing_user(client: GraphDBClient):
    """Test that delete successfully deletes a user."""
    username = "test_delete_user_12345"
    user = UserCreate(
        username=username,
        password="password123",
        grantedAuthorities=["ROLE_USER"],
        appSettings={},
        gptThreads=[],
    )

    # Create the user first
    client.users.create(username, user)

    # Delete the user
    result = client.users.delete(username)
    assert result is None

    # Verify the user was deleted
    with pytest.raises(NotFoundError, match="User not found"):
        client.users.get(username)


@pytest.mark.testcontainer
def test_delete_user_removes_from_users_list(client: GraphDBClient):
    """Test that a deleted user no longer appears in the users list."""
    username = "test_delete_list_12345"
    user = UserCreate(
        username=username,
        password="password123",
        grantedAuthorities=["ROLE_USER"],
        appSettings={},
        gptThreads=[],
    )

    # Create the user first
    client.users.create(username, user)

    # Verify user exists in list
    users = client.users.list()
    usernames = [u.username for u in users]
    assert username in usernames

    # Delete the user
    client.users.delete(username)

    # Verify user no longer in list
    users = client.users.list()
    usernames = [u.username for u in users]
    assert username not in usernames


@pytest.mark.testcontainer
def test_delete_user_raises_not_found_for_nonexistent_user(client: GraphDBClient):
    """Test that delete raises NotFoundError for a non-existent user."""
    with pytest.raises(NotFoundError, match="User not found"):
        client.users.delete("nonexistent_user_12345")


@pytest.mark.testcontainer
def test_update_user_updates_app_settings(client: GraphDBClient):
    """Test that update successfully updates a user's appSettings via PATCH."""
    username = "test_update_user_12345"
    user = UserCreate(
        username=username,
        password="password123",
        grantedAuthorities=["ROLE_USER"],
        appSettings={"initial_setting": "initial_value"},
        gptThreads=[],
    )

    try:
        # Create the user first
        client.users.create(username, user)

        # Update only the appSettings using PATCH with a dict
        user_dict = {"appSettings": {"updated_setting": "updated_value"}}
        result = client.users.update(username, user_dict)
        assert result is None

        # Verify the user was updated
        fetched_user = client.users.get(username)
        assert fetched_user.appSettings.get("updated_setting") == "updated_value"
    finally:
        # Clean up
        try:
            client.users.delete(username)
        except Exception:
            pass


@pytest.mark.testcontainer
def test_update_user_preserves_existing_fields(client: GraphDBClient):
    """Test that update via PATCH preserves fields not included in the update."""
    username = "test_update_preserve_12345"
    user = UserCreate(
        username=username,
        password="password123",
        grantedAuthorities=["ROLE_USER", "READ_REPO_test-repo"],
        appSettings={"existing_setting": "existing_value"},
        gptThreads=[],
    )

    try:
        # Create the user first
        client.users.create(username, user)

        # Update only the appSettings using PATCH with a dict
        # Note: PATCH only affects certain properties like appSettings
        user_dict = {"appSettings": {"theme": "dark"}}
        client.users.update(username, user_dict)

        # Verify the role is preserved (authorities are not affected by PATCH)
        fetched_user = client.users.get(username)
        assert "ROLE_USER" in fetched_user.grantedAuthorities
        assert "READ_REPO_test-repo" in fetched_user.grantedAuthorities
    finally:
        # Clean up
        try:
            client.users.delete(username)
        except Exception:
            pass


@pytest.mark.testcontainer
def test_update_user_returns_none(client: GraphDBClient):
    """Test that update returns None on success."""
    username = "test_update_none_12345"
    user = UserCreate(
        username=username,
        password="password123",
        grantedAuthorities=["ROLE_USER"],
        appSettings={},
        gptThreads=[],
    )

    try:
        # Create the user first
        client.users.create(username, user)

        # Update the user with a dict
        user_dict = {"appSettings": {"key": "value"}}
        result = client.users.update(username, user_dict)

        assert result is None
    finally:
        # Clean up
        try:
            client.users.delete(username)
        except Exception:
            pass


@pytest.mark.testcontainer
def test_update_user_with_user_update_model(client: GraphDBClient):
    """Test that update works with UserUpdate model."""
    username = "test_update_model_12345"
    user = UserCreate(
        username=username,
        password="password123",
        grantedAuthorities=["ROLE_USER"],
        appSettings={},
        gptThreads=[],
    )

    try:
        # Create the user first
        client.users.create(username, user)

        # Update the user with a UserUpdate model
        user_update = UserUpdate(appSettings={"model_setting": "model_value"})
        result = client.users.update(username, user_update)

        assert result is None

        # Verify the user was updated
        fetched_user = client.users.get(username)
        assert fetched_user.appSettings.get("model_setting") == "model_value"
    finally:
        # Clean up
        try:
            client.users.delete(username)
        except Exception:
            pass


@pytest.mark.testcontainer
def test_custom_roles_returns_list(client: GraphDBClient):
    """Test that custom_roles returns a list for an existing user."""
    roles = client.users.custom_roles("admin")
    assert isinstance(roles, list)


@pytest.mark.testcontainer
def test_custom_roles_returns_empty_list_for_user_without_custom_roles(
    client: GraphDBClient,
):
    """Test that custom_roles returns an empty list for a user without custom roles."""
    # The admin user typically doesn't have custom roles by default
    roles = client.users.custom_roles("admin")
    # By default, the admin user has no custom roles
    assert roles == []


@pytest.mark.testcontainer
def test_custom_roles_raises_not_found_for_nonexistent_user(client: GraphDBClient):
    """Test that custom_roles raises NotFoundError for a non-existent user."""
    with pytest.raises(NotFoundError, match="User not found"):
        client.users.custom_roles("nonexistent_user_12345")


@pytest.mark.testcontainer
def test_custom_roles_for_created_user(client: GraphDBClient):
    """Test that custom_roles works for a newly created user."""
    username = "test_custom_roles_12345"
    user = UserCreate(
        username=username,
        password="password123",
        grantedAuthorities=["ROLE_USER"],
        appSettings={},
        gptThreads=[],
    )

    try:
        # Create the user
        client.users.create(username, user)

        # Get custom roles for the user
        roles = client.users.custom_roles(username)

        assert isinstance(roles, list)
        # A newly created user without custom roles should have an empty list
        assert roles == []
    finally:
        # Clean up
        try:
            client.users.delete(username)
        except Exception:
            pass
