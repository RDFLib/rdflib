"""
Parser plugin interface.

This module defines the parser plugin interface and contains other
related parser support code.

The module is mainly useful for those wanting to write a parser that
can plugin to rdflib. If you are wanting to invoke a parser you likely
want to do so through the Graph class parse method.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys

from six import BytesIO
from six import string_types
from six import text_type

from six.moves.urllib.request import pathname2url
from six.moves.urllib.request import Request
from six.moves.urllib.request import url2pathname
from six.moves.urllib.parse import urljoin
from six.moves.urllib.request import urlopen

from xml.sax import xmlreader

from rdflib import __version__
from rdflib.term import URIRef
from rdflib.namespace import Namespace

__all__ = [
    'Parser', 'InputSource', 'StringInputSource',
    'URLInputSource', 'FileInputSource']


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
        self.auto_close = False  # see Graph.parse(), true if opened by us

    def close(self):
        f = self.getByteStream()
        if f and hasattr(f, 'close'):
            f.close()


class StringInputSource(InputSource):
    """
    TODO:
    """

    def __init__(self, value, system_id=None):
        super(StringInputSource, self).__init__(system_id)
        stream = BytesIO(value)
        self.setByteStream(stream)
        # TODO:
        #   encoding = value.encoding
        #   self.setEncoding(encoding)


headers = {
    'User-agent':
    'rdflib-%s (http://rdflib.net/; eikeon@eikeon.com)' % __version__
}


class URLInputSource(InputSource):
    """
    TODO:
    """

    def __init__(self, system_id=None, format=None):
        super(URLInputSource, self).__init__(system_id)
        self.url = system_id

        # copy headers to change
        myheaders = dict(headers)
        if format == 'application/rdf+xml':
            myheaders['Accept'] = 'application/rdf+xml, */*;q=0.1'
        elif format == 'n3':
            myheaders['Accept'] = 'text/n3, */*;q=0.1'
        elif format == 'turtle':
            myheaders['Accept'] = 'text/turtle,application/x-turtle, */*;q=0.1'
        elif format == 'nt':
            myheaders['Accept'] = 'text/plain, */*;q=0.1'
        elif format == 'json-ld':
            myheaders['Accept'] = (
                'application/ld+json, application/json;q=0.9, */*;q=0.1')
        else:
            myheaders['Accept'] = (
                'application/rdf+xml,text/rdf+n3;q=0.9,' +
                'application/xhtml+xml;q=0.5, */*;q=0.1')

        req = Request(system_id, None, myheaders)
        file = urlopen(req)
        # Fix for issue 130 https://github.com/RDFLib/rdflib/issues/130
        self.url = file.geturl()    # in case redirections took place
        self.setPublicId(self.url)
        self.content_type = file.info().get('content-type')
        if self.content_type is not None:
            self.content_type = self.content_type.split(";", 1)[0]
        self.setByteStream(file)
        # TODO: self.setEncoding(encoding)
        self.response_info = file.info()  # a mimetools.Message instance

    def __repr__(self):
        return self.url


class FileInputSource(InputSource):

    def __init__(self, file):
        base = urljoin("file:", pathname2url(os.getcwd()))
        system_id = URIRef(urljoin("file:", pathname2url(file.name)), base=base)
        super(FileInputSource, self).__init__(system_id)
        self.file = file
        self.setByteStream(file)
        # TODO: self.setEncoding(encoding)

    def __repr__(self):
        return repr(self.file)


def create_input_source(source=None, publicID=None,
                        location=None, file=None, data=None, format=None):
    """
    Return an appropriate InputSource instance for the given
    parameters.
    """

    # test that exactly one of source, location, file, and data is not None.
    if sum((
        source is not None,
        location is not None,
        file is not None,
        data is not None,
    )) != 1:
        raise ValueError(
            'exactly one of source, location, file or data must be given'
        )

    input_source = None

    if source is not None:
        if isinstance(source, InputSource):
            input_source = source
        else:
            if isinstance(source, string_types):
                location = source
            elif hasattr(source, "read") and not isinstance(source, Namespace):
                f = source
                input_source = InputSource()
                input_source.setByteStream(f)
                if f is sys.stdin:
                    input_source.setSystemId("file:///dev/stdin")
                elif hasattr(f, "name"):
                    input_source.setSystemId(f.name)
            else:
                raise Exception("Unexpected type '%s' for source '%s'" %
                                (type(source), source))

    absolute_location = None  # Further to fix for issue 130

    auto_close = False  # make sure we close all file handles we open
    if location is not None:
        # Fix for Windows problem https://github.com/RDFLib/rdflib/issues/145
        if os.path.exists(location):
            location = pathname2url(location)
        base = urljoin("file:", "%s/" % pathname2url(os.getcwd()))
        absolute_location = URIRef(location, base=base).defrag()
        if absolute_location.startswith("file:///"):
            filename = url2pathname(absolute_location.replace("file:///", "/"))
            file = open(filename, "rb")
        else:
            input_source = URLInputSource(absolute_location, format)
        auto_close = True
        # publicID = publicID or absolute_location  # Further to fix
        # for issue 130

    if file is not None:
        input_source = FileInputSource(file)

    if data is not None:
        if isinstance(data, text_type):
            data = data.encode('utf-8')
        input_source = StringInputSource(data)
        auto_close = True

    if input_source is None:
        raise Exception("could not create InputSource")
    else:
        input_source.auto_close |= auto_close
        if publicID is not None:  # Further to fix for issue 130
            input_source.setPublicId(publicID)
        # Further to fix for issue 130
        elif input_source.getPublicId() is None:
            input_source.setPublicId(absolute_location or "")
        return input_source
