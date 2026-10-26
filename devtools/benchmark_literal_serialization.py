"""Benchmark Turtle serialization of graphs containing ordinary text literals.

Run with ``uv run python -m devtools.benchmark_literal_serialization`` on each
revision being compared. Graph construction is excluded from the timings.
"""

from __future__ import annotations

import argparse
from timeit import repeat

from rdflib import Graph, Literal, URIRef


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--triples", type=int, default=1000)
    parser.add_argument("--number", type=int, default=3)
    parser.add_argument("--repeat", type=int, default=5)
    args = parser.parse_args()
    if min(args.triples, args.number, args.repeat) < 1:
        parser.error("--triples, --number and --repeat must be positive")

    print("text\tcharacters\ttriples\tseconds per serialization (best)")
    for text_kind, character in [("ASCII", "a"), ("Unicode", "é")]:
        for length in (1000, 10_000):
            graph = Graph()
            predicate = URIRef("urn:benchmark:text")
            for index in range(args.triples):
                graph.add(
                    (
                        URIRef(f"urn:benchmark:subject:{index}"),
                        predicate,
                        Literal(character * length),
                    )
                )
            timings = repeat(
                lambda: graph.serialize(format="turtle"),
                number=args.number,
                repeat=args.repeat,
            )
            print(
                f"{text_kind}\t{length}\t{args.triples}\t"
                f"{min(timings) / args.number:.6f}"
            )


if __name__ == "__main__":
    main()
