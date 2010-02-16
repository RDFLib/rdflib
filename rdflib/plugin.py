"""
Plugin support for rdf.

There are a number of plugin points for rdf: parser, serializer,
store, query processor, and query result. Plugins can be registered
either through setuptools entry_points or by calling
rdf.plugin.register directly.

If you have a package that uses a setuptools based setup.py you can add the following to your setup::

    entry_points = {
        'rdf.plugins.parser': [
            'nt =     rdf.plugins.parsers.nt:NTParser',
            ],
        'rdf.plugins.serializer': [
            'nt =     rdf.plugins.serializers.NTSerializer:NTSerializer',
            ],
        }

See the `setuptools dynamic discovery of services and plugins <http://peak.telecommunity.com/DevCenter/setuptools#dynamic-discovery-of-services-and-plugins> for more information.

"""

from rdflib.store import Store
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib import query
from rdflib.exceptions import Error


entry_points = {'rdf.plugins.store': Store,
                'rdf.plugins.serializer': Serializer,
                'rdf.plugins.parser': Parser}

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


def register(name, kind, module_path, class_name):
    """
    Register the plugin for (name, kind). The module_path and
    class_name should be the path to a plugin class.
    """
    p = Plugin(name, kind, module_path, class_name)
    _plugins[(name, kind)] = p


def get(name, kind):
    """
    Return the class for the specified (name, kind). Raises a
    PluginException if unable to do so.
    """
    try:
        p = _plugins[(name, kind)]
    except KeyError, e:
        raise PluginException("No plugin registered for (%s, %s)" % (name, kind))
    return p.getClass()


try:
    from pkg_resources import iter_entry_points
except ImportError:
    pass # TODO: log a message
else:
    # add the plugins specified via pkg_resources' EntryPoints.
    for entry_point, kind in entry_points.iteritems():
        for ep in iter_entry_points(entry_point):
            _plugins[(ep.name, kind)] = PKGPlugin(ep.name, kind, ep)


def plugins(name=None, kind=None):
    """
    A generator of the plugins.

    Pass in name and kind to filter... else leave None to match all.
    """
    for p in _plugins.values():
        if (name is None or name==p.name) and (kind is None or kind==p.kind):
            yield p

register('default', Store, 'rdflib.plugins.memory', 'IOMemory')
register('IOMemory', Store, 'rdflib.plugins.memory', 'IOMemory')
register('Sleepycat', Store, 'rdflib.plugins.sleepycat', 'Sleepycat')

register('xml', Serializer, 'rdflib.plugins.serializers.rdfxml',
         'XMLSerializer')
register('n3', Serializer, 'rdflib.plugins.serializers.n3',
         'N3Serializer')
register('turtle', Serializer, 'rdflib.plugins.serializers.turtle',
         'TurtleSerializer')
register('nt', Serializer, 'rdflib.plugins.serializers.nt',
         'NTSerializer')
register('pretty-xml', Serializer,
        'rdflib.plugins.serializers.rdfxml', 'PrettyXMLSerializer')
register('trix', Serializer,
        'rdflib.plugins.serializers.trix', 'TriXSerializer')

register('application/rdf+xml', Parser,
        'rdflib.plugins.parsers.rdfxml', 'RDFXMLParser')
register('xml', Parser, 'rdflib.plugins.parsers.rdfxml', 'RDFXMLParser')
register('n3', Parser, 'rdflib.plugins.parsers.notation3', 'N3Parser')
register('nt', Parser, 'rdflib.plugins.parsers.nt', 'NTParser')
register('trix', Parser, 'rdflib.plugins.parsers.trix', 'TriXParser')
register('rdfa', Parser, 'rdflib.plugins.parsers.rdfa', 'RDFaParser')

