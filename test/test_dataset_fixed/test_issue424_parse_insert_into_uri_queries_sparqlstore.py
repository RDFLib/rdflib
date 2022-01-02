from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore


def test_issue424_parse_insert_into_uri_queries_sparqlstore():

    # STATUS: FIXED no longer an issue

    # https://github.com/RDFLib/rdflib/issues/167#issuecomment-873620457

    # Note that this is also observed when using Dataset instances. In particular,

    store = SPARQLUpdateStore(
        query_endpoint="http://localhost:3030/db/sparql",
        update_endpoint="http://localhost:3030/db/update",
    )

    store.update(
        "INSERT DATA { GRAPH <urn:context-1> { <urn@tarek> <urn:likes> <urn:pizza> } }"
    )

    # PREFIX dc:  <http://purl.org/dc/elements/1.1/>
    # PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    # INSERT INTO <http://example/bookStore2>
    #  { ?book ?p ?v }
    # WHERE
    #   { GRAPH  <http://example/bookStore>
    #        { ?book dc:date ?date .
    #          FILTER ( ?date < "2000-01-01T00:00:00"^^xsd:dateTime )
    #          ?book ?p ?v
    #   } }

    # PREFIX dcterms: <http://purl.org/dc/terms/>

    # INSERT DATA {
    #     GRAPH <http://example/shelf_A> {
    #         <http://example/author> dcterms:name "author" .
    #         <http://example/book> dcterms:title "book" ;
    #         dcterms:author <http://example/author> .
    #     }
    # }
