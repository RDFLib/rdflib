from __future__ import generators

import RDF
import Redland
from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.Literal import Literal

class RedlandStore(object):
    def __init__(self):
        super(RedlandStore, self).__init__()
        self.ImpedanceMatch = 1

    def open(self, **args):
        """Set up the Redland storage according to the keywords
        supplied.

        Must be called directly after instantiating class.
        """
        #print args
        self._storage = apply(RDF.Storage, [], args)
        self._model = RDF.Model(storage=self._storage)


    def _inNode(self, n):
        if (n is None):
            return None
        
        node = None
        if (isinstance(n, URIRef)):
            node = RDF.Node(uri_string=str(n))
        if (isinstance(n, BNode)):
            node = RDF.Node(blank=str(n))
        if (isinstance(n, Literal)):
            if (n.language != '' and n.datatype is not None):
                #print "both %s %s"%(n.language, n.datatype)
                languri = RDF.Uri(string=n.language)
                dtypuri = RDF.Uri(string=n.datatype)
                node = RDF.Node(literal=str(n), xml_language=languri,
                                datatype=dtypuri)
            elif (n.datatype is not None):
                #print "dtype %s"%(n.datatype,)
                dtypuri = RDF.Uri(string=n.datatype)
                node = RDF.Node(literal=str(n), datatype=dtypuri)
            elif (n.language != ''):
                #print "lang %s"%(n.language,)
                languri = RDF.Uri(string=n.language)
                node = RDF.Node(literal=str(n), xml_language=languri)
            else:
                node = RDF.Node(literal=str(n))
                
                

        if node is None:
            raise Exception("Unknown type of node!")
        return node
    
    def _inStatement(self, (s,p,o)):
        sub = self._inNode(s)
        pred = self._inNode(p)
        obj = self._inNode(o)

        statement = RDF.Statement(subject=sub,predicate=pred,object=obj)
        return statement

    def _outNode(self, n):
        if (n is None):
            return None

        node = None
        if n.is_resource():
            node = URIRef(str(n.uri))
        if n.is_literal():
            litval = n.get_literal_value()
            node = Literal(litval['string'], lang=litval['language'],
                           datatype=litval['datatype'])
        if n.is_blank():
            # There is no clean way currently to get the blank identifier
            # from Redland
            id = Redland.librdf_node_get_blank_identifier(n._node)
            node = BNode(id)

        if node is None:
            raise Exception("Unknown type!")
        return node

    def _outStatement(self, statement):

        s = self._outNode(statement.subject)
        p = self._outNode(statement.predicate)
        o = self._outNode(statement.object)

        return (s,p,o)


    def add(self, tuple):
        """Convert tuple to a Redland statement, then submit it to the
        Redland Model.
        """
        statement = self._inStatement(tuple)
        self._model.add_statement(statement)

    def remove(self, tuple):
        """Convert the tuple to a Redland statement, then remove that
        statement from the redland model.
        """
        statement = self._inStatement(tuple)
        self._model.remove_statement(tuple)

    def triples(self, tuple):
        """Convert the tuple to a Redland statement, then find the statements
        in the Redland Model.
        Returns a generator over the result set.
        """
        statement = self._inStatement(tuple)
        stream = self._model.find_statements(statement)
        seen = {}
        while not stream.end():
            statement = stream.current()
            #print statement
            tuple = self._outStatement(statement)
            if (self.ImpedanceMatch):
                if not seen.has_key(tuple):
                    seen[tuple] = 1
                    yield tuple
            else:
                yield tuple
            stream.next()




    

            
