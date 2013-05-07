# -*- coding: utf-8 -*-
#
"""
This is an RDFLib store around Ivan Herman et al.'s SPARQL service wrapper.
This was first done in layer-cake, and then ported to RDFLib 3 and rdfextras

This version works with vanilla SPARQLWrapper installed by ``easy_install``, ``pip`` or similar. If you installed ``rdflib`` with a tool that understands dependencies, it should have been installed automatically for you

Changes:
    - Layercake adding support for namespace binding, I removed it again to
      work with vanilla SPARQLWrapper
    - JSON object mapping support suppressed
    - Replaced '4Suite-XML Domlette with Elementtree
    - Incorporated as an RDFLib store

"""

import re
# import warnings
try:
    from SPARQLWrapper import SPARQLWrapper, XML
except ImportError:
    raise Exception(
        "SPARQLWrapper not found! SPARQL Store will not work." +
        "Install with 'easy_install SPARQLWrapper'")

import sys
if getattr(sys, 'pypy_version_info', None) is not None \
    or sys.platform.startswith('java') \
        or sys.version_info[:2] < (2, 6):
    # import elementtree as etree
    from elementtree import ElementTree
    assert ElementTree
else:
    try:
        from xml.etree import ElementTree
        assert ElementTree
    except ImportError:
        from elementtree import ElementTree

from rdflib.plugins.stores.regexmatching import NATIVE_REGEX

from rdflib.store import Store
from rdflib.query import Result
from rdflib import Variable, Namespace, BNode, URIRef, Literal

import httplib
import urlparse


class NSSPARQLWrapper(SPARQLWrapper):
    nsBindings = {}

    def setNamespaceBindings(self, bindings):
        """
        A shortcut for setting namespace bindings that will be added
        to the prolog of the query

        @param bindings: A dictionary of prefixs to URIs
        """
        self.nsBindings.update(bindings)

    def setQuery(self, query):
        """
        Set the SPARQL query text. Note: no check is done on the
        validity of the query (syntax or otherwise) by this module,
        except for testing the query type (SELECT, ASK, etc).

        Syntax and validity checking is done by the SPARQL service itself.

        @param query: query text
        @type query: string
        @bug: #2320024
        """
        self.queryType = self._parseQueryType(query)
        self.queryString = '\n'.join(
            ['\n'.join(['PREFIX %s: <%s>' % (key, val)
                        for key, val in self.nsBindings.items()]),
             query])

BNODE_IDENT_PATTERN = re.compile('(?P<label>_\:[^\s]+)')
SPARQL_NS = Namespace('http://www.w3.org/2005/sparql-results#')
sparqlNsBindings = {u'sparql': SPARQL_NS}
ElementTree._namespace_map["sparql"] = SPARQL_NS


def TraverseSPARQLResultDOM(doc, asDictionary=False):
    """
    Returns a generator over tuples of results
    """
    # namespace handling in elementtree xpath sub-set is not pretty :(
    vars = [Variable(v.attrib["name"]) for v in doc.findall(
            './{http://www.w3.org/2005/sparql-results#}head/' +
            '{http://www.w3.org/2005/sparql-results#}variable')]
    for result in doc.findall(
            './{http://www.w3.org/2005/sparql-results#}results/' +
            '{http://www.w3.org/2005/sparql-results#}result'):
        currBind = {}
        values = []
        for binding in result.findall(
                '{http://www.w3.org/2005/sparql-results#}binding'):
            varVal = binding.attrib["name"]
            var = Variable(varVal)
            term = CastToTerm(binding.findall('*')[0])
            values.append(term)
            currBind[var] = term
        if asDictionary:
            yield currBind, vars
        else:
            def __locproc(values):
                if len(values) == 1:
                    return values[0]
                else:
                    return tuple(values)
            yield __locproc(values), vars


def localName(qname):
    # wtf - elementtree cant do this for me
    return qname[qname.index("}") + 1:]


def CastToTerm(node):
    """
    Helper function that casts XML node in SPARQL results
    to appropriate rdflib term
    """
    if node.tag == '{%s}bnode' % SPARQL_NS:
        return BNode(node.text)
    elif node.tag == '{%s}uri' % SPARQL_NS:
        return URIRef(node.text)
    elif node.tag == '{%s}literal' % SPARQL_NS:
        if 'datatype' in node.attrib:
            dT = URIRef(node.attrib['datatype'])
            if False:  # not node.xpath('*'):
                return Literal('', datatype=dT)
            else:
                return Literal(node.text, datatype=dT)
        elif '{http://www.w3.org/XML/1998/namespace}lang' in node.attrib:
            return Literal(node.text, lang=node.attrib[
                "{http://www.w3.org/XML/1998/namespace}lang"])
        else:
            return Literal(node.text)
    else:
        raise Exception('Unknown answer type')


class SPARQLStore(NSSPARQLWrapper, Store):
    """
    An RDFLib store around a SPARQL endpoint

    This is in theory context-aware, and should work OK
    when the context is specified. (I.e. for Graph objects)
    then all queries should work against the named graph with the
    identifier of the graph only.

    For ConjunctiveGraphs, reading is done from the "default graph"
    Exactly what this means depends on your endpoint.
    General SPARQL does not offer a simple way to query the
    union of all graphs.

    Fuseki/TDB has a flag for specifying that the default graph
    is the union of all graphs (tdb:unionDefaultGraph in the Fuseki config)
    If this is set this will work fine.

    .. warning:: The SPARQL Store does not support blank-nodes!  

                 As blank-nodes acts as variables in SPARQL queries
                 there is no way to query for a particular blank node.
                 
                 See http://www.w3.org/TR/sparql11-query/#BGPsparqlBNodes


    """
    formula_aware = False
    transaction_aware = False
    regex_matching = NATIVE_REGEX
    batch_unification = False

    def __init__(self,
                 endpoint=None, bNodeAsURI=False,
                 sparql11=True, context_aware=True):
        """
        """
        if endpoint:
            super(SPARQLStore, self).__init__(endpoint, returnFormat=XML)
        self.bNodeAsURI = bNodeAsURI
        self.nsBindings = {}
        self.sparql11 = sparql11
        self.context_aware = context_aware

    # Database Management Methods
    def create(self, configuration):
        raise TypeError('The SPARQL store is read only')

    def open(self, configuration, create=False):
        """
        sets the endpoint URL for this SPARQLStore
        if create==True an exception is thrown.
        """
        if create:
            raise Exception("Cannot create a SPARQL Endpoint")

        self.query_endpoint = configuration

    def __set_query_endpoint(self, queryEndpoint):
        super(SPARQLStore, self).__init__(queryEndpoint, returnFormat=XML)
        self.endpoint = queryEndpoint

    def __get_query_endpoint(self):
        return self.endpoint

    query_endpoint = property(__get_query_endpoint, __set_query_endpoint)

    def destroy(self, configuration):
        """
        FIXME: Add documentation
        """
        raise TypeError('The SPARQL store is read only')

    # Transactional interfaces
    def commit(self):
        """ """
        raise TypeError('The SPARQL store is read only')

    def rollback(self):
        """ """
        raise TypeError('The SPARQL store is read only')

    def add(self, (subject, predicate, obj), context=None, quoted=False):
        """ Add a triple to the store of triples. """
        raise TypeError('The SPARQL store is read only')

    def addN(self, quads):
        """
        Adds each item in the list of statements to a specific context.
        The quoted argument is interpreted by formula-aware stores to
        indicate this statement is quoted/hypothetical.

        Note that the default implementation is a redirect to add.
        """
        raise TypeError('The SPARQL store is read only')

    def remove(self, (subject, predicate, obj), context):
        """ Remove a triple from the store """
        raise TypeError('The SPARQL store is read only')

    def query(self, query,
              initNs={},
              initBindings={},
              queryGraph=None,
              DEBUG=False):
        self.debug = DEBUG
        assert isinstance(query, basestring)
        self.setNamespaceBindings(initNs)
        if initBindings:
            if not self.sparql11:
                raise Exception(
                    "initBindings not supported for SPARQL 1.0 Endpoints.")
            v = list(initBindings)

            # VALUES was added to SPARQL 1.1 on 2012/07/24
            query += "\nVALUES ( %s )\n{ ( %s ) }\n"\
                % (" ".join("?" + str(x) for x in v),
                   " ".join(initBindings[x].n3() for x in v))

        self.resetQuery()

        if self.context_aware and queryGraph and queryGraph != '__UNION__':
            # we care about context

            if not re.search('[\s{]GRAPH[{\s]', query, flags=re.I):
                # if a GRAPH clause was already specified, move on...

                # insert GRAPH clause after/before first/last { }
                # not 100% sure how rock-steady this is
                i1 = query.index("{") + 1
                i2 = query.rindex("}")
                query = query[:i1] + ' GRAPH %s { ' % queryGraph.n3() + \
                    query[i1:i2] + ' } ' + query[i2:]

        self.setQuery(query)

        return Result.parse(SPARQLWrapper.query(self).response)

    def triples(self, (s, p, o), context=None):
        """
        SELECT ?subj ?pred ?obj WHERE { ?subj ?pred ?obj }
        """

        if ( isinstance(s, BNode) or
             isinstance(p, BNode) or 
             isinstance(o, BNode) ): 
            raise Exception("SPARQLStore does not support Bnodes! See http://www.w3.org/TR/sparql11-query/#BGPsparqlBNodes")

        vars = []
        if not s:
            s = Variable('s')
            vars.append(s)

        if not p:
            p = Variable('p')
            vars.append(p)
        if not o:
            o = Variable('o')
            vars.append(o)

        if vars:
            v = ' '.join([term.n3() for term in vars])
        else:
            v = '*'
        if self.context_aware and context is not None:

            query = "SELECT %s WHERE { GRAPH %s { %s %s %s } }" % \
                (v, context.identifier.n3(),
                 s.n3(), p.n3(), o.n3())
        else:
            query = "SELECT %s WHERE { %s %s %s }" % \
                (v, s.n3(), p.n3(), o.n3())

        self.setQuery(query)
        doc = ElementTree.parse(SPARQLWrapper.query(self).response)
        # ElementTree.dump(doc)
        for rt, vars in TraverseSPARQLResultDOM(doc, asDictionary=True):
            yield (rt.get(s, s),
                   rt.get(p, p),
                   rt.get(o, o)), None

    def triples_choices(self, (subject, predicate, object_), context=None):
        """
        A variant of triples that can take a list of terms instead of a
        single term in any slot.  Stores can implement this to optimize
        the response time from the import default 'fallback' implementation,
        which will iterate over each term in the list and dispatch to
        triples.
        """
        raise NotImplementedError('Triples choices currently not supported')

    def __len__(self, context=None):
        if not self.sparql11:
            raise NotImplementedError(
                "For performance reasons, this is not" +
                "supported for sparql1.0 endpoints")
        else:
            if self.context_aware and context is not None:
                q = "SELECT (count(*) as ?c) FROM %s WHERE {?s ?p ?o .}" % (
                    context.identifier.n3())
            else:
                q = "SELECT (count(*) as ?c) WHERE {?s ?p ?o .}"
            self.setQuery(q)
            doc = ElementTree.parse(SPARQLWrapper.query(self).response)
            rt, vars = iter(
                TraverseSPARQLResultDOM(doc, asDictionary=True)).next()
            return int(rt.get(Variable("c")))

    def contexts(self, triple=None):
        """
        Iterates over results to SELECT ?NAME { GRAPH ?NAME { ?s ?p ?o } }
        returning instances of this store with the SPARQL wrapper
        object updated via addNamedGraph(?NAME)
        This causes a named-graph-uri key / value  pair to be sent over
        the protocol
        """

        if triple:
            s, p, o = triple
        else:
            s = p = o = None

        params = ((s if s else Variable('s')).n3(),
                  (p if p else Variable('p')).n3(),
                  (o if o else Variable('o')).n3())

        self.setQuery(
            'SELECT ?name WHERE { GRAPH ?name { %s %s %s }}' % params)
        doc = ElementTree.parse(SPARQLWrapper.query(self).response)

        return (rt.get(Variable("name"))
                for rt, vars in TraverseSPARQLResultDOM(doc, asDictionary=True))

    # Namespace persistence interface implementation
    def bind(self, prefix, namespace):
        self.nsBindings[prefix] = namespace

    def prefix(self, namespace):
        """ """
        return dict(
            [(v, k) for k, v in self.nsBindings.items()]
        ).get(namespace)

    def namespace(self, prefix):
        return self.nsBindings.get(prefix)

    def namespaces(self):
        for prefix, ns in self.nsBindings.items():
            yield prefix, ns


class SPARQLUpdateStore(SPARQLStore):
    """
    A store using SPARQL queries for read-access
    and SPARQL Update for changes

    This can be context-aware, if so, any changes will
    be to the given named graph only.

    For Graph objects, everything works as expected.

    .. warning:: The SPARQL Update Store does not support blank-nodes!  

                 As blank-nodes acts as variables in SPARQL queries
                 there is no way to query for a particular blank node.
                 
                 See http://www.w3.org/TR/sparql11-query/#BGPsparqlBNodes



    """

    def __init__(self,
                 queryEndpoint=None, update_endpoint=None,
                 bNodeAsURI=False, sparql11=True,
                 context_aware=True):

        SPARQLStore.__init__(self,
                             queryEndpoint, bNodeAsURI, sparql11, context_aware)

        self.connection = None
        if update_endpoint:
            self.update_endpoint = update_endpoint

        self.headers = {'Content-type': "application/sparql-update",
                        'Connection': 'Keep-alive'}

    def __set_update_endpoint(self, update_endpoint):
        self.__update_endpoint = update_endpoint

        p = urlparse.urlparse(self.update_endpoint)

        assert not p.username, \
            "SPARQL Update store does not support HTTP authentication"
        assert not p.password, \
            "SPARQL Update store does not support HTTP authentication"
        assert p.scheme == "http", "SPARQL Update is an http protocol!"
        self.host = p.hostname
        self.port = p.port
        self.path = p.path
        self.connection = httplib.HTTPConnection(
            self.host, self.port)

    def __get_update_endpoint(self):
        return self.__update_endpoint

    update_endpoint = property(
        __get_update_endpoint,
        __set_update_endpoint,
        doc='the HTTP URL for the Update endpoint, typically' +
            'something like http://server/dataset/update')

    def open(self, configuration, create=False):
        """
        sets the endpoint URLs for this SPARQLStore
        :param configuration: either a tuple of (queryEndpoint, update_endpoint), or a string with the query endpoint
        :param create: if True an exception is thrown.
        """

        if create:
            raise Exception("Cannot create a SPARQL Endpoint")

        if isinstance(configuration, tuple):
            self.query_endpoint = configuration[0]
            if len(configuration) > 1:
                self.update_endpoint = configuration[1]
        else:
            self.endpoint = configuration

        if not self.update_endpoint:
            self.update_endpoint = self.endpoint

    # Transactional interfaces
    def commit(self):
        """ """
        raise TypeError('The SPARQL Update store is not transaction aware!')

    def rollback(self):
        """ """
        raise TypeError('The SPARQL Update store is not transaction aware')

    def add(self, spo, context=None, quoted=False):
        """ Add a triple to the store of triples. """

        if not self.connection:
            raise "UpdateEndpoint is not set - call 'open'"

        assert not quoted
        (subject, predicate, obj) = spo

        if ( isinstance(subject, BNode) or
             isinstance(predicate, BNode) or 
             isinstance(obj, BNode) ): 
            raise Exception("SPARQLStore does not support Bnodes! See http://www.w3.org/TR/sparql11-query/#BGPsparqlBNodes")


        triple = "%s %s %s ." % (subject.n3(), predicate.n3(), obj.n3())
        if self.context_aware and context is not None:
            q = "INSERT DATA { GRAPH %s { %s } }" % (
                context.identifier.n3(), triple)
        else:
            q = "INSERT DATA { %s }" % triple
        r = self._do_update(q)
        content = r.read()  # we expect no content
        if r.status not in (200, 204):
            raise Exception("Could not update: %d %s\n%s" % (
                r.status, r.reason, content))

    def addN(self, quads):
        """ Add a list of quads to the store. """
        if not self.connection:
            raise "UpdateEndpoint is not set - call 'open'"

        data = ""
        for spoc in quads:
            (subject, predicate, obj, context) = spoc

            if ( isinstance(subject, BNode) or
                 isinstance(predicate, BNode) or 
                 isinstance(obj, BNode) ): 
                raise Exception("SPARQLStore does not support Bnodes! See http://www.w3.org/TR/sparql11-query/#BGPsparqlBNodes")


            triple = "%s %s %s ." % (subject.n3(), predicate.n3(), obj.n3())
            data += "INSERT DATA { GRAPH <%s> { %s } }\n" % (
                context.identifier, triple)
        r = self._do_update(data)
        content = r.read()  # we expect no content
        if r.status not in (200, 204):
            raise Exception("Could not update: %d %s\n%s" % (
                r.status, r.reason, content))

    def remove(self, spo, context):
        """ Remove a triple from the store """
        if not self.connection:
            raise "UpdateEndpoint is not set - call 'open'"

        (subject, predicate, obj) = spo
        if not subject:
            subject = Variable("S")
        if not predicate:
            predicate = Variable("P")
        if not obj:
            obj = Variable("O")

        triple = "%s %s %s ." % (subject.n3(), predicate.n3(), obj.n3())
        if self.context_aware and context is not None:
            q = "DELETE { GRAPH %s { %s } } WHERE { GRAPH %s { %s } }" % (
                context.identifier.n3(), triple,
                context.identifier.n3(), triple)
        else:
            q = "DELETE { %s } WHERE { %s } " % (triple, triple)
        r = self._do_update(q)
        content = r.read()  # we expect no content
        if r.status not in (200, 204):
            raise Exception("Could not update: %d %s\n%s" % (
                r.status, r.reason, content))

    def _do_update(self, update):
        import urllib
        update = urllib.urlencode({'query': update})
        self.connection.request(
            'POST', self.path, update.encode("utf-8"), self.headers)
        return self.connection.getresponse()

    def update(self, query):
        """
        Perform a SPARQL Update Query against the endpoint,
        INSERT, LOAD, DELETE etc.
        """
        r = self._do_update(query)
        content = r.read()  # we expect no content
        if r.status not in (200, 204):
            raise Exception("Could not update: %d %s\n%s" % (
                r.status, r.reason, content))
