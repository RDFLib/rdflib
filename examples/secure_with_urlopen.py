"""
This example demonstrates how to use a custom global URL opener installed with `urllib.request.install_opener` to block access to URLs.
"""

from __future__ import annotations

import http.client
import logging
import os
import sys
from typing import Optional
from urllib.request import HTTPHandler, OpenerDirector, Request, install_opener

from rdflib import Graph


class SecuredHTTPHandler(HTTPHandler):
    """
    A HTTP handler that blocks access to URLs that end with "blocked.jsonld".
    """

    def http_open(self, req: Request) -> http.client.HTTPResponse:
        """
        Block access to URLs that end with "blocked.jsonld".

        :param req: The request to open.
        :return: The response.
        :raises PermissionError: If the URL ends with "blocked.jsonld".
        """
        if req.get_full_url().endswith("blocked.jsonld"):
            raise PermissionError("Permission denied for URL")
        return super().http_open(req)


def main() -> None:
    """
    The main code of the example.

    The important steps are:

    * Install a custom global URL opener that blocks some URLs.
    * Attempt to parse a JSON-LD document that will result in a blocked URL being accessed.
    * Verify that the URL opener blocked access to the URL.
    """

    logging.basicConfig(
        level=os.environ.get("PYTHON_LOGGING_LEVEL", logging.INFO),
        stream=sys.stderr,
        datefmt="%Y-%m-%dT%H:%M:%S",
        format=(
            "%(asctime)s.%(msecs)03d %(process)d %(thread)d %(levelno)03d:%(levelname)-8s "
            "%(name)-12s %(module)s:%(lineno)s:%(funcName)s %(message)s"
        ),
    )

    opener = OpenerDirector()
    opener.add_handler(SecuredHTTPHandler())
    install_opener(opener)

    graph = Graph()

    # Attempt to parse a JSON-LD document that will result in the blocked URL
    # being accessed.
    error: Optional[PermissionError] = None
    try:
        graph.parse(
            data=r"""{
            "@context": "http://example.org/blocked.jsonld",
            "@id": "example:subject",
            "example:predicate": { "@id": "example:object" }
        }""",
            format="json-ld",
        )
    except PermissionError as caught:
        logging.info("Permission denied: %s", caught)
        error = caught

    # `Graph.parse` would have resulted in a `PermissionError` being raised from
    # the url opener.
    assert isinstance(error, PermissionError)
    assert error.args[0] == "Permission denied for URL"


if __name__ == "__main__":
    main()
