from rdflib.namespace import Namespace

from ._DAWGT import DAWGT
from ._EARL import EARL
from ._MF import MF
from ._QT import QT
from ._RDFT import RDFT
from ._UT import UT

EGDC = Namespace("http://example.com/")
EGDO = Namespace("http://example.org/")
EGSCHEME = Namespace("example:")
EGURN = Namespace("urn:example:")


__all__ = [
    "EARL",
    "RDFT",
    "MF",
    "DAWGT",
    "QT",
    "UT",
    "EGDC",
    "EGDO",
    "EGSCHEME",
    "EGURN",
]
