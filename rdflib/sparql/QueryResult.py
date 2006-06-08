from rdflib import QueryResult

class SPARQLQueryResult(QueryResult.QueryResult):
    """
    Query result class for SPARQL
        
    xml   : as an XML string conforming to the SPARQL XML result format: http://www.w3.org/TR/rdf-sparql-XMLres/
    python: as Python objects
    json  : as JSON   
    graph : as an RDFLib Graph - for CONSTRUCT and DESCRIBE queries
    """
    def __init__(self,pythonResult):
        """
        The constructor is the result straight from sparql-p, which is a list of tuples 
        (in select order, each item is the valid binding for the corresponding variable or 'None') for SELECTs
        , a SPARQLGraph for DESCRIBE/CONSTRUCT, and boolean for ASK  
        """
        self.rt = pythonResult
        
    def __iter__(self):
        """Iterates over the result entries"""
        if isinstance(self.rt,list):
            for item in self.rt:
                yield item        
        else:
            yield self.rt
        
    def serialize(self,format='xml'):
        if format == 'python':
            return self.rt
        else:
            raise Exception("Result format not implemented: %s"%format) 