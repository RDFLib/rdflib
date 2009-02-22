# RDF Library

__version__ = "2.5.0"
__date__ = "not/yet/released"

import sys
# generator expressions require 2.4
assert sys.version_info >= (2,4,0), "rdflib requires Python 2.4 or higher"
del sys

import logging
_logger = logging.getLogger("rdflib")
_logger.info("version: %s" % __version__)

