import pytest

from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

from rdflib.exceptions import ParserError

from rdflib import Graph
from rdflib.util import guess_format


from rdflib.plugin import register
from rdflib.parser import Parser
from rdflib.serializer import Serializer

import rdflib
from rdflib import URIRef
from rdflib.namespace import RDF
from rdflib.namespace import FOAF

g = Graph()
g.parse(data="test/turtle-star/turtle-star-syntax-basic-01.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtle-star/turtle-star-syntax-basic-02.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtle-star/turtle-star-syntax-inside-01.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtle-star/turtle-star-syntax-inside-02.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtle-star/turtle-star-syntax-nested-01.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtle-star/turtle-star-syntax-nested-02.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtle-star/turtle-star-syntax-compound.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtle-star/turtle-star-syntax-bnode-01.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtle-star/turtle-star-syntax-bnode-02.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtle-star/turtle-star-syntax-bnode-03.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtle-star/turtle-star-annotation-1.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtle-star/turtle-star-annotation-2.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtle-star/nt-ttl-star-syntax-1.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtle-star/nt-ttl-star-syntax-2.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtle-star/nt-ttl-star-syntax-3.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtle-star/nt-ttl-star-syntax-4.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtle-star/nt-ttl-star-syntax-5.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtle-star/nt-ttl-star-bnode-1.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtle-star/nt-ttl-star-bnode-2.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtle-star/nt-ttl-star-nested-1.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtle-star/nt-ttl-star-nested-2.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))
