from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb.models import (
        NodeStatus,
        RecoveryOperation,
        RecoveryStatus,
        TopologyStatus,
    )


# ============================================================================
# TopologyStatus Tests
# ============================================================================


def test_topology_status_initialization():
    """Test creating TopologyStatus with valid values."""
    topology = TopologyStatus(state="ACTIVE", primaryTags={"tag1": "value1"})

    assert topology.state == "ACTIVE"
    assert topology.primaryTags == {"tag1": "value1"}


def test_topology_status_frozen():
    """Test that TopologyStatus is immutable."""
    topology = TopologyStatus(state="ACTIVE", primaryTags={})

    with pytest.raises(AttributeError):
        topology.state = "INACTIVE"


@pytest.mark.parametrize(
    "state",
    [123, None, [], {}, True],
)
def test_topology_status_invalid_state(state):
    """Test that invalid state types raise ValueError."""
    with pytest.raises(ValueError):
        TopologyStatus(state=state, primaryTags={})


@pytest.mark.parametrize(
    "primary_tags",
    ["not_a_dict", 123, None, [], True],
)
def test_topology_status_invalid_primary_tags_type(primary_tags):
    """Test that invalid primaryTags types raise ValueError."""
    with pytest.raises(ValueError):
        TopologyStatus(state="ACTIVE", primaryTags=primary_tags)


@pytest.mark.parametrize(
    "primary_tags",
    [
        {123: "value"},  # Non-string key
        {None: "value"},  # None key
        {("tuple",): "value"},  # Tuple key
    ],
)
def test_topology_status_invalid_primary_tags_keys(primary_tags):
    """Test that invalid primaryTags keys raise ValueError."""
    with pytest.raises(ValueError):
        TopologyStatus(state="ACTIVE", primaryTags=primary_tags)


def test_topology_status_empty_primary_tags():
    """Test creating TopologyStatus with empty primaryTags dict."""
    topology = TopologyStatus(state="ACTIVE", primaryTags={})
    assert topology.primaryTags == {}


# ============================================================================
# RecoveryOperation Tests
# ============================================================================


def test_recovery_operation_initialization():
    """Test creating RecoveryOperation with valid values."""
    operation = RecoveryOperation(name="BACKUP", message="Backup in progress")

    assert operation.name == "BACKUP"
    assert operation.message == "Backup in progress"


def test_recovery_operation_frozen():
    """Test that RecoveryOperation is immutable."""
    operation = RecoveryOperation(name="BACKUP", message="Test")

    with pytest.raises(AttributeError):
        operation.name = "RESTORE"


@pytest.mark.parametrize(
    "name",
    [123, None, [], {}, True],
)
def test_recovery_operation_invalid_name(name):
    """Test that invalid name types raise ValueError."""
    with pytest.raises(ValueError):
        RecoveryOperation(name=name, message="Test")


@pytest.mark.parametrize(
    "message",
    [123, None, [], {}, False],
)
def test_recovery_operation_invalid_message(message):
    """Test that invalid message types raise ValueError."""
    with pytest.raises(ValueError):
        RecoveryOperation(name="BACKUP", message=message)


# ============================================================================
# RecoveryStatus Tests
# ============================================================================


def test_recovery_status_initialization_with_all_fields():
    """Test creating RecoveryStatus with all fields populated."""
    operation = RecoveryOperation(name="BACKUP", message="Backup in progress")
    recovery = RecoveryStatus(
        state=operation, message="Recovery message", affectedNodes=["node1", "node2"]
    )

    assert recovery.state == operation
    assert recovery.message == "Recovery message"
    assert recovery.affectedNodes == ["node1", "node2"]


def test_recovery_status_initialization_with_defaults():
    """Test creating RecoveryStatus with default values."""
    recovery = RecoveryStatus()

    assert recovery.state is None
    assert recovery.message is None
    assert recovery.affectedNodes == []


def test_recovery_status_frozen():
    """Test that RecoveryStatus is immutable."""
    recovery = RecoveryStatus()

    with pytest.raises(AttributeError):
        recovery.message = "New message"


@pytest.mark.parametrize(
    "state",
    ["not_an_operation", 123, [], {}, True],
)
def test_recovery_status_invalid_state(state):
    """Test that invalid state types raise ValueError."""
    with pytest.raises(ValueError):
        RecoveryStatus(state=state)


@pytest.mark.parametrize(
    "message",
    [123, [], {}, False],
)
def test_recovery_status_invalid_message(message):
    """Test that invalid message types raise ValueError."""
    with pytest.raises(ValueError):
        RecoveryStatus(message=message)


@pytest.mark.parametrize(
    "affected_nodes",
    ["not_a_list", 123, {}, True],
)
def test_recovery_status_invalid_affected_nodes_type(affected_nodes):
    """Test that invalid affectedNodes types raise ValueError."""
    with pytest.raises(ValueError):
        RecoveryStatus(affectedNodes=affected_nodes)


@pytest.mark.parametrize(
    "affected_nodes",
    [
        [123, "node2"],
        ["node1", None],
        [True, False],
        ["node1", []],
    ],
)
def test_recovery_status_invalid_affected_nodes_elements(affected_nodes):
    """Test that invalid affectedNodes elements raise ValueError."""
    with pytest.raises(ValueError):
        RecoveryStatus(affectedNodes=affected_nodes)


def test_recovery_status_from_dict_empty():
    """Test creating RecoveryStatus from empty dict."""
    recovery = RecoveryStatus.from_dict({})

    assert recovery.state is None
    assert recovery.message is None
    assert recovery.affectedNodes == []


def test_recovery_status_from_dict_with_all_fields():
    """Test creating RecoveryStatus from dict with all fields."""
    data = {
        "state": {"name": "BACKUP", "message": "Backup in progress"},
        "message": "Recovery message",
        "affectedNodes": ["node1", "node2"],
    }
    recovery = RecoveryStatus.from_dict(data)

    assert isinstance(recovery.state, RecoveryOperation)
    assert recovery.state.name == "BACKUP"
    assert recovery.state.message == "Backup in progress"
    assert recovery.message == "Recovery message"
    assert recovery.affectedNodes == ["node1", "node2"]


def test_recovery_status_from_dict_with_none_state():
    """Test creating RecoveryStatus from dict with None state."""
    data = {"state": None, "message": "Test", "affectedNodes": []}
    recovery = RecoveryStatus.from_dict(data)

    assert recovery.state is None
    assert recovery.message == "Test"
    assert recovery.affectedNodes == []


def test_recovery_status_from_dict_partial_fields():
    """Test creating RecoveryStatus from dict with partial fields."""
    data = {"message": "Test message"}
    recovery = RecoveryStatus.from_dict(data)

    assert recovery.state is None
    assert recovery.message == "Test message"
    assert recovery.affectedNodes == []


def test_recovery_status_from_dict_invalid_state():
    """Test that from_dict raises TypeError for invalid state."""
    data = {"state": {"name": "BACKUP"}}  # Missing 'message' field

    with pytest.raises(TypeError):
        RecoveryStatus.from_dict(data)


def test_recovery_status_from_dict_invalid_affected_nodes():
    """Test that from_dict raises ValueError for invalid affectedNodes."""
    data = {"affectedNodes": [123, "node2"]}

    with pytest.raises(ValueError):
        RecoveryStatus.from_dict(data)


# ============================================================================
# NodeStatus Tests
# ============================================================================


def test_node_status_initialization_leader():
    """Test creating NodeStatus for a leader node."""
    recovery_status = RecoveryStatus()
    topology_status = TopologyStatus(state="ACTIVE", primaryTags={})

    node = NodeStatus(
        address="graphdb1.example.com:7300",
        nodeState="LEADER",
        term=2,
        syncStatus={
            "graphdb2.example.com:7300": "IN_SYNC",
            "graphdb3.example.com:7300": "IN_SYNC",
        },
        lastLogTerm=0,
        lastLogIndex=0,
        endpoint="http://graphdb1.example.com:7200",
        recoveryStatus=recovery_status,
        topologyStatus=topology_status,
        clusterEnabled=True,
    )

    assert node.address == "graphdb1.example.com:7300"
    assert node.nodeState == "LEADER"
    assert node.term == 2
    assert len(node.syncStatus) == 2
    assert node.syncStatus["graphdb2.example.com:7300"] == "IN_SYNC"
    assert node.lastLogTerm == 0
    assert node.lastLogIndex == 0
    assert node.endpoint == "http://graphdb1.example.com:7200"
    assert node.recoveryStatus == recovery_status
    assert node.topologyStatus == topology_status
    assert node.clusterEnabled is True


def test_node_status_initialization_follower():
    """Test creating NodeStatus for a follower node."""
    recovery_status = RecoveryStatus()

    node = NodeStatus(
        address="graphdb2.example.com:7300",
        nodeState="FOLLOWER",
        term=2,
        syncStatus={},
        lastLogTerm=0,
        lastLogIndex=0,
        endpoint="http://graphdb2.example.com:7200",
        recoveryStatus=recovery_status,
        topologyStatus=None,
        clusterEnabled=None,
    )

    assert node.address == "graphdb2.example.com:7300"
    assert node.nodeState == "FOLLOWER"
    assert node.syncStatus == {}
    assert node.topologyStatus is None
    assert node.clusterEnabled is None


def test_node_status_frozen():
    """Test that NodeStatus is immutable."""
    node = NodeStatus(
        address="test:7300",
        nodeState="LEADER",
        term=1,
        syncStatus={},
        lastLogTerm=0,
        lastLogIndex=0,
        endpoint="http://test:7200",
        recoveryStatus=None,
        topologyStatus=None,
        clusterEnabled=None,
    )

    with pytest.raises(AttributeError):
        node.nodeState = "FOLLOWER"


@pytest.mark.parametrize(
    "address",
    [123, None, [], {}, True],
)
def test_node_status_invalid_address(address):
    """Test that invalid address types raise ValueError."""
    with pytest.raises(ValueError):
        NodeStatus(
            address=address,
            nodeState="LEADER",
            term=1,
            syncStatus={},
            lastLogTerm=0,
            lastLogIndex=0,
            endpoint="http://test:7200",
            recoveryStatus=None,
            topologyStatus=None,
            clusterEnabled=None,
        )


@pytest.mark.parametrize(
    "node_state",
    [123, None, [], {}, True],
)
def test_node_status_invalid_node_state(node_state):
    """Test that invalid nodeState types raise ValueError."""
    with pytest.raises(ValueError):
        NodeStatus(
            address="test:7300",
            nodeState=node_state,
            term=1,
            syncStatus={},
            lastLogTerm=0,
            lastLogIndex=0,
            endpoint="http://test:7200",
            recoveryStatus=None,
            topologyStatus=None,
            clusterEnabled=None,
        )


@pytest.mark.parametrize(
    "term",
    ["1", 1.5, None, [], {}, True],
)
def test_node_status_invalid_term(term):
    """Test that invalid term types raise ValueError."""
    with pytest.raises(ValueError):
        NodeStatus(
            address="test:7300",
            nodeState="LEADER",
            term=term,
            syncStatus={},
            lastLogTerm=0,
            lastLogIndex=0,
            endpoint="http://test:7200",
            recoveryStatus=None,
            topologyStatus=None,
            clusterEnabled=None,
        )


@pytest.mark.parametrize(
    "sync_status",
    ["not_a_dict", 123, None, [], True],
)
def test_node_status_invalid_sync_status_type(sync_status):
    """Test that invalid syncStatus types raise ValueError."""
    with pytest.raises(ValueError):
        NodeStatus(
            address="test:7300",
            nodeState="LEADER",
            term=1,
            syncStatus=sync_status,
            lastLogTerm=0,
            lastLogIndex=0,
            endpoint="http://test:7200",
            recoveryStatus=None,
            topologyStatus=None,
            clusterEnabled=None,
        )


@pytest.mark.parametrize(
    "sync_status",
    [
        {123: "IN_SYNC"},  # Non-string key
        {"node1": 123},  # Non-string value
        {None: "IN_SYNC"},  # None key
        {"node1": None},  # None value
    ],
)
def test_node_status_invalid_sync_status_content(sync_status):
    """Test that invalid syncStatus content raises ValueError."""
    with pytest.raises(ValueError):
        NodeStatus(
            address="test:7300",
            nodeState="LEADER",
            term=1,
            syncStatus=sync_status,
            lastLogTerm=0,
            lastLogIndex=0,
            endpoint="http://test:7200",
            recoveryStatus=None,
            topologyStatus=None,
            clusterEnabled=None,
        )


@pytest.mark.parametrize(
    "last_log_term",
    ["0", 0.5, None, [], {}, True],
)
def test_node_status_invalid_last_log_term(last_log_term):
    """Test that invalid lastLogTerm types raise ValueError."""
    with pytest.raises(ValueError):
        NodeStatus(
            address="test:7300",
            nodeState="LEADER",
            term=1,
            syncStatus={},
            lastLogTerm=last_log_term,
            lastLogIndex=0,
            endpoint="http://test:7200",
            recoveryStatus=None,
            topologyStatus=None,
            clusterEnabled=None,
        )


@pytest.mark.parametrize(
    "last_log_index",
    ["0", 0.5, None, [], {}, False],
)
def test_node_status_invalid_last_log_index(last_log_index):
    """Test that invalid lastLogIndex types raise ValueError."""
    with pytest.raises(ValueError):
        NodeStatus(
            address="test:7300",
            nodeState="LEADER",
            term=1,
            syncStatus={},
            lastLogTerm=0,
            lastLogIndex=last_log_index,
            endpoint="http://test:7200",
            recoveryStatus=None,
            topologyStatus=None,
            clusterEnabled=None,
        )


@pytest.mark.parametrize(
    "endpoint",
    [123, None, [], {}, True],
)
def test_node_status_invalid_endpoint(endpoint):
    """Test that invalid endpoint types raise ValueError."""
    with pytest.raises(ValueError):
        NodeStatus(
            address="test:7300",
            nodeState="LEADER",
            term=1,
            syncStatus={},
            lastLogTerm=0,
            lastLogIndex=0,
            endpoint=endpoint,
            recoveryStatus=None,
            topologyStatus=None,
            clusterEnabled=None,
        )


@pytest.mark.parametrize(
    "recovery_status",
    ["not_a_recovery", 123, [], {}, True],
)
def test_node_status_invalid_recovery_status(recovery_status):
    """Test that invalid recoveryStatus types raise ValueError."""
    with pytest.raises(ValueError):
        NodeStatus(
            address="test:7300",
            nodeState="LEADER",
            term=1,
            syncStatus={},
            lastLogTerm=0,
            lastLogIndex=0,
            endpoint="http://test:7200",
            recoveryStatus=recovery_status,
            topologyStatus=None,
            clusterEnabled=None,
        )


@pytest.mark.parametrize(
    "topology_status",
    ["not_a_topology", 123, [], {}, True],
)
def test_node_status_invalid_topology_status(topology_status):
    """Test that invalid topologyStatus types raise ValueError."""
    with pytest.raises(ValueError):
        NodeStatus(
            address="test:7300",
            nodeState="LEADER",
            term=1,
            syncStatus={},
            lastLogTerm=0,
            lastLogIndex=0,
            endpoint="http://test:7200",
            recoveryStatus=None,
            topologyStatus=topology_status,
            clusterEnabled=None,
        )


@pytest.mark.parametrize(
    "cluster_enabled",
    ["true", 1, 0, [], {}, "false"],
)
def test_node_status_invalid_cluster_enabled(cluster_enabled):
    """Test that invalid clusterEnabled types raise ValueError."""
    with pytest.raises(ValueError):
        NodeStatus(
            address="test:7300",
            nodeState="LEADER",
            term=1,
            syncStatus={},
            lastLogTerm=0,
            lastLogIndex=0,
            endpoint="http://test:7200",
            recoveryStatus=None,
            topologyStatus=None,
            clusterEnabled=cluster_enabled,
        )


def test_node_status_from_dict_leader():
    """Test creating NodeStatus from dict for a leader node."""
    data = {
        "address": "graphdb1.example.com:7300",
        "endpoint": "http://graphdb1.example.com:7200",
        "lastLogIndex": 0,
        "lastLogTerm": 0,
        "nodeState": "LEADER",
        "syncStatus": {
            "graphdb2.example.com:7300": "IN_SYNC",
            "graphdb3.example.com:7300": "IN_SYNC",
        },
        "term": 2,
        "recoveryStatus": {},
    }

    node = NodeStatus.from_dict(data)

    assert node.address == "graphdb1.example.com:7300"
    assert node.nodeState == "LEADER"
    assert node.term == 2
    assert len(node.syncStatus) == 2
    assert node.syncStatus["graphdb2.example.com:7300"] == "IN_SYNC"
    assert node.lastLogTerm == 0
    assert node.lastLogIndex == 0
    assert node.endpoint == "http://graphdb1.example.com:7200"
    assert isinstance(node.recoveryStatus, RecoveryStatus)
    assert node.recoveryStatus.state is None
    assert node.topologyStatus is None
    assert node.clusterEnabled is None


def test_node_status_from_dict_follower():
    """Test creating NodeStatus from dict for a follower node."""
    data = {
        "address": "graphdb2.example.com:7300",
        "endpoint": "http://graphdb2.example.com:7200",
        "lastLogIndex": 0,
        "lastLogTerm": 0,
        "nodeState": "FOLLOWER",
        "syncStatus": {},
        "term": 2,
        "recoveryStatus": {},
    }

    node = NodeStatus.from_dict(data)

    assert node.address == "graphdb2.example.com:7300"
    assert node.nodeState == "FOLLOWER"
    assert node.term == 2
    assert node.syncStatus == {}
    assert isinstance(node.recoveryStatus, RecoveryStatus)
    assert node.topologyStatus is None


def test_node_status_from_dict_with_topology():
    """Test creating NodeStatus from dict with topology status."""
    data = {
        "address": "test:7300",
        "endpoint": "http://test:7200",
        "lastLogIndex": 0,
        "lastLogTerm": 0,
        "nodeState": "LEADER",
        "syncStatus": {},
        "term": 1,
        "recoveryStatus": {},
        "topologyStatus": {"state": "ACTIVE", "primaryTags": {"tag1": "value1"}},
        "clusterEnabled": True,
    }

    node = NodeStatus.from_dict(data)

    assert isinstance(node.topologyStatus, TopologyStatus)
    assert node.topologyStatus.state == "ACTIVE"
    assert node.topologyStatus.primaryTags == {"tag1": "value1"}
    assert node.clusterEnabled is True


def test_node_status_from_dict_with_recovery_data():
    """Test creating NodeStatus from dict with recovery status data."""
    data = {
        "address": "test:7300",
        "endpoint": "http://test:7200",
        "lastLogIndex": 0,
        "lastLogTerm": 0,
        "nodeState": "LEADER",
        "syncStatus": {},
        "term": 1,
        "recoveryStatus": {
            "state": {"name": "BACKUP", "message": "Backup in progress"},
            "message": "Recovery message",
            "affectedNodes": ["node1"],
        },
    }

    node = NodeStatus.from_dict(data)

    assert isinstance(node.recoveryStatus, RecoveryStatus)
    assert isinstance(node.recoveryStatus.state, RecoveryOperation)
    assert node.recoveryStatus.state.name == "BACKUP"
    assert node.recoveryStatus.message == "Recovery message"
    assert node.recoveryStatus.affectedNodes == ["node1"]


@pytest.mark.parametrize(
    "missing_key",
    [
        "address",
        "nodeState",
        "term",
        "syncStatus",
        "lastLogTerm",
        "lastLogIndex",
        "endpoint",
    ],
)
def test_node_status_from_dict_missing_key(missing_key):
    """Test that from_dict raises KeyError when required keys are missing."""
    data = {
        "address": "test:7300",
        "endpoint": "http://test:7200",
        "lastLogIndex": 0,
        "lastLogTerm": 0,
        "nodeState": "LEADER",
        "syncStatus": {},
        "term": 1,
    }
    del data[missing_key]

    with pytest.raises(KeyError):
        NodeStatus.from_dict(data)


@pytest.mark.parametrize(
    "field,invalid_value",
    [
        ("address", 123),
        ("nodeState", None),
        ("term", "2"),
        ("syncStatus", "not_a_dict"),
        ("syncStatus", {123: "value"}),
        ("syncStatus", {"key": 123}),
        ("lastLogTerm", "0"),
        ("lastLogIndex", None),
        ("endpoint", []),
        ("clusterEnabled", "true"),
    ],
)
def test_node_status_from_dict_invalid_field_types(field, invalid_value):
    """Test that from_dict raises ValueError for invalid field types."""
    data = {
        "address": "test:7300",
        "endpoint": "http://test:7200",
        "lastLogIndex": 0,
        "lastLogTerm": 0,
        "nodeState": "LEADER",
        "syncStatus": {},
        "term": 1,
    }
    data[field] = invalid_value

    with pytest.raises(ValueError):
        NodeStatus.from_dict(data)


def test_node_status_from_dict_invalid_topology_status():
    """Test that from_dict raises TypeError for invalid topology status."""
    data = {
        "address": "test:7300",
        "endpoint": "http://test:7200",
        "lastLogIndex": 0,
        "lastLogTerm": 0,
        "nodeState": "LEADER",
        "syncStatus": {},
        "term": 1,
        "topologyStatus": {"state": "ACTIVE"},  # Missing primaryTags
    }

    with pytest.raises(TypeError):
        NodeStatus.from_dict(data)


def test_node_status_from_dict_invalid_recovery_status():
    """Test that from_dict raises TypeError for invalid recovery status."""
    data = {
        "address": "test:7300",
        "endpoint": "http://test:7200",
        "lastLogIndex": 0,
        "lastLogTerm": 0,
        "nodeState": "LEADER",
        "syncStatus": {},
        "term": 1,
        "recoveryStatus": {"state": {"name": "BACKUP"}},  # Missing message field
    }

    with pytest.raises(TypeError):
        NodeStatus.from_dict(data)
