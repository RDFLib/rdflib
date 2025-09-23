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
g.parse(data="test/ntriples-star/ntriples-star-syntax-1.nt", format = "ntstar")
print(g.serialize(format = "ntstar"))

g = Graph()
g.parse("test/ntriples-star/ntriples-star-syntax-2.nt", format = "ntstar")
print(g.serialize(format = "ntstar"))

g = Graph()
g.parse("test/ntriples-star/ntriples-star-syntax-3.nt", format = "ntstar")
print(g.serialize(format = "ntstar"))

g = Graph()
g.parse("test/ntriples-star/ntriples-star-syntax-4.nt", format = "ntstar")
print(g.serialize(format = "ntstar"))

g = Graph()
g.parse("test/ntriples-star/ntriples-star-syntax-5.nt", format = "ntstar")
print(g.serialize(format = "ntstar"))

g = Graph()
g.parse("test/ntriples-star/ntriples-star-bnode-1.nt", format = "ntstar")
print(g.serialize(format = "ntstar"))

g = Graph()
g.parse("test/ntriples-star/ntriples-star-bnode-2.nt", format = "ntstar")
print(g.serialize(format = "ntstar"))

g = Graph()
g.parse("test/ntriples-star/ntriples-star-nested-1.nt", format = "ntstar")
print(g.serialize(format = "ntstar"))

g = Graph()
g.parse("test/ntriples-star/ntriples-star-nested-2.nt", format = "ntstar")
print(g.serialize(format = "ntstar"))
