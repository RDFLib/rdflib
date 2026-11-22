from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb.models import ClusterRequest


@pytest.mark.parametrize(
    "election_min_timeout, election_range_timeout, heartbeat_interval, "
    "message_size_kb, verification_timeout, transaction_log_max_size_gb, "
    "batch_update_interval",
    [
        (1000, 2000, 500, 1024, 3000, 10, 100),
        (0, 0, 0, 0, 0, 0, 0),
        (-1, -1, -1, -1, -1, -1, -1),  # Negative values are technically int
    ],
)
def test_cluster_request_initialization(
    election_min_timeout,
    election_range_timeout,
    heartbeat_interval,
    message_size_kb,
    verification_timeout,
    transaction_log_max_size_gb,
    batch_update_interval,
):
    """Test creating ClusterRequest with various valid integer values."""
    nodes = ["node1:7200", "node2:7200"]
    request = ClusterRequest(
        electionMinTimeout=election_min_timeout,
        electionRangeTimeout=election_range_timeout,
        heartbeatInterval=heartbeat_interval,
        messageSizeKB=message_size_kb,
        verificationTimeout=verification_timeout,
        transactionLogMaximumSizeGB=transaction_log_max_size_gb,
        batchUpdateInterval=batch_update_interval,
        nodes=nodes,
    )

    assert request.electionMinTimeout == election_min_timeout
    assert request.electionRangeTimeout == election_range_timeout
    assert request.heartbeatInterval == heartbeat_interval
    assert request.messageSizeKB == message_size_kb
    assert request.verificationTimeout == verification_timeout
    assert request.transactionLogMaximumSizeGB == transaction_log_max_size_gb
    assert request.batchUpdateInterval == batch_update_interval
    assert request.nodes == nodes


def test_cluster_request_frozen():
    """Test that ClusterRequest is immutable."""
    request = ClusterRequest(
        electionMinTimeout=1000,
        electionRangeTimeout=2000,
        heartbeatInterval=500,
        messageSizeKB=1024,
        verificationTimeout=3000,
        transactionLogMaximumSizeGB=10,
        batchUpdateInterval=100,
        nodes=["node1:7200"],
    )
    with pytest.raises(AttributeError):
        request.electionMinTimeout = 2000


@pytest.mark.parametrize(
    "election_min_timeout",
    ["1000", 1000.5, None, [], {}, True],
)
def test_cluster_request_invalid_election_min_timeout(election_min_timeout):
    """Test that invalid electionMinTimeout types raise ValueError."""
    with pytest.raises(ValueError):
        ClusterRequest(
            electionMinTimeout=election_min_timeout,
            electionRangeTimeout=2000,
            heartbeatInterval=500,
            messageSizeKB=1024,
            verificationTimeout=3000,
            transactionLogMaximumSizeGB=10,
            batchUpdateInterval=100,
            nodes=["node1:7200"],
        )


@pytest.mark.parametrize(
    "election_range_timeout",
    ["2000", 2000.5, None, [], {}, False],
)
def test_cluster_request_invalid_election_range_timeout(election_range_timeout):
    """Test that invalid electionRangeTimeout types raise ValueError."""
    with pytest.raises(ValueError):
        ClusterRequest(
            electionMinTimeout=1000,
            electionRangeTimeout=election_range_timeout,
            heartbeatInterval=500,
            messageSizeKB=1024,
            verificationTimeout=3000,
            transactionLogMaximumSizeGB=10,
            batchUpdateInterval=100,
            nodes=["node1:7200"],
        )


@pytest.mark.parametrize(
    "heartbeat_interval",
    ["500", 500.5, None, [], {}, True],
)
def test_cluster_request_invalid_heartbeat_interval(heartbeat_interval):
    """Test that invalid heartbeatInterval types raise ValueError."""
    with pytest.raises(ValueError):
        ClusterRequest(
            electionMinTimeout=1000,
            electionRangeTimeout=2000,
            heartbeatInterval=heartbeat_interval,
            messageSizeKB=1024,
            verificationTimeout=3000,
            transactionLogMaximumSizeGB=10,
            batchUpdateInterval=100,
            nodes=["node1:7200"],
        )


@pytest.mark.parametrize(
    "message_size_kb",
    ["1024", 1024.5, None, [], {}, False],
)
def test_cluster_request_invalid_message_size_kb(message_size_kb):
    """Test that invalid messageSizeKB types raise ValueError."""
    with pytest.raises(ValueError):
        ClusterRequest(
            electionMinTimeout=1000,
            electionRangeTimeout=2000,
            heartbeatInterval=500,
            messageSizeKB=message_size_kb,
            verificationTimeout=3000,
            transactionLogMaximumSizeGB=10,
            batchUpdateInterval=100,
            nodes=["node1:7200"],
        )


@pytest.mark.parametrize(
    "verification_timeout",
    ["3000", 3000.5, None, [], {}, True],
)
def test_cluster_request_invalid_verification_timeout(verification_timeout):
    """Test that invalid verificationTimeout types raise ValueError."""
    with pytest.raises(ValueError):
        ClusterRequest(
            electionMinTimeout=1000,
            electionRangeTimeout=2000,
            heartbeatInterval=500,
            messageSizeKB=1024,
            verificationTimeout=verification_timeout,
            transactionLogMaximumSizeGB=10,
            batchUpdateInterval=100,
            nodes=["node1:7200"],
        )


@pytest.mark.parametrize(
    "transaction_log_max_size_gb",
    ["10", 10.5, None, [], {}, False],
)
def test_cluster_request_invalid_transaction_log_max_size_gb(
    transaction_log_max_size_gb,
):
    """Test that invalid transactionLogMaximumSizeGB types raise ValueError."""
    with pytest.raises(ValueError):
        ClusterRequest(
            electionMinTimeout=1000,
            electionRangeTimeout=2000,
            heartbeatInterval=500,
            messageSizeKB=1024,
            verificationTimeout=3000,
            transactionLogMaximumSizeGB=transaction_log_max_size_gb,
            batchUpdateInterval=100,
            nodes=["node1:7200"],
        )


@pytest.mark.parametrize(
    "batch_update_interval",
    ["100", 100.5, None, [], {}, True],
)
def test_cluster_request_invalid_batch_update_interval(batch_update_interval):
    """Test that invalid batchUpdateInterval types raise ValueError."""
    with pytest.raises(ValueError):
        ClusterRequest(
            electionMinTimeout=1000,
            electionRangeTimeout=2000,
            heartbeatInterval=500,
            messageSizeKB=1024,
            verificationTimeout=3000,
            transactionLogMaximumSizeGB=10,
            batchUpdateInterval=batch_update_interval,
            nodes=["node1:7200"],
        )


@pytest.mark.parametrize(
    "nodes",
    ["node1:7200", 123, {"node": "value"}, ("node1", "node2"), None],
)
def test_cluster_request_invalid_nodes_type(nodes):
    """Test that invalid nodes types (non-list) raise ValueError."""
    with pytest.raises(ValueError):
        ClusterRequest(
            electionMinTimeout=1000,
            electionRangeTimeout=2000,
            heartbeatInterval=500,
            messageSizeKB=1024,
            verificationTimeout=3000,
            transactionLogMaximumSizeGB=10,
            batchUpdateInterval=100,
            nodes=nodes,
        )


@pytest.mark.parametrize(
    "nodes",
    [
        [123, "node2:7200"],
        ["node1:7200", None],
        ["node1:7200", ["nested"]],
        [True, False],
        ["node1:7200", 456],
    ],
)
def test_cluster_request_invalid_nodes_elements(nodes):
    """Test that invalid node element types raise ValueError."""
    with pytest.raises(ValueError):
        ClusterRequest(
            electionMinTimeout=1000,
            electionRangeTimeout=2000,
            heartbeatInterval=500,
            messageSizeKB=1024,
            verificationTimeout=3000,
            transactionLogMaximumSizeGB=10,
            batchUpdateInterval=100,
            nodes=nodes,
        )


def test_cluster_request_empty_nodes():
    """Test that ClusterRequest can be created with an empty nodes list."""
    request = ClusterRequest(
        electionMinTimeout=1000,
        electionRangeTimeout=2000,
        heartbeatInterval=500,
        messageSizeKB=1024,
        verificationTimeout=3000,
        transactionLogMaximumSizeGB=10,
        batchUpdateInterval=100,
        nodes=[],
    )
    assert request.nodes == []


def test_cluster_request_multiple_invalid_fields():
    """Test that multiple invalid fields are collected in the error."""
    with pytest.raises(ValueError) as exc_info:
        ClusterRequest(
            electionMinTimeout="invalid",
            electionRangeTimeout="invalid",
            heartbeatInterval="invalid",
            messageSizeKB="invalid",
            verificationTimeout="invalid",
            transactionLogMaximumSizeGB="invalid",
            batchUpdateInterval="invalid",
            nodes="not_a_list",
        )

    error_tuple = exc_info.value.args
    assert "Invalid ClusterRequest values" in error_tuple[0]
    invalid_list = error_tuple[1]
    field_names = [item[0] for item in invalid_list]
    assert "electionMinTimeout" in field_names
    assert "electionRangeTimeout" in field_names
    assert "heartbeatInterval" in field_names
    assert "messageSizeKB" in field_names
    assert "verificationTimeout" in field_names
    assert "transactionLogMaximumSizeGB" in field_names
    assert "batchUpdateInterval" in field_names
    assert "nodes" in field_names


def test_cluster_request_from_dict_valid():
    """Test creating ClusterRequest from a valid dict."""
    data = {
        "electionMinTimeout": 1000,
        "electionRangeTimeout": 2000,
        "heartbeatInterval": 500,
        "messageSizeKB": 1024,
        "verificationTimeout": 3000,
        "transactionLogMaximumSizeGB": 10,
        "batchUpdateInterval": 100,
        "nodes": ["node1:7200", "node2:7200"],
    }
    request = ClusterRequest.from_dict(data)

    assert request.electionMinTimeout == 1000
    assert request.electionRangeTimeout == 2000
    assert request.heartbeatInterval == 500
    assert request.messageSizeKB == 1024
    assert request.verificationTimeout == 3000
    assert request.transactionLogMaximumSizeGB == 10
    assert request.batchUpdateInterval == 100
    assert request.nodes == ["node1:7200", "node2:7200"]


def test_cluster_request_from_dict_empty_nodes():
    """Test creating ClusterRequest from dict with empty nodes list."""
    data = {
        "electionMinTimeout": 1000,
        "electionRangeTimeout": 2000,
        "heartbeatInterval": 500,
        "messageSizeKB": 1024,
        "verificationTimeout": 3000,
        "transactionLogMaximumSizeGB": 10,
        "batchUpdateInterval": 100,
        "nodes": [],
    }
    request = ClusterRequest.from_dict(data)
    assert request.nodes == []


@pytest.mark.parametrize(
    "missing_key",
    [
        "electionMinTimeout",
        "electionRangeTimeout",
        "heartbeatInterval",
        "messageSizeKB",
        "verificationTimeout",
        "transactionLogMaximumSizeGB",
        "batchUpdateInterval",
        "nodes",
    ],
)
def test_cluster_request_from_dict_missing_key(missing_key):
    """Test that from_dict raises KeyError when required keys are missing."""
    data = {
        "electionMinTimeout": 1000,
        "electionRangeTimeout": 2000,
        "heartbeatInterval": 500,
        "messageSizeKB": 1024,
        "verificationTimeout": 3000,
        "transactionLogMaximumSizeGB": 10,
        "batchUpdateInterval": 100,
        "nodes": ["node1:7200"],
    }
    del data[missing_key]

    with pytest.raises(KeyError):
        ClusterRequest.from_dict(data)


@pytest.mark.parametrize(
    "field,invalid_value",
    [
        ("electionMinTimeout", "1000"),
        ("electionRangeTimeout", 2000.5),
        ("heartbeatInterval", None),
        ("messageSizeKB", []),
        ("verificationTimeout", {}),
        ("transactionLogMaximumSizeGB", True),
        ("batchUpdateInterval", "100"),
    ],
)
def test_cluster_request_from_dict_invalid_int_fields(field, invalid_value):
    """Test that from_dict raises ValueError for invalid integer field types."""
    data = {
        "electionMinTimeout": 1000,
        "electionRangeTimeout": 2000,
        "heartbeatInterval": 500,
        "messageSizeKB": 1024,
        "verificationTimeout": 3000,
        "transactionLogMaximumSizeGB": 10,
        "batchUpdateInterval": 100,
        "nodes": ["node1:7200"],
    }
    data[field] = invalid_value

    with pytest.raises(ValueError):
        ClusterRequest.from_dict(data)


@pytest.mark.parametrize(
    "invalid_nodes",
    [
        "node1:7200",  # String instead of list
        123,  # Integer instead of list
        {"node": "value"},  # Dictionary instead of list
        None,  # None instead of list
        [123, "node2:7200"],  # List with non-string element
        ["node1:7200", None],  # List with None element
        [True, False],  # List with boolean elements
    ],
)
def test_cluster_request_from_dict_invalid_nodes(invalid_nodes):
    """Test that from_dict raises ValueError for invalid nodes field."""
    data = {
        "electionMinTimeout": 1000,
        "electionRangeTimeout": 2000,
        "heartbeatInterval": 500,
        "messageSizeKB": 1024,
        "verificationTimeout": 3000,
        "transactionLogMaximumSizeGB": 10,
        "batchUpdateInterval": 100,
        "nodes": invalid_nodes,
    }

    with pytest.raises(ValueError):
        ClusterRequest.from_dict(data)


def test_cluster_request_from_dict_negative_values():
    """Test that from_dict accepts negative integer values (they're still int)."""
    data = {
        "electionMinTimeout": -1,
        "electionRangeTimeout": -2,
        "heartbeatInterval": -3,
        "messageSizeKB": -4,
        "verificationTimeout": -5,
        "transactionLogMaximumSizeGB": -6,
        "batchUpdateInterval": -7,
        "nodes": ["node1:7200"],
    }
    request = ClusterRequest.from_dict(data)

    assert request.electionMinTimeout == -1
    assert request.electionRangeTimeout == -2
    assert request.heartbeatInterval == -3
    assert request.messageSizeKB == -4
    assert request.verificationTimeout == -5
    assert request.transactionLogMaximumSizeGB == -6
    assert request.batchUpdateInterval == -7
