from __future__ import annotations

import io
import pathlib
from unittest.mock import ANY, Mock

import pytest

from rdflib import Dataset, Graph
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    import httpx
    from rdflib.contrib.rdf4j.client import Repository


@pytest.mark.parametrize("class_type", [Graph, Dataset])
def test_repo_upload_graph(
    repo: Repository, monkeypatch: pytest.MonkeyPatch, class_type: type[Graph | Dataset]
):
    """Test that the upload method handles Graphs and Datasets as data input."""
    file_path = pathlib.Path(__file__).parent.parent.parent / "data/quads-1.nq"
    mock = Mock()
    monkeypatch.setattr(httpx.Client, "post", mock)
    headers = {
        "Content-Type": "application/n-quads",
    }
    params: dict[str, str] = {}
    graph = class_type().parse(file_path)
    repo.upload(graph)
    mock.assert_called_once_with(
        "/repositories/test-repo/statements",
        headers=headers,
        params=params,
        content=ANY,
    )
    call_args = mock.call_args
    content = call_args.kwargs["content"]
    assert isinstance(content, io.BytesIO)
    assert content.closed


def test_repo_upload_file_path(repo: Repository, monkeypatch: pytest.MonkeyPatch):
    """Test that a file path is treated as a file to be read and closed when done."""
    file_path = pathlib.Path(__file__).parent.parent.parent / "data/quads-1.nq"
    mock = Mock()
    monkeypatch.setattr(httpx.Client, "post", mock)
    headers = {
        "Content-Type": "application/n-quads",
    }
    params: dict[str, str] = {}
    repo.upload(str(file_path), content_type="application/n-quads")
    mock.assert_called_once_with(
        "/repositories/test-repo/statements",
        headers=headers,
        params=params,
        content=ANY,
    )
    call_args = mock.call_args
    content = call_args.kwargs["content"]
    assert hasattr(content, "read")
    assert hasattr(content, "name")
    assert content.name == str(file_path)
    assert content.closed


def test_repo_upload_buffered_reader(repo: Repository, monkeypatch: pytest.MonkeyPatch):
    """Test that a file-like object is read and not closed when done."""
    file_path = pathlib.Path(__file__).parent.parent.parent / "data/quads-1.nq"
    mock = Mock()
    monkeypatch.setattr(httpx.Client, "post", mock)
    with open(file_path, "rb") as file:
        headers = {
            "Content-Type": "application/n-quads",
        }
        params: dict[str, str] = {}
        repo.upload(file, content_type="application/n-quads")
        mock.assert_called_once_with(
            "/repositories/test-repo/statements",
            headers=headers,
            params=params,
            content=file,
        )
        call_args = mock.call_args
        content = call_args.kwargs["content"]
        assert not content.closed


@pytest.mark.parametrize(
    "data",
    [
        "<http://example.com/s> <http://example.com/p> <http://example.com/o> .",
        b"<http://example.com/s> <http://example.com/p> <http://example.com/o> .",
    ],
)
def test_repo_upload_data(
    repo: Repository, data: str | bytes, monkeypatch: pytest.MonkeyPatch
):
    """Test that str and bytes data is treated as content."""
    mock = Mock()
    monkeypatch.setattr(httpx.Client, "post", mock)
    headers = {
        "Content-Type": "application/n-quads",
    }
    params: dict[str, str] = {}
    repo.upload(data, content_type="application/n-quads")
    mock.assert_called_once_with(
        "/repositories/test-repo/statements",
        headers=headers,
        params=params,
        content=ANY,
    )
    call_args = mock.call_args
    content = call_args.kwargs["content"]
    assert isinstance(content, io.BytesIO)
    assert not content.closed


@pytest.mark.parametrize(
    "base_uri, expected_params",
    [
        ["", {"baseURI": ""}],
        ["http://example.com", {"baseURI": "http://example.com"}],
        [None, {}],
    ],
)
def test_repo_upload_base_uri(
    repo: Repository,
    base_uri: str | None,
    expected_params: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that base_uri is passed as a query parameter."""
    mock = Mock()
    monkeypatch.setattr(httpx.Client, "post", mock)
    headers = {
        "Content-Type": "application/n-quads",
    }
    repo.upload("", base_uri=base_uri, content_type="application/n-quads")
    mock.assert_called_once_with(
        "/repositories/test-repo/statements",
        headers=headers,
        params=expected_params,
        content=ANY,
    )


def test_repo_upload_nonexistent_file_path(
    repo: Repository, monkeypatch: pytest.MonkeyPatch
):
    """Test that a string that looks like a file path but doesn't exist is treated as content."""
    mock = Mock()
    monkeypatch.setattr(httpx.Client, "post", mock)
    headers = {
        "Content-Type": "application/n-quads",
    }
    params: dict[str, str] = {}
    nonexistent_path = "/nonexistent/path/file.nq"
    repo.upload(nonexistent_path, content_type="application/n-quads")
    mock.assert_called_once_with(
        "/repositories/test-repo/statements",
        headers=headers,
        params=params,
        content=ANY,
    )
    call_args = mock.call_args
    content = call_args.kwargs["content"]
    assert isinstance(content, io.BytesIO)
    assert not content.closed


def test_repo_upload_string_with_newline(
    repo: Repository, monkeypatch: pytest.MonkeyPatch
):
    """Test that a string with newlines is treated as content, not a file path."""
    mock = Mock()
    monkeypatch.setattr(httpx.Client, "post", mock)
    headers = {
        "Content-Type": "application/n-quads",
    }
    params: dict[str, str] = {}
    data_with_newline = "<http://example.com/s> <http://example.com/p> <http://example.com/o> .\n<http://example.com/s2> <http://example.com/p2> <http://example.com/o2> ."
    repo.upload(data_with_newline, content_type="application/n-quads")
    mock.assert_called_once_with(
        "/repositories/test-repo/statements",
        headers=headers,
        params=params,
        content=ANY,
    )
    call_args = mock.call_args
    content = call_args.kwargs["content"]
    assert isinstance(content, io.BytesIO)
    assert not content.closed


def test_repo_upload_long_string(repo: Repository, monkeypatch: pytest.MonkeyPatch):
    """Test that a string longer than 260 characters is treated as content, not a file path."""
    mock = Mock()
    monkeypatch.setattr(httpx.Client, "post", mock)
    headers = {
        "Content-Type": "application/n-quads",
    }
    params: dict[str, str] = {}
    # Create a string longer than 260 characters
    long_string = "a" * 261
    repo.upload(long_string, content_type="application/n-quads")
    mock.assert_called_once_with(
        "/repositories/test-repo/statements",
        headers=headers,
        params=params,
        content=ANY,
    )
    call_args = mock.call_args
    content = call_args.kwargs["content"]
    assert isinstance(content, io.BytesIO)
    assert not content.closed
