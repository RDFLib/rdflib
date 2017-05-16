import logging
import threading
import requests

import os

from io import BytesIO

from rdflib.query import Result

log = logging.getLogger(__name__)

class SPARQLWrapperException(Exception): pass

_response_mime_types = {
    'xml': 'application/sparql-results+xml, application/rdf+xml',
}

class SPARQLWrapper(object):

    """
    this class deals with nitty gritty details of talking to a SPARQL server
    """

    def __init__(self, query_endpoint=None, update_endpoint=None, returnFormat='xml', method='GET', timeout=None):

        self.returnFormat = returnFormat
        self.query_endpoint = query_endpoint
        self.update_endpoint = update_endpoint
        self.timeout = timeout
        self.method = method

        # it is recommended to have one session object per thread/process. This assures that is the case.
        # https://github.com/kennethreitz/requests/issues/1871

        self._session = threading.local()


    @property
    def session(self):
        k = 'session_%d'%os.getpid()
        self._session.__dict__.setdefault(k, requests.Session())
        log.debug('Session %s %s', os.getpid(), id(self._session.__dict__[k]))
        return self._session.__dict__[k]

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, method):
        if method not in ('GET', 'POST'):
            print 'cake'
            raise SPARQLWrapperException('Method must be "GET" or "POST"')

        self._method = method


    def query(self, query, default_graph=None):

        if not self.query_endpoint:
            raise SPARQLWrapperException("Query endpoint not set!")

        params = { 'query': query }
        if default_graph: params["default-graph-uri"] = default_graph

        headers = { 'Accept': _response_mime_types[self.returnFormat] }

        args = dict(url=self.query_endpoint,
                    headers=headers,
                    timeout=self.timeout)


        if self.method == 'GET':
            args['params'] = params
        elif self.method == 'POST':
            args['data'] = params
        else:
            raise SPARQLWrapperException("Unknown method %s"%self.method)

        res = self.session.request(self.method, **args)

        res.raise_for_status()
        return Result.parse(BytesIO(res.content), content_type=res.headers['Content-type'])

    def update(self, update, default_graph=None):
        if not self.update_endpoint:
            raise SPARQLWrapperException("Query endpoint not set!")

        params = { }

        if default_graph: params["using-graph-uri"] = default_graph

        headers = { 'Accept': _response_mime_types[self.returnFormat] }

        res = self.session.post(self.update_endpoint,
                            params=params,
                            data=update.encode('utf-8'),
                            headers=headers,
                            timeout=self.timeout)


        res.raise_for_status()


    def close(self):
        pass
        #self.session.close()
