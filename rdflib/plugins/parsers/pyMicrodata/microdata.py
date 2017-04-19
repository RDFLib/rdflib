# -*- coding: utf-8 -*-
"""

The core of the Microdata->RDF conversion, a more or less verbatim implementation of the
U{W3C IG Note<http://www.w3.org/TR/microdata-rdf/>}. Because the implementation was also used to check
the note itself, it tries to be fairly close to the text.


@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
"""

"""
$Id: microdata.py,v 1.6 2014-12-17 08:52:43 ivan Exp $
$Date: 2014-12-17 08:52:43 $

Added a reaction on the RDFaStopParsing exception: if raised while setting up the local execution context, parsing
is stopped (on the whole subtree)
"""


from rdflib import URIRef
from rdflib import Literal
from rdflib import BNode
from rdflib import Namespace

from rdflib import RDF as ns_rdf
from rdflib import XSD as ns_xsd

from six.moves.urllib.parse import urlsplit, urlunsplit

ns_owl = Namespace("http://www.w3.org/2002/07/owl#")

from .registry import registry, vocab_names
from .utils import get_Literal, get_time_type
from .utils import get_lang_from_hierarchy, is_absolute_URI, generate_URI, \
    fragment_escape




# ----------------------------------------------------------------------------


class EvaluationContext(object):
    """
    Evaluation context structure. See Section 6.1 of the U{W3C IG Note<http://www.w3.org/TR/microdata-rdf/>}for the details.

    @ivar current_type : an absolute URL for the current type, used when an item does not contain an item type
    @ivar memory: mapping from items to RDF subjects
    @type memory: dictionary
    @ivar current_name: an absolute URL for the in-scope name, used for generating URIs for properties of items without an item type
    @ivar current_vocabulary: an absolute URL for the current vocabulary, from the registry
    """

    def __init__(self):
        self.current_type = None
        self.memory = {}
        self.current_name = None
        self.current_vocabulary = None

    def get_memory(self, item):
        """
        Get the memory content (ie, RDF subject) for 'item', or None if not stored yet
        @param item: an 'item', in microdata terminology
        @type item: DOM Element Node
        @return: None, or an RDF Subject (URIRef or BNode)
        """
        if item in self.memory:
            return self.memory[item]
        else:
            return None

    def set_memory(self, item, subject):
        """
        Set the memory content, ie, the subject, for 'item'.
        @param item: an 'item', in microdata terminology
        @type item: DOM Element Node
        @param subject: RDF Subject
        @type subject: URIRef or Blank Node
        """
        self.memory[item] = subject

    def new_copy(self, itype):
        """
        During the generation algorithm a new copy of the current context has to be done with a new current type.

        At the moment, the content of memory is copied, ie, a fresh dictionary is created and the content copied over.
        Not clear whether that is necessary, though, maybe a simple reference is enough...
        @param itype : an absolute URL for the current type
        @return: a new evaluation context instance
        """
        retval = EvaluationContext()
        for k in self.memory:
            retval.memory[k] = self.memory[k]

        retval.current_type = itype
        retval.current_name = self.current_name
        retval.current_vocabulary = self.current_vocabulary
        return retval

    def __str__(self):
        retval = "Evaluation context:\n"
        retval += "  current type:       %s\n" % self.current_type
        retval += "  current name:       %s\n" % self.current_name
        retval += "  current vocabulary: %s\n" % self.current_vocabulary
        retval += "  memory:             %s\n" % self.memory
        retval += "----\n"
        return retval


class Microdata(object):
    """
    This class encapsulates methods that are defined by the U{microdata spec<http://www.w3.org/TR/microdata/>},
    as opposed to the RDF conversion note.

    @ivar document: top of the DOM tree, as returned by the HTML5 parser
    @ivar base: the base URI of the Dom tree, either set from the outside or via a @base element
    """

    def __init__(self, document, base=None):
        """
        @param document: top of the DOM tree, as returned by the HTML5 parser
        @param base: the base URI of the Dom tree, either set from the outside or via a @base element
        """
        self.document = document
        # set the document base, will be used to generate top level URIs
        self.base = None
        # handle the base element case for HTML
        for set_base in document.getElementsByTagName("base"):
            if set_base.hasAttribute("href"):
                # Yep, there is a local setting for base
                self.base = set_base.getAttribute("href")
                return
        # If got here, ie, if no local setting for base occurs, the input argument has it
        self.base = base

    def get_top_level_items(self):
        """
        A top level item is and element that has the @itemscope set, but no @itemtype. They are
        collected in pre-order and depth-first fashion.

        @return: list of items (ie, DOM Nodes)
        """

        def collect_items(node):
            items = []
            for child in node.childNodes:
                if child.nodeType == node.ELEMENT_NODE:
                    items += collect_items(child)

            if node.hasAttribute("itemscope") and not node.hasAttribute(
                    "itemprop"):
                # This is also a top level item
                items.append(node)

            return items

        return collect_items(self.document)

    def get_item_properties(self, item):
        """
        Collect the item's properties, ie, all DOM descendant nodes with @itemprop until the subtree hits another @itemscope. @itemrefs are also added at this point.

        @param item: current item
        @type item: DOM Node
        @return: array of items, ie, DOM Nodes
        """
        # go down the tree until another itemprop is hit, take care of the itemrefs, too; see the microdata doc
        # probably the ugliest stuff around!
        # returns a series of element nodes.
        # Is it worth filtering the ones with itemprop at that level???
        results = []
        memory = [item]
        pending = [child for child in item.childNodes if
                   child.nodeType == item.ELEMENT_NODE]

        # Add the possible "@itemref" targets to the nodes to work on
        if item.hasAttribute("itemref"):
            for it in item.getAttribute("itemref").strip().split():
                obj = self.getElementById(it)
                if obj is not None: pending.append(obj)

        while len(pending) > 0:
            current = pending.pop(0)
            if current in memory:
                # in general this raises an error; the same item cannot be there twice. In this case this is
                # simply ignored
                continue
            else:
                # this for the check above
                memory.append(current)

            # @itemscope is the barrier...
            if not current.hasAttribute("itemscope"):
                pending = [child for child in current.childNodes if
                           child.nodeType == child.ELEMENT_NODE] + pending

            if current.hasAttribute("itemprop") and current.getAttribute(
                    "itemprop").strip() != "":
                results.append(current)
            elif current.hasAttribute(
                    "itemprop-reverse") and current.getAttribute(
                    "itemprop-reverse").strip() != "":
                results.append(current)

        return results

    def getElementById(self, id):
        """This is a method defined for DOM 2 HTML, but the HTML5 parser does not seem to define it. Oh well...
        @param id: value of an @id attribute to look for
        @return: array of nodes whose @id attribute matches C{id} (formally, there should be only one...)
        """

        def collect_ids(node):
            lids = []
            for child in node.childNodes:
                if child.nodeType == node.ELEMENT_NODE:
                    lids += collect_ids(child)

            if node.hasAttribute("id") and node.getAttribute("id") == id:
                # This is also a top level item
                lids.append(node)

            return lids

        ids = collect_ids(self.document)
        if len(ids) > 0:
            return ids[0]
        else:
            return None


class MicrodataConversion(Microdata):
    """
    Top level class encapsulating the conversion algorithms as described in the W3C note.

    @ivar graph: an RDF graph; an RDFLib Graph
    @type graph: RDFLib Graph
    @ivar document: top of the DOM tree, as returned by the HTML5 parser
    @ivar base: the base of the Dom tree, either set from the outside or via a @base element
    @ivar subs: dictionary mapping predicates to possible superproperties
    @ivar bnodes: dictionary mapping items to bnodes (to be used when an item is the target of an @itemref)
    """

    def __init__(self, document, graph, base=None):
        """
        @param graph: an RDF graph; an RDFLib Graph
        @type graph: RDFLib Graph
        @param document: top of the DOM tree, as returned by the HTML5 parser
        @keyword base: the base of the Dom tree, either set from the outside or via a @base element
        """
        Microdata.__init__(self, document, base)
        self.graph = graph
        self.subs = {}
        self.bnodes = {}

        # Get the vocabularies defined in the registry bound to proper names, if any...
        for vocab in registry:
            if vocab in vocab_names:
                self.graph.bind(vocab_names[vocab], vocab)
            else:
                hvocab = vocab + '#'
                if hvocab in vocab_names:
                    self.graph.bind(vocab_names[hvocab], hvocab)

                    # Add the prefixes defined in the RDFa initial context to improve the outlook of the output
                    # I put this into a try: except: in case the pyRdfa package is not available...
                    # This is put in a debug branch; in general, the RDFLib Turtle serializer adds all the
                    # namespace declarations, which can be a bit of a problem for reading the results...

                    # try :
                    #     try :
                    #         from ..pyRdfa.initialcontext import initial_context
                    #     except :
                    #         from pyRdfa.initialcontext import initial_context
                    #     vocabs = initial_context["http://www.w3.org/2011/rdfa-context/rdfa-1.1"].ns
                    #     for prefix in list(vocabs.keys()) :
                    #         uri = vocabs[prefix]
                    #         if uri not in registry :
                    #             # if it is in the registry, then it may have needed some special microdata massage...
                    #             self.graph.bind(prefix,uri)
                    # except :
                    #     pass

    def convert(self):
        """
        Top level entry to convert and generate all the triples. It finds the top level items,
        and generates triples for each of them.
        """
        for top_level_item in self.get_top_level_items():
            self.generate_triples(top_level_item, EvaluationContext())

    def generate_triples(self, item, context):
        """
        Generate the triples for a specific item. See the W3C Note for the details.

        @param item: the DOM Node for the specific item
        @type item: DOM Node
        @param context: an instance of an evaluation context
        @type context: L{EvaluationContext}
        @return: a URIRef or a BNode for the (RDF) subject
        """

        def _get_predicate_object(prop, name, item_type):
            """
            Generate the predicate and the object for an item that contains either "itemprop" or "itemprop-reverse".
            Steps 9.1.1 to 9.1.3 of the processing steps

            @param prop: the item that should produce a predicate
            @type prop: a DOM Node for an element
            @param name: an itemprop or itemprop-reverse item
            @type name: string
            @param item_type: the type of the item; necessary for the creation of a new context
            @type item_type: a string with the absolute URI of the type
            @return: a tuple consisting of the predicate (URI) and the object for the triple to be generated
            """
            # 9.1.1. set a new context
            new_context = context.new_copy(item_type)
            # 9.1.2, generate the URI for the property name, that will be the predicate
            # Also update the context
            # Note that the method also checks, and stores, the possible superproperty/equivalent property values
            new_context.current_name = predicate = self.generate_predicate_URI(
                name, new_context)
            # 9.1.3, generate the property value. The extra flag signals that the value is a new item
            # Note that 9.1.4 step is done in the method itself, ie, a recursion may occur there
            # if a new item is hit (in which case the return value is a RDF resource chaining to a subject)
            # Note that the value may be None (e.g, for an <img> element without a @src), in which case nothing
            # is generated
            value = self.get_property_value(prop, new_context)
            return (predicate, value)

        # Step 1,2: if the subject has to be set, store it in memory
        subject = context.get_memory(item)

        if subject is None:
            # nop, there is no subject set. If there is a valid @itemid, that carries it
            if item.hasAttribute("itemid"):
                subject = URIRef(generate_URI(self.base, item.getAttribute(
                    "itemid").strip()))
            else:
                if item in self.bnodes:
                    subject = self.bnodes[item]
                else:
                    subject = BNode()
                    self.bnodes[item] = subject
            context.set_memory(item, subject)

        # Step 3: set the type triples if any
        types = []
        if item.hasAttribute("itemtype"):
            types = item.getAttribute("itemtype").strip().split()
            for t in types:
                if is_absolute_URI(t):
                    self.graph.add((subject, ns_rdf["type"], URIRef(t)))

        # Step 4, 5 to set the typing variable
        if len(types) == 0:
            itype = None
        else:
            if is_absolute_URI(types[0]):
                itype = types[0]
                context.current_name = None
            elif context.current_type is not None:
                itype = context.current_type
            else:
                itype = None

        # Step 6, 7: Check the registry for possible keys and set the vocab
        vocab = None
        if itype is not None:
            for key in list(registry.keys()):
                if itype.startswith(key):
                    # There is a predefined vocabulary for this type...
                    vocab = key
                    break
            # The registry has not set the vocabulary; it has to be extracted from the type
            if vocab is None:
                parsed = urlsplit(itype)
                if parsed.fragment != "":
                    vocab = urlunsplit((parsed.scheme, parsed.netloc,
                                        parsed.path, parsed.query, "")) + '#'
                elif parsed.path == "" and parsed.query == "":
                    vocab = itype
                    if vocab[-1] != '/': vocab += '/'
                else:
                    vocab = itype.rsplit('/', 1)[0] + '/'

        # Step 8: update vocab in the context
        if vocab is not None:
            context.current_vocabulary = vocab
        elif item.hasAttribute("itemtype"):
            context.current_vocabulary = None

        # Step 9: Get the item properties and run a cycle on those
        # each entry in the dictionary is an array of RDF objects
        for prop in self.get_item_properties(item):
            for name in prop.getAttribute("itemprop").strip().split():
                # Steps 9.1.1 to 9.1.3 are done in a separate function
                (predicate, value) = _get_predicate_object(prop, name, itype)
                if value is None: continue
                # 9.1.5, generate the triple
                self.graph.add((subject, URIRef(predicate), value))
                # 9.1.6, take care of the possible subProperty/equivalentProperty
                if name in self.subs and self.subs[name] is not None:
                    for sup in self.subs[name]:
                        self.graph.add((subject, sup, value))

        # Step 10: Almost identical to step 9, except for itemprop-reverse
        # The only difference is that a Literal value must be ignored
        for prop in self.get_item_properties(item):
            for name in prop.getAttribute("itemprop-reverse").strip().split():
                # Steps 9.1.1 to 9.1.3 are done in a separate function
                (predicate, value) = _get_predicate_object(prop, name, itype)
                if value is None or isinstance(value, Literal):
                    continue
                # 9.1.5, generate the triple
                self.graph.add((value, URIRef(predicate), subject))
                # 9.1.6, take care of the possible subProperty/equivalentProperty
                if name in self.subs and self.subs[name] is not None:
                    for sup in self.subs[name]:
                        self.graph.add((value, sup, subject))

        # Step 11: return the subject to the caller
        return subject

    def generate_predicate_URI(self, name, context):
        """
        Generate a full URI for a predicate, using the type, the vocabulary, etc.

        For details of this entry, see Section 4.4
        @param name: name of the property, ie, what appears in @itemprop
        @param context: an instance of an evaluation context
        @type context: L{EvaluationContext}
        """

        def add_to_subs(subpr):
            if subpr is not None:
                if isinstance(subpr, list):
                    self.subs[name] = []
                    for p in subpr:
                        self.subs[name].append(URIRef(p))
                else:
                    self.subs[name] = [URIRef(subpr)]

        # Step 1: absolute URI-s are fine, take them as they are
        if is_absolute_URI(name): return name

        # Step 2: if type is none, that this is just used as a fragment
        # if not context.current_type  :
        if context.current_type is None and context.current_vocabulary is None:
            if self.base[-1] == '#':
                b = self.base[:-1]
            else:
                b = self.base
            return b + '#' + fragment_escape(name)

        # Extract the possible subproperty/equivalentProperty relations on the fly
        # see if there are subproperty/equivalentProperty relations
        if name not in self.subs:
            try:
                vocab_mapping = \
                registry[context.current_vocabulary]["properties"][name]
                for rel in ["subPropertyOf", "equivalentProperty"]:
                    if rel in vocab_mapping:
                        add_to_subs(vocab_mapping[rel])
            except:
                # no harm done, no extra vocabulary term
                self.subs[name] = None
        else:
            self.subs[name] = None

        escaped_name = fragment_escape(name)
        if context.current_vocabulary[-1] == '#' or context.current_vocabulary[
            -1] == '/':
            return context.current_vocabulary + escaped_name
        else:
            return context.current_vocabulary + '#' + escaped_name

    def get_property_value(self, node, context):
        """
        Generate an RDF object, ie, the value of a property. Note that if this element contains
        an @itemscope, then a recursive call to L{MicrodataConversion.generate_triples} is done and the
        return value of that method (ie, the subject for the corresponding item) is return as an
        object.

        Otherwise, either URIRefs are created for <a>, <img>, etc, elements, or a Literal; the latter
        gets a time-related type for the <time> element, and possible numeric types for the @value
        attribute of the <meter> and <data> elements.

        @param node: the DOM Node for which the property values should be generated
        @type node: DOM Node
        @param context: an instance of an evaluation context
        @type context: L{EvaluationContext}
        @return: an RDF resource (URIRef, BNode, or Literal)
        """
        URI_attrs = {
            "a": "href",
            "audio": "src",
            "area": "href",
            "embed": "src",
            "iframe": "src",
            "img": "src",
            "link": "href",
            "object": "data",
            "source": "src",
            "track": "src",
            "video": "src"
        }
        lang = get_lang_from_hierarchy(self.document, node)

        if node.hasAttribute("itemscope"):
            # THIS IS A RECURSION ENTRY POINT!
            return self.generate_triples(node, context)

        elif node.tagName in URI_attrs:
            if node.hasAttribute(URI_attrs[node.tagName]):
                return URIRef(generate_URI(self.base, node.getAttribute(
                        URI_attrs[node.tagName]).strip()))
            else:
                return None

        elif node.tagName == "meta" and node.hasAttribute("content"):
            if lang:
                return Literal(node.getAttribute("content"), lang=lang)
            else:
                return Literal(node.getAttribute("content"))

        elif node.tagName == "time" and node.hasAttribute("datetime"):
            litval = node.getAttribute("datetime")
            dtype = get_time_type(litval)
            if dtype:
                return Literal(litval, datatype=dtype)
            else:
                return Literal(litval)

        elif node.tagName == "meter" or node.tagName == "data":
            if node.hasAttribute("value"):
                val = node.getAttribute("value")
                # check whether the attribute value can be defined as a float or an integer
                try:
                    fval = int(val)
                    return Literal(val, datatype=ns_xsd["integer"])
                except:
                    # Well, not an int, try then a float
                    try:
                        fval = float(val)
                        return Literal(val, datatype=ns_xsd["double"])
                    except:
                        # Sigh, this is not a valid value, but let it go through as a plain literal nevertheless
                        return Literal(val)
            else:
                return Literal("")

        else:
            if lang:
                return Literal(get_Literal(node), lang=lang)
            else:
                return Literal(get_Literal(node))
