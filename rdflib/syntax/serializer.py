from rdflib.exceptions import SerializerDispatchNameError, SerializerDispatchNameClashError
import rdflib.syntax.serializers

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
        pass

class SerializationDispatcher(object):

    def __init__(self, store):
        self.store = store
        for ser in rdflib.syntax.serializers.__all__:
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
        if stream==None:
            stream = StringIO()
            getattr(self, format).serialize(stream)
            return stream.getvalue()
        else:
            return getattr(self, format).serialize(stream)            
