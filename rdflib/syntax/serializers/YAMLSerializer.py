#$Id: YAMLSerializer.py,v 1.3 2003/10/28 05:14:13 eikeon Exp $

from rdflib.syntax.serializer import AbstractSerializer

class YAMLSerializer(AbstractSerializer):

    short_name = "yaml"

    def __init__(self, store):
        super(YAMLSerializer, self).__init__(store)

    def serialize(self, stream=None): pass
