import logging
import threading
import requests

import os

from io import BytesIO

from rdflib.query import Result

log = logging.getLogger(__name__)


class SPARQLConnectorException(Exception):
    pass

# TODO: Pull in these from the result implementation plugins?
_response_mime_types = {
    'xml': 'application/sparql-results+xml, application/rdf+xml',
    'json': 'application/sparql-results+json',
    'csv': 'text/csv',
    'tsv': 'text/tab-separated-values',
    'application/rdf+xml': 'application/rdf+xml',
}


class SPARQLConnector(object):

    """
    this class deals with nitty gritty details of talking to a SPARQL server
    """

    def __init__(self, query_endpoint=None, update_endpoint=None, returnFormat='xml', method='GET', **kwargs):
        """
        Any additional keyword arguments will be passed to requests, and can be used to setup timesouts, basic auth, etc.
        """

        self.returnFormat = returnFormat
        self.query_endpoint = query_endpoint
        self.update_endpoint = update_endpoint
        self.kwargs = kwargs
        self.method = method

        # it is recommended to have one session object per thread/process. This assures that is the case.
        # https://github.com/kennethreitz/requests/issues/1871

        self._session = threading.local()

    @property
    def session(self):
        k = 'session_%d' % os.getpid()
        self._session.__dict__.setdefault(k, requests.Session())
        log.debug('Session %s %s', os.getpid(), id(self._session.__dict__[k]))
        return self._session.__dict__[k]

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, method):
        if method not in ('GET', 'POST'):
            raise SPARQLConnectorException('Method must be "GET" or "POST"')

        self._method = method

    def query(self, query, default_graph=None):

        if not self.query_endpoint:
            raise SPARQLConnectorException("Query endpoint not set!")

        params = {'query': query}
        if default_graph:
            params["default-graph-uri"] = default_graph

        headers = {'Accept': _response_mime_types[self.returnFormat]}

        args = dict(self.kwargs)
        args.update(url=self.query_endpoint)

        # merge params/headers dicts
        args.setdefault('params', {})

        args.setdefault('headers', {})
        args['headers'].update(headers)

        if self.method == 'GET':
            args['params'].update(params)
        elif self.method == 'POST':
            args['data'] = params
        else:
            raise SPARQLConnectorException("Unknown method %s" % self.method)

        res = self.session.request(self.method, **args)

        res.raise_for_status()

        return Result.parse(BytesIO(res.content), content_type=res.headers['Content-type'])

    def update(self, update, default_graph=None):
        if not self.update_endpoint:
            raise SPARQLConnectorException("Query endpoint not set!")

        params = {}

        if default_graph:
            params["using-graph-uri"] = default_graph

        headers = {'Accept': _response_mime_types[self.returnFormat]}

        args = dict(self.kwargs)

        args.update(url=self.update_endpoint,
                    data=update.encode('utf-8'))

        # merge params/headers dicts
        args.setdefault('params', {})
        args['params'].update(params)
        args.setdefault('headers', {})
        args['headers'].update(headers)

        res = self.session.post(**args)

        res.raise_for_status()

    def close(self):
        self.session.close()
