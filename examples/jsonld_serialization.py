"""
JSON-LD is "A JSON-based Serialization for Linked Data" (https://www.w3.org/TR/json-ld/)
that RDFLib implements for RDF serialization.

This file demonstrated some of the JSON-LD things you can do with RDFLib. Parsing &
serializing so far. More to be added later.


Parsing
-------

There are a number of "flavours" of JSON-LD - compact and verbose etc. RDFLib can parse
all of these in a normal RDFLib way.


Serialization
-------------

JSON-LD has a number of options for serialization - more than other RDF formats. For
example, IRIs within JSON-LD can be compacted down to CURIES when a "context" statement
is added to the JSON-LD data that maps identifiers - short codes - to IRIs and namespace
IRIs like this:

.. code-block:: json

    "@context": {
        "dcterms": "http://purl.org/dc/terms/",
        "schema": "https://schema.org/"
    }

Here the short code "dcterms" is mapped to the IRI http://purl.org/dc/terms/ and
"schema" to https://schema.org/, as per RDFLib's in-build namespace prefixes.
"""

# import RDFLib and other things
try:
    from rdflib import Graph
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).parent.parent))
    from rdflib import Graph

# 1. JSON-LD Parsing

# RDFLib can read all forms of JSON-LD. Here is an example:

json_ld_data_string = """
{
  "@context": {
    "dct": "http://purl.org/dc/terms/",
    "sdo": "https://schema.org/"
  },
  "@graph": [
    {
      "@id": "https://kurrawong.ai",
      "@type": [
        "dct:Agent",
        "sdo:Organization"
      ],
      "sdo:name": "KurrawongAI"
    },
    {
      "@id": "http://example.com/person/nick",
      "@type": "dct:Agent",
      "sdo:memberOf": {
        "@id": "https://kurrawong.ai"
      },
      "sdo:name": "Nicholas Car"
    }
  ]
}
"""

# Parse the data in the 'normal' RDFLib way, setting the format parameter to "json-ld"

g = Graph()
g.parse(data=json_ld_data_string, format="json-ld")

# print out a count of triples to show successful parsing

print(len(g))

# should be 6

# tidy up...
del g


# 2. JSON-LD Serialization

# Load an RDF graph with some data - parsing Turtle input

g = Graph().parse(
    data="""
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    <http://example.com/person/nick>
        a dcterms:Agent ;
        <https://schema.org/name> "Nicholas Car" ;
        <https://schema.org/memberOf> <https://kurrawong.ai> ;
    .

    <https://kurrawong.ai>
        a dcterms:Agent , <https://schema.org/Organization> ;
        <https://schema.org/name> "KurrawongAI" ;
    .
    """
)

# 2.1 Basic JSON-LD serialization

# Serialize with only the format option indicated
# Notice:
#   - all IRIs are in long form - no CURIES / prefixes used
print(g.serialize(format="json-ld"))

"""
[
  {
    "@id": "https://kurrawong.ai",
    "@type": [
      "http://purl.org/dc/terms/Agent",
      "https://schema.org/Organization"
    ],
    "https://schema.org/name": [
      {
        "@value": "KurrawongAI"
      }
    ]
  },
  {
    "@id": "http://example.com/person/nick",
    "@type": [
      "http://purl.org/dc/terms/Agent"
    ],
    "https://schema.org/memberOf": [
      {
        "@id": "https://kurrawong.ai"
      }
    ],
    "https://schema.org/name": [
      {
        "@value": "Nicholas Car"
      }
    ]
  }
]
"""

# 2.2 Compact the JSON-LD by using RDFLib's in-built namespace prefixes
# Notice:
#   - the "@context" JSON element with prefix / namespace mappings
#   - no prefix is known for schema.org since we are using only RDFLib's core namespace prefixes

print(g.serialize(format="json-ld", auto_compact=True))

"""
{
  "@context": {
    "dcterms": "http://purl.org/dc/terms/",
    "owl": "http://www.w3.org/2002/07/owl#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd": "http://www.w3.org/2001/XMLSchema#"
  },
  "@graph": [
    {
      "@id": "http://example.com/person/nick",
      "@type": "dcterms:Agent",
      "https://schema.org/memberOf": {
        "@id": "https://kurrawong.ai"
      },
      "https://schema.org/name": "Nicholas Car"
    },
    {
      "@id": "https://kurrawong.ai",
      "@type": [
        "dcterms:Agent",
        "https://schema.org/Organization"
      ],
      "https://schema.org/name": "KurrawongAI"
    }
  ]
}
"""

# 2.3 Compact the JSON-LD by supplying own context
# We now override RDFLib's namespace prefixes by supplying our own context information
context = {"sdo": "https://schema.org/", "dct": "http://purl.org/dc/terms/"}

# Now when we serialise the RDF data, this context can be used to overwrite the default RDFLib one. auto_compact need not be specified
print(g.serialize(format="json-ld", context=context))

"""
{
  "@context": {
    "dct": "http://purl.org/dc/terms/",
    "sdo": "https://schema.org/"
  },
  "@graph": [
    {
      "@id": "https://kurrawong.ai",
      "@type": [
        "dct:Agent",
        "sdo:Organization"
      ],
      "sdo:name": "KurrawongAI"
    },
    {
      "@id": "http://example.com/person/nick",
      "@type": "dct:Agent",
      "sdo:memberOf": {
        "@id": "https://kurrawong.ai"
      },
      "sdo:name": "Nicholas Car"
    }
  ]
}
"""
