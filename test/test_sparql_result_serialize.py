from contextlib import ExitStack
import itertools
from typing import (
    IO,
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Set,
    TextIO,
    Union,
    cast,
)
from rdflib.query import Result, ResultRow
from test.test_serializer import DestinationFactory, DestinationType
from test.testutils import GraphHelper
from rdflib.term import Node
import unittest
from rdflib import Graph, Namespace
from tempfile import TemporaryDirectory
from pathlib import Path, PurePath
from io import BytesIO, IOBase, StringIO
import inspect

EG = Namespace("http://example.com/")


class FormatInfo(NamedTuple):
    serializer_name: str
    deserializer_name: str
    encodings: Set[str]


class FormatInfos(Dict[str, FormatInfo]):
    def add_format(
        self,
        serializer_name: str,
        deserializer_name: str,
        *,
        encodings: Set[str],
    ) -> None:
        self[serializer_name] = FormatInfo(
            serializer_name,
            deserializer_name,
            encodings,
        )

    def select(
        self,
        *,
        name: Optional[Set[str]] = None,
    ) -> Iterable[FormatInfo]:
        for format in self.values():
            if name is not None and format.serializer_name in name:
                yield format

    @classmethod
    def make(cls) -> "FormatInfos":
        result = cls()
        result.add_format("csv", "csv", encodings={"utf-8"})
        result.add_format("json", "json", encodings={"utf-8"})
        result.add_format("xml", "xml", encodings={"utf-8"})
        result.add_format("txt", "txt", encodings={"utf-8"})

        return result


format_infos = FormatInfos.make()


class ResultHelper:
    @classmethod
    def to_list(cls, result: Result) -> List[Dict[str, Node]]:
        output: List[Dict[str, Node]] = []
        row: ResultRow
        for row in result:
            output.append(row.asdict())
        return output


def check_txt(test_case: unittest.TestCase, result: Result, data: str) -> None:
    """
    This does somewhat of a smoke tests that data is the txt serialization of the
    given result. This is by no means perfect but better than nothing.
    """
    txt_lines = data.splitlines()
    test_case.assertEqual(len(txt_lines) - 2, len(result))
    test_case.assertRegex(txt_lines[1], r"^[-]+$")
    header = txt_lines[0]
    test_case.assertIsNotNone(result.vars)
    assert result.vars is not None
    for var in result.vars:
        test_case.assertIn(var, header)
    for row_index, row in enumerate(result):
        txt_row = txt_lines[row_index + 2]
        value: Node
        for key, value in row.asdict().items():
            test_case.assertIn(f"{value}", txt_row)


class TestSerializeSelect(unittest.TestCase):
    def setUp(self) -> None:
        graph = Graph()
        triples = [
            (EG["e0"], EG["a0"], EG["e1"]),
            (EG["e0"], EG["a0"], EG["e2"]),
            (EG["e0"], EG["a0"], EG["e3"]),
            (EG["e1"], EG["a1"], EG["e2"]),
            (EG["e1"], EG["a1"], EG["e3"]),
            (EG["e2"], EG["a2"], EG["e3"]),
        ]
        GraphHelper.add_triples(graph, triples)

        query = """
        PREFIX eg: <http://example.com/>
        SELECT ?subject ?predicate ?object WHERE {
            VALUES ?predicate { eg:a1 }
            ?subject ?predicate ?object
        } ORDER BY ?object
        """
        self.result = graph.query(query)
        self.result_table = [
            ["subject", "predicate", "object"],
            ["http://example.com/e1", "http://example.com/a1", "http://example.com/e2"],
            ["http://example.com/e1", "http://example.com/a1", "http://example.com/e3"],
        ]

        self._tmpdir = TemporaryDirectory()
        self.tmpdir = Path(self._tmpdir.name)

        return super().setUp()

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_str(self) -> None:
        for format in format_infos.keys():

            def check(data: str) -> None:
                with self.subTest(format=format, caller=inspect.stack()[1]):
                    self.assertIsInstance(data, str)
                    format_info = format_infos[format]
                    if format_info.deserializer_name == "txt":
                        check_txt(self, self.result, data)
                    else:
                        result_check = Result.parse(
                            StringIO(data), format=format_info.deserializer_name
                        )
                        self.assertEqual(self.result, result_check)

            if format == "txt":
                check(self.result.serialize())
                check(self.result.serialize(None, None, None))
            check(self.result.serialize(None, None, format))
            check(self.result.serialize(format=format))
            check(self.result.serialize(destination=None, format=format))
            check(self.result.serialize(destination=None, encoding=None, format=format))

    def test_bytes(self) -> None:
        for (format, encoding) in itertools.chain(
            *(
                itertools.product({format_info.serializer_name}, format_info.encodings)
                for format_info in format_infos.values()
            )
        ):

            def check(data: bytes) -> None:
                with self.subTest(format=format, caller=inspect.stack()[1]):
                    self.assertIsInstance(data, bytes)
                    format_info = format_infos[format]
                    if format_info.deserializer_name == "txt":
                        check_txt(self, self.result, data.decode(encoding))
                    else:
                        result_check = Result.parse(
                            BytesIO(data), format=format_info.deserializer_name
                        )
                        self.assertEqual(self.result, result_check)

            if format == "txt":
                check(self.result.serialize(encoding=encoding))
                check(self.result.serialize(None, encoding, None))
                check(self.result.serialize(None, encoding))
            check(self.result.serialize(None, encoding, format))
            check(self.result.serialize(format=format, encoding=encoding))
            check(
                self.result.serialize(
                    destination=None, format=format, encoding=encoding
                )
            )
            check(
                self.result.serialize(
                    destination=None, encoding=encoding, format=format
                )
            )

    def test_file(self) -> None:

        dest_factory = DestinationFactory(self.tmpdir)

        for (format, encoding, dest_type) in itertools.chain(
            *(
                itertools.product(
                    {format_info.serializer_name},
                    format_info.encodings,
                    set(DestinationType),
                )
                for format_info in format_infos.values()
            )
        ):
            with ExitStack() as stack:
                dest_path: Path
                _dest: Union[str, Path, PurePath, IO[bytes], TextIO]

                def dest() -> Union[str, Path, PurePath, IO[bytes], TextIO]:
                    nonlocal dest_path
                    nonlocal _dest
                    _dest, dest_path = dest_factory.make(dest_type, stack)
                    return _dest

                def check(none: None) -> None:
                    with self.subTest(
                        format=format,
                        encoding=encoding,
                        dest_type=dest_type,
                        caller=inspect.stack()[1],
                    ):
                        if isinstance(_dest, IOBase):  # type: ignore[unreachable]
                            _dest.flush()
                        format_info = format_infos[format]
                        data_str = dest_path.read_text(encoding=encoding)
                        if format_info.deserializer_name == "txt":
                            check_txt(self, self.result, data_str)
                        else:
                            result_check = Result.parse(
                                StringIO(data_str), format=format_info.deserializer_name
                            )
                            self.assertEqual(self.result, result_check)
                        dest_path.unlink()

                if dest_type == DestinationType.IO_BYTES:
                    check(
                        self.result.serialize(
                            cast(IO[bytes], dest()),
                            encoding,
                            format,
                        )
                    )
                    check(
                        self.result.serialize(
                            cast(IO[bytes], dest()),
                            encoding,
                            format=format,
                        )
                    )
                    check(
                        self.result.serialize(
                            cast(IO[bytes], dest()),
                            encoding=encoding,
                            format=format,
                        )
                    )
                    check(
                        self.result.serialize(
                            destination=cast(IO[bytes], dest()),
                            encoding=encoding,
                            format=format,
                        )
                    )
                check(
                    self.result.serialize(
                        destination=dest(), encoding=None, format=format
                    )
                )
                check(self.result.serialize(destination=dest(), format=format))
                check(self.result.serialize(dest(), format=format))
                check(self.result.serialize(dest(), None, format))


if __name__ == "__main__":
    unittest.main()
