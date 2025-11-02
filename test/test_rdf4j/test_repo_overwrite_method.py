from __future__ import annotations

import io
import pathlib
from typing import Iterable
from unittest.mock import ANY, Mock

import httpx
import pytest

from rdflib import BNode, IdentifiedNode, URIRef
from rdflib.contrib.rdf4j import RDF4JClient
from rdflib.contrib.rdf4j.client import Repository, RepositoryManager
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID


@pytest.fixture(scope="function")
def client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(RDF4JClient, "protocol", 12)
    with RDF4JClient("http://localhost/", auth=("admin", "admin")) as client:
        yield client


@pytest.fixture(scope="function")
def repo(client: RDF4JClient, monkeypatch: pytest.MonkeyPatch):
    with httpx.Client() as http_client:
        monkeypatch.setattr(
            RepositoryManager,
            "create",
            lambda *args, **kwargs: Repository("test-repo", http_client),
        )

        repo = client.repositories.create("test-repo", "")
        assert repo.identifier == "test-repo"
        yield repo


def test_repo_overwrite_file_path(repo: Repository, monkeypatch: pytest.MonkeyPatch):
    """Test that a file path is treated as a file to be read and closed when done."""
    file_path = pathlib.Path(__file__).parent / "data/quads-1.nq"
    mock = Mock()
    monkeypatch.setattr(httpx.Client, "put", mock)
    headers = {
        "Content-Type": "application/n-quads",
    }
    params = {}
    repo.overwrite(str(file_path), "application/n-quads")
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


def test_repo_overwrite_buffered_reader(
    repo: Repository, monkeypatch: pytest.MonkeyPatch
):
    """Test that a file-like object is read and not closed when done."""
    file_path = pathlib.Path(__file__).parent / "data/quads-1.nq"
    mock = Mock()
    monkeypatch.setattr(httpx.Client, "put", mock)
    with open(file_path, "rb") as file:
        headers = {
            "Content-Type": "application/n-quads",
        }
        params = {}
        repo.overwrite(file, "application/n-quads")
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
def test_repo_overwrite_data(
    repo: Repository, data: str | bytes, monkeypatch: pytest.MonkeyPatch
):
    """Test that str and bytes data is treated as content."""
    mock = Mock()
    monkeypatch.setattr(httpx.Client, "put", mock)
    headers = {
        "Content-Type": "application/n-quads",
    }
    params = {}
    repo.overwrite(data, "application/n-quads")
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
    "graph_name, expected_graph_name_param",
    [
        [DATASET_DEFAULT_GRAPH_ID, "null"],
        ["http://example.com/graph", "<http://example.com/graph>"],
        [URIRef("http://example.com/graph"), "<http://example.com/graph>"],
        [BNode("some-bnode"), "_:some-bnode"],
        [
            [URIRef("http://example.com/graph"), BNode("some-bnode")],
            "<http://example.com/graph>,_:some-bnode",
        ],
        [None, None],
    ],
)
def test_repo_overwrite_graph_name(
    repo: Repository,
    graph_name: IdentifiedNode | Iterable[IdentifiedNode] | str | None,
    expected_graph_name_param: str,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that graph_name is passed as a query parameter and correctly handles the different type variations."""
    mock = Mock()
    monkeypatch.setattr(httpx.Client, "put", mock)
    headers = {
        "Content-Type": "application/n-quads",
    }
    if graph_name is None:
        params = {}
    else:
        params = {"context": expected_graph_name_param}
    repo.overwrite("", "application/n-quads", graph_name)
    mock.assert_called_once_with(
        "/repositories/test-repo/statements",
        headers=headers,
        params=params,
        content=ANY,
    )


@pytest.mark.parametrize(
    "base_uri, expected_params",
    [
        ["", {"baseURI": ""}],
        ["http://example.com", {"baseURI": "http://example.com"}],
        [None, {}],
    ],
)
def test_repo_overwrite_base_uri(
    repo: Repository,
    base_uri: str | None,
    expected_params: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that base_uri is passed as a query parameter."""
    mock = Mock()
    monkeypatch.setattr(httpx.Client, "put", mock)
    headers = {
        "Content-Type": "application/n-quads",
    }
    repo.overwrite("", "application/n-quads", base_uri=base_uri)
    mock.assert_called_once_with(
        "/repositories/test-repo/statements",
        headers=headers,
        params=expected_params,
        content=ANY,
    )


def test_repo_overwrite_nonexistent_file_path(
    repo: Repository, monkeypatch: pytest.MonkeyPatch
):
    """Test that a string that looks like a file path but doesn't exist is treated as content."""
    mock = Mock()
    monkeypatch.setattr(httpx.Client, "put", mock)
    headers = {
        "Content-Type": "application/n-quads",
    }
    params = {}
    nonexistent_path = "/nonexistent/path/file.nq"
    repo.overwrite(nonexistent_path, "application/n-quads")
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


def test_repo_overwrite_string_with_newline(
    repo: Repository, monkeypatch: pytest.MonkeyPatch
):
    """Test that a string with newlines is treated as content, not a file path."""
    mock = Mock()
    monkeypatch.setattr(httpx.Client, "put", mock)
    headers = {
        "Content-Type": "application/n-quads",
    }
    params = {}
    data_with_newline = "<http://example.com/s> <http://example.com/p> <http://example.com/o> .\n<http://example.com/s2> <http://example.com/p2> <http://example.com/o2> ."
    repo.overwrite(data_with_newline, "application/n-quads")
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


def test_repo_overwrite_long_string(repo: Repository, monkeypatch: pytest.MonkeyPatch):
    """Test that a string longer than 260 characters is treated as content, not a file path."""
    mock = Mock()
    monkeypatch.setattr(httpx.Client, "put", mock)
    headers = {
        "Content-Type": "application/n-quads",
    }
    params = {}
    # Create a string longer than 260 characters
    long_string = "a" * 261
    repo.overwrite(long_string, "application/n-quads")
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


def test_repo_overwrite_graph_name_and_base_uri(
    repo: Repository, monkeypatch: pytest.MonkeyPatch
):
    """Test that both graph_name and base_uri can be provided together."""
    mock = Mock()
    monkeypatch.setattr(httpx.Client, "put", mock)
    headers = {
        "Content-Type": "application/n-quads",
    }
    params = {
        "context": "<http://example.com/graph>",
        "baseURI": "http://example.com/base",
    }
    repo.overwrite(
        "",
        "application/n-quads",
        graph_name="http://example.com/graph",
        base_uri="http://example.com/base",
    )
    mock.assert_called_once_with(
        "/repositories/test-repo/statements",
        headers=headers,
        params=params,
        content=ANY,
    )
