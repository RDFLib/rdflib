from urllib2 import urlopen, Request

from xml.sax.xmlreader import InputSource

from rdflib import __version__
from StringIO import StringIO

class StringInputSource(InputSource, object):
    def __init__(self, value, system_id=None):
        super(StringInputSource, self).__init__(system_id)
        stream = StringIO(value)
        self.setByteStream(stream)
        # TODO:
        #   encoding = value.encoding
        #   self.setEncoding(encoding)
