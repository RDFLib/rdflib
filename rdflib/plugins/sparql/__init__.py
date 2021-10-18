"""
SPARQL implementation for RDFLib

.. versionadded:: 4.0
"""


SPARQL_LOAD_GRAPHS = True
"""
If True, using FROM <uri> and FROM NAMED <uri>
will load/parse more data
"""


SPARQL_DEFAULT_GRAPH_UNION = True
"""
If True - the default graph in the RDF Dataset is the union of all
named graphs (like RDFLib's ConjunctiveGraph)
"""


CUSTOM_EVALS = {}
"""
Custom evaluation functions

These must be functions taking (ctx, part) and raise
NotImplementedError if they cannot handle a certain part
"""


PLUGIN_ENTRY_POINT = "rdf.plugins.sparqleval"

import sys
from . import parser
from . import operators
from . import parserutils

from .processor import prepareQuery, processUpdate

assert parser
assert operators
assert parserutils

if sys.version_info < (3, 8):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

all_entry_points = entry_points()
if isinstance(all_entry_points, dict):
    # Prior to Python 3.10, this returns a dict instead of the selection interface
    for ep in all_entry_points.get(PLUGIN_ENTRY_POINT, []):
        CUSTOM_EVALS[ep.name] = ep.load()
else:
    for ep in all_entry_points.select(group=PLUGIN_ENTRY_POINT):
        CUSTOM_EVALS[ep.name] = ep.load()
