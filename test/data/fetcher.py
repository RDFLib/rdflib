#!/usr/bin/env python
import argparse
import enum
import logging
import os
import random
import re
import shutil
import string
import sys
import tarfile
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from tarfile import TarFile, TarInfo
from tempfile import TemporaryDirectory, mkdtemp
from typing import IO, Generator, List, Pattern, Union
from urllib.request import Request, urlopen
from zipfile import ZipFile, ZipInfo

DATA_PATH = Path(__file__).parent


@dataclass
class Resource:
    remote: Union[str, Request]
    local_path: Path

    def fetch(self, tmp_path: Path) -> None:
        raise NotImplementedError()


@dataclass
class FileResource(Resource):
    def fetch(self, tmp_path: Path) -> None:
        if self.local_path.exists():
            logging.debug("info %s", self.local_path)
            os.remove(self.local_path)

        with ExitStack() as xstack:
            request = (
                self.remote
                if isinstance(self.remote, Request)
                else Request(self.remote)
            )
            response = urlopen(request)
            remote_io: IO[bytes] = xstack.enter_context(response)

            local_io = xstack.enter_context(self.local_path.open("wb+"))
            shutil.copyfileobj(remote_io, local_io)

        logging.info("Downloaded %s to %s", request.full_url, self.local_path)


class ArchiveType(enum.Enum):
    ZIP = "zip"
    TAR_GZ = "tar.gz"


@dataclass
class ArchiveResource(Resource):
    type: ArchiveType
    pattern: Pattern[str]
    clean_local: bool = True

    def fetch(self, tmp_path: Path) -> None:
        if self.clean_local and self.local_path.exists():
            logging.debug("info %s", self.local_path)
            shutil.rmtree(self.local_path)
        with ExitStack() as xstack:
            request = (
                self.remote
                if isinstance(self.remote, Request)
                else Request(self.remote)
            )
            response = urlopen(request)
            remote_io: IO[bytes] = xstack.enter_context(response)
            name = (
                "".join(
                    random.choices(
                        string.ascii_uppercase + string.digits + string.ascii_lowercase,
                        k=10,
                    )
                )
                + f".{self.type.value}"
            )
            tmp_file = tmp_path / name
            logging.info("fetching %s to temp file %s", self.remote, tmp_file)
            with tmp_file.open("wb+") as tmp_io:
                shutil.copyfileobj(remote_io, tmp_io)

            archive_file: Union[ZipFile, TarFile]
            if self.type is ArchiveType.ZIP:
                archive_file = xstack.enter_context(ZipFile(tmp_file))
            elif self.type is ArchiveType.TAR_GZ:
                archive_file = xstack.enter_context(tarfile.open(tmp_file, mode="r:gz"))
                # archive_file = xstack.enter_context(TarFile(tmp_file, mode="r|gz"))
            else:
                raise ValueError(f"invalid type {self.type}")

            for member_info in self._member_list(archive_file):
                member_filename = self._member_filename(member_info)
                if self._member_isdir(member_info):
                    logging.debug("Ignoring directory %s", member_filename)
                    continue

                match = self.pattern.match(member_filename)
                if match is None:
                    logging.debug("Ignoring unmatched %s", member_filename)
                    continue
                groups = match.groups()
                if len(groups) > 0:
                    dest_filename = groups[0]

                member_io: IO[bytes]
                with self._member_io(archive_file, member_info) as member_io:
                    local_file = self.local_path / dest_filename
                    if not local_file.parent.exists():
                        local_file.parent.mkdir(parents=True)
                    logging.debug("writing %s to %s", member_filename, local_file)
                    local_file.write_bytes(member_io.read())

        logging.info(
            "Downloaded %s and extracted files matching %s to %s",
            request.full_url,
            self.pattern,
            self.local_path,
        )

        patch_dir = self.local_path.parent / f"{self.local_path.name}.patch"
        if patch_dir.exists():
            logging.info(
                "merging patch content from %s into %s", patch_dir, self.local_path
            )
            for child in patch_dir.glob("**/*"):
                if child.is_dir():
                    logging.debug("ignoring directory %s", child)
                    continue
                if child.name == "README.md" or child.name.endswith(".patch"):
                    logging.debug("ignoring special %s", child)
                    continue
                rel_child = child.relative_to(patch_dir)
                dest = self.local_path / rel_child
                logging.info("copying patch content %s to %s", child, dest)
                shutil.copy2(child, dest)

    @classmethod
    def _member_list(
        cls, archive: Union[ZipFile, TarFile]
    ) -> Union[List[ZipInfo], List[TarInfo]]:
        if isinstance(archive, ZipFile):
            return archive.infolist()
        return archive.getmembers()

    @classmethod
    def _member_isdir(cls, member_info: Union[ZipInfo, TarInfo]) -> bool:
        if isinstance(member_info, ZipInfo):
            return member_info.is_dir()
        return member_info.isdir()

    @classmethod
    def _member_filename(cls, member_info: Union[ZipInfo, TarInfo]) -> str:
        if isinstance(member_info, ZipInfo):
            return member_info.filename
        return member_info.name

    @classmethod
    @contextmanager
    def _member_io(
        cls, archive: Union[ZipFile, TarFile], member_info: Union[ZipInfo, TarInfo]
    ) -> Generator[IO[bytes], None, None]:
        if isinstance(archive, ZipFile):
            assert isinstance(member_info, ZipInfo)
            with archive.open(member_info) as member_io:
                yield member_io
        else:
            assert isinstance(member_info, TarInfo)
            opt_io = archive.extractfile(member_info)
            assert opt_io is not None
            yield opt_io


RESOURCES: List[Resource] = [
    ArchiveResource(
        remote="https://github.com/w3c/N3/archive/c44d123c5958ca04117e28ca3769e2c0820f72e6.zip",
        local_path=(DATA_PATH / "suites" / "w3c" / "n3"),
        type=ArchiveType.ZIP,
        pattern=re.compile(r"^[^\/]+[\/]tests[\/](.+)$"),
    ),
    ArchiveResource(
        remote="https://www.w3.org/2013/TurtleTests/TESTS.tar.gz",
        local_path=(DATA_PATH / "suites" / "w3c" / "turtle"),
        type=ArchiveType.TAR_GZ,
        pattern=re.compile(r"^[^\/]+[\/](.+)$"),
    ),
    ArchiveResource(
        remote="https://www.w3.org/2013/N-QuadsTests/TESTS.tar.gz",
        local_path=(DATA_PATH / "suites" / "w3c" / "nquads"),
        type=ArchiveType.TAR_GZ,
        pattern=re.compile(r"^(.+)$"),
    ),
    ArchiveResource(
        remote="https://www.w3.org/2013/N-TriplesTests/TESTS.tar.gz",
        local_path=(DATA_PATH / "suites" / "w3c" / "ntriples"),
        type=ArchiveType.TAR_GZ,
        pattern=re.compile(r"^(.+)$"),
    ),
    ArchiveResource(
        remote="https://www.w3.org/2013/TrigTests/TESTS.tar.gz",
        local_path=(DATA_PATH / "suites" / "w3c" / "trig"),
        type=ArchiveType.TAR_GZ,
        pattern=re.compile(r"^(.+)$"),
    ),
    ArchiveResource(
        remote="https://www.w3.org/2013/RDFXMLTests/TESTS.zip",
        local_path=(DATA_PATH / "suites" / "w3c" / "rdf-xml"),
        type=ArchiveType.ZIP,
        pattern=re.compile(r"^(.+)$"),
    ),
    ArchiveResource(
        # This is taken from a specific git commit instead of the published
        # test suite as the tests are non-normative and not considered part of
        # the test suite, so they could potentially be removed.
        remote="https://github.com/w3c/rdf-tests/archive/d2cc355bf601d8574116f3ee76ca570925f35ac3.zip",
        local_path=(DATA_PATH / "suites" / "w3c" / "rdf-xml-non-normative"),
        type=ArchiveType.ZIP,
        # Not cleaning local directory as it has a constructed manifest.
        clean_local=False,
        pattern=re.compile(
            r"^[^\/]+[\/]rdf-xml[\/]((?:rdfms-empty-property-elements/error003|rdfms-empty-property-elements/test003|rdfms-empty-property-elements/test009|rdfms-xmllang/test001|rdfms-xmllang/test002|rdfms-xml-literal-namespaces/test001|rdfms-xml-literal-namespaces/test002)[.][^.]+)$"
        ),
    ),
    ArchiveResource(
        remote="https://www.w3.org/2009/sparql/docs/tests/sparql11-test-suite-20121023.tar.gz",
        local_path=(DATA_PATH / "suites" / "w3c" / "sparql11"),
        type=ArchiveType.TAR_GZ,
        pattern=re.compile(r"^[^\/]+[\/](.+)$"),
    ),
    ArchiveResource(
        remote="https://www.w3.org/2001/sw/DataAccess/tests/data-r2.tar.gz",
        local_path=(DATA_PATH / "suites" / "w3c" / "dawg-data-r2"),
        type=ArchiveType.TAR_GZ,
        pattern=re.compile(r"^[^\/]+[\/]data-r2[\/](.+)$"),
    ),
    FileResource(
        remote=Request(
            "http://www.w3.org/2000/01/rdf-schema#", headers={"Accept": "text/turtle"}
        ),
        local_path=(DATA_PATH / "defined_namespaces/rdfs.ttl"),
    ),
    FileResource(
        remote=Request("https://www.w3.org/ns/rdftest.ttl"),
        local_path=(DATA_PATH / "defined_namespaces/rdftest.ttl"),
    ),
    FileResource(
        remote=Request("https://www.w3.org/2001/sw/DataAccess/tests/test-manifest#"),
        local_path=(DATA_PATH / "defined_namespaces/mf.ttl"),
    ),
    FileResource(
        remote=Request("https://www.w3.org/2001/sw/DataAccess/tests/test-dawg#"),
        local_path=(DATA_PATH / "defined_namespaces/dawgt.ttl"),
    ),
    FileResource(
        remote=Request("https://www.w3.org/2001/sw/DataAccess/tests/test-query#"),
        local_path=(DATA_PATH / "defined_namespaces/qt.ttl"),
    ),
    FileResource(
        remote=Request("https://www.w3.org/2009/sparql/docs/tests/test-update.n3"),
        local_path=(DATA_PATH / "defined_namespaces/ut.n3"),
    ),
]


@dataclass
class Application:
    parser: argparse.ArgumentParser = field(
        default_factory=lambda: argparse.ArgumentParser(add_help=True)
    )

    def __post_init__(self) -> None:
        parser = self.parser
        parser.add_argument(
            "-v",
            "--verbose",
            action="count",
            dest="verbosity",
            help="increase verbosity level",
        )
        parser.add_argument(
            "--keep-tmp",
            action="store_true",
            default=False,
        )
        parser.add_argument("paths", nargs="*", type=str)
        parser.set_defaults(handler=self.handle)

    def run(self, args: List[str]) -> None:
        parse_result = self.parser.parse_args(args)

        verbosity = parse_result.verbosity
        if verbosity is not None:
            root_logger = logging.getLogger("")
            root_logger.propagate = True
            new_level = (
                root_logger.getEffectiveLevel()
                - (min(1, verbosity)) * 10
                - min(max(0, verbosity - 1), 9) * 1
            )
            root_logger.setLevel(new_level)

        logging.debug(
            "args = %s, parse_result = %s, logging.level = %s",
            args,
            parse_result,
            logging.getLogger("").getEffectiveLevel(),
        )

        parse_result.handler(parse_result)

    def handle(self, parse_result: argparse.Namespace) -> None:
        logging.debug("entry ...")

        paths = {Path(path).absolute() for path in parse_result.paths}

        logging.debug("paths = %s", paths)

        if parse_result.keep_tmp:
            tmp_path = Path(mkdtemp())
        else:
            tmp_dir = TemporaryDirectory()
            tmp_path = Path(tmp_dir.name)

        for resource in RESOURCES:
            if paths:
                include = False
                for path in paths:
                    try:
                        resource.local_path.absolute().relative_to(path)
                        include = True
                    except ValueError:
                        # not relative to, ignoring
                        pass
                if not include:
                    logging.info("skipping %s", resource.local_path)
                    continue
            resource.fetch(tmp_path)


def main() -> None:
    logging.basicConfig(
        level=os.environ.get("PYLOGGING_LEVEL", logging.INFO),
        stream=sys.stderr,
        datefmt="%Y-%m-%dT%H:%M:%S",
        format=(
            "%(asctime)s.%(msecs)03d %(process)d %(thread)d %(levelno)03d:%(levelname)-8s "
            "%(name)-12s %(module)s:%(lineno)s:%(funcName)s %(message)s"
        ),
    )

    Application().run(sys.argv[1:])


if __name__ == "__main__":
    main()
