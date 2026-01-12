from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb.models import (
        RepositoryStatistics,
        RepositoryStatisticsEntityPool,
        RepositoryStatisticsQueries,
        StructuresStatistics,
    )


def test_structure_statistics_valid():
    """Test creating a valid StructuresStatistics."""
    settings = StructuresStatistics(cacheHit=100, cacheMiss=50)

    assert settings.cacheHit == 100
    assert settings.cacheMiss == 50


def test_structure_statistics_zero_values():
    """Test StructuresStatistics with zero values."""
    settings = StructuresStatistics(cacheHit=0, cacheMiss=0)

    assert settings.cacheHit == 0
    assert settings.cacheMiss == 0


def test_structure_statistics_negative_values():
    """Test StructuresStatistics with negative values (allowed as integers)."""
    settings = StructuresStatistics(cacheHit=-1, cacheMiss=-10)

    assert settings.cacheHit == -1
    assert settings.cacheMiss == -10


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


def test_repository_statistics_queries_valid():
    """Test creating a valid RepositoryStatisticsQueries."""
    queries = RepositoryStatisticsQueries(slow=10, suboptimal=5)

    assert queries.slow == 10
    assert queries.suboptimal == 5


def test_repository_statistics_queries_zero_values():
    """Test RepositoryStatisticsQueries with zero values."""
    queries = RepositoryStatisticsQueries(slow=0, suboptimal=0)

    assert queries.slow == 0
    assert queries.suboptimal == 0


def test_repository_statistics_queries_negative_values():
    """Test RepositoryStatisticsQueries with negative values (allowed as integers)."""
    queries = RepositoryStatisticsQueries(slow=-1, suboptimal=-10)

    assert queries.slow == -1
    assert queries.suboptimal == -10


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


def test_repository_statistics_entity_pool_valid():
    """Test creating a valid RepositoryStatisticsEntityPool."""
    pool = RepositoryStatisticsEntityPool(
        epoolReads=100, epoolWrites=50, epoolSize=1000
    )

    assert pool.epoolReads == 100
    assert pool.epoolWrites == 50
    assert pool.epoolSize == 1000


def test_repository_statistics_entity_pool_zero_values():
    """Test RepositoryStatisticsEntityPool with zero values."""
    pool = RepositoryStatisticsEntityPool(epoolReads=0, epoolWrites=0, epoolSize=0)

    assert pool.epoolReads == 0
    assert pool.epoolWrites == 0
    assert pool.epoolSize == 0


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


def test_repository_statistics_valid():
    """Test creating a valid RepositoryStatistics."""
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

    assert stats.queries == queries
    assert stats.entityPool == entity_pool
    assert stats.activeTransactions == 3
    assert stats.openConnections == 10


def test_repository_statistics_zero_values():
    """Test RepositoryStatistics with zero transaction/connection values."""
    queries = RepositoryStatisticsQueries(slow=0, suboptimal=0)
    entity_pool = RepositoryStatisticsEntityPool(
        epoolReads=0, epoolWrites=0, epoolSize=0
    )
    stats = RepositoryStatistics(
        queries=queries,
        entityPool=entity_pool,
        activeTransactions=0,
        openConnections=0,
    )

    assert stats.activeTransactions == 0
    assert stats.openConnections == 0


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


def test_repository_statistics_from_dict_valid():
    """Test creating RepositoryStatistics from a valid dict."""
    data = {
        "queries": {"slow": 10, "suboptimal": 5},
        "entityPool": {"epoolReads": 100, "epoolWrites": 50, "epoolSize": 1000},
        "activeTransactions": 3,
        "openConnections": 10,
    }

    stats = RepositoryStatistics.from_dict(data)

    assert isinstance(stats, RepositoryStatistics)
    assert isinstance(stats.queries, RepositoryStatisticsQueries)
    assert isinstance(stats.entityPool, RepositoryStatisticsEntityPool)
    assert stats.queries.slow == 10
    assert stats.queries.suboptimal == 5
    assert stats.entityPool.epoolReads == 100
    assert stats.entityPool.epoolWrites == 50
    assert stats.entityPool.epoolSize == 1000
    assert stats.activeTransactions == 3
    assert stats.openConnections == 10


def test_repository_statistics_from_dict_zero_values():
    """Test creating RepositoryStatistics from dict with zero values."""
    data = {
        "queries": {"slow": 0, "suboptimal": 0},
        "entityPool": {"epoolReads": 0, "epoolWrites": 0, "epoolSize": 0},
        "activeTransactions": 0,
        "openConnections": 0,
    }

    stats = RepositoryStatistics.from_dict(data)

    assert stats.queries.slow == 0
    assert stats.queries.suboptimal == 0
    assert stats.entityPool.epoolReads == 0
    assert stats.entityPool.epoolWrites == 0
    assert stats.entityPool.epoolSize == 0
    assert stats.activeTransactions == 0
    assert stats.openConnections == 0


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
