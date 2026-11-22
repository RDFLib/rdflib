"""Convert RDF to N-Quads without retaining the input graph.

Run ``python -m examples.streaming_parse input.rdf --format xml > output.nq``.
Omit the source to run a small bundled demonstration in the selected format.
Supported input formats are N-Triples, N-Quads and RDF/XML. Callbacks write
each statement synchronously, so a slow output also slows reading the input.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from io import BytesIO
from typing import BinaryIO, TextIO

from rdflib.graph import _TripleType
from rdflib.sink import Sink
from rdflib.term import Identifier

_DEMO_INPUTS = {
    "nt": b'<urn:example:s> <urn:example:p> "Hello streaming" .\n',
    "nquads": (
        b'<urn:example:s> <urn:example:p> "Hello streaming" <urn:example:graph> .\n'
    ),
    "xml": (
        b'<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
        b'xmlns:ex="urn:example:"><rdf:Description rdf:about="urn:example:s">'
        b"<ex:p>Hello streaming</ex:p></rdf:Description></rdf:RDF>"
    ),
}


def convert(
    source: pathlib.Path | BinaryIO, destination: TextIO, format: str = "nt"
) -> int:
    """Write every parsed statement, including duplicates, and return its count."""
    count = 0

    def write(triple: _TripleType, graph: Identifier | None) -> None:
        nonlocal count
        terms = [term.n3() for term in triple]
        if graph is not None:
            terms.append(graph.n3())
        destination.write(" ".join(terms) + " .\n")
        count += 1

    Sink(write).parse(source, format=format)
    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source",
        type=pathlib.Path,
        nargs="?",
        help="input file (default: bundled demo)",
    )
    parser.add_argument("--format", choices=["nt", "nquads", "xml"], default="nt")
    options = parser.parse_args()
    if options.source is None:
        with BytesIO(_DEMO_INPUTS[options.format]) as source:
            count = convert(source, sys.stdout, options.format)
    else:
        count = convert(options.source, sys.stdout, options.format)
    print(f"Processed {count} statements", file=sys.stderr)
