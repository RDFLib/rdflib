from rdflib.exceptions import SerializerDispatchNameError, SerializerDispatchNameClashError
import serializers

class AbstractSerializer(object):

    def __init__(self, store):
        self.__short_name = ""
        self._write = None
        self.encoding = "UTF-8"
        self.store = store
        
    def write(self, uni):
        self._stream.write(uni.encode(self.encoding, 'replace'))

    def serialize(self, stream=None):
        if stream != None: return self._output(stream)
        else:
            try:
                from cStringIO import StringIO
            except ImportError:
                from StringIO import StringIO
            s = StringIO()
            self._output(s)
            return s.getvalue()


class SerializationDispatcher(object):

    def __init__(self, store):
        self.store = store
        for ser in serializers.__all__:
            module = __import__("serializers." + ser, globals(), locals(), ["serializers"])
            aSerializer  = getattr(module, ser)
            short_name = getattr(aSerializer, "short_name")
            self.add(aSerializer, name=short_name)
                                   
    def add(self, serializer, name=None):
        #first, check if there's a name or a shortname, else throw exception
        if name != None:
            the_name = name
        elif hasattr(serializer, "short_name"):
            the_name = serializer.short_name
        else:
            msg = "You didn't set a short name for the  serializer or pass in a name to add()"
            raise SerializerDispatchNameError(msg)
        #check for name clash
        if hasattr(self, the_name):
            raise SerializerDispatchNameClashError("That name is already registered.")
        else:
            setattr(self, the_name, serializer(self.store))

    def __call__(self, format="xml", stream=None):
        return getattr(self, format).serialize(stream)
