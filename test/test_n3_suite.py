import os
import logging

import pytest

log = logging.getLogger(__name__)

from .testutils import check_serialize_parse


def _get_test_files_formats():
    skiptests = []
    for f in os.listdir("test/n3"):
        if f not in skiptests:
            fpath = "test/n3/" + f
            if f.endswith(".rdf"):
                yield fpath, "xml"
            elif f.endswith(".n3"):
                yield fpath, "n3"


def all_n3_files():
    skiptests = [
        "test/n3/example-lots_of_graphs.n3",  # only n3 can serialize QuotedGraph, no point in testing roundtrip
    ]
    for fpath, fmt in _get_test_files_formats():
        if fpath in skiptests:
            log.debug("Skipping %s, known issue" % fpath)
        else:
            yield fpath, fmt


@pytest.mark.parametrize(
    "fpath,fmt",
    _get_test_files_formats(),
)
def test_n3_writing(fpath, fmt):
    check_serialize_parse(fpath, fmt, "n3")
