import logging
import re #, stopdict

_logger = logging.getLogger(__name__)


try:
    from hashlib import md5
except ImportError:
    from md5 import md5
    
from rdflib.graph import ConjunctiveGraph
from rdflib.term import Literal
from rdflib.term import NamespaceDict as Namespace
from rdflib.term import URIRef
from rdflib.store import TripleAddedEvent, TripleRemovedEvent


def get_stopdict():
    """Return a dictionary of stopwords."""
    return _dict

_words = [
    "a", "and", "are", "as", "at", "be", "but", "by",
    "for", "if", "in", "into", "is", "it",
    "no", "not", "of", "on", "or", "such",
    "that", "the", "their", "then", "there", "these",
    "they", "this", "to", "was", "will", "with"
]

_dict = {}
for w in _words:
    _dict[w] = None

word_pattern = re.compile(r"(?u)\w+")
has_stop = get_stopdict().has_key

def splitter(s):
    return word_pattern.findall(s)

def stopper(s):
    return [w.lower() for w in s if not has_stop(w)]



class TextIndex(ConjunctiveGraph):
    """
    An rdflib graph event handler than indexes text literals that are
    added to a another graph.

    This class lets you 'search' the text literals in an RDF graph.
    Typically in RDF to search for a substring in an RDF graph you
    would have to 'brute force' search every literal string looking
    for your substring.

    Instead, this index stores the words in literals into another
    graph whose structure makes searching for terms much less
    expensive.  It does this by chopping up the literals into words,
    removing very common words (currently only in English) and then
    adding each of those words into an RDF graph that describes the
    statements in the original graph that the word came from.

    First, let's create a graph that will transmit events and a text
    index that will receive those events, and then subscribe the text
    index to the event graph:

      >>> e = ConjunctiveGraph()
      >>> t = TextIndex()
      >>> t.subscribe_to(e)

    When triples are added to the event graph (e) events will be fired
    that trigger event handlers in subscribers.  In this case our only
    subscriber is a text index and its action is to index triples that
    contain literal RDF objects.  Here are 3 such triples:

      >>> e.add((URIRef('a'), URIRef('title'), Literal('one two three')))
      >>> e.add((URIRef('b'), URIRef('title'), Literal('two three four')))
      >>> e.add((URIRef('c'), URIRef('title'), Literal('three four five')))

    Of the three literal objects that were added, they all contain
    five unique terms.  These terms can be queried directly from the
    text index:
    
      >>> t.term_strings() ==  set(['four', 'five', 'three', 'two', 'one'])
      True

    Now we can search for statement that contain certain terms.  Let's
    search for 'one' which occurs in only one of the literals
    provided, 'a'.  This can be queried for:

      >>> t.search('one')==set([(URIRef('a'), URIRef('title'), None)])
      True

    'one' and 'five' only occur in one statement each, 'two' and
    'four' occur in two, and 'three' occurs in three statements:

      >>> len(list(t.search('one')))
      1
      >>> len(list(t.search('two')))
      2
      >>> len(list(t.search('three')))
      3
      >>> len(list(t.search('four')))
      2
      >>> len(list(t.search('five')))
      1

    Lets add some more statements with different predicates.

      >>> e.add((URIRef('a'), URIRef('creator'), Literal('michel')))
      >>> e.add((URIRef('b'), URIRef('creator'), Literal('Atilla the one Hun')))
      >>> e.add((URIRef('c'), URIRef('creator'), Literal('michel')))
      >>> e.add((URIRef('d'), URIRef('creator'), Literal('Hun Mung two')))

    Now 'one' occurs in two statements:

      >>> assert len(list(t.search('one'))) == 2

    And 'two' occurs in three statements, here they are:

      >>> t.search('two')==set([(URIRef('d'), URIRef('creator'), None), (URIRef('a'), URIRef('title'), None), (URIRef('b'), URIRef('title'), None)])
      True

    The predicates that are searched can be restricted by provding an
    argument to 'search()':

      >>> t.search('two', URIRef('creator'))==set([(URIRef('d'), URIRef('creator'), None)])
      True

      >>> t.search('two', URIRef(u'title'))==set([(URIRef('a'), URIRef('title'), None), (URIRef('b'), URIRef('title'), None)])
      True

    You can search for more than one term by simply including it in
    the query:
    
      >>> t.search('two three', URIRef(u'title'))==set([(URIRef('c'), URIRef('title'), None), (URIRef('a'), URIRef('title'), None), (URIRef('b'), URIRef('title'), None)])
      True

    The above query returns all the statements that contain 'two' OR
    'three'.  For the documents that contain 'two' AND 'three', do an
    intersection of two queries:

      >>> t.search('two', URIRef(u'title')).intersection(t.search(u'three', URIRef(u'title')))==set([(URIRef('a'), URIRef('title'), None), (URIRef('b'), URIRef('title'), None)])
      True

    Intersection two queries like this is probably not the most
    efficient way to do it, but for reasonable data sets this isn't a
    problem.  Larger data sets will want to query the graph with
    sparql or something else more efficient.

    In all the above queries, the object of each statement was always
    'None'.  This is because the index graph does not store the object
    data, that would make it very large, and besides the data is
    available in the original data graph.  For convenience, a method
    is provides to 'link' an index graph to a data graph.  This allows
    the index to also provide object data in query results.

      >>> t.link_to(e)
      >>> set([str(i[2]) for i in t.search('two', URIRef(u'title')).intersection(t.search(u'three', URIRef(u'title')))]) ==  set(['two three four', 'one two three'])
      True

    You can remove the link by assigning None:

      >>> t.link_to(None)

    Unindexing means to remove statments from the index graph that
    corespond to a statement in the data graph.  Note that while it is
    possible to remove the index information of the occurances of
    terms in statements, it is not possible to remove the terms
    themselves, terms are 'absolute' and are never removed from the
    index graph.  This is not a problem since languages have finite
    terms:

      >>> e.remove((URIRef('a'), URIRef('creator'), Literal('michel')))
      >>> e.remove((URIRef('b'), URIRef('creator'), Literal('Atilla the one Hun')))
      >>> e.remove((URIRef('c'), URIRef('creator'), Literal('michel')))
      >>> e.remove((URIRef('d'), URIRef('creator'), Literal('Hun Mung two')))

    Now 'one' only occurs in one statement:

      >>> assert len(list(t.search('one'))) == 1

    And 'two' only occurs in two statements, here they are:

      >>> t.search('two')==set([(URIRef('a'), URIRef('title'), None), (URIRef('b'), URIRef('title'), None)])
      True

    The predicates that are searched can be restricted by provding an
    argument to 'search()':

      >>> t.search('two', URIRef(u'creator'))
      set([])

      >>> t.search('two', URIRef(u'title'))==set([(URIRef('a'), URIRef('title'), None), (URIRef('b'), URIRef('title'), None)])
      True

    """

    linked_data = None

    text_index = Namespace('http://rdflib.net/text_index#')
    term = Namespace('http://rdflib.net/text_index#')["term"]
    termin = Namespace('http://rdflib.net/text_index#')["termin"]

    def __init__(self, store='default'):
        super(TextIndex, self).__init__(store)

    def add_handler(self, event):
        if type(event.triple[2]) is Literal:
            self.index(event.triple)
        
    def remove_handler(self, event):
        if type(event.triple[2]) is Literal:
            self.unindex(event.triple)

    def index(self, (s, p, o)):
        # this code is tricky so it's annotated.  unindex is the reverse of this method.
                
        if type(o) is Literal:                            # first, only index statements that have a literal object
            for word in stopper(splitter(o)):             # split the literal and remove any stopwords
                word = Literal(word)                      # create a new literal for each word in the object
                
                # if that word already exists in the statement
                # loop over each context the term occurs in
                if self.value(predicate=self.term, object=word, any=True): 
                    for t in set(self.triples((None, self.term, word))):
                        t = t[0]
                        # if the graph does not contain an occurance of the term in the statement's subject
                        # then add it
                        if not (t, self.termin, s) in self:
                            self.add((t, self.termin, s))

                        # ditto for the predicate
                        if not (p, t, s) in self:
                            self.add((p, t, s))

                else: # if the term does not exist in the graph, add it, and the references to the statement.
                    # t gets used as a predicate, create identifier accordingly (AKA can't be a BNode)
                    h = md5(word.encode('utf-8')); h.update(s.encode('utf-8')); h.update(p.encode('utf-8'))
                    t = self.text_index["term_%s" % h.hexdigest()]
                    self.add((t, self.term, word))
                    self.add((t, self.termin, s))
                    self.add((p, t, s))
        
    def unindex(self, (s, p, o)):
        if type(o) is Literal:
            for word in stopper(splitter(o)):
                word = Literal(word)
                if self.value(predicate=self.term, object=word, any=True):
                    for t in self.triples((None, self.term, word)):
                        t = t[0]
                        if (t, self.termin, s) in self:
                            self.remove((t, self.termin, s))
                        if (p, t, s) in self:
                            self.remove((p, t, s))

    def terms(self):
        """ Returns a generator that yields all of the term literals in the graph. """
        return set(self.objects(None, self.term))

    def term_strings(self):
        """ Return a list of term strings. """
        return set([str(i) for i in self.terms()])

    def search(self, terms, predicate=None):
        """ Returns a set of all the statements the term occurs in. """
        if predicate and not isinstance(predicate, URIRef):
            _logger.warning("predicate is not a URIRef")
            predicate = URIRef(predicate)
        results = set()
        terms = [Literal(term) for term in stopper(splitter(terms))]    

        for term in terms:
            for t in self.triples((None, self.term, term)):
                for o in self.objects(t[0], self.termin):
                    for p in self.triples((predicate, t[0], o)):
                        if self.linked_data is None:
                            results.add((o, p[0], None))
                        else:
                            results.add((o, p[0], self.linked_data.value(o, p[0])))
        return results

    def index_graph(self, graph):
        """
        Index a whole graph.  Must be a conjunctive graph.
        """
        for t in graph.triples((None,None,None)):
            self.index(t)

    def link_to(self, graph):
        """
        Link to a graph
        """
        self.linked_data = graph

    def subscribe_to(self, graph):
        """
        Subscribe this index to a graph.
        """
        graph.store.dispatcher.subscribe(TripleAddedEvent, self.add_handler)
        graph.store.dispatcher.subscribe(TripleRemovedEvent, self.remove_handler)


def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()
