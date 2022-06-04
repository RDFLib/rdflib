from typing import TYPE_CHECKING, Set, Tuple

from rdflib.parser import Parser

if TYPE_CHECKING:
    from rdflib.graph import Graph
    from rdflib.namespace import Namespace
    from rdflib.parser import InputSource
    from rdflib.term import URIRef


class ExampleParser(Parser):
    def __init__(self):
        super().__init__()

    def parse(self, source: "InputSource", sink: "Graph"):
        for triple in self.constant_output():
            sink.add(triple)

    @classmethod
    def namespace(cls) -> "Namespace":
        return Namespace("example:rdflib:plugin:parser:")

    @classmethod
    def constant_output(
        cls,
    ) -> Set[Tuple["URIRef", "URIRef", "URIRef"]]:
        return {(cls.namespace().subj, cls.namespace().pred, cls.namespace().obj)}


from rdflib.namespace import Namespace
