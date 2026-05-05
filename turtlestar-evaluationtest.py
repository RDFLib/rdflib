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
g.parse(data="test/turtlestar-evaluation/turtle-star-eval-01.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtlestar-evaluation/turtle-star-eval-02.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtlestar-evaluation/turtle-star-eval-bnode-1.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtlestar-evaluation/turtle-star-eval-bnode-2.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtlestar-evaluation/turtle-star-eval-annotation-1.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtlestar-evaluation/turtle-star-eval-annotation-2.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtlestar-evaluation/turtle-star-eval-annotation-3.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtlestar-evaluation/turtle-star-eval-annotation-4.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtlestar-evaluation/turtle-star-eval-annotation-5.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtlestar-evaluation/turtle-star-eval-quoted-annotation-1.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtlestar-evaluation/turtle-star-eval-quoted-annotation-2.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))

g = Graph()
g.parse("test/turtlestar-evaluation/turtle-star-eval-quoted-annotation-3.ttl", format = "ttls")
print(g.serialize(format = "ttlstar"))
