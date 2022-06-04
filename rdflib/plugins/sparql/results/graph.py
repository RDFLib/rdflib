from rdflib import Graph
from rdflib.query import Result, ResultParser


class GraphResultParser(ResultParser):
    def parse(self, source, content_type):

        res = Result("CONSTRUCT")  # hmm - or describe?type_)
        res.graph = Graph()
        res.graph.parse(source, format=content_type)

        return res
