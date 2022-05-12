from test.utils.httpservermock import (
    BaseHTTPServerMock,
    MethodName,
    MockHTTPResponse,
    ServedBaseHTTPServerMock,
    ctx_http_server,
)
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest


def test_base() -> None:
    httpmock = BaseHTTPServerMock()
    with ctx_http_server(httpmock.Handler) as server:
        url = "http://{}:{}".format(*server.server_address)
        # add two responses the server should give:
        httpmock.responses[MethodName.GET].append(
            MockHTTPResponse(404, "Not Found", b"gone away", {})
        )
        httpmock.responses[MethodName.GET].append(
            MockHTTPResponse(200, "OK", b"here it is", {})
        )

        # send a request to get the first response
        with pytest.raises(HTTPError) as raised:
            urlopen(f"{url}/bad/path")
        assert raised.value.code == 404

        # get and validate request that the mock received
        req = httpmock.requests[MethodName.GET].pop(0)
        assert req.path == "/bad/path"

        # send a request to get the second response
        resp = urlopen(f"{url}/")
        assert resp.status == 200
        assert resp.read() == b"here it is"

        req = httpmock.requests[MethodName.GET].pop(0)
        assert req.path == "/"

        assert httpmock.call_count == 2

        httpmock.reset()

        httpmock.responses[MethodName.PATCH].append(
            MockHTTPResponse(
                200, "OK", b"patched", {"Authorization": ["Bearer faketoken"]}
            )
        )

        send_req = Request(f"{url}/", method=MethodName.PATCH.name, data=b"new value")
        resp = urlopen(send_req)
        assert resp.status == 200
        assert resp.read() == b"patched"
        assert resp.headers.get("Authorization") == "Bearer faketoken"

        req = httpmock.requests[MethodName.PATCH].pop(0)
        assert req.path == "/"
        assert req.body == send_req.data

        assert httpmock.call_count == 1


def test_served() -> None:
    with ServedBaseHTTPServerMock() as httpmock:
        httpmock.responses[MethodName.GET].append(
            MockHTTPResponse(404, "Not Found", b"gone away", {})
        )
        httpmock.responses[MethodName.GET].append(
            MockHTTPResponse(200, "OK", b"here it is", {})
        )

        # send a request to get the first response
        with pytest.raises(HTTPError) as raised:
            urlopen(f"{httpmock.url}/bad/path")
        assert raised.value.code == 404

        # get and validate request that the mock received
        req = httpmock.requests[MethodName.GET].pop(0)
        assert req.path == "/bad/path"

        # send a request to get the second response
        resp = urlopen(f"{httpmock.url}/")
        assert resp.status == 200
        assert resp.read() == b"here it is"

        httpmock.responses[MethodName.GET].append(
            MockHTTPResponse(404, "Not Found", b"gone away", {})
        )
        httpmock.responses[MethodName.GET].append(
            MockHTTPResponse(200, "OK", b"here it is", {})
        )
