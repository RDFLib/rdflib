CR="\x0d"
LF="\x0a"
CRLF=CR+LF

import socket, asyncore, asynchat
from urlparse import urlparse
import sys

from xml.sax import make_parser
from xml.sax.saxutils import handler
from xml.sax.handler import ErrorHandler

from rdflib import __version__
from rdflib.syntax.XMLRDFHandler import XMLRDFHandler
from rdflib.TripleStore import TripleStore
from rdflib.util import first
from rdflib.Namespace import Namespace
from rdflib.URIRef import URIRef
from rdflib.Literal import Literal
from rdflib.BNode import BNode

HTTP_HEADER = Namespace("http://rdflib.net/2002/http_header#")
HTTP_DATE = HTTP_HEADER["date"]
HTTP_ETAG = HTTP_HEADER["etag"]

from rdflib.exceptions import ParserError, Error
INFORMATION_STORE = Namespace("http://rdflib.net/2002/InformationStore#")
UPDATE_PERIOD = INFORMATION_STORE["updatePeriod"]

SECONDS_IN_DAY = 60*60*24

from rdflib.constants import TYPE
from rdflib.util import date_time, parse_date_time
DATE = URIRef("http://purl.org/dc/elements/1.1/date")

class _Locator:
    def __init__(self, system_id, parser):
        self.system_id = system_id
        self.parser = parser
        
    def getColumnNumber(self):
        try:
            return self.parser._parser.ErrorColumnNumber
        except:
            return None

    def getLineNumber(self):
        try:
            return self.parser._parser.ErrorLineNumber
        except:
            return None

    def getPublicId(self):
        return None

    def getSystemId(self):
        return self.system_id


_resolver = None
class _HTTPClient(object, asynchat.async_chat):
    def __init__(self, store):
        super(_HTTPClient, self).__init__()
        asynchat.async_chat.__init__(self)
        self.store = store        
        self.buffer = ''
        self.set_terminator(CRLF)
        self.connected = 0
        self.part = self.status_line
        self.chunk_size = 0
        self.chunk_read = 0
        self.length_read = 0        
        self.length = 0
        self.encoding = None
        self.url = None        
        self.pending_urls = []
    
    def urlopen(self, url):
        store = self.store
        id = store.identifier
        last_update = first(self.store.objects(id, INFORMATION_STORE["updateEvent"]))
        if last_update:
            for triple in self.store.triples((last_update, None, None)):
                self.store.remove_triples(triple)
        self.update_event = update_event = BNode()
        self.store.add((update_event, TYPE, INFORMATION_STORE["UpdateEvent"]))
        self.store.add((update_event, DATE, Literal(date_time())))                
        self.store.remove_triples((id, INFORMATION_STORE["updateEvent"], None))
        self.store.add((id, INFORMATION_STORE["updateEvent"], update_event))
        if self.url:
            self.pending_urls.append(url)
            return
        else:
            self.url = url
        scheme, host, path, params, query, fragment = urlparse(url)
        if not scheme=="http":
            raise NotImplementedError
        self.host = host
        if ":" in host:
            hostname, port = host.split(":", 1)
            port = int(port)
        else:
            hostname = host
            port = 80

        self.path = "?".join([path, query])
        

        self.port = port
        if _resolver:
            def callback(host, ttl, answer):
                if answer:
                    self.__connect(host)
                else:
                    event = self.update_event                    
                    ERROR = INFORMATION_STORE["error"]
                    msg = "Could not resolve ip for:", host
                    self.store.add((event, ERROR, Literal(msg)))
            try:
                _resolver.resolve(hostname, callback)
            except:
                event = self.update_event
                ERROR = INFORMATION_STORE["error"]
                self.store.add((event, ERROR, Literal(u"Trying to resolve: " % hostname)))
        else:
            self.__connect(hostname)
            
    def __connect(self, ip):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((ip, self.port))        
        
        self.parser = make_parser()
        # Workaround for bug in expatreader.py. Needed when
        # expatreader is trying to guess a prefix.
        self.parser.start_namespace_decl("xml", "http://www.w3.org/XML/1998/namespace")
        self.parser.setFeature(handler.feature_namespaces, 1)
        rdfxml = XMLRDFHandler(self.store)
        rdfxml.setDocumentLocator(_Locator(self.url, self.parser))
        self.parser.setContentHandler(rdfxml)
        self.parser.setErrorHandler(ErrorHandler())

    
    def close (self):
        self.connected = 0
        self.del_channel()
        #self.connected = 0        
        self.socket.close()
        self.url = None
        if self.pending_urls:
            url = self.pending_urls.pop(0)
            self.urlopen(url)

    def header(self, name, value):
        self.push('%s: %s' % (name, value))
        self.push(CRLF)        
        
    # asyncore methods
    def handle_error (self):
        if self.connected:
            url = self.url
            self.part = self.ignore                
            self.close()
            t,v,tb = sys.exc_info()        
            msg = "error: %s %s" % (url, t)            
            ERROR = INFORMATION_STORE["error"]
            event = self.update_event
            self.store.add((event, ERROR, Literal(msg)))
        
    def handle_connect(self):
        self.connected = 1        
        method = "GET"
        version = "HTTP/1.1"
        self.push("%s %s %s" % (method, self.path, version))
        self.push(CRLF)
        self.header("Host", self.host)

        store = self.store
        id = store.identifier
        date = first(self.store.objects(id, HTTP_DATE))
        if date:
            self.header("If-Modified-Since", date)
        etag = first(self.store.objects(id, HTTP_ETAG))
        if etag:
            self.header("If-None-Match", etag)
        self.header('Accept-Encoding', 'identity')
        self.header('Accept', 'text/xml, application/xml, application/rdf+xml, application/xml+rdf, text/plain, application/xhtml+xml, application/*, */*')
        self.header('User-agent', 'rdflib-%s (http://rdflib.net/; eikeon@eikeon.com)' % __version__)
        
        self.push(CRLF)
        self.push(CRLF)

    def feed(self, data):
        try:
            self.parser.feed(data)
        except ParserError, pe:
            ERROR = INFORMATION_STORE["error"]
            event = self.update_event
            self.store.add((event, ERROR, Literal(pe.msg)))
            self.part = self.ignore                
            self.close()
        except Exception, e:
            ERROR = INFORMATION_STORE["error"]
            event = self.update_event
            self.store.add((event, ERROR, Literal(e)))
            self.part = self.ignore                
            self.close()
        
    def collect_incoming_data(self, bytes):
        self.buffer = self.buffer + bytes
        if self.part==self.body:
            self.feed(self.buffer)
            self.buffer = ''

    def found_terminator(self):
        self.part()
        self.buffer = ''        

    def ignore(self):
        self.buffer = ''
    
    def status_line(self):
        line = self.buffer
        try:
            version, status, reason = line.split(None, 2)
            if not version.startswith('HTTP/'):
                raise BadStatusLine(line)
        except:
            self.part = self.ignore
            msg = "Bad status line: '%s'" % line
            self.store.add((self.update_event, INFORMATION_STORE["error"], Literal(msg)))
            self.close()
            
        self.store.add((self.update_event,
                        INFORMATION_STORE["http_status"], Literal(status)))
        # The status code is a three-digit number
        try:
            n = int(status)
            status = n
        except ValueError:
            pass

        if status==404:
            update_event = self.update_event
            context = self.store[self.store.identifier]
            try:
                every = int(context[UPDATE_PERIOD] or str(SECONDS_IN_DAY))
            except:
                every = SECONDS_IN_DAY
            every *= 2
            context[UPDATE_PERIOD] = Literal(every)

        if status==200:
            self.part = self.headers
            #self.store.remove_triples((None, None, None))
            store = self.store
            for s, p, o in store:
                if s!=store.identifier:
                    store.remove((s, p, o))
        else:
            self.part = self.ignore
            self.close()
        return version, status, reason

    def headers(self):
        line = self.buffer
        if not line:
            if self.encoding=="chunked":
                self.part = self.chunked_size
            else:
                self.part = self.body
                self.set_terminator(self.length)
        else:
            name, value = line.split(":", 1)
            value = value.strip()
            if name.lower()=="Transfer-Encoding".lower():
                self.encoding = value
            elif name.lower()=="Content-Length".lower():
                self.length = int(value)
            elif name.lower()=="date":
                # TODO: remove date and etag triple from id...
                #       use update_event
                store = self.store
                id = store.identifier
                store.remove_triples((id, HTTP_DATE, None))
                store.add((id, HTTP_DATE, Literal(value)))
            elif name.lower()=="etag":
                store = self.store
                id = store.identifier
                store.remove_triples((id, HTTP_ETAG, None))
                store.add((id, HTTP_ETAG, Literal(value)))
            http_tag = HTTP_HEADER[name.lower()]
            store = self.store
            update_event = self.update_event
            store.remove_triples((update_event, http_tag, None))
            store.add((update_event, http_tag, Literal(value)))

    def body(self):
        self.close()

    def chunked_size(self):
        line = self.buffer
        if not line:
            return
        chunk_size = int(line.split()[0], 16)
        if chunk_size==0:
            self.part = self.trailer
        else:
            self.set_terminator(chunk_size)
            self.part = self.chunked_body            
        self.length += chunk_size
        
    def chunked_body(self):
        line = self.buffer
        self.set_terminator(CRLF)
        self.part = self.chunked_size
        self.feed(line)

    def trailer(self):
        # http://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html#sec3.6.1
        # trailer        = *(entity-header CRLF)
        line = self.buffer
        if line==CRLF:
            self.parser.feed("", 1)
            self.close()
            
