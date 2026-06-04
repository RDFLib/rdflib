"""Regression test for the "billion laughs" entity-expansion DoS in the
``xml.sax``-backed RDF/XML and TriX parsers.

Both parsers historically built their SAX reader via ``xml.sax.make_parser()``
without any entity hardening. A ~720-byte payload of seven nested entity
declarations causes the parser to allocate / spin until the OS kills it
(see ``rdflib/plugins/parsers/rdfxml.py`` and ``rdflib/plugins/parsers/trix.py``).

The hardening rejects DTD entity declarations outright, so the parsers should
either raise a SAX exception (preferred) or return quickly without expanding
the bomb. Either outcome is a pass; what must NOT happen is a multi-second
hang during parse of < 1 KiB of input.
"""

from __future__ import annotations

import platform
import signal
from xml.sax import SAXException

import pytest

from rdflib import Graph

# Seven levels of nested entity refs would expand to 10**7 copies of "lol"
# if the parser cooperated. The whole DTD is well under one kilobyte.
_BILLION_LAUGHS_DTD = b"""<!DOCTYPE rdf:RDF [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
  <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
  <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
  <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
]>"""

RDFXML_PAYLOAD = (
    b'<?xml version="1.0"?>\n'
    + _BILLION_LAUGHS_DTD
    + b'\n<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"'
    + b' xmlns:ex="http://example.org/">\n'
    + b'  <rdf:Description rdf:about="http://example.org/s">\n'
    + b"    <ex:p>&lol7;</ex:p>\n"
    + b"  </rdf:Description>\n"
    + b"</rdf:RDF>\n"
)

TRIX_PAYLOAD = (
    b'<?xml version="1.0"?>\n'
    + _BILLION_LAUGHS_DTD.replace(b"rdf:RDF", b"TriX")
    + b'\n<TriX xmlns="http://www.w3.org/2004/03/trix/trix-1/">\n'
    + b"  <graph>\n"
    + b"    <uri>http://example.org/g</uri>\n"
    + b"    <triple>\n"
    + b"      <uri>http://example.org/s</uri>\n"
    + b"      <uri>http://example.org/p</uri>\n"
    + b"      <plainLiteral>&lol7;</plainLiteral>\n"
    + b"    </triple>\n"
    + b"  </graph>\n"
    + b"</TriX>\n"
)

# signal.alarm is POSIX-only; the test still has value on the platforms that
# have it, which is what the CVE PoC ran on.
_SUPPORTS_ALARM = hasattr(signal, "SIGALRM") and platform.system() != "Windows"


class _Timeout(Exception):
    pass


def _on_alarm(signum, frame):  # pragma: no cover - signal handler
    raise _Timeout("billion-laughs payload took too long to parse")


@pytest.mark.skipif(not _SUPPORTS_ALARM, reason="requires POSIX signal.SIGALRM")
@pytest.mark.parametrize(
    "fmt,payload",
    [
        ("application/rdf+xml", RDFXML_PAYLOAD),
        ("trix", TRIX_PAYLOAD),
    ],
)
def test_billion_laughs_is_rejected_or_bounded(fmt: str, payload: bytes) -> None:
    prev = signal.signal(signal.SIGALRM, _on_alarm)
    signal.alarm(5)
    try:
        with pytest.raises(SAXException):
            Graph().parse(data=payload, format=fmt)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, prev)
