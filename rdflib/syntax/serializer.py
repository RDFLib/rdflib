from rdflib.exceptions import SerializerDispatchNameError, SerializerDispatchNameClashError

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class AbstractSerializer(object):

    def __init__(self, store):
        self.store = store
        self.encoding = "UTF-8"
        
    def serialize(self, stream):
        """Abstract method"""


class SerializationDispatcher(object):

    def __init__(self, store):
        self.store = store
        self.__serializer = {}
        self.__module_info = {}
        self.register('xml', 'rdflib.syntax.serializers.XMLSerializer', 'XMLSerializer')
        self.register('pretty-xml', 'rdflib.syntax.serializers.PrettyXMLSerializer', 'PrettyXMLSerializer')
        self.register('nt', 'rdflib.syntax.serializers.NTSerializer', 'NTSerializer')
        
    def register(self, short_name, module_path, class_name):
        if short_name in self.__module_info:
            raise Exception("serializer already registered for:", short_name)
        self.__module_info[short_name] = (module_path, class_name)

    def serializer(self, format):
        serializer = self.__serializer.get(format, None)
        if serializer is None:
            module_path, class_name = self.__module_info[format]
            module = __import__(module_path, globals(), locals(), True)
            # TODO: catch import error?
            serializer = getattr(module, class_name)(self.store)
            self.__serializer[format] = serializer
        return serializer

    def __call__(self, format="xml", stream=None):
        if stream==None:
            stream = StringIO()
            self.serializer(format).serialize(stream)
            return stream.getvalue()
        else:
            return self.serializer(format).serialize(stream)
