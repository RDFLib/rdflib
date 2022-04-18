import pyld
from pyld.jsonld import (
    ContextResolver,
    IdentifierIssuer,
    JsonLdError,
    _default_document_loader,
    _is_absolute_iri,
    _is_string,
    _resolved_context_cache,
)


def to_rdf(self: pyld.jsonld.JsonLdProcessor, input_: dict, options: dict) -> None:
    """
    Outputs the RDF dataset found in the given JSON-LD object.

    :param input_: the JSON-LD input.
    :param options: the options to use.
        [base] the base IRI to use.
        [contextResolver] internal use only.
        [format] the format if input is a string:
        'application/n-quads' for N-Quads.
        [produceGeneralizedRdf] true to output generalized RDF, false
        to produce only standard RDF (default: false).
        [documentLoader(url, options)] the document loader
        (default: _default_document_loader).
        [rdfDirection] Only 'i18n-datatype' supported
        (default: None).

    :return: the resulting RDF dataset (or a serialization of it).
    """
    # set default options
    options = options.copy() if options else {}
    options.setdefault("base", input_ if _is_string(input_) else "")
    options.setdefault("produceGeneralizedRdf", False)
    options.setdefault("documentLoader", _default_document_loader)
    options.setdefault(
        "contextResolver",
        ContextResolver(_resolved_context_cache, options["documentLoader"]),
    )
    options.setdefault("extractAllScripts", True)
    options.setdefault("processingMode", "json-ld-1.1")

    try:
        # expand input
        expanded = self.expand(input_, options)
    except JsonLdError as cause:
        raise JsonLdError(
            "Could not expand input before serialization to " "RDF.",
            "jsonld.RdfError",
            cause=cause,
        ) from cause

    # create node map for default graph (and any named graphs)
    issuer = IdentifierIssuer("_:b")
    node_map = {"@default": {}}
    self._create_node_map(expanded, node_map, "@default", issuer)

    # output RDF dataset
    for graph_name, graph in sorted(node_map.items()):
        # skip relative IRIs
        if graph_name == "@default" or _is_absolute_iri(graph_name):
            self._graph_to_rdf(graph_name, graph, issuer, options)
