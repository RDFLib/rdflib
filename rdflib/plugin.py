from rdflib.backends import Backend
from rdflib.syntax import serializer, serializers
from rdflib.syntax import parsers

_kinds = {}
_adaptors = {}

def register(name, kind, module_path, class_name):
    _module_info = _kinds.get(kind, None)
    if _module_info is None:
        _module_info = _kinds[kind] = {}
    _module_info[name] = (module_path, class_name)

def get(name, kind):
    _module_info = _kinds.get(kind)
    if _module_info and name in _module_info:
        module_path, class_name = _module_info[name]
        module = __import__(module_path, globals(), locals(), True)
        return getattr(module, class_name)
    else:
        Adaptor = kind # TODO: look up of adaptor, for now just use kind
        try:
            Adaptee = get(name, _adaptors[kind])
        except Exception, e:
            raise Exception("could not get plugin for %s, %s: %s" % (name, kind, e))
        def const(*args, **keywords):
            return Adaptor(Adaptee(*args, **keywords))
        return const

def register_adaptor(adaptor, adaptee):
    _adaptors[adaptor] = adaptee


register_adaptor(serializer.Serializer, serializers.Serializer)
#register_adaptor(parser.Parser, parsers.Parser)


register('xml', serializers.Serializer,
         'rdflib.syntax.serializers.XMLSerializer', 'XMLSerializer')

register('pretty-xml', serializers.Serializer,
         'rdflib.syntax.serializers.PrettyXMLSerializer', 'PrettyXMLSerializer')

register('nt', serializers.Serializer,
         'rdflib.syntax.serializers.NTSerializer', 'NTSerializer')

register('xml', parsers.Parser,
         'rdflib.syntax.parsers.RDFXMLParser', 'RDFXMLParser')

register('n3', parsers.Parser,
         'rdflib.syntax.parsers.N3Parser', 'N3Parser')

register('nt', parsers.Parser,
         'rdflib.syntax.parsers.NTParser', 'NTParser')

register('n3', parsers.Parser,
         'rdflib.syntax.parsers.N3Parser', 'N3Parser')

register('default', Backend,
         'rdflib.backends.IOMemory', 'IOMemory')

register('IOMemory', Backend,
         'rdflib.backends.IOMemory', 'IOMemory')

register('Memory', Backend,
         'rdflib.backends.Memory', 'Memory')

register('Sleepycat', Backend,
         'rdflib.backends.Sleepycat', 'Sleepycat')

register('Sleepycat_new', Backend,
         'rdflib.backends.Sleepycat_new', 'Sleepycat_new')

register('ZODB', Backend,
         'rdflib.backends.ZODB', 'ZODB')

register('sqlobject', Backend,
         'rdflib.backends._sqlobject', 'SQLObject')

register('Redland', Backend,
         'rdflib.backends.Redland', 'Redland')
