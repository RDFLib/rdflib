from __future__ import annotations

from dataclasses import replace
from unittest.mock import Mock

import pytest

from rdflib.contrib.graphdb.exceptions import (
    BadRequestError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    ResponseFormatError,
    UnauthorisedError,
)
from rdflib.contrib.graphdb.models import ImportSettings, ParserSettings
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.graphdb.client import GraphDBClient, Repository


@pytest.fixture
def repository(client: GraphDBClient) -> Repository:
    """Create a Repository instance for testing."""
    return Repository("test-repo", client.http_client)


def _make_import_settings() -> ImportSettings:
    """Return a sample ImportSettings instance for testing."""
    return ImportSettings(
        name="test-file.ttl",
        status="NONE",
        message="",
        context=None,
        replaceGraphs=[],
        baseURI=None,
        forceSerial=False,
        type="file",
        format=None,
        data=None,
        parserSettings=ParserSettings(),
        size="1024",
        lastModified=1704067200000,
        imported=0,
        addedStatements=0,
        removedStatements=0,
        numReplacedGraphs=0,
    )


def _to_json_response(settings: list[ImportSettings]) -> list[dict]:
    """Convert ImportSettings instances to JSON-like dicts (as returned by API)."""
    result = []
    for s in settings:
        d = s.as_dict()
        # The parserSettings is already serialized as a dict by as_dict()
        result.append(d)
    return result


def test_get_server_import_files_returns_list(
    repository: Repository,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get_server_import_files returns a list of ImportSettings."""
    import_settings = [_make_import_settings()]
    json_response = _to_json_response(import_settings)

    mock_response = Mock(spec=httpx.Response, json=lambda: json_response)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = repository.get_server_import_files()

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].name == "test-file.ttl"
    assert result[0].status == "NONE"
    mock_httpx_get.assert_called_once_with(
        "/rest/repositories/test-repo/import/server",
        headers={"Accept": "application/json"},
    )


def test_get_server_import_files_returns_empty_list(
    repository: Repository,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get_server_import_files returns an empty list when no files are available."""
    mock_response = Mock(spec=httpx.Response, json=lambda: [])
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = repository.get_server_import_files()

    assert result == []


@pytest.mark.parametrize(
    "status_code, exception_class",
    [
        (401, UnauthorisedError),
        (403, ForbiddenError),
        (500, InternalServerError),
    ],
)
def test_get_server_import_files_http_errors(
    repository: Repository,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    exception_class: type,
):
    """Test that get_server_import_files raises appropriate exceptions for HTTP errors."""
    mock_response = Mock(spec=httpx.Response, status_code=status_code, text="Error")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(exception_class):
        repository.get_server_import_files()


@pytest.mark.parametrize(
    "status_code",
    [400, 404, 409, 502, 503],
)
def test_get_server_import_files_reraises_other_http_errors(
    repository: Repository,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    """Test that get_server_import_files re-raises HTTPStatusError for unhandled status codes."""
    mock_response = Mock(spec=httpx.Response, status_code=status_code, text="Error")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(httpx.HTTPStatusError):
        repository.get_server_import_files()


def test_get_server_import_files_raises_response_format_error_on_json_parse_error(
    repository: Repository,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get_server_import_files raises ResponseFormatError when JSON parsing fails."""
    mock_response = Mock(spec=httpx.Response)
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ResponseFormatError, match="Failed to parse response"):
        repository.get_server_import_files()


def test_get_server_import_files_raises_response_format_error_on_invalid_data(
    repository: Repository,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get_server_import_files raises ResponseFormatError when data is invalid."""
    # Return a list with invalid item (missing required fields)
    mock_response = Mock(spec=httpx.Response, json=lambda: [{"name": "test.ttl"}])
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ResponseFormatError, match="Failed to parse response"):
        repository.get_server_import_files()


def test_get_server_import_files_parses_multiple_files(
    repository: Repository,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get_server_import_files correctly parses multiple files."""
    first = _make_import_settings()
    second = replace(
        first,
        name="another-file.ttl",
        status="DONE",
        addedStatements=100,
    )
    json_response = _to_json_response([first, second])

    mock_response = Mock(spec=httpx.Response, json=lambda: json_response)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = repository.get_server_import_files()

    assert len(result) == 2
    assert result[0].name == "test-file.ttl"
    assert result[0].status == "NONE"
    assert result[1].name == "another-file.ttl"
    assert result[1].status == "DONE"
    assert result[1].addedStatements == 100


@pytest.mark.parametrize(
    "status",
    ["PENDING", "IMPORTING", "DONE", "ERROR", "NONE", "INTERRUPTING"],
)
def test_get_server_import_files_parses_all_valid_statuses(
    repository: Repository,
    monkeypatch: pytest.MonkeyPatch,
    status: str,
):
    """Test that get_server_import_files correctly parses all valid status values."""
    settings = replace(_make_import_settings(), status=status)  # type: ignore[arg-type]
    json_response = _to_json_response([settings])

    mock_response = Mock(spec=httpx.Response, json=lambda: json_response)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = repository.get_server_import_files()

    assert result[0].status == status


# --- Tests for import_server_import_file ---


def test_import_server_import_file_success(
    repository: Repository,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that import_server_import_file successfully posts a server import request."""
    from rdflib.contrib.graphdb.models import ServerImportBody

    mock_response = Mock(spec=httpx.Response)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    body = ServerImportBody(fileNames=["test-file.ttl"])
    repository.import_server_import_file(body)

    mock_httpx_post.assert_called_once_with(
        "/rest/repositories/test-repo/import/server",
        headers={"Content-Type": "application/json"},
        json={"fileNames": ["test-file.ttl"]},
    )


def test_import_server_import_file_with_import_settings(
    repository: Repository,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that import_server_import_file correctly serializes importSettings."""
    from rdflib.contrib.graphdb.models import ServerImportBody

    mock_response = Mock(spec=httpx.Response)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    import_settings = _make_import_settings()
    body = ServerImportBody(fileNames=["test-file.ttl"], importSettings=import_settings)
    repository.import_server_import_file(body)

    call_kwargs = mock_httpx_post.call_args.kwargs
    assert "importSettings" in call_kwargs["json"]
    assert call_kwargs["json"]["fileNames"] == ["test-file.ttl"]


@pytest.mark.parametrize(
    "status_code, exception_class",
    [
        (400, BadRequestError),
        (401, UnauthorisedError),
        (403, ForbiddenError),
        (404, NotFoundError),
    ],
)
def test_import_server_import_file_http_errors(
    repository: Repository,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    exception_class: type,
):
    """Test that import_server_import_file raises appropriate exceptions for HTTP errors."""
    from rdflib.contrib.graphdb.models import ServerImportBody

    mock_response = Mock(spec=httpx.Response, status_code=status_code, text="Error")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    body = ServerImportBody(fileNames=["test-file.ttl"])
    with pytest.raises(exception_class):
        repository.import_server_import_file(body)


@pytest.mark.parametrize(
    "status_code",
    [500, 502, 503],
)
def test_import_server_import_file_reraises_other_http_errors(
    repository: Repository,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    """Test that import_server_import_file re-raises HTTPStatusError for unhandled status codes."""
    from rdflib.contrib.graphdb.models import ServerImportBody

    mock_response = Mock(spec=httpx.Response, status_code=status_code, text="Error")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    body = ServerImportBody(fileNames=["test-file.ttl"])
    with pytest.raises(httpx.HTTPStatusError):
        repository.import_server_import_file(body)
