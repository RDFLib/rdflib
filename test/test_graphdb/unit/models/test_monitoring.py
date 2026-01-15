from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb.models import (
        BackupOperationBean,
        InfrastructureMemoryUsage,
        InfrastructureStatistics,
        InfrastructureStorageMemory,
        RepositoryStatistics,
        RepositoryStatisticsEntityPool,
        RepositoryStatisticsQueries,
        SnapshotOptionsBean,
        StructuresStatistics,
    )


@pytest.mark.parametrize(
    "cache_hit, cache_miss",
    [(100, 50), (0, 0), (-1, -10)],
)
def test_structure_statistics_initialization(cache_hit, cache_miss):
    """Test creating StructuresStatistics with various valid integer values."""
    settings = StructuresStatistics(cacheHit=cache_hit, cacheMiss=cache_miss)

    assert settings.cacheHit == cache_hit
    assert settings.cacheMiss == cache_miss


def test_structure_statistics_frozen():
    """Test that StructuresStatistics is immutable."""
    settings = StructuresStatistics(cacheHit=100, cacheMiss=50)
    with pytest.raises(AttributeError):
        settings.cacheHit = 200


@pytest.mark.parametrize(
    "cache_hit",
    ["100", 100.5, None, [], {}, True],
)
def test_structure_statistics_invalid_cache_hit(cache_hit):
    """Test that invalid cacheHit types raise ValueError."""
    with pytest.raises(ValueError):
        StructuresStatistics(cacheHit=cache_hit, cacheMiss=50)


@pytest.mark.parametrize(
    "cache_miss",
    ["50", 50.5, None, [], {}, False],
)
def test_structure_statistics_invalid_cache_miss(cache_miss):
    """Test that invalid cacheMiss types raise ValueError."""
    with pytest.raises(ValueError):
        StructuresStatistics(cacheHit=100, cacheMiss=cache_miss)


def test_structure_statistics_multiple_invalid_fields():
    """Test that multiple invalid fields are collected in the error."""
    with pytest.raises(ValueError) as exc_info:
        StructuresStatistics(cacheHit="invalid", cacheMiss="also_invalid")

    error_tuple = exc_info.value.args
    assert "Invalid StructuresStatistics values" in error_tuple[0]
    # The invalid list should contain both fields
    invalid_list = error_tuple[1]
    field_names = [item[0] for item in invalid_list]
    assert "cacheHit" in field_names
    assert "cacheMiss" in field_names


@pytest.mark.parametrize(
    "slow, suboptimal",
    [(10, 5), (0, 0), (-1, -10)],
)
def test_repository_statistics_queries_initialization(slow, suboptimal):
    """Test creating RepositoryStatisticsQueries with various valid integer values."""
    queries = RepositoryStatisticsQueries(slow=slow, suboptimal=suboptimal)

    assert queries.slow == slow
    assert queries.suboptimal == suboptimal


def test_repository_statistics_queries_frozen():
    """Test that RepositoryStatisticsQueries is immutable."""
    queries = RepositoryStatisticsQueries(slow=10, suboptimal=5)
    with pytest.raises(AttributeError):
        queries.slow = 20


@pytest.mark.parametrize(
    "slow",
    ["10", 10.5, None, [], {}, True],
)
def test_repository_statistics_queries_invalid_slow(slow):
    """Test that invalid slow types raise ValueError."""
    with pytest.raises(ValueError):
        RepositoryStatisticsQueries(slow=slow, suboptimal=5)


@pytest.mark.parametrize(
    "suboptimal",
    ["5", 5.5, None, [], {}, False],
)
def test_repository_statistics_queries_invalid_suboptimal(suboptimal):
    """Test that invalid suboptimal types raise ValueError."""
    with pytest.raises(ValueError):
        RepositoryStatisticsQueries(slow=10, suboptimal=suboptimal)


def test_repository_statistics_queries_multiple_invalid_fields():
    """Test that multiple invalid fields are collected in the error."""
    with pytest.raises(ValueError) as exc_info:
        RepositoryStatisticsQueries(slow="invalid", suboptimal="also_invalid")

    error_tuple = exc_info.value.args
    assert "Invalid RepositoryStatisticsQueries values" in error_tuple[0]
    invalid_list = error_tuple[1]
    field_names = [item[0] for item in invalid_list]
    assert "slow" in field_names
    assert "suboptimal" in field_names


@pytest.mark.parametrize(
    "reads, writes, size",
    [(100, 50, 1000), (0, 0, 0)],
)
def test_repository_statistics_entity_pool_initialization(reads, writes, size):
    """Test creating RepositoryStatisticsEntityPool with various valid integer values."""
    pool = RepositoryStatisticsEntityPool(
        epoolReads=reads, epoolWrites=writes, epoolSize=size
    )

    assert pool.epoolReads == reads
    assert pool.epoolWrites == writes
    assert pool.epoolSize == size


def test_repository_statistics_entity_pool_frozen():
    """Test that RepositoryStatisticsEntityPool is immutable."""
    pool = RepositoryStatisticsEntityPool(
        epoolReads=100, epoolWrites=50, epoolSize=1000
    )
    with pytest.raises(AttributeError):
        pool.epoolReads = 200


@pytest.mark.parametrize(
    "epool_reads",
    ["100", 100.5, None, [], {}, True],
)
def test_repository_statistics_entity_pool_invalid_epool_reads(epool_reads):
    """Test that invalid epoolReads types raise ValueError."""
    with pytest.raises(ValueError):
        RepositoryStatisticsEntityPool(
            epoolReads=epool_reads, epoolWrites=50, epoolSize=1000
        )


@pytest.mark.parametrize(
    "epool_writes",
    ["50", 50.5, None, [], {}, False],
)
def test_repository_statistics_entity_pool_invalid_epool_writes(epool_writes):
    """Test that invalid epoolWrites types raise ValueError."""
    with pytest.raises(ValueError):
        RepositoryStatisticsEntityPool(
            epoolReads=100, epoolWrites=epool_writes, epoolSize=1000
        )


@pytest.mark.parametrize(
    "epool_size",
    ["1000", 1000.5, None, [], {}, True],
)
def test_repository_statistics_entity_pool_invalid_epool_size(epool_size):
    """Test that invalid epoolSize types raise ValueError."""
    with pytest.raises(ValueError):
        RepositoryStatisticsEntityPool(
            epoolReads=100, epoolWrites=50, epoolSize=epool_size
        )


def test_repository_statistics_entity_pool_multiple_invalid_fields():
    """Test that multiple invalid fields are collected in the error."""
    with pytest.raises(ValueError) as exc_info:
        RepositoryStatisticsEntityPool(
            epoolReads="invalid", epoolWrites="also_invalid", epoolSize="bad"
        )

    error_tuple = exc_info.value.args
    assert "Invalid RepositoryStatisticsEntityPool values" in error_tuple[0]
    invalid_list = error_tuple[1]
    field_names = [item[0] for item in invalid_list]
    assert "epoolReads" in field_names
    assert "epoolWrites" in field_names
    assert "epoolSize" in field_names


@pytest.mark.parametrize(
    "active_tx, open_conn",
    [(3, 10), (0, 0)],
)
def test_repository_statistics_initialization(active_tx, open_conn):
    """Test creating RepositoryStatistics with valid values."""
    queries = RepositoryStatisticsQueries(slow=10, suboptimal=5)
    entity_pool = RepositoryStatisticsEntityPool(
        epoolReads=100, epoolWrites=50, epoolSize=1000
    )
    stats = RepositoryStatistics(
        queries=queries,
        entityPool=entity_pool,
        activeTransactions=active_tx,
        openConnections=open_conn,
    )

    assert stats.activeTransactions == active_tx
    assert stats.openConnections == open_conn


def test_repository_statistics_frozen():
    """Test that RepositoryStatistics is immutable."""
    queries = RepositoryStatisticsQueries(slow=10, suboptimal=5)
    entity_pool = RepositoryStatisticsEntityPool(
        epoolReads=100, epoolWrites=50, epoolSize=1000
    )
    stats = RepositoryStatistics(
        queries=queries,
        entityPool=entity_pool,
        activeTransactions=3,
        openConnections=10,
    )
    with pytest.raises(AttributeError):
        stats.activeTransactions = 5


@pytest.mark.parametrize(
    "queries",
    [{"slow": 10, "suboptimal": 5}, "invalid", 123, None, [], True],
)
def test_repository_statistics_invalid_queries(queries):
    """Test that invalid queries types raise ValueError."""
    entity_pool = RepositoryStatisticsEntityPool(
        epoolReads=100, epoolWrites=50, epoolSize=1000
    )
    with pytest.raises(ValueError):
        RepositoryStatistics(
            queries=queries,
            entityPool=entity_pool,
            activeTransactions=3,
            openConnections=10,
        )


@pytest.mark.parametrize(
    "entity_pool",
    [
        {"epoolReads": 100, "epoolWrites": 50, "epoolSize": 1000},
        "invalid",
        123,
        None,
        [],
        False,
    ],
)
def test_repository_statistics_invalid_entity_pool(entity_pool):
    """Test that invalid entityPool types raise ValueError."""
    queries = RepositoryStatisticsQueries(slow=10, suboptimal=5)
    with pytest.raises(ValueError):
        RepositoryStatistics(
            queries=queries,
            entityPool=entity_pool,
            activeTransactions=3,
            openConnections=10,
        )


@pytest.mark.parametrize(
    "active_transactions",
    ["3", 3.5, None, [], {}, True],
)
def test_repository_statistics_invalid_active_transactions(active_transactions):
    """Test that invalid activeTransactions types raise ValueError."""
    queries = RepositoryStatisticsQueries(slow=10, suboptimal=5)
    entity_pool = RepositoryStatisticsEntityPool(
        epoolReads=100, epoolWrites=50, epoolSize=1000
    )
    with pytest.raises(ValueError):
        RepositoryStatistics(
            queries=queries,
            entityPool=entity_pool,
            activeTransactions=active_transactions,
            openConnections=10,
        )


@pytest.mark.parametrize(
    "open_connections",
    ["10", 10.5, None, [], {}, False],
)
def test_repository_statistics_invalid_open_connections(open_connections):
    """Test that invalid openConnections types raise ValueError."""
    queries = RepositoryStatisticsQueries(slow=10, suboptimal=5)
    entity_pool = RepositoryStatisticsEntityPool(
        epoolReads=100, epoolWrites=50, epoolSize=1000
    )
    with pytest.raises(ValueError):
        RepositoryStatistics(
            queries=queries,
            entityPool=entity_pool,
            activeTransactions=3,
            openConnections=open_connections,
        )


def test_repository_statistics_multiple_invalid_fields():
    """Test that multiple invalid fields are collected in the error."""
    with pytest.raises(ValueError) as exc_info:
        RepositoryStatistics(
            queries="invalid",
            entityPool="also_invalid",
            activeTransactions="bad",
            openConnections="wrong",
        )

    error_tuple = exc_info.value.args
    assert "Invalid RepositoryStatistics values" in error_tuple[0]
    invalid_list = error_tuple[1]
    field_names = [item[0] for item in invalid_list]
    assert "queries" in field_names
    assert "entityPool" in field_names
    assert "activeTransactions" in field_names
    assert "openConnections" in field_names


@pytest.mark.parametrize(
    "values",
    [
        {
            "queries": {"slow": 10, "suboptimal": 5},
            "entityPool": {"epoolReads": 100, "epoolWrites": 50, "epoolSize": 1000},
            "activeTransactions": 3,
            "openConnections": 10,
        },
        {
            "queries": {"slow": 0, "suboptimal": 0},
            "entityPool": {"epoolReads": 0, "epoolWrites": 0, "epoolSize": 0},
            "activeTransactions": 0,
            "openConnections": 0,
        },
    ],
)
def test_repository_statistics_from_dict(values):
    """Test creating RepositoryStatistics from a valid dict."""
    stats = RepositoryStatistics.from_dict(values)

    assert isinstance(stats, RepositoryStatistics)
    assert isinstance(stats.queries, RepositoryStatisticsQueries)
    assert isinstance(stats.entityPool, RepositoryStatisticsEntityPool)
    assert stats.activeTransactions == values["activeTransactions"]
    assert stats.openConnections == values["openConnections"]


def test_repository_statistics_from_dict_missing_key():
    """Test that from_dict raises KeyError for missing required keys."""
    data = {
        "queries": {"slow": 10, "suboptimal": 5},
        # Missing entityPool, activeTransactions, openConnections
    }

    with pytest.raises(KeyError):
        RepositoryStatistics.from_dict(data)


def test_repository_statistics_from_dict_invalid_nested_data():
    """Test that from_dict raises ValueError for invalid nested data types."""
    data = {
        "queries": {"slow": "invalid", "suboptimal": 5},  # slow should be int
        "entityPool": {"epoolReads": 100, "epoolWrites": 50, "epoolSize": 1000},
        "activeTransactions": 3,
        "openConnections": 10,
    }

    with pytest.raises(ValueError):
        RepositoryStatistics.from_dict(data)


@pytest.mark.parametrize(
    "values",
    [
        {
            "max": 16789798912,
            "committed": 1874853888,
            "init": 1073741824,
            "used": 1189000104,
        },
        {"max": 0, "committed": 0, "init": 0, "used": 0},
    ],
)
def test_infrastructure_memory_usage_initialization(values):
    """Test creating InfrastructureMemoryUsage with valid or zero values."""
    usage = InfrastructureMemoryUsage(**values)

    assert usage.max == values["max"]
    assert usage.committed == values["committed"]
    assert usage.init == values["init"]
    assert usage.used == values["used"]


def test_infrastructure_memory_usage_frozen():
    """Test that InfrastructureMemoryUsage is immutable."""
    usage = InfrastructureMemoryUsage(
        max=16789798912, committed=1874853888, init=1073741824, used=1189000104
    )
    with pytest.raises(AttributeError):
        usage.max = 20000000000


@pytest.mark.parametrize(
    "field_name",
    ["max", "committed", "init", "used"],
)
@pytest.mark.parametrize(
    "invalid_value",
    ["100", 100.5, None, [], {}, True],
)
def test_infrastructure_memory_usage_invalid_types(field_name, invalid_value):
    """Test that invalid types for InfrastructureMemoryUsage fields raise ValueError."""
    kwargs = {"max": 0, "committed": 0, "init": 0, "used": 0}
    kwargs[field_name] = invalid_value
    with pytest.raises(ValueError):
        InfrastructureMemoryUsage(**kwargs)


@pytest.mark.parametrize(
    "values",
    [
        {
            "dataDirUsed": 773518331904,
            "workDirUsed": 773518331904,
            "logsDirUsed": 773518331904,
            "dataDirFree": 1193202618368,
            "workDirFree": 1193202618368,
            "logsDirFree": 1193202618368,
        },
        {
            "dataDirUsed": 0,
            "workDirUsed": 0,
            "logsDirUsed": 0,
            "dataDirFree": 0,
            "workDirFree": 0,
            "logsDirFree": 0,
        },
    ],
)
def test_infrastructure_storage_memory_initialization(values):
    """Test creating InfrastructureStorageMemory with valid or zero values."""
    storage = InfrastructureStorageMemory(**values)
    assert storage.dataDirUsed == values["dataDirUsed"]
    assert storage.dataDirFree == values["dataDirFree"]


def test_infrastructure_storage_memory_frozen():
    """Test that InfrastructureStorageMemory is immutable."""
    storage = InfrastructureStorageMemory(
        dataDirUsed=0,
        workDirUsed=0,
        logsDirUsed=0,
        dataDirFree=0,
        workDirFree=0,
        logsDirFree=0,
    )
    with pytest.raises(AttributeError):
        storage.dataDirUsed = 100


@pytest.mark.parametrize(
    "field_name",
    [
        "dataDirUsed",
        "workDirUsed",
        "logsDirUsed",
        "dataDirFree",
        "workDirFree",
        "logsDirFree",
    ],
)
@pytest.mark.parametrize(
    "invalid_value",
    ["100", 100.5, None, [], {}, True],
)
def test_infrastructure_storage_memory_invalid_types(field_name, invalid_value):
    """Test that invalid types for InfrastructureStorageMemory fields raise ValueError."""
    kwargs = {
        "dataDirUsed": 0,
        "workDirUsed": 0,
        "logsDirUsed": 0,
        "dataDirFree": 0,
        "workDirFree": 0,
        "logsDirFree": 0,
    }
    kwargs[field_name] = invalid_value
    with pytest.raises(ValueError):
        InfrastructureStorageMemory(**kwargs)


def test_infrastructure_statistics_valid():
    """Test creating a valid InfrastructureStatistics."""
    memory = InfrastructureMemoryUsage(max=0, committed=0, init=0, used=0)
    storage = InfrastructureStorageMemory(
        dataDirUsed=0,
        workDirUsed=0,
        logsDirUsed=0,
        dataDirFree=0,
        workDirFree=0,
        logsDirFree=0,
    )
    stats = InfrastructureStatistics(
        heapMemoryUsage=memory,
        nonHeapMemoryUsage=memory,
        storageMemory=storage,
        threadCount=35,
        cpuLoad=6.25,
        classCount=20240,
        gcCount=15,
        openFileDescriptors=696,
        maxFileDescriptors=524288,
    )

    assert stats.heapMemoryUsage == memory
    assert stats.threadCount == 35
    assert stats.cpuLoad == 6.25


@pytest.mark.parametrize("cpu_load", [6.25, 10])
def test_infrastructure_statistics_from_dict(cpu_load):
    """Test creating InfrastructureStatistics from a dict with float or int cpuLoad."""
    data = {
        "heapMemoryUsage": {
            "max": 16789798912,
            "committed": 1874853888,
            "init": 1073741824,
            "used": 1189000104,
        },
        "nonHeapMemoryUsage": {
            "max": 137438953472,
            "committed": 199446528,
            "init": 7667712,
            "used": 192552832,
        },
        "storageMemory": {
            "dataDirUsed": 773518331904,
            "workDirUsed": 773518331904,
            "logsDirUsed": 773518331904,
            "dataDirFree": 1193202618368,
            "workDirFree": 1193202618368,
            "logsDirFree": 1193202618368,
        },
        "threadCount": 35,
        "cpuLoad": cpu_load,
        "classCount": 20240,
        "gcCount": 15,
        "openFileDescriptors": 696,
        "maxFileDescriptors": 524288,
    }

    stats = InfrastructureStatistics.from_dict(data)

    assert isinstance(stats, InfrastructureStatistics)
    assert isinstance(stats.heapMemoryUsage, InfrastructureMemoryUsage)
    assert stats.heapMemoryUsage.max == 16789798912
    assert stats.cpuLoad == float(cpu_load)
    assert isinstance(stats.cpuLoad, float)
    assert stats.threadCount == 35


def test_infrastructure_statistics_from_dict_missing_key():
    """Test that from_dict raises KeyError for missing required keys."""
    data = {
        "heapMemoryUsage": {
            "max": 16789798912,
            "committed": 1874853888,
            "init": 1073741824,
            "used": 1189000104,
        },
        # Missing nonHeapMemoryUsage, storageMemory, and other required fields
    }

    with pytest.raises(KeyError):
        InfrastructureStatistics.from_dict(data)


def test_infrastructure_statistics_from_dict_invalid_nested_data():
    """Test that from_dict raises ValueError for invalid nested data types."""
    data = {
        "heapMemoryUsage": {
            "max": "invalid",  # Should be int
            "committed": 1874853888,
            "init": 1073741824,
            "used": 1189000104,
        },
        "nonHeapMemoryUsage": {
            "max": 137438953472,
            "committed": 199446528,
            "init": 7667712,
            "used": 192552832,
        },
        "storageMemory": {
            "dataDirUsed": 773518331904,
            "workDirUsed": 773518331904,
            "logsDirUsed": 773518331904,
            "dataDirFree": 1193202618368,
            "workDirFree": 1193202618368,
            "logsDirFree": 1193202618368,
        },
        "threadCount": 35,
        "cpuLoad": 6.25,
        "classCount": 20240,
        "gcCount": 15,
        "openFileDescriptors": 696,
        "maxFileDescriptors": 524288,
    }

    with pytest.raises(ValueError):
        InfrastructureStatistics.from_dict(data)


def test_infrastructure_statistics_from_dict_nested_missing_key():
    """Test that from_dict raises TypeError for missing nested keys."""
    data = {
        "heapMemoryUsage": {
            "max": 16789798912,
            # Missing committed, init, used
        },
        "nonHeapMemoryUsage": {
            "max": 137438953472,
            "committed": 199446528,
            "init": 7667712,
            "used": 192552832,
        },
        "storageMemory": {
            "dataDirUsed": 773518331904,
            "workDirUsed": 773518331904,
            "logsDirUsed": 773518331904,
            "dataDirFree": 1193202618368,
            "workDirFree": 1193202618368,
            "logsDirFree": 1193202618368,
        },
        "threadCount": 35,
        "cpuLoad": 6.25,
        "classCount": 20240,
        "gcCount": 15,
        "openFileDescriptors": 696,
        "maxFileDescriptors": 524288,
    }

    with pytest.raises(TypeError):
        InfrastructureStatistics.from_dict(data)


@pytest.mark.parametrize(
    "with_repo_data, with_sys_data, clean_data_dir, repositories",
    [
        (True, True, True, None),
        (False, False, False, None),
        (True, False, True, ["repo1", "repo2"]),
        (False, True, False, []),
    ],
)
def test_snapshot_options_bean_initialization(
    with_repo_data, with_sys_data, clean_data_dir, repositories
):
    """Test creating SnapshotOptionsBean with various valid values."""
    options = SnapshotOptionsBean(
        withRepositoryData=with_repo_data,
        withSystemData=with_sys_data,
        cleanDataDir=clean_data_dir,
        repositories=repositories,
    )

    assert options.withRepositoryData == with_repo_data
    assert options.withSystemData == with_sys_data
    assert options.cleanDataDir == clean_data_dir
    assert options.repositories == repositories


def test_snapshot_options_bean_frozen():
    """Test that SnapshotOptionsBean is immutable."""
    options = SnapshotOptionsBean(
        withRepositoryData=True,
        withSystemData=True,
        cleanDataDir=False,
    )
    with pytest.raises(AttributeError):
        options.withRepositoryData = False


@pytest.mark.parametrize(
    "with_repository_data",
    ["true", "True", 1, 0, None, [], {}, ""],
)
def test_snapshot_options_bean_invalid_with_repository_data(with_repository_data):
    """Test that invalid withRepositoryData types raise ValueError."""
    with pytest.raises(ValueError):
        SnapshotOptionsBean(
            withRepositoryData=with_repository_data,
            withSystemData=True,
            cleanDataDir=True,
        )


@pytest.mark.parametrize(
    "with_system_data",
    ["false", "False", 1, 0, None, [], {}, ""],
)
def test_snapshot_options_bean_invalid_with_system_data(with_system_data):
    """Test that invalid withSystemData types raise ValueError."""
    with pytest.raises(ValueError):
        SnapshotOptionsBean(
            withRepositoryData=True,
            withSystemData=with_system_data,
            cleanDataDir=True,
        )


@pytest.mark.parametrize(
    "clean_data_dir",
    ["true", 1, 0, None, [], {}, ""],
)
def test_snapshot_options_bean_invalid_clean_data_dir(clean_data_dir):
    """Test that invalid cleanDataDir types raise ValueError."""
    with pytest.raises(ValueError):
        SnapshotOptionsBean(
            withRepositoryData=True,
            withSystemData=True,
            cleanDataDir=clean_data_dir,
        )


@pytest.mark.parametrize(
    "repositories",
    ["repo1", 123, {"repo": "value"}, ("repo1", "repo2")],
)
def test_snapshot_options_bean_invalid_repositories_type(repositories):
    """Test that invalid repositories types (non-list) raise ValueError."""
    with pytest.raises(ValueError):
        SnapshotOptionsBean(
            withRepositoryData=True,
            withSystemData=True,
            cleanDataDir=True,
            repositories=repositories,
        )


@pytest.mark.parametrize(
    "repositories",
    [
        [123, "repo2"],
        ["repo1", None],
        ["repo1", ["nested"]],
        [True, False],
    ],
)
def test_snapshot_options_bean_invalid_repositories_elements(repositories):
    """Test that invalid repository element types raise ValueError."""
    with pytest.raises(ValueError):
        SnapshotOptionsBean(
            withRepositoryData=True,
            withSystemData=True,
            cleanDataDir=True,
            repositories=repositories,
        )


def test_snapshot_options_bean_multiple_invalid_fields():
    """Test that multiple invalid fields are collected in the error."""
    with pytest.raises(ValueError) as exc_info:
        SnapshotOptionsBean(
            withRepositoryData="invalid",
            withSystemData=123,
            cleanDataDir=None,
            repositories="not_a_list",
        )

    error_tuple = exc_info.value.args
    assert "Invalid SnapshotOptionsBean values" in error_tuple[0]
    invalid_list = error_tuple[1]
    field_names = [item[0] for item in invalid_list]
    assert "withRepositoryData" in field_names
    assert "withSystemData" in field_names
    assert "cleanDataDir" in field_names
    assert "repositories" in field_names


def _create_valid_snapshot_options():
    """Helper to create a valid SnapshotOptionsBean for tests."""
    return SnapshotOptionsBean(
        withRepositoryData=True,
        withSystemData=True,
        cleanDataDir=False,
    )


@pytest.mark.parametrize(
    "operation",
    [
        "CREATE_BACKUP_IN_PROGRESS",
        "RESTORE_BACKUP_IN_PROGRESS",
        "CREATE_CLOUD_BACKUP_IN_PROGRESS",
        "RESTORE_CLOUD_BACKUP_IN_PROGRESS",
    ],
)
def test_backup_operation_bean_initialization(operation):
    """Test creating BackupOperationBean with various valid operation values."""
    snapshot_options = _create_valid_snapshot_options()
    bean = BackupOperationBean(
        id="backup-123",
        username="admin",
        operation=operation,
        affectedRepositories=["repo1", "repo2"],
        msSinceCreated=5000,
        snapshotOptions=snapshot_options,
    )

    assert bean.id == "backup-123"
    assert bean.username == "admin"
    assert bean.operation == operation
    assert bean.affectedRepositories == ["repo1", "repo2"]
    assert bean.msSinceCreated == 5000
    assert bean.snapshotOptions == snapshot_options
    assert bean.nodePerformingClusterBackup is None


def test_backup_operation_bean_with_node_performing_cluster_backup():
    """Test creating BackupOperationBean with optional nodePerformingClusterBackup."""
    snapshot_options = _create_valid_snapshot_options()
    bean = BackupOperationBean(
        id="backup-456",
        username="admin",
        operation="CREATE_BACKUP_IN_PROGRESS",
        affectedRepositories=["repo1"],
        msSinceCreated=1000,
        snapshotOptions=snapshot_options,
        nodePerformingClusterBackup="node-1",
    )

    assert bean.nodePerformingClusterBackup == "node-1"


def test_backup_operation_bean_frozen():
    """Test that BackupOperationBean is immutable."""
    snapshot_options = _create_valid_snapshot_options()
    bean = BackupOperationBean(
        id="backup-123",
        username="admin",
        operation="CREATE_BACKUP_IN_PROGRESS",
        affectedRepositories=["repo1"],
        msSinceCreated=5000,
        snapshotOptions=snapshot_options,
    )
    with pytest.raises(AttributeError):
        bean.id = "new-id"


@pytest.mark.parametrize(
    "id_value",
    [123, None, [], {}, True, 1.5],
)
def test_backup_operation_bean_invalid_id(id_value):
    """Test that invalid id types raise ValueError."""
    snapshot_options = _create_valid_snapshot_options()
    with pytest.raises(ValueError):
        BackupOperationBean(
            id=id_value,
            username="admin",
            operation="CREATE_BACKUP_IN_PROGRESS",
            affectedRepositories=["repo1"],
            msSinceCreated=5000,
            snapshotOptions=snapshot_options,
        )


@pytest.mark.parametrize(
    "username",
    [123, None, [], {}, True, 1.5],
)
def test_backup_operation_bean_invalid_username(username):
    """Test that invalid username types raise ValueError."""
    snapshot_options = _create_valid_snapshot_options()
    with pytest.raises(ValueError):
        BackupOperationBean(
            id="backup-123",
            username=username,
            operation="CREATE_BACKUP_IN_PROGRESS",
            affectedRepositories=["repo1"],
            msSinceCreated=5000,
            snapshotOptions=snapshot_options,
        )


@pytest.mark.parametrize(
    "operation",
    [
        "INVALID_OPERATION",
        "CREATE_BACKUP",
        "create_backup_in_progress",
        "",
        None,
        123,
        [],
        {},
    ],
)
def test_backup_operation_bean_invalid_operation(operation):
    """Test that invalid operation values raise ValueError."""
    snapshot_options = _create_valid_snapshot_options()
    with pytest.raises(ValueError):
        BackupOperationBean(
            id="backup-123",
            username="admin",
            operation=operation,
            affectedRepositories=["repo1"],
            msSinceCreated=5000,
            snapshotOptions=snapshot_options,
        )


@pytest.mark.parametrize(
    "affected_repositories",
    ["repo1", 123, {"repo": "value"}, ("repo1", "repo2"), None],
)
def test_backup_operation_bean_invalid_affected_repositories_type(
    affected_repositories,
):
    """Test that invalid affectedRepositories types (non-list) raise ValueError."""
    snapshot_options = _create_valid_snapshot_options()
    with pytest.raises(ValueError):
        BackupOperationBean(
            id="backup-123",
            username="admin",
            operation="CREATE_BACKUP_IN_PROGRESS",
            affectedRepositories=affected_repositories,
            msSinceCreated=5000,
            snapshotOptions=snapshot_options,
        )


@pytest.mark.parametrize(
    "affected_repositories",
    [
        [123, "repo2"],
        ["repo1", None],
        ["repo1", ["nested"]],
        [True, False],
    ],
)
def test_backup_operation_bean_invalid_affected_repositories_elements(
    affected_repositories,
):
    """Test that invalid affectedRepositories element types raise ValueError."""
    snapshot_options = _create_valid_snapshot_options()
    with pytest.raises(ValueError):
        BackupOperationBean(
            id="backup-123",
            username="admin",
            operation="CREATE_BACKUP_IN_PROGRESS",
            affectedRepositories=affected_repositories,
            msSinceCreated=5000,
            snapshotOptions=snapshot_options,
        )


@pytest.mark.parametrize(
    "ms_since_created",
    ["5000", 5000.5, None, [], {}, True],
)
def test_backup_operation_bean_invalid_ms_since_created(ms_since_created):
    """Test that invalid msSinceCreated types raise ValueError."""
    snapshot_options = _create_valid_snapshot_options()
    with pytest.raises(ValueError):
        BackupOperationBean(
            id="backup-123",
            username="admin",
            operation="CREATE_BACKUP_IN_PROGRESS",
            affectedRepositories=["repo1"],
            msSinceCreated=ms_since_created,
            snapshotOptions=snapshot_options,
        )


@pytest.mark.parametrize(
    "snapshot_options",
    [
        {"withRepositoryData": True, "withSystemData": True, "cleanDataDir": False},
        "invalid",
        123,
        None,
        [],
        True,
    ],
)
def test_backup_operation_bean_invalid_snapshot_options(snapshot_options):
    """Test that invalid snapshotOptions types raise ValueError."""
    with pytest.raises(ValueError):
        BackupOperationBean(
            id="backup-123",
            username="admin",
            operation="CREATE_BACKUP_IN_PROGRESS",
            affectedRepositories=["repo1"],
            msSinceCreated=5000,
            snapshotOptions=snapshot_options,
        )


@pytest.mark.parametrize(
    "node_performing_cluster_backup",
    [123, [], {}, True, 1.5],
)
def test_backup_operation_bean_invalid_node_performing_cluster_backup(
    node_performing_cluster_backup,
):
    """Test that invalid nodePerformingClusterBackup types raise ValueError."""
    snapshot_options = _create_valid_snapshot_options()
    with pytest.raises(ValueError):
        BackupOperationBean(
            id="backup-123",
            username="admin",
            operation="CREATE_BACKUP_IN_PROGRESS",
            affectedRepositories=["repo1"],
            msSinceCreated=5000,
            snapshotOptions=snapshot_options,
            nodePerformingClusterBackup=node_performing_cluster_backup,
        )


def test_backup_operation_bean_multiple_invalid_fields():
    """Test that multiple invalid fields are collected in the error."""
    with pytest.raises(ValueError) as exc_info:
        BackupOperationBean(
            id=123,
            username=None,
            operation="INVALID",
            affectedRepositories="not_a_list",
            msSinceCreated="5000",
            snapshotOptions="invalid",
            nodePerformingClusterBackup=123,
        )

    error_tuple = exc_info.value.args
    assert "Invalid BackupOperationBean values" in error_tuple[0]
    invalid_list = error_tuple[1]
    field_names = [item[0] for item in invalid_list]
    assert "id" in field_names
    assert "username" in field_names
    assert "operation" in field_names
    assert "affectedRepositories" in field_names
    assert "msSinceCreated" in field_names
    assert "snapshotOptions" in field_names
    assert "nodePerformingClusterBackup" in field_names


def test_backup_operation_bean_empty_affected_repositories():
    """Test that empty affectedRepositories list is valid."""
    snapshot_options = _create_valid_snapshot_options()
    bean = BackupOperationBean(
        id="backup-123",
        username="admin",
        operation="CREATE_BACKUP_IN_PROGRESS",
        affectedRepositories=[],
        msSinceCreated=5000,
        snapshotOptions=snapshot_options,
    )

    assert bean.affectedRepositories == []


@pytest.mark.parametrize(
    "operation",
    [
        "CREATE_BACKUP_IN_PROGRESS",
        "RESTORE_BACKUP_IN_PROGRESS",
        "CREATE_CLOUD_BACKUP_IN_PROGRESS",
        "RESTORE_CLOUD_BACKUP_IN_PROGRESS",
    ],
)
def test_backup_operation_bean_from_dict(operation):
    """Test creating BackupOperationBean from a valid dict."""
    data = {
        "id": "backup-123",
        "username": "admin",
        "operation": operation,
        "affectedRepositories": ["repo1", "repo2"],
        "msSinceCreated": 5000,
        "snapshotOptions": {
            "withRepositoryData": True,
            "withSystemData": True,
            "cleanDataDir": False,
            "repositories": None,
        },
    }

    bean = BackupOperationBean.from_dict(data)

    assert isinstance(bean, BackupOperationBean)
    assert bean.id == "backup-123"
    assert bean.username == "admin"
    assert bean.operation == operation
    assert bean.affectedRepositories == ["repo1", "repo2"]
    assert bean.msSinceCreated == 5000
    assert isinstance(bean.snapshotOptions, SnapshotOptionsBean)
    assert bean.snapshotOptions.withRepositoryData is True
    assert bean.snapshotOptions.withSystemData is True
    assert bean.snapshotOptions.cleanDataDir is False
    assert bean.nodePerformingClusterBackup is None


def test_backup_operation_bean_from_dict_with_node_performing_cluster_backup():
    """Test creating BackupOperationBean from dict with optional nodePerformingClusterBackup."""
    data = {
        "id": "backup-456",
        "username": "admin",
        "operation": "CREATE_BACKUP_IN_PROGRESS",
        "affectedRepositories": ["repo1"],
        "msSinceCreated": 1000,
        "snapshotOptions": {
            "withRepositoryData": True,
            "withSystemData": False,
            "cleanDataDir": True,
            "repositories": ["repo1"],
        },
        "nodePerformingClusterBackup": "node-1",
    }

    bean = BackupOperationBean.from_dict(data)

    assert bean.nodePerformingClusterBackup == "node-1"
    assert bean.snapshotOptions.repositories == ["repo1"]


def test_backup_operation_bean_from_dict_missing_key():
    """Test that from_dict raises KeyError for missing required keys."""
    data = {
        "id": "backup-123",
        "username": "admin",
        # Missing operation, affectedRepositories, msSinceCreated, snapshotOptions
    }

    with pytest.raises(KeyError):
        BackupOperationBean.from_dict(data)


def test_backup_operation_bean_from_dict_invalid_nested_data():
    """Test that from_dict raises ValueError for invalid nested data types."""
    data = {
        "id": "backup-123",
        "username": "admin",
        "operation": "CREATE_BACKUP_IN_PROGRESS",
        "affectedRepositories": ["repo1"],
        "msSinceCreated": 5000,
        "snapshotOptions": {
            "withRepositoryData": "invalid",  # Should be bool
            "withSystemData": True,
            "cleanDataDir": False,
            "repositories": None,
        },
    }

    with pytest.raises(ValueError):
        BackupOperationBean.from_dict(data)
