"""
Query plugin interface.

This module is useful for those wanting to write a query processor
that can plugin to rdf. If you are wanting to execute a query you
likely want to do so through the Graph class query method.

"""


class Processor(object):

    def __init__(self, graph):
        pass

    def query(self, strOrQuery, initBindings={}, initNs={}, DEBUG=False):
        pass


class Result(object):
    """
    A common class for representing query result in a variety of formats, namely:

    xml   : as an XML string using the XML result format of the query language
    python: as Python objects
    json  : as JSON
    """
    def __init__(self, pythonResult):
        self.rt = pythonResult

    def serialize(self, format='xml'):
        pass
