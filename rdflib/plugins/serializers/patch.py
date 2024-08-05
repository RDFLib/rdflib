from __future__ import annotations

import warnings
from typing import IO, Optional
from uuid import uuid4

from rdflib import Dataset, Graph
from rdflib.plugins.serializers.nquads import _nq_row
from rdflib.plugins.serializers.nt import _nt_row
from rdflib.serializer import Serializer

add_remove_methods = {"add": "A", "remove": "D"}


class PatchSerializer(Serializer):
    """
    Creates an RDF patch file to add and remove triples/quads.
    Can either:
    - Create an add or delete patch for a single Dataset.
    - Create a patch to represent the difference between two Datasets.
    """

    def __init__(
        self,
        store: Dataset,
    ):
        self.store = store
        super().__init__(store)

    def serialize(
        self,
        stream: IO[bytes],
        base: Optional[str] = None,
        encoding: Optional[str] = None,
        operation: Optional[str] = None,
        target: Optional[Graph] = None,
        header_id: Optional[str] = None,
        header_prev: Optional[str] = None,
    ):
        if not header_id:
            header_id = f"uuid:{uuid4()}"
        encoding = self.encoding
        if base is not None:
            warnings.warn("PatchSerializer does not support base.")
        if encoding is not None and encoding.lower() != self.encoding.lower():
            warnings.warn(
                "PatchSerializer does not use custom encoding. "
                f"Given encoding was: {encoding}"
            )

        def write_header():
            stream.write(f"H id <{header_id}> .\n".encode(encoding, "replace"))
            if header_prev:
                stream.write(f"H prev <{header_prev}>\n".encode(encoding, "replace"))
            stream.write("TX .\n".encode(encoding, "replace"))

        def write_triples(contexts, op_code):
            for context in contexts:
                context_id = (
                    None
                    if context == self.store.default_context
                    else context.identifier
                )
                for triple in context:
                    stream.write(
                        _patch_row(triple, context_id, op_code).encode(
                            encoding, "replace"
                        )
                    )

        if operation:
            assert operation in add_remove_methods, f"Invalid operation: {operation}"

        write_header()
        if operation:
            operation_code = add_remove_methods.get(operation)
            write_triples(self.store.contexts(), operation_code)
        elif target:
            to_add, to_remove = self._diff(target)
            write_triples(to_add.contexts(), "A")
            write_triples(to_remove.contexts(), "D")

        stream.write("TC .\n".encode(encoding, "replace"))

    def _diff(self, target):
        rows_to_add = target - self.store
        rows_to_remove = self.store - target
        return rows_to_add, rows_to_remove


def _patch_row(triple, context_id, operation):
    if context_id:
        return f"{operation} {_nq_row(triple, context_id)}"
    else:
        return f"{operation} {_nt_row(triple)}"
