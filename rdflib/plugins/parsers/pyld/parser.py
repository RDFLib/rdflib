import json
from io import BufferedReader, StringIO
from typing import Union, List

import rdflib.plugins.parsers.pyld.pyld as pyld
from rdflib.plugins.parsers.pyld.pyld import jsonld
from rdflib.plugins.parsers.pyld.pyld.jsonld import (
    RDF_TYPE,
    _is_absolute_iri,
    _is_keyword,
)

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID
from rdflib.parser import BytesIOWrapper, InputSource, Parser, PythonInputSource

from .to_rdf import to_rdf

# Monkey patch pyld.
pyld.jsonld.JsonLdProcessor.to_rdf = to_rdf


def _get_object(object):
    if object["type"] == "IRI":
        o = URIRef(object["value"])
    elif object["type"] == "blank node":
        o = BNode(object["value"][2:])
    else:
        o = Literal(
            object["value"],
            datatype=URIRef(object["datatype"])
            if object["datatype"]
            != "http://www.w3.org/1999/02/22-rdf-syntax-ns#langString"
            and object["datatype"] != "http://www.w3.org/2001/XMLSchema#string"
            else None,
            lang=object.get("language"),
        )
    return o


class JSONLDParser(Parser):
    def parse(self, source: InputSource, sink: Graph) -> None:
        # TODO: Do we need to set up a document loader?
        #       See https://github.com/digitalbazaar/pyld#document-loader
        #       Using a document loader requires either Requests or aiohttp

        def _graph_to_rdf(
            self: pyld.jsonld.JsonLdProcessor,
            pyld_graph_name: str,
            pyld_graph_dict: dict,
            issuer: pyld.jsonld.IdentifierIssuer,
            options: dict,
        ):
            """
            Creates an array of RDF triples for the given graph.

            :param pyld_graph_name: the graph name of the triples.
            :param pyld_graph_dict: the graph to create RDF triples for.
            :param issuer: the IdentifierIssuer for issuing blank node identifiers.
            :param options: the RDF serialization options.

            :return: the array of RDF triples for the given graph.
            """
            triples: List[dict] = []

            graph_name: Union[Graph, URIRef, BNode, None] = None
            if pyld_graph_name == "@default":
                # TODO: This should set the graph_name to the default graph.
                #       For now, we need to stick with `graph_name = sink`` to pass tests.
                #       Otherwise Graph does not work properly.

                # Setting this to default graph is the correctly behaviour for Dataset but
                # fails to add triples to a Graph object.
                # graph_name = DATASET_DEFAULT_GRAPH_ID
                graph_name = sink
            elif pyld_graph_name.startswith("_:"):
                graph_name = BNode(pyld_graph_name[2:])
            else:
                graph_name = URIRef(pyld_graph_name)

            for id_, node in sorted(pyld_graph_dict.items()):
                for property, items in sorted(node.items()):
                    if property == "@type":
                        property = RDF_TYPE
                    elif _is_keyword(property):
                        continue

                    for item in items:
                        # skip relative IRI subjects and predicates
                        if not (_is_absolute_iri(id_) and _is_absolute_iri(property)):
                            continue

                        # RDF subject
                        subject: Union[URIRef, BNode, None] = None
                        if id_.startswith("_:"):
                            subject = BNode(id_[2:])
                        else:
                            subject = URIRef(id_)

                        # RDF predicate
                        predicate: Union[URIRef, BNode, None] = None
                        if property.startswith("_:"):
                            # skip bnode predicates unless producing
                            # generalized RDF
                            if not options["produceGeneralizedRdf"]:
                                continue
                            predicate = BNode(property[2:])
                        else:
                            predicate = URIRef(property)

                        # convert list, value or node object to triple
                        object = self._object_to_rdf(
                            item, issuer, triples, options.get("rdfDirection")
                        )

                        # skip None objects (they are relative IRIs)
                        if object is not None:
                            o = _get_object(object)

                            sink.store.add(
                                (
                                    subject,
                                    predicate,
                                    o,
                                ),
                                graph_name,
                            )

            # Add RDF list items.
            for triple in triples:
                s = (
                    URIRef(triple["subject"]["value"])
                    if triple["subject"]["type"] == "IRI"
                    else BNode(triple["subject"]["value"][2:])
                )
                p = (
                    URIRef(triple["predicate"]["value"])
                    if triple["predicate"]["type"] == "IRI"
                    else BNode(triple["predicate"]["value"][2:])
                )
                o = _get_object(triple["object"])
                sink.store.add((s, p, o), graph_name)

        # Monkey patch pyld.
        pyld.jsonld.JsonLdProcessor._graph_to_rdf = _graph_to_rdf

        if isinstance(source, PythonInputSource):
            data = source.data
            jsonld.to_rdf(data)
        else:
            stream: Union[
                StringIO, BytesIOWrapper, BufferedReader
            ] = source.getByteStream()

            if isinstance(stream, (StringIO, BytesIOWrapper, BufferedReader)):
                data = json.loads(stream.read())
            else:
                raise TypeError(f"Unhandled type for 'stream' as {type(stream)}.")

            try:
                jsonld.to_rdf(data)
            finally:
                stream.close()
