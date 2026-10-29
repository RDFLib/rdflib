from __future__ import annotations

import codecs
import xml.dom.minidom
from collections.abc import Callable, Generator
from typing import IO, Any
from xml.sax.saxutils import escape, quoteattr

from rdflib.collection import Collection
from rdflib.graph import Graph
from rdflib.namespace import RDF, RDFS, Namespace, NamespaceManager  # , split_uri
from rdflib.plugins.parsers.RDFVOC import RDFVOC
from rdflib.plugins.serializers.xmlwriter import XMLWriter
from rdflib.serializer import Serializer
from rdflib.term import BNode, IdentifiedNode, Identifier, Literal, Node, URIRef
from rdflib.util import first, more_than

from ._xmlsort import (
    CanonicalSerializerStore,
    canonical_option,
    collection_cells,
    first_ordered_object,
    is_safe_collection,
    ordered_predicate_objects,
    ordered_subjects,
    term_sort_key,
)
from .xmlwriter import ESCAPE_ENTITIES

__all__ = ["fix", "XMLSerializer", "PrettyXMLSerializer"]


def _compute_qname_strict_for_term(
    nm: NamespaceManager, term: Node
) -> tuple[str, str, str]:
    """Compute the strict qname for predicate ``term``, raising a clear
    error if it cannot be split into a namespace and a valid XML local
    name (and therefore cannot be represented in RDF/XML).
    """
    try:
        # type error: Argument 1 to "compute_qname_strict" of "NamespaceManager" has incompatible type "Node"; expected "str"
        return nm.compute_qname_strict(term)  # type: ignore[arg-type]
    except ValueError as e:
        raise ValueError(
            f"Cannot serialize predicate {term} to RDF/XML: it cannot be "
            "split into a namespace and a valid XML local name, so it "
            "cannot be written as an XML element name."
        ) from e


class XMLSerializer(Serializer):
    """RDF/XML RDF graph serializer."""

    def __init__(self, store: Graph):
        super(XMLSerializer, self).__init__(store)

    def __bindings(self) -> Generator[tuple[str, URIRef], None, None]:
        store = self.store
        nm = store.namespace_manager
        bindings: dict[str, URIRef] = {}

        for predicate in set(store.predicates()):
            prefix, namespace, name = _compute_qname_strict_for_term(nm, predicate)
            bindings[prefix] = URIRef(namespace)

        RDFNS = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#")  # noqa: N806

        if "rdf" in bindings:
            assert bindings["rdf"] == RDFNS
        else:
            bindings["rdf"] = RDFNS

        for prefix, namespace in bindings.items():
            yield prefix, namespace

    def _relativize(self, uri: str) -> str:
        return self.relativize(uri)

    def _get_base(self, base: str | None, **args: Any) -> str | None:
        if args.get("canon") is True:
            return base
        return super()._get_base(base, **args)

    def serialize(
        self,
        stream: IO[bytes],
        base: str | None = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        canonical = canonical_option(kwargs.pop("canon", False))
        with CanonicalSerializerStore(self, canonical):
            self._serialize(
                stream,
                base=base,
                encoding=encoding,
                canonical=canonical,
                **kwargs,
            )

    def _serialize(
        self,
        stream: IO[bytes],
        *,
        base: str | None,
        encoding: str | None,
        canonical: bool,
        **kwargs: Any,
    ) -> None:
        if canonical or base is not None:
            self.base = base
        elif self.store.base is not None:
            self.base = self.store.base
        self.__stream = stream
        self.__serialized: dict[Identifier, int] = {}
        self._canonical = canonical
        encoding = (encoding or self.encoding) if canonical else self.encoding
        self.write: Callable[[str], object]
        write: Callable[[str], object]
        if canonical:
            if codecs.lookup(encoding).name == "utf-8":
                encoding = "utf-8"
            self.write = write = codecs.getwriter(encoding)(stream).write
        else:
            self.write = write = lambda uni: stream.write(
                uni.encode(encoding, "replace")
            )

        # startDocument
        write('<?xml version="1.0" encoding="%s"?>\n' % encoding)

        # startRDF
        write("<rdf:RDF\n")

        # If provided, write xml:base attribute for the RDF
        if "xml_base" in kwargs:
            write("   xml:base=%s\n" % self._quoteattr(kwargs["xml_base"]))
        elif self.base:
            write("   xml:base=%s\n" % self._quoteattr(self.base))
        # TODO:
        # assert(
        #    namespaces["http://www.w3.org/1999/02/22-rdf-syntax-ns#"]=='rdf')
        bindings = list(self.__bindings())
        bindings.sort()

        for prefix, namespace in bindings:
            if prefix:
                write("   xmlns:%s=%s\n" % (prefix, self._quoteattr(namespace)))
            else:
                write("   xmlns=%s\n" % self._quoteattr(namespace))
        write(">\n")

        # write out triples by subject
        subjects = ordered_subjects(self.store) if canonical else self.store.subjects()
        for subject in subjects:
            # type error: Argument 1 to "subject" of "XMLSerializer" has incompatible type "Node"; expected "Identifier"
            self.subject(subject, 1)  # type: ignore[arg-type]

        # endRDF
        write("</rdf:RDF>\n")

        # Set to None so that the memory can get garbage collected.
        # self.__serialized = None
        del self.__serialized

    def _quoteattr(self, value: str) -> str:
        return quoteattr(value) if self._canonical else '"%s"' % value

    def subject(self, subject: Identifier, depth: int = 1) -> None:
        if subject not in self.__serialized:
            self.__serialized[subject] = 1

            if isinstance(subject, (BNode, URIRef)):
                write = self.write
                indent = "  " * depth
                element_name = "rdf:Description"

                if isinstance(subject, BNode):
                    write('%s<%s rdf:nodeID="%s"' % (indent, element_name, subject))
                else:
                    uri = quoteattr(self._relativize(subject))
                    write("%s<%s rdf:about=%s" % (indent, element_name, uri))

                if (subject, None, None) in self.store:
                    write(">\n")

                    pairs = (
                        ordered_predicate_objects(self.store, subject)
                        if self._canonical
                        else self.store.predicate_objects(subject)
                    )
                    for predicate, object in pairs:
                        # type error: Argument 1 to "predicate" of "XMLSerializer" has incompatible type "Node"; expected "Identifier"
                        # type error: Argument 2 to "predicate" of "XMLSerializer" has incompatible type "Node"; expected "Identifier"
                        self.predicate(predicate, object, depth + 1)  # type: ignore[arg-type]
                    write("%s</%s>\n" % (indent, element_name))

                else:
                    write("/>\n")

    def predicate(
        self, predicate: Identifier, object: Identifier, depth: int = 1
    ) -> None:
        write = self.write
        indent = "  " * depth
        qname = self.store.namespace_manager.qname_strict(predicate)

        if isinstance(object, Literal):
            attributes = ""

            if object.language:
                attributes += " xml:lang=%s" % self._quoteattr(object.language)

            if object.datatype:
                attributes += " rdf:datatype=%s" % self._quoteattr(object.datatype)

            write(
                "%s<%s%s>%s</%s>\n"
                % (
                    indent,
                    qname,
                    attributes,
                    escape(object, ESCAPE_ENTITIES),
                    qname,
                )
            )
        else:
            if isinstance(object, BNode):
                write('%s<%s rdf:nodeID="%s"/>\n' % (indent, qname, object))
            else:
                write(
                    "%s<%s rdf:resource=%s/>\n"
                    % (indent, qname, quoteattr(self._relativize(object)))
                )


XMLLANG = "http://www.w3.org/XML/1998/namespacelang"
XMLBASE = "http://www.w3.org/XML/1998/namespacebase"
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")


# TODO:
def fix(val: str) -> str:
    "strip off _: from nodeIDs... as they are not valid NCNames"
    if val.startswith("_:"):
        return val[2:]
    else:
        return val


class PrettyXMLSerializer(Serializer):
    """Pretty RDF/XML RDF graph serializer."""

    def __init__(self, store: Graph, max_depth=3):
        super(PrettyXMLSerializer, self).__init__(store)
        self.forceRDFAbout: set[URIRef] = set()

    def _relativize(self, uri: str) -> str:
        return self.relativize(uri)

    def _get_base(self, base: str | None, **args: Any) -> str | None:
        if args.get("canon") is True:
            return base
        return super()._get_base(base, **args)

    def serialize(
        self,
        stream: IO[bytes],
        base: str | None = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        canonical = canonical_option(kwargs.pop("canon", False))
        with CanonicalSerializerStore(self, canonical):
            self._serialize(
                stream,
                base=base,
                encoding=encoding,
                canonical=canonical,
                **kwargs,
            )

    def _serialize(
        self,
        stream: IO[bytes],
        *,
        base: str | None,
        encoding: str | None,
        canonical: bool,
        **kwargs: Any,
    ) -> None:
        self.__serialized: dict[Identifier, int] = {}
        self._canonical = canonical
        store = self.store
        # if base is given here, use that, if not and a base is set for the graph use that
        if canonical or base is not None:
            self.base = base
        elif store.base is not None:
            self.base = store.base
        self.max_depth = kwargs.get("max_depth", 3)
        assert self.max_depth > 0, "max_depth must be greater than 0"

        self.nm = nm = store.namespace_manager
        if canonical and codecs.lookup(encoding or self.encoding).name == "utf-8":
            encoding = "utf-8"
        self.writer = writer = XMLWriter(
            stream,
            nm,
            encoding,
            extra_ns={"rdf": Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")},
            canonical=canonical,
        )
        namespaces = {}

        predicates = set(store.predicates())
        ordered_predicates = (
            sorted(predicates, key=term_sort_key) if canonical else predicates
        )
        for predicate in ordered_predicates:
            prefix, namespace, local = _compute_qname_strict_for_term(nm, predicate)
            namespaces[prefix] = namespace

        # rdf:type objects are only used as element names when they can be
        # shortened; the others are written as rdf:type properties of an
        # rdf:Description element (see `subject`), so failing to shorten one
        # is not an error.
        types = store.objects(None, RDF.type)
        ordered_types = sorted(set(types), key=term_sort_key) if canonical else types
        for type_ in ordered_types:
            if canonical and not isinstance(type_, URIRef):
                continue
            try:
                # type error: Argument 1 to "compute_qname_strict" of "NamespaceManager" has incompatible type "Node"; expected "str"
                prefix, namespace, local = nm.compute_qname_strict(type_)  # type: ignore[arg-type]
            except ValueError:
                continue
            namespaces[prefix] = namespace

        writer.push(RDFVOC.RDF)

        if "xml_base" in kwargs:
            writer.attribute(XMLBASE, kwargs["xml_base"])
        elif self.base:
            writer.attribute(XMLBASE, self.base)

        namespace_items = (
            sorted(namespaces.items()) if canonical else namespaces.items()
        )
        writer.namespaces(namespace_items)

        subject: IdentifiedNode
        # Write out subjects that can not be inline
        # type error: Incompatible types in assignment (expression has type "Node", variable has type "IdentifiedNode")
        first_subjects = ordered_subjects(store) if canonical else store.subjects()
        for subject in first_subjects:  # type: ignore[assignment]
            if (None, None, subject) in store:
                if (subject, None, subject) in store:
                    self.subject(subject, 1)
            else:
                self.subject(subject, 1)

        # write out anything that has not yet been reached
        # write out BNodes last (to ensure they can be inlined where possible)
        bnodes = set()

        # type error: Incompatible types in assignment (expression has type "Node", variable has type "IdentifiedNode")
        remaining_subjects = ordered_subjects(store) if canonical else store.subjects()
        for subject in remaining_subjects:  # type: ignore[assignment]
            if isinstance(subject, BNode):
                bnodes.add(subject)
                continue
            self.subject(subject, 1)

        # now serialize only those BNodes that have not been serialized yet
        final_bnodes = sorted(bnodes, key=term_sort_key) if canonical else bnodes
        for bnode in final_bnodes:
            if bnode not in self.__serialized:
                self.subject(bnode if canonical else subject, 1)

        writer.pop(RDFVOC.RDF)
        if canonical:
            writer.stream.write("\n")
        else:
            stream.write("\n".encode("latin-1"))

        # Set to None so that the memory can get garbage collected.
        self.__serialized = None  # type: ignore[assignment]

    def subject(self, subject: Identifier, depth: int = 1):
        store = self.store
        writer = self.writer

        if subject in self.forceRDFAbout:
            writer.push(RDFVOC.Description)
            writer.attribute(RDFVOC.about, self._relativize(subject))
            writer.pop(RDFVOC.Description)
            self.forceRDFAbout.remove(subject)  # type: ignore[arg-type]

        elif subject not in self.__serialized:
            self.__serialized[subject] = 1
            type = (
                first_ordered_object(store, subject, RDF.type)
                if self._canonical
                else first(store.objects(subject, RDF.type))
            )

            if self._canonical:
                if not isinstance(type, URIRef) or type.startswith(str(RDF)):
                    type = None
                else:
                    try:
                        self.nm.qname_strict(type)
                    except ValueError:
                        type = None
            else:
                try:
                    # RDF types that cannot be shortened stay rdf:type properties.
                    self.nm.qname_strict(type)  # type: ignore[arg-type]
                except Exception:
                    type = None

            element = type or RDFVOC.Description
            # type error: Argument 1 to "push" of "XMLWriter" has incompatible type "Node"; expected "str"
            writer.push(element)  # type: ignore[arg-type]

            if isinstance(subject, BNode):

                def subj_as_obj_more_than(ceil):
                    return True
                    # more_than(store.triples((None, None, subject)), ceil)

                # here we only include BNode labels if they are referenced
                # more than once (this reduces the use of redundant BNode
                # identifiers)
                if subj_as_obj_more_than(1):
                    writer.attribute(RDFVOC.nodeID, fix(subject))

            else:
                writer.attribute(RDFVOC.about, self._relativize(subject))

            if (subject, None, None) in store:
                pairs = (
                    ordered_predicate_objects(store, subject)
                    if self._canonical
                    else store.predicate_objects(subject)
                )
                for predicate, object in pairs:
                    if not (predicate == RDF.type and object == type):
                        # type error: Argument 1 to "predicate" of "PrettyXMLSerializer" has incompatible type "Node"; expected "Identifier"
                        # type error: Argument 2 to "predicate" of "PrettyXMLSerializer" has incompatible type "Node"; expected "Identifier"
                        self.predicate(predicate, object, depth + 1)  # type: ignore[arg-type]

            # type error: Argument 1 to "pop" of "XMLWriter" has incompatible type "Node"; expected "str | None"
            writer.pop(element)  # type: ignore[arg-type]

        elif subject in self.forceRDFAbout:
            # TODO FIXME?: this looks like a duplicate of first condition
            writer.push(RDFVOC.Description)
            writer.attribute(RDFVOC.about, self._relativize(subject))
            writer.pop(RDFVOC.Description)
            self.forceRDFAbout.remove(subject)  # type: ignore[arg-type]

    def predicate(
        self, predicate: Identifier, object: Identifier, depth: int = 1
    ) -> None:
        writer = self.writer
        store = self.store
        writer.push(predicate)

        if isinstance(object, Literal):
            if object.language:
                writer.attribute(XMLLANG, object.language)

            if (
                not self._canonical
                and object.datatype == RDF.XMLLiteral
                and isinstance(object.value, xml.dom.minidom.Document)
            ):
                writer.attribute(RDFVOC.parseType, "Literal")
                writer.text("")
                writer.stream.write(object)
            else:
                if object.datatype:
                    writer.attribute(RDFVOC.datatype, object.datatype)
                writer.text(object)

        elif (
            object in self.__serialized or not (object, None, None) in store  # noqa: E713
        ):
            if isinstance(object, BNode):
                if more_than(store.triples((None, None, object)), 0):
                    writer.attribute(RDFVOC.nodeID, fix(object))
            else:
                writer.attribute(RDFVOC.resource, self._relativize(object))

        else:
            if first(store.objects(object, RDF.first)) and (
                not self._canonical or is_safe_collection(store, object)
            ):  # may not have type
                # RDF.List

                self.__serialized[object] = 1

                # Warn that any assertions on object other than
                # RDF.first and RDF.rest are ignored... including RDF.List
                import warnings

                if not self._canonical:
                    warnings.warn(
                        "Assertions on %s other than RDF.first " % repr(object)
                        + "and RDF.rest are ignored ... including RDF.List",
                        UserWarning,
                        stacklevel=2,
                    )
                writer.attribute(RDFVOC.parseType, "Collection")

                if self._canonical:
                    for cell in collection_cells(store, object):
                        if isinstance(cell, Identifier):
                            self.__serialized[cell] = 1

                col = Collection(store, object)

                for item in col:
                    if isinstance(item, URIRef):
                        self.forceRDFAbout.add(item)
                    # type error: Argument 1 to "subject" of "PrettyXMLSerializer" has incompatible type "Node"; expected "Identifier"
                    self.subject(item)  # type: ignore[arg-type]

                    if not isinstance(item, URIRef):
                        # type error: Invalid index type "Node" for "dict[Identifier, int]"; expected type "Identifier"
                        self.__serialized[item] = 1  # type: ignore[index]
            else:
                if first(
                    store.triples_choices(
                        # type error: Argument 1 to "triples_choices" of "Graph" has incompatible type "tuple[Identifier, URIRef, list[URIRef]]"; expected "Union[tuple[list[Node], Node, Node], tuple[Node, list[Node], Node], tuple[Node, Node, list[Node]]]"
                        (object, RDF.type, [OWL_NS.Class, RDFS.Class])  # type: ignore[arg-type]
                    )
                ) and isinstance(object, URIRef):
                    writer.attribute(RDFVOC.resource, self._relativize(object))

                elif depth <= self.max_depth:
                    self.subject(object, depth + 1)

                elif isinstance(object, BNode):
                    if (
                        object not in self.__serialized
                        and (object, None, None) in store
                        and len(list(store.subjects(object=object))) == 1
                    ):
                        # inline blank nodes if they haven't been serialized yet
                        # and are only referenced once (regardless of depth)
                        self.subject(object, depth + 1)
                    else:
                        writer.attribute(RDFVOC.nodeID, fix(object))

                else:
                    writer.attribute(RDFVOC.resource, self._relativize(object))

        writer.pop(predicate)
