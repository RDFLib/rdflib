"""
Plugin support for rdf.

There are a number of plugin points for rdf: parser, serializer,
store, query processor, and query result. Plugins can be registered
either through setuptools entry_points or by calling
rdf.plugin.register directly.

If you have a package that uses a setuptools based setup.py you can add the
following to your setup::

    entry_points = {
        'rdf.plugins.parser': [
            'nt =     rdf.plugins.parsers.ntriples:NTParser',
            ],
        'rdf.plugins.serializer': [
            'nt =     rdf.plugins.serializers.NTSerializer:NTSerializer',
            ],
        }

See the `setuptools dynamic discovery of services and plugins`__ for more
information.

.. __: http://peak.telecommunity.com/DevCenter/setuptools#dynamic-discovery-of-services-and-plugins

"""

from rdflib.store import Store
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.query import (
    ResultParser,
    ResultSerializer,
    Processor,
    Result,
    UpdateProcessor,
)
from rdflib.exceptions import Error
from typing import Type, TypeVar

__all__ = ["register", "get", "plugins", "PluginException", "Plugin", "PKGPlugin"]

entry_points = {
    "rdf.plugins.store": Store,
    "rdf.plugins.serializer": Serializer,
    "rdf.plugins.parser": Parser,
    "rdf.plugins.resultparser": ResultParser,
    "rdf.plugins.resultserializer": ResultSerializer,
    "rdf.plugins.queryprocessor": Processor,
    "rdf.plugins.queryresult": Result,
    "rdf.plugins.updateprocessor": UpdateProcessor,
}

_plugins = {}


class PluginException(Error):
    pass


class Plugin(object):
    def __init__(self, name, kind, module_path, class_name):
        self.name = name
        self.kind = kind
        self.module_path = module_path
        self.class_name = class_name
        self._class = None

    def getClass(self):
        if self._class is None:
            module = __import__(self.module_path, globals(), locals(), [""])
            self._class = getattr(module, self.class_name)
        return self._class


class PKGPlugin(Plugin):
    def __init__(self, name, kind, ep):
        self.name = name
        self.kind = kind
        self.ep = ep
        self._class = None

    def getClass(self):
        if self._class is None:
            self._class = self.ep.load()
        return self._class


def register(name: str, kind, module_path, class_name):
    """
    Register the plugin for (name, kind). The module_path and
    class_name should be the path to a plugin class.
    """
    p = Plugin(name, kind, module_path, class_name)
    _plugins[(name, kind)] = p


PluginT = TypeVar("PluginT")


def get(name: str, kind: Type[PluginT]) -> Type[PluginT]:
    """
    Return the class for the specified (name, kind). Raises a
    PluginException if unable to do so.
    """
    try:
        p = _plugins[(name, kind)]
    except KeyError:
        raise PluginException("No plugin registered for (%s, %s)" % (name, kind))
    return p.getClass()


try:
    from pkg_resources import iter_entry_points
except ImportError:
    pass  # TODO: log a message
else:
    # add the plugins specified via pkg_resources' EntryPoints.
    for entry_point, kind in entry_points.items():
        for ep in iter_entry_points(entry_point):
            _plugins[(ep.name, kind)] = PKGPlugin(ep.name, kind, ep)


def plugins(name=None, kind=None):
    """
    A generator of the plugins.

    Pass in name and kind to filter... else leave None to match all.
    """
    for p in _plugins.values():
        if (name is None or name == p.name) and (kind is None or kind == p.kind):
            yield p


# Register Store Plugins
register("default", Store, "rdflib.plugins.stores.memory", "Memory")
register("Memory", Store, "rdflib.plugins.stores.memory", "Memory")
register("SimpleMemory", Store, "rdflib.plugins.stores.memory", "SimpleMemory")
register("Auditable", Store, "rdflib.plugins.stores.auditable", "AuditableStore")
register("Concurrent", Store, "rdflib.plugins.stores.concurrent", "ConcurrentStore")
register("BerkeleyDB", Store, "rdflib.plugins.stores.berkeleydb", "BerkeleyDB")
register("SPARQLStore", Store, "rdflib.plugins.stores.sparqlstore", "SPARQLStore")
register(
    "SPARQLUpdateStore", Store, "rdflib.plugins.stores.sparqlstore", "SPARQLUpdateStore"
)

# Register Triple Serializers
register(
    "application/rdf+xml",
    Serializer,
    "rdflib.plugins.serializers.rdfxml",
    "XMLSerializer",
)
register("xml", Serializer, "rdflib.plugins.serializers.rdfxml", "XMLSerializer")
register(
    "pretty-xml", Serializer, "rdflib.plugins.serializers.rdfxml", "PrettyXMLSerializer"
)
register("text/n3", Serializer, "rdflib.plugins.serializers.n3", "N3Serializer")
register("n3", Serializer, "rdflib.plugins.serializers.n3", "N3Serializer")
register(
    "text/turtle", Serializer, "rdflib.plugins.serializers.turtle", "TurtleSerializer"
)
register("turtle", Serializer, "rdflib.plugins.serializers.turtle", "TurtleSerializer")
register("ttl", Serializer, "rdflib.plugins.serializers.turtle", "TurtleSerializer")
register(
    "application/n-triples", Serializer, "rdflib.plugins.serializers.nt", "NTSerializer"
)
register("ntriples", Serializer, "rdflib.plugins.serializers.nt", "NTSerializer")
register("nt", Serializer, "rdflib.plugins.serializers.nt", "NTSerializer")
register("nt11", Serializer, "rdflib.plugins.serializers.nt", "NT11Serializer")
register("json-ld", Serializer, "rdflib.plugins.serializers.jsonld", "JsonLDSerializer")
register(
    "application/ld+json",
    Serializer,
    "rdflib.plugins.serializers.jsonld",
    "JsonLDSerializer",
)

# Register Quad Serializers
register(
    "application/n-quads",
    Serializer,
    "rdflib.plugins.serializers.nquads",
    "NQuadsSerializer",
)
register("nquads", Serializer, "rdflib.plugins.serializers.nquads", "NQuadsSerializer")
register(
    "application/trix", Serializer, "rdflib.plugins.serializers.trix", "TriXSerializer"
)
register("trix", Serializer, "rdflib.plugins.serializers.trix", "TriXSerializer")
register(
    "application/trig", Serializer, "rdflib.plugins.serializers.trig", "TrigSerializer"
)
register("trig", Serializer, "rdflib.plugins.serializers.trig", "TrigSerializer")

# Register Triple Parsers
register("application/rdf+xml", Parser, "rdflib.plugins.parsers.rdfxml", "RDFXMLParser")
register("xml", Parser, "rdflib.plugins.parsers.rdfxml", "RDFXMLParser")
register("text/n3", Parser, "rdflib.plugins.parsers.notation3", "N3Parser")
register("n3", Parser, "rdflib.plugins.parsers.notation3", "N3Parser")
register("text/turtle", Parser, "rdflib.plugins.parsers.notation3", "TurtleParser")
register("turtle", Parser, "rdflib.plugins.parsers.notation3", "TurtleParser")
register("ttl", Parser, "rdflib.plugins.parsers.notation3", "TurtleParser")
register("application/n-triples", Parser, "rdflib.plugins.parsers.ntriples", "NTParser")
register("ntriples", Parser, "rdflib.plugins.parsers.ntriples", "NTParser")
register("nt", Parser, "rdflib.plugins.parsers.ntriples", "NTParser")
register("nt11", Parser, "rdflib.plugins.parsers.ntriples", "NTParser")
register("application/ld+json", Parser, "rdflib.plugins.parsers.jsonld", "JsonLDParser")
register("json-ld", Parser, "rdflib.plugins.parsers.jsonld", "JsonLDParser")


# Register Quad Parsers
register("application/n-quads", Parser, "rdflib.plugins.parsers.nquads", "NQuadsParser")
register("nquads", Parser, "rdflib.plugins.parsers.nquads", "NQuadsParser")
register("application/trix", Parser, "rdflib.plugins.parsers.trix", "TriXParser")
register("trix", Parser, "rdflib.plugins.parsers.trix", "TriXParser")
register("application/trig", Parser, "rdflib.plugins.parsers.trig", "TrigParser")
register("trig", Parser, "rdflib.plugins.parsers.trig", "TrigParser")

# Register SPARQL Processors
register("sparql", Result, "rdflib.plugins.sparql.processor", "SPARQLResult")
register("sparql", Processor, "rdflib.plugins.sparql.processor", "SPARQLProcessor")
register(
    "sparql",
    UpdateProcessor,
    "rdflib.plugins.sparql.processor",
    "SPARQLUpdateProcessor",
)

# Register SPARQL Result Serializers
register(
    "xml",
    ResultSerializer,
    "rdflib.plugins.sparql.results.xmlresults",
    "XMLResultSerializer",
)
register(
    "application/sparql-results+xml",
    ResultSerializer,
    "rdflib.plugins.sparql.results.xmlresults",
    "XMLResultSerializer",
)
register(
    "txt",
    ResultSerializer,
    "rdflib.plugins.sparql.results.txtresults",
    "TXTResultSerializer",
)
register(
    "json",
    ResultSerializer,
    "rdflib.plugins.sparql.results.jsonresults",
    "JSONResultSerializer",
)
register(
    "application/sparql-results+json",
    ResultSerializer,
    "rdflib.plugins.sparql.results.jsonresults",
    "JSONResultSerializer",
)
register(
    "csv",
    ResultSerializer,
    "rdflib.plugins.sparql.results.csvresults",
    "CSVResultSerializer",
)
register(
    "text/csv",
    ResultSerializer,
    "rdflib.plugins.sparql.results.csvresults",
    "CSVResultSerializer",
)

# Register SPARQL Result Parsers
register(
    "xml", ResultParser, "rdflib.plugins.sparql.results.xmlresults", "XMLResultParser"
)
register(
    "application/sparql-results+xml",
    ResultParser,
    "rdflib.plugins.sparql.results.xmlresults",
    "XMLResultParser",
)
register(
    "application/sparql-results+xml; charset=UTF-8",
    ResultParser,
    "rdflib.plugins.sparql.results.xmlresults",
    "XMLResultParser",
)
register(
    "application/rdf+xml",
    ResultParser,
    "rdflib.plugins.sparql.results.graph",
    "GraphResultParser",
)
register(
    "json",
    ResultParser,
    "rdflib.plugins.sparql.results.jsonresults",
    "JSONResultParser",
)
register(
    "application/sparql-results+json",
    ResultParser,
    "rdflib.plugins.sparql.results.jsonresults",
    "JSONResultParser",
)
register(
    "csv", ResultParser, "rdflib.plugins.sparql.results.csvresults", "CSVResultParser"
)
register(
    "text/csv",
    ResultParser,
    "rdflib.plugins.sparql.results.csvresults",
    "CSVResultParser",
)
register(
    "tsv", ResultParser, "rdflib.plugins.sparql.results.tsvresults", "TSVResultParser"
)
register(
    "text/tab-separated-values",
    ResultParser,
    "rdflib.plugins.sparql.results.tsvresults",
    "TSVResultParser",
)
