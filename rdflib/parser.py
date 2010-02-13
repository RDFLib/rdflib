"""
Parser plugin interface.

This module defines the parser plugin interface and contains other
related parser support code.

The module is mainly useful for those wanting to write a parser that
can plugin to rdflib. If you are wanting to invoke a parser you likely
want to do so through the Graph class parse method.

"""

import os
import __builtin__
import warnings
from urllib import pathname2url, url2pathname
from urllib2 import urlopen, Request, HTTPError
from urlparse import urljoin
from StringIO import StringIO
from xml.sax import xmlreader
from xml.sax.saxutils import prepare_input_source
import types
try:
    _StringTypes = (types.StringType, types.UnicodeType)
except AttributeError:
    _StringTypes = (types.StringType,)

from rdflib import __version__
from rdflib.term import URIRef
from rdflib.namespace import Namespace


class Parser(object):

    def __init__(self):
        pass

    def parse(self, source, sink):
        pass


class InputSource(xmlreader.InputSource, object):
    """
    TODO:
    """

    def __init__(self, system_id=None):
        xmlreader.InputSource.__init__(self, system_id=system_id)
        self.content_type = None


class StringInputSource(InputSource):
    """
    TODO:
    """

    def __init__(self, value, system_id=None):
        super(StringInputSource, self).__init__(system_id)
        stream = StringIO(value)
        self.setByteStream(stream)
        # TODO:
        #   encoding = value.encoding
        #   self.setEncoding(encoding)


headers = {
    'User-agent': 'rdflib-%s (http://rdflib.net/; eikeon@eikeon.com)' % __version__
    }


class URLInputSource(InputSource):
    """
    TODO:
    """

    def __init__(self, system_id=None, format=None):
        super(URLInputSource, self).__init__(system_id)
        self.url = system_id

        # copy headers to change
        myheaders=dict(headers)
        if format=='application/rdf+xml':                 
            myheaders['Accept']='application/rdf+xml, */*;q=0.1'
        elif format=='n3':
            myheaders['Accept']='text/n3, */*;q=0.1'
        elif format=='nt':
            myheaders['Accept']='text/plain, */*;q=0.1'
        else: 
            myheaders['Accept']='application/rdf+xml,text/rdf+n3;q=0.9,application/xhtml+xml;q=0.5, */*;q=0.1'
        
        req = Request(system_id, None, myheaders)
        try:
            file = urlopen(req)
        except HTTPError, e:
            # TODO:
            raise Exception('"%s" while trying to open "%s"' % (e, self.url))
        self.content_type = file.info().get('content-type')
        self.content_type = self.content_type.split(";", 1)[0]
        self.setByteStream(file)
        # TODO: self.setEncoding(encoding)

    def __repr__(self):
        return self.url


class FileInputSource(InputSource):
    """
    TODO:
    """

    def __init__(self, file):
        base = urljoin("file:", pathname2url(os.getcwd()))
        system_id = URIRef(file.name, base=base)
        super(FileInputSource, self).__init__(system_id)
        self.file = file
        self.setByteStream(file)
        # TODO: self.setEncoding(encoding)

    def __repr__(self):
        return `self.file`


def create_input_source(source=None, publicID=None,
                        location=None, file=None, data=None, format=None):
    """
    Return an appropriate InputSource instance for the given
    parameters.
    """

    # TODO: test that exactly one of source, location, file, and data
    # is not None.

    input_source = None

    if source is not None:
        if isinstance(source, InputSource):
            input_source = source
        else:
            if isinstance(source, _StringTypes):
                location = source
            elif hasattr(source, "read") and not isinstance(source, Namespace):
                f = source
                input_source = InputSource()
                input_source.setByteStream(f)
                if hasattr(f, "name"):
                    input_source.setSystemId(f.name)
            else:
                raise Exception("Unexpected type '%s' for source '%s'" % (type(source), source))

    if location is not None:
        base = urljoin("file:", "%s/" % pathname2url(os.getcwd()))
        absolute_location = URIRef(location, base=base).defrag()
        if absolute_location.startswith("file:///"):
            filename = url2pathname(absolute_location.replace("file:///", "/"))
            file = __builtin__.file(filename, "rb")
        else:
            input_source = URLInputSource(absolute_location, format)
        publicID = publicID or absolute_location

    if file is not None:
        input_source = FileInputSource(file)

    if data is not None:
        if isinstance(data, unicode):
            data = data.encode('utf-8')
        input_source = StringInputSource(data)

    if input_source is None:
        raise Exception("could not create InputSource")
    else:
        if publicID:
            input_source.setPublicId(publicID)

        # TODO: what motivated this bit?
        id = input_source.getPublicId()
        if id is None:
            input_source.setPublicId("")
        return input_source


