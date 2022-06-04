"""
LongTurtle RDF graph serializer for RDFLib.
See <http://www.w3.org/TeamSubmission/turtle/> for syntax specification.

This variant, longturtle as opposed to just turtle, makes some small format changes
to turtle - the original turtle serializer. It:

* uses PREFIX instead of @prefix
* uses BASE instead of @base
* adds a new line at RDF.type, or 'a'
* adds a newline and an indent for all triples with more than one object (object list)
* adds a new line and ';' for the last triple in a set with '.'
    on the start of the next line
* uses default encoding (encode()) is used instead of "latin-1"

- Nicholas Car, 2021
"""

from rdflib.exceptions import Error
from rdflib.namespace import RDF
from rdflib.term import BNode, Literal, URIRef

from .turtle import RecursiveSerializer

__all__ = ["LongTurtleSerializer"]

SUBJECT = 0
VERB = 1
OBJECT = 2

_GEN_QNAME_FOR_DT = False
_SPACIOUS_OUTPUT = False


class LongTurtleSerializer(RecursiveSerializer):

    short_name = "longturtle"
    indentString = "    "

    def __init__(self, store):
        self._ns_rewrite = {}
        super(LongTurtleSerializer, self).__init__(store)
        self.keywords = {RDF.type: "a"}
        self.reset()
        self.stream = None
        self._spacious = _SPACIOUS_OUTPUT

    def addNamespace(self, prefix, namespace):
        # Turtle does not support prefixes that start with _
        # if they occur in the graph, rewrite to p_blah
        # this is more complicated since we need to make sure p_blah
        # does not already exist. And we register namespaces as we go, i.e.
        # we may first see a triple with prefix _9 - rewrite it to p_9
        # and then later find a triple with a "real" p_9 prefix

        # so we need to keep track of ns rewrites we made so far.

        if (prefix > "" and prefix[0] == "_") or self.namespaces.get(
            prefix, namespace
        ) != namespace:

            if prefix not in self._ns_rewrite:
                p = "p" + prefix
                while p in self.namespaces:
                    p = "p" + p
                self._ns_rewrite[prefix] = p

            prefix = self._ns_rewrite.get(prefix, prefix)

        super(LongTurtleSerializer, self).addNamespace(prefix, namespace)
        return prefix

    def reset(self):
        super(LongTurtleSerializer, self).reset()
        self._shortNames = {}
        self._started = False
        self._ns_rewrite = {}

    def serialize(self, stream, base=None, encoding=None, spacious=None, **args):
        self.reset()
        self.stream = stream
        # if base is given here, use, if not and a base is set for the graph use that
        if base is not None:
            self.base = base
        elif self.store.base is not None:
            self.base = self.store.base

        if spacious is not None:
            self._spacious = spacious

        self.preprocess()
        subjects_list = self.orderSubjects()

        self.startDocument()

        firstTime = True
        for subject in subjects_list:
            if self.isDone(subject):
                continue
            if firstTime:
                firstTime = False
            if self.statement(subject) and not firstTime:
                self.write("\n")

        self.endDocument()
        self.write("\n")

        self.base = None

    def preprocessTriple(self, triple):
        super(LongTurtleSerializer, self).preprocessTriple(triple)
        for i, node in enumerate(triple):
            if node in self.keywords:
                continue
            # Don't use generated prefixes for subjects and objects
            self.getQName(node, gen_prefix=(i == VERB))
            if isinstance(node, Literal) and node.datatype:
                self.getQName(node.datatype, gen_prefix=_GEN_QNAME_FOR_DT)
        p = triple[1]
        if isinstance(p, BNode):  # hmm - when is P ever a bnode?
            self._references[p] += 1

    def getQName(self, uri, gen_prefix=True):
        if not isinstance(uri, URIRef):
            return None

        try:
            parts = self.store.compute_qname(uri, generate=gen_prefix)
        except:
            # is the uri a namespace in itself?
            pfx = self.store.store.prefix(uri)

            if pfx is not None:
                parts = (pfx, uri, "")
            else:
                # nothing worked
                return None

        prefix, namespace, local = parts

        # QName cannot end with .
        if local.endswith("."):
            return None

        prefix = self.addNamespace(prefix, namespace)

        return "%s:%s" % (prefix, local)

    def startDocument(self):
        self._started = True
        ns_list = sorted(self.namespaces.items())

        if self.base:
            self.write(self.indent() + "BASE <%s>\n" % self.base)
        for prefix, uri in ns_list:
            self.write(self.indent() + "PREFIX %s: <%s>\n" % (prefix, uri))
        if ns_list and self._spacious:
            self.write("\n")

    def endDocument(self):
        if self._spacious:
            self.write("\n")

    def statement(self, subject):
        self.subjectDone(subject)
        return self.s_squared(subject) or self.s_default(subject)

    def s_default(self, subject):
        self.write("\n" + self.indent())
        self.path(subject, SUBJECT)
        self.write("\n" + self.indent())
        self.predicateList(subject)
        self.write(" ;\n.")
        return True

    def s_squared(self, subject):
        if (self._references[subject] > 0) or not isinstance(subject, BNode):
            return False
        self.write("\n" + self.indent() + "[]")
        self.predicateList(subject)
        self.write(" ;\n.")
        return True

    def path(self, node, position, newline=False):
        if not (
            self.p_squared(node, position, newline)
            or self.p_default(node, position, newline)
        ):
            raise Error("Cannot serialize node '%s'" % (node,))

    def p_default(self, node, position, newline=False):
        if position != SUBJECT and not newline:
            self.write(" ")
        self.write(self.label(node, position))
        return True

    def label(self, node, position):
        if node == RDF.nil:
            return "()"
        if position is VERB and node in self.keywords:
            return self.keywords[node]
        if isinstance(node, Literal):
            return node._literal_n3(
                use_plain=True,
                qname_callback=lambda dt: self.getQName(dt, _GEN_QNAME_FOR_DT),
            )
        else:
            node = self.relativize(node)

            return self.getQName(node, position == VERB) or node.n3()

    def p_squared(self, node, position, newline=False):
        if (
            not isinstance(node, BNode)
            or node in self._serialized
            or self._references[node] > 1
            or position == SUBJECT
        ):
            return False

        if not newline:
            self.write(" ")

        if self.isValidList(node):
            # this is a list
            self.depth += 2
            self.write("(\n")
            self.depth -= 1
            self.doList(node)
            self.depth -= 1
            self.write("\n" + self.indent(1) + ")")
        else:
            self.subjectDone(node)
            self.depth += 2
            self.write("[\n")
            self.depth -= 1
            self.predicateList(node, newline=False)
            self.depth -= 1
            self.write("\n" + self.indent(1) + "]")

        return True

    def isValidList(self, l_):
        """
        Checks if l is a valid RDF list, i.e. no nodes have other properties.
        """
        try:
            if self.store.value(l_, RDF.first) is None:
                return False
        except:
            return False
        while l_:
            if l_ != RDF.nil and len(list(self.store.predicate_objects(l_))) != 2:
                return False
            l_ = self.store.value(l_, RDF.rest)
        return True

    def doList(self, l_):
        i = 0
        while l_:
            item = self.store.value(l_, RDF.first)
            if item is not None:
                if i == 0:
                    self.write(self.indent(1))
                else:
                    self.write("\n" + self.indent(1))
                self.path(item, OBJECT, newline=True)
                self.subjectDone(l_)
            l_ = self.store.value(l_, RDF.rest)
            i += 1

    def predicateList(self, subject, newline=False):
        properties = self.buildPredicateHash(subject)
        propList = self.sortProperties(properties)
        if len(propList) == 0:
            return
        self.write(self.indent(1))
        self.verb(propList[0], newline=True)
        self.objectList(properties[propList[0]])
        for predicate in propList[1:]:
            self.write(" ;\n" + self.indent(1))
            self.verb(predicate, newline=True)
            self.objectList(properties[predicate])

    def verb(self, node, newline=False):
        self.path(node, VERB, newline)

    def objectList(self, objects):
        count = len(objects)
        if count == 0:
            return
        depthmod = (count == 1) and 0 or 1
        self.depth += depthmod
        first_nl = False
        if count > 1:
            self.write("\n" + self.indent(1))
            first_nl = True
        self.path(objects[0], OBJECT, newline=first_nl)
        for obj in objects[1:]:
            self.write(" ,\n")
            self.write(self.indent(1))
            self.path(obj, OBJECT, newline=True)
        self.depth -= depthmod
