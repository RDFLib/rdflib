import difflib
from pathlib import Path
from textwrap import dedent

from rdflib import RDF, BNode, Graph, Literal, Namespace
from rdflib.compare import isomorphic
from rdflib.namespace import GEO, SDO
from rdflib.plugins.serializers.longturtle import LongTurtleSerializer


def test_longturtle():
    """Compares the output of a longturtle graph serialization to a fixed, hand-typed, target
    to test most of the longtertle differences to regular turtle

    Includes basic triples, Blank Nodes - 2-levels deep - Collections and so on"""
    # load graph with data
    g = Graph().parse(
        data="""
            {
              "@context": {
                    "cn": "https://linked.data.gov.au/def/cn/",
                    "sdo": "https://schema.org/",
                    "Organization": "sdo:Organization",
                    "Person": "sdo:Person",
                    "Place": "sdo:Place",
                    "PostalAddress": "sdo:PostalAddress",
                    "address": "sdo:address",
                    "addressLocality": "sdo:addressLocality",
                    "addressRegion": "sdo:addressRegion",
                    "postalCode": "sdo:postalCode",
                    "addressCountry": "sdo:addressCountry",
                    "streetAddress": "sdo:streetAddress",
                    "age": "sdo:age",
                    "alternateName": "sdo:alternateName",
                    "geo": "sdo:geo",
                    "hasPart": "sdo:hasPart",
                    "identifier": "sdo:identifier",
                    "location": "sdo:location",
                    "name": "sdo:name",
                    "polygon": "sdo:polygon",
                    "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#value",
                    "wktLiteral": "http://www.opengis.net/ont/geosparql#wktLiteral",
                    "worksFor": "sdo:worksFor"
                },
                "@graph": [
                  {
                        "@id": "https://kurrawong.ai",
                        "@type": "Organization",
                        "location": {
                            "@id": "https://kurrawong.ai/hq"
                        }
                    },
                    {
                        "@id": "https://kurrawong.ai/hq",
                        "@type": "Place",
                        "address": {
                            "@id": "_:n6924e85bfee648a4a45bac9f4ab9909ab8"
                        },
                        "geo": {
                            "@id": "_:n6924e85bfee648a4a45bac9f4ab9909ab13"
                        },
                        "name": "KurrawongAI HQ"
                    },
                    {
                        "@id": "_:n6924e85bfee648a4a45bac9f4ab9909ab8",
                        "@type": "PostalAddress",
                        "addressCountry": {
                            "@id": "_:n6924e85bfee648a4a45bac9f4ab9909ab12"
                        },
                        "addressLocality": "Shorncliffe",
                        "addressRegion": "QLD",
                        "postalCode": 4017,
                        "streetAddress": {
                            "@list": [
                                72,
                                "Yundah",
                                "Street"
                            ]
                        }
                    },
                    {
                        "@id": "_:n6924e85bfee648a4a45bac9f4ab9909ab12",
                        "identifier": "au",
                        "name": "Australia"
                    },
                    {
                        "@id": "_:n6924e85bfee648a4a45bac9f4ab9909ab13",
                        "polygon": {
                            "@type": "wktLiteral",
                            "@value": "POLYGON((153.082403 -27.325801, 153.08241 -27.32582, 153.082943 -27.325612, 153.083010 -27.325742, 153.083543 -27.325521, 153.083456 -27.325365, 153.082403 -27.325801))"
                        }
                    },
                    {
                        "@id": "http://example.com/nicholas",
                        "@type": "Person",
                        "age": 41,
                        "alternateName": [
                            "Nick Car",
                            "N.J. Car",
                            {
                                "@id": "_:n6924e85bfee648a4a45bac9f4ab9909ab1"
                            }
                        ],
                        "name": {
                            "@id": "_:n6924e85bfee648a4a45bac9f4ab9909ab2"
                        },
                        "worksFor": {
                            "@id": "https://kurrawong.ai"
                        }
                    },
                    {
                        "@id": "_:n6924e85bfee648a4a45bac9f4ab9909ab1",
                        "name": "Dr N.J. Car"
                    },
                    {
                        "@id": "_:n6924e85bfee648a4a45bac9f4ab9909ab2",
                        "@type": "cn:CompoundName",
                        "hasPart": [{
                                "@id": "_:n6924e85bfee648a4a45bac9f4ab9909ab3"
                            },
                            {
                                "@id": "_:n6924e85bfee648a4a45bac9f4ab9909ab4"
                            },
                            {
                                "@id": "_:n6924e85bfee648a4a45bac9f4ab9909ab5"
                            }
                        ]
                    },
                    {
                        "@id": "_:n6924e85bfee648a4a45bac9f4ab9909ab3",
                        "@type": "cn:CompoundName",
                        "value": "Nicholas"
                    },
                    {
                        "@id": "_:n6924e85bfee648a4a45bac9f4ab9909ab4",
                        "@type": "cn:CompoundName",
                        "value": "John"
                    },
                    {
                        "@id": "_:n6924e85bfee648a4a45bac9f4ab9909ab5",
                        "@type": "cn:CompoundName",
                        "hasPart": [{
                                "@id": "_:n6924e85bfee648a4a45bac9f4ab9909ab6"
                            },
                            {
                                "@id": "_:n6924e85bfee648a4a45bac9f4ab9909ab7"
                            }
                        ]
                    },
                    {
                        "@id": "_:n6924e85bfee648a4a45bac9f4ab9909ab6",
                        "@type": "cn:CompoundName",
                        "value": "Car"
                    },
                    {
                        "@id": "_:n6924e85bfee648a4a45bac9f4ab9909ab7",
                        "@type": "cn:CompoundName",
                        "value": "Maxov"
                    }
                ]
            }
        """,
        format="application/ld+json",
    )

    # declare a few namespaces for Turtle
    g.bind("ex", Namespace("http://example.com/"))
    g.bind("geo", GEO)
    g.bind("cn", Namespace("https://linked.data.gov.au/def/cn/"))
    g.bind("sdo", SDO)

    # run the long turtle serializer
    output = g.serialize(format="longturtle", canon=True)

    # fix the target
    current_dir = Path.cwd()  # Get the current directory
    target_file_path = current_dir / "test/data/longturtle" / "longturtle-target.ttl"

    with open(target_file_path, encoding="utf-8") as file:
        target = file.read()

    # compare output to target
    # - any differences will produce output
    diff = "\n".join(list(difflib.unified_diff(target.split("\n"), output.split("\n"))))

    assert not diff, diff


def test_longturtle_undeclared_prefix_when_using_base():
    """
    See https://github.com/RDFLib/rdflib/issues/3160
    """
    from rdflib import Graph, Literal, URIRef

    g = Graph()
    g.add(
        (
            URIRef("https://example.com/subject"),
            URIRef("https://example.com/p/predicate"),
            Literal("object"),
        )
    )
    output = g.serialize(format="longturtle", base="https://example.com/")
    expected = dedent(
        """
        BASE <https://example.com/>
        PREFIX ns1: <https://example.com/p/>

        <subject>
            ns1:predicate "object" ;
        .
    """
    )
    assert output.strip() == expected.strip()


def test_longturtle_shared_list_tail_round_trips():
    """
    A list cell that is pointed to from more than one place (here, the tail of
    one list is also referenced directly by another subject) cannot be safely
    written with ``( … )`` collection syntax: the inline form only defines the
    cell once, at whichever reference happens to consume it, leaving the other
    reference dangling in the output.

    Same regression as the turtle serializer's
    ``test_turtle_shared_list_tail_round_trips``; ``longturtle`` duplicates
    ``TurtleSerializer.isValidList`` rather than inheriting it, so it needs
    the same fix.
    """
    ns = Namespace("http://example.org/ns/")
    g = Graph()
    tail = BNode()
    head = BNode()
    g.add((tail, RDF.first, Literal("b")))
    g.add((tail, RDF.rest, RDF.nil))
    g.add((head, RDF.first, Literal("a")))
    g.add((head, RDF.rest, tail))
    g.add((ns.s1, ns.p, head))
    g.add((ns.s2, ns.p, tail))

    serializer = LongTurtleSerializer(g)
    assert serializer.isValidList(head) is False
    assert serializer.isValidList(tail) is False

    ttl_dump = g.serialize(format="longturtle")
    g2 = Graph()
    g2.parse(data=ttl_dump, format="turtle")
    assert len(g2) == len(g)
    assert isomorphic(g, g2)
