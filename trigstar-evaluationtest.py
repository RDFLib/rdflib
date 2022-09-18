import pytest

from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

from rdflib.exceptions import ParserError

from rdflib import Graph, ConjunctiveGraph
from rdflib.util import guess_format


from rdflib.plugin import register
from rdflib.parser import Parser
from rdflib.serializer import Serializer

import rdflib
from rdflib import URIRef
from rdflib.namespace import RDF
from rdflib.namespace import FOAF

g = ConjunctiveGraph()
g.parse(data="test/trigstar-evaluation/trig-star-eval-01.trig", format = "trigs")
print(g.serialize(format = "trigstar"))

g = ConjunctiveGraph()
g.parse("test/trigstar-evaluation/trig-star-eval-02.trig", format = "trigs")
print(g.serialize(format = "trigstar"))

g = ConjunctiveGraph()
g.parse("test/trigstar-evaluation/trig-star-eval-bnode-1.trig", format = "trigs")
print(g.serialize(format = "trigstar"))

g = ConjunctiveGraph()
g.parse("test/trigstar-evaluation/trig-star-eval-bnode-2.trig", format = "trigs")
print(g.serialize(format = "trigstar"))

g = ConjunctiveGraph()
g.parse("test/trigstar-evaluation/trig-star-eval-annotation-1.trig", format = "trigs")
print(g.serialize(format = "trigstar"))

g = ConjunctiveGraph()
g.parse("test/trigstar-evaluation/trig-star-eval-annotation-2.trig", format = "trigs")
print(g.serialize(format = "trigstar"))

g = ConjunctiveGraph()
g.parse("test/trigstar-evaluation/trig-star-eval-annotation-3.trig", format = "trigs")
print(g.serialize(format = "trigstar"))

g = ConjunctiveGraph()
g.parse("test/trigstar-evaluation/trig-star-eval-annotation-4.trig", format = "trigs")
print(g.serialize(format = "trigstar"))

g = ConjunctiveGraph()
g.parse("test/trigstar-evaluation/trig-star-eval-annotation-5.trig", format = "trigs")
print(g.serialize(format = "trigstar"))

g = ConjunctiveGraph()
g.parse("test/trigstar-evaluation/trig-star-eval-quoted-annotation-1.trig", format = "trigs")
print(g.serialize(format = "trigstar"))

g = ConjunctiveGraph()
g.parse("test/trigstar-evaluation/trig-star-eval-quoted-annotation-2.trig", format = "trigs")
print(g.serialize(format = "trigstar"))

g = ConjunctiveGraph()
g.parse("test/trigstar-evaluation/trig-star-eval-quoted-annotation-3.trig", format = "trigs")
print(g.serialize(format = "trigstar"))
