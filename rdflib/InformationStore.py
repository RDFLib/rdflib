from rdflib.store.AbstractInformationStore import AbstractInformationStore
from rdflib.store.SCBacked import SCBacked

from rdflib.model.schema import Schema

from os import getcwd

from urlparse import urldefrag, urljoin
from urllib import pathname2url, url2pathname
from xml.sax.xmlreader import InputSource

from rdflib.store.AbstractTripleStore import AbstractTripleStore
from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.Literal import Literal
from rdflib.Namespace import  Namespace
from rdflib.model.schema import Schema
from rdflib.syntax.loadsave import LoadSave
from rdflib.constants import TYPE, RDFS_LABEL, RDFSNS
from rdflib.URLInputSource import URLInputSource
from rdflib.util import term, first, uniq, date_time

from rdflib.store._HTTPClient import _HTTPClient

INFORMATION_STORE = Namespace("http://rdflib.net/2002/InformationStore#")
CONTEXT = INFORMATION_STORE["Context"]
SOURCE = INFORMATION_STORE["source"]

TIMESTAMP = INFORMATION_STORE["timestamp"]

def get_system_id(source):
    if isinstance(source, InputSource):
        system_id = source.getSystemId()
    else:
        cwd = urljoin("file:", pathname2url(getcwd()))
        system_id = urljoin("%s/" % cwd, source)
        system_id, frag = urldefrag(system_id)
    if system_id:
        system_id = URIRef(system_id)
    return system_id

class InformationStore(Schema, SCBacked, AbstractInformationStore):
    """
    """
    def __init__(self, path=None):
        super(InformationStore, self).__init__()
        if path:
            self.open(path)

    def open(self, path):
        super(InformationStore, self).open(path)

    def load(self, source):
        system_id = get_system_id(source)
        if system_id:
            for context in self.subjects(SOURCE, system_id):
                self.remove_context(context)            

        context = BNode()
        store = super(InformationStore, self).load(source, context)

        self.add((context, TYPE, CONTEXT), context)
        self.add((context, SOURCE, system_id), context)
        self.add((context, TIMESTAMP, Literal(date_time())), context)

        return store

