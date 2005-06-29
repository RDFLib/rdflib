
class Serializer(object):

    def __init__(self, store):
        self.store = store        
        self.encoding = "UTF-8"
        
    def serialize(self, stream, base=None):
        """Abstract method"""

