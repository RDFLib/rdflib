"""
This file provides a single function `serialize_in_chunks()` which can serialize a
Graph into a number of NT files with a maximum number of triples or maximum file size.

There is an option to preserve any prefixes declared for the original graph in the first
file, which will be a Turtle file.
"""

from pathlib import Path
import os

try:
    from rdflib import Graph, Literal
except Exception:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.absolute()))
    from rdflib import Graph, Literal

__all__ = ["serialize_in_chunks"]


def serialize_in_chunks(
    g: Graph,
    max_triples: int = 10000,
    max_file_size_kb: int = None,
    file_name_stem: str = "chunk",
    output_dir: Path = Path(__file__).parent,
    first_file_contains_prefixes: bool = False,
):
    """
    Serializes a given Graph into a series of n-triples with a given length

    max_file_size_kb:
        Maximum size per NT file in MB
        Equivalent to ~6,000 triples

    max_triples:
        Maximum size per NT file in triples
        Equivalent to lines in file

    file_name_stem:
        Prefix of each file name
        e.g. "chunk" = chunk_001.nt, chunk_002.nt...

    output_dir:
        The directory you want the files to be written to

    first_file_contains_prefixes:
        The first file created is a Turtle file containing original graph prefixes


    See ../test/test_tools/test_chunk_serializer.py for examples of this in use.
    """

    if not output_dir.is_dir():
        raise ValueError(
            "If you specify an output_dir, it must actually be a directory!")

    def _nt_row(triple):
        if isinstance(triple[2], Literal):
            return "%s %s %s .\n" % (
                triple[0].n3(),
                triple[1].n3(),
                _quote_literal(triple[2]),
            )
        else:
            return "%s %s %s .\n" % (triple[0].n3(), triple[1].n3(), triple[2].n3())

    def _quote_literal(l_):
        """
        a simpler version of term.Literal.n3()
        """

        encoded = _quote_encode(l_)

        if l_.language:
            if l_.datatype:
                raise Exception("Literal has datatype AND language!")
            return "%s@%s" % (encoded, l_.language)
        elif l_.datatype:
            return "%s^^<%s>" % (encoded, l_.datatype)
        else:
            return "%s" % encoded

    def _quote_encode(l_):
        return '"%s"' % l_.replace("\\", "\\\\").replace("\n", "\\n").replace(
            '"', '\\"'
        ).replace("\r", "\\r")

    def _start_new_file(file_no):
        fp = Path(output_dir) / f"{file_name_stem}_{str(file_no).zfill(6)}.nt"
        fh = open(fp, "a")
        return fp, fh

    def _serialize_prefixes(g):
        pres = []
        for k, v in g.namespace_manager.namespaces():
            pres.append(f"PREFIX {k}: <{v}>")

        return "\n".join(sorted(pres)) + "\n"

    if first_file_contains_prefixes:
        with open(Path(output_dir) / f"{file_name_stem}_000000.ttl", "w") as fh:
            fh.write(_serialize_prefixes(g))

    if max_file_size_kb is not None:
        file_no = 1 if first_file_contains_prefixes else 0
        for i, t in enumerate(g.triples((None, None, None))):
            if i == 0:
                fp, fh = _start_new_file(file_no)
            elif os.path.getsize(fp) >= max_file_size_kb * 1000:
                file_no += 1
                fp, fh = _start_new_file(file_no)

            fh.write(_nt_row(t))
    else:
        # count the triples in the graph
        graph_length = len(g)

        if graph_length <= max_triples:
            # the graph is less than max so just NT serialize the whole thing
            g.serialize(
                destination=Path(output_dir) / f"{file_name_stem}_all.nt",
                format="nt"
            )
        else:
            # graph_length is > max_lines, make enough files for all graph
            # no_files = math.ceil(graph_length / max_triples)
            file_no = 1 if first_file_contains_prefixes else 0
            for i, t in enumerate(g.triples((None, None, None))):
                if i % max_triples == 0:
                    fp, fh = _start_new_file(file_no)
                    file_no += 1
                fh.write(_nt_row(t))
        return
