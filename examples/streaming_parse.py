"""Convert RDF to N-Quads without retaining the input graph.

Run ``python -m examples.streaming_parse input.rdf --format xml > output.nq``.
Supported input formats are N-Triples, N-Quads and RDF/XML. Callbacks write
each statement synchronously, so a slow output also slows reading the input.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from typing import TextIO

from rdflib.graph import _TripleType
from rdflib.sink import Sink
from rdflib.term import Identifier


def convert(source: pathlib.Path, destination: TextIO, format: str = "nt") -> int:
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
    parser.add_argument("source", type=pathlib.Path)
    parser.add_argument("--format", choices=["nt", "nquads", "xml"], default="nt")
    options = parser.parse_args()
    count = convert(options.source, sys.stdout, options.format)
    print(f"Processed {count} statements", file=sys.stderr)
