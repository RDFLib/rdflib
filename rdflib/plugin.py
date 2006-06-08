from rdflib.store import Store
from rdflib.syntax import serializer, serializers
from rdflib.syntax import parsers
from rdflib import sparql
from rdflib.QueryResult import QueryResult

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


register('rdf', serializers.Serializer,
         'rdflib.syntax.serializers.XMLSerializer', 'XMLSerializer')

register('xml', serializers.Serializer,
         'rdflib.syntax.serializers.XMLSerializer', 'XMLSerializer')

register('rdf/xml', serializers.Serializer,
         'rdflib.syntax.serializers.XMLSerializer', 'XMLSerializer')

register('pretty-xml', serializers.Serializer,
         'rdflib.syntax.serializers.PrettyXMLSerializer', 'PrettyXMLSerializer')

register('nt', serializers.Serializer,
         'rdflib.syntax.serializers.NTSerializer', 'NTSerializer')

register('n3', serializers.Serializer,
         'rdflib.syntax.serializers.N3Serializer', 'N3Serializer')

register('xml', parsers.Parser,
         'rdflib.syntax.parsers.RDFXMLParser', 'RDFXMLParser')

register('n3', parsers.Parser,
         'rdflib.syntax.parsers.N3Parser', 'N3Parser')

register('notation3', parsers.Parser,
         'rdflib.syntax.parsers.N3Parser', 'N3Parser')

register('nt', parsers.Parser,
         'rdflib.syntax.parsers.NTParser', 'NTParser')

register('n3', parsers.Parser,
         'rdflib.syntax.parsers.N3Parser', 'N3Parser')

register('rdfa', parsers.Parser,
         'rdflib.syntax.parsers.RDFaParser', 'RDFaParser')

register('default', Store,
         'rdflib.store.IOMemory', 'IOMemory')

register('IOMemory', Store,
         'rdflib.store.IOMemory', 'IOMemory')

register('Memory', Store,
         'rdflib.store.Memory', 'Memory')

register('Sleepycat', Store,
         'rdflib.store.Sleepycat', 'Sleepycat')

register('MySQL', Store,
         'rdflib.store.MySQL', 'MySQL')         
         
register('SQLite', Store,
         'rdflib.store.SQLite', 'SQLite')         

register('ZODB', Store,
         'rdflib.store.ZODB', 'ZODB')

register('sqlobject', Store,
         'rdflib.store._sqlobject', 'SQLObject')

register('Redland', Store,
         'rdflib.store.Redland', 'Redland')

register('MySQL', Store,
         'rdflib.store.MySQL', 'MySQL')

register("bison", sparql.Processor,
         'rdflib.sparql.bison.Processor', 'Processor')

register("SPARQLQueryResult", QueryResult,
         'rdflib.sparql.QueryResult', 'SPARQLQueryResult')
         