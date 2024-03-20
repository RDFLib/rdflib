"""
This example demonstrates how to use `Python audit hooks
<https://docs.python.org/3/library/sys.html#sys.addaudithook>`_ to block access
to files and URLs.

It installs a audit hook with `sys.addaudithook <https://docs.python.org/3/library/sys.html#sys.addaudithook>`_ that blocks access to files and
URLs that end with ``blocked.jsonld``.

The code in the example then verifies that the audit hook is blocking access to
URLs and files as expected.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Any, Optional, Tuple

from rdflib import Graph


def audit_hook(name: str, args: Tuple[Any, ...]) -> None:
    """
    An audit hook that blocks access when an attempt is made to open a
    file or URL that ends with ``blocked.jsonld``.

    Details of the audit events can be seen in the `audit events
    table <https://docs.python.org/3/library/audit_events.html>`_.

    :param name: The name of the audit event.
    :param args: The arguments of the audit event.
    :return: `None` if the audit hook does not block access.
    :raises PermissionError: If the file or URL being accessed ends with ``blocked.jsonld``.
    """
    if name == "urllib.Request" and args[0].endswith("blocked.jsonld"):
        raise PermissionError("Permission denied for URL")
    if name == "open" and args[0].endswith("blocked.jsonld"):
        raise PermissionError("Permission denied for file")
    return None


def main() -> None:
    """
    The main code of the example.

    The important steps are:

    * Install a custom audit hook that blocks some URLs and files.
    * Attempt to parse a JSON-LD document that will result in a blocked URL being accessed.
    * Verify that the audit hook blocked access to the URL.
    * Attempt to parse a JSON-LD document that will result in a blocked file being accessed.
    * Verify that the audit hook blocked access to the file.
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

    # Install the audit hook
    sys.addaudithook(audit_hook)

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
    # the audit hook.
    assert isinstance(error, PermissionError)
    assert error.args[0] == "Permission denied for URL"

    # Attempt to parse a JSON-LD document that will result in the blocked file
    # being accessed.
    error = None
    try:
        graph.parse(
            data=r"""{
            "@context": "file:///srv/blocked.jsonld",
            "@id": "example:subject",
            "example:predicate": { "@id": "example:object" }
        }""",
            format="json-ld",
        )
    except PermissionError as caught:
        logging.info("Permission denied: %s", caught)
        error = caught

    # `Graph.parse` would have resulted in a `PermissionError` being raised from
    # the audit hook.
    assert isinstance(error, PermissionError)
    assert error.args[0] == "Permission denied for file"


if __name__ == "__main__":
    main()
