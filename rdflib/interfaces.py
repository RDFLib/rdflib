
try:
    from zope.interface import Interface, classImplements, implements
except ImportError:
    class Interface(object): pass
    def classImplements(c, i): pass
    def implements(*args): pass

from rdflib import RDF
    
class IGraph(Interface):
    """\
    An rdflib.Graph indexes data expressed in the Resource Description
    Framework (RDF).  Any kind of content, whether inside Zope or from
    some outside source, can be cataloged if it can describe itself
    using the RDF standard.  Any kind of RDF vocabulary like RSS, OWL,
    DAML+OIL, Dublin Core, or any kind of XML schema or data can be
    expressed into the graph.

    Once data is graphed it can be queried using either the Python
    query interface, a TALES-based RDF query expression language, or
    the sparql rdf query language.  Results of a query can be either a
    generator of result records or RDF in xml or NT format.

    In Semantic Web terms, a graph is a persistent triple store.  RDF
    is broken down into subject, predicate, and object relations
    (called triples) and each relation is indexed.  The triple store
    can then be queried for triples that match patterns.
    """

    def parse(rdf, format="xml"):
        """ Parse RDF-XML into the catalog. """

    def add((subject, predicate, object)):
        """ Add one triple to the catalog.  """

    def remove((subject, predicate, object)):
        """ Remove one triple from the catalog. """

    def triples((subject, predicate, object), *args):
        """ Query the triple store. """

    def contexts(triple=None):
        """ Generator over all contexts in the graph. If triple is
        specified, a generator over all contexts the triple is in."""

    def value(subject, predicate=RDF.value, object=None, default=None, any=False):
        """ Get a value for a subject/predicate, predicate/object, or
        subject/object pair -- exactly one of subject, predicate,
        object must be None. Useful if one knows that there may only
        be one value.

        It is one of those situations that occur a lot, hence this
        'macro' like utility

        Parameters:
        -----------
        subject, predicate, object  -- exactly one must be None
        default -- value to be returned if no values found
        any -- if True:
                 return any value in the case there is more than one
               else:
                 raise UniquenessError
        """

    def label(subject, default=''):
        """ Queries for the RDFS.label of the subject, returns default
        if no label exists."""

    def comment(subject, default=''):
        """ Queries for the RDFS.comment of the subject, returns
        default if no comment exists."""

    def items(list):
        """Generator over all items in the resource specified by list
        (an RDF collection)"""

    def __iter__():
        """ Iterates over all triples in the store."""

    def __contains__(triple):
        """ Support for 'triple in graph' syntax."""

    def __len__(context=None):
        """ Returns the number of triples in the graph. If context is
        specified then the number of triples in the context is
        returned instead."""

    def __eq__(other):
        """ Test if Graph is exactly equal to Graph other."""

    def __iadd__(other):
        """ Add all triples in Graph other to Graph."""

    def __isub__(other):
        """ Subtract all triples in Graph other from Graph."""

    def subjects(predicate=None, object=None):
        """ A generator of subjects with the given predicate and
        object."""

    def predicates(subject=None, object=None):
        """ A generator of predicates with the given subject and
        object."""

    def objects(subject=None, predicate=None):
        """ A generator of objects with the given subject and
        predicate."""

    def subject_predicates(object=None):
        """ A generator of (subject, predicate) tuples for the given
        object"""

    def subject_objects(predicate=None):
        """ A generator of (subject, object) tuples for the given
        predicate"""

    def predicate_objects(subject=None):
        """ A generator of (predicate, object) tuples for the given
        subject"""

    def get_context(identifier):
        """ Returns a Context graph for the given identifier, which
        must be a URIRef or BNode."""

    def remove_context(identifier):
        """ Removes the given context from the graph. """

    def transitive_objects(subject, property, remember=None):
        """ """

    def transitive_subjects(predicate, object, remember=None):
        """ """

    def load(location, publicID=None, format="xml"):
        """ for b/w compat. See parse."""

    def save(location, format="xml", base=None, encoding=None):
        """ for b/x compat. See serialize."""

    def context_id(uri):
        pass

    def parse(source, publicID=None, format="xml"):
        """ Parse source into Graph. If Graph is context-aware it'll
        get loaded into it's own context (sub graph). Format defaults
        to xml (AKA rdf/xml). The publicID argument is for specifying
        the logical URI for the case that it's different from the
        physical source URI. Returns the context into which the source
        was parsed."""

    def serialize(destination=None, format="xml", base=None, encoding=None):
        """ Serialize the Graph to destination. If destination is None
        serialize method returns the serialization as a string. Format
        defaults to xml (AKA rdf/xml)."""

    def seq(subject):
        """
        Check if subject is an rdf:Seq. If yes, it returns a Seq
        class instance, None otherwise.
        """

    def absolutize(uri, defrag=1):
        """ Will turn uri into an absolute URI if it's not one already. """

    def bind(prefix, namespace, override=True):
        """Bind prefix to namespace. If override is True will bind
        namespace to given prefix if namespace was already bound to a
        different prefix."""

    def namespaces():
        """Generator over all the prefix, namespace tuples.
        """

class IIdentifier(Interface):

    def n3():
        """ Return N3 representation of identifier. """

    def startswith(string):
        """ dummy. """

    def __cmp__(other):
        """ dummy. """
