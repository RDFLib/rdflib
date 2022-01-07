from rdflib import Dataset, Literal, URIRef

jsonld_output = [
    (
        "[\n"
        "  {\n"
        '    "@graph": [\n'
        "      {\n"
        '        "@id": "urn:B#S",\n'
        '        "urn:B#p": [\n'
        "          {\n"
        '            "@value": "\U000f23f1"\n'
        "          },\n"
        "          {\n"
        '            "@value": "f"\n'
        "          },\n"
        "          {\n"
        '            "@value": "⏲"\n'
        "          }\n"
        "        ]\n"
        "      }\n"
        "    ],\n"
        '    "@id": "urn:tg2"\n'
        "  },\n"
        "  {\n"
        '    "@graph": [\n'
        "      {\n"
        '        "@id": "urn:A#S",\n'
        '        "urn:A#p": [\n'
        "          {\n"
        '            "@value": "\U000f23f1"\n'
        "          },\n"
        "          {\n"
        '            "@value": "f"\n'
        "          },\n"
        "          {\n"
        '            "@value": "⏲"\n'
        "          }\n"
        "        ]\n"
        "      }\n"
        "    ],\n"
        '    "@id": "urn:tg1"\n'
        "  }\n"
        "]"
    ),
    (
        "[\n"
        "  {\n"
        '    "@graph": [\n'
        "      {\n"
        '        "@id": "urn:A#S",\n'
        '        "urn:A#p": [\n'
        "          {\n"
        '            "@value": "\U000f23f1"\n'
        "          },\n"
        "          {\n"
        '            "@value": "f"\n'
        "          },\n"
        "          {\n"
        '            "@value": "⏲"\n'
        "          }\n"
        "        ]\n"
        "      }\n"
        "    ],\n"
        '    "@id": "urn:tg1"\n'
        "  },\n"
        "  {\n"
        '    "@graph": [\n'
        "      {\n"
        '        "@id": "urn:B#S",\n'
        '        "urn:B#p": [\n'
        "          {\n"
        '            "@value": "\U000f23f1"\n'
        "          },\n"
        "          {\n"
        '            "@value": "f"\n'
        "          },\n"
        "          {\n"
        '            "@value": "⏲"\n'
        "          }\n"
        "        ]\n"
        "      }\n"
        "    ],\n"
        '    "@id": "urn:tg2"\n'
        "  }\n"
        "]"
    ),
]

trig_output = [
    (
        "@prefix ns1: <urn:B#> .\n"
        "@prefix ns2: <urn:x-rdflib:> .\n"
        "@prefix ns3: <urn:A#> .\n"
        "@prefix urn: <urn:> .\n"
        "\n"
        "urn:tg2 {\n"
        '    ns1:S ns1:p "f",\n'
        '            "⏲",\n'
        '            "\U000f23f1" .\n'
        "}\n"
        "\n"
        "urn:tg1 {\n"
        '    ns3:S ns3:p "f",\n'
        '            "⏲",\n'
        '            "\U000f23f1" .\n'
        "}\n"
        "\n"
    ),
    (
        "@prefix ns1: <urn:B#> .\n"
        "@prefix ns2: <urn:A#> .\n"
        "@prefix ns3: <urn:x-rdflib:> .\n"
        "@prefix urn: <urn:> .\n"
        "\n"
        "urn:tg2 {\n"
        '    ns1:S ns1:p "f",\n'
        '            "⏲",\n'
        '            "\U000f23f1" .\n'
        "}\n"
        "\n"
        "urn:tg1 {\n"
        '    ns2:S ns2:p "f",\n'
        '            "⏲",\n'
        '            "\U000f23f1" .\n'
        "}\n"
        "\n"
    ),
    (
        "@prefix ns1: <urn:x-rdflib:> .\n"
        "@prefix ns2: <urn:A#> .\n"
        "@prefix ns3: <urn:B#> .\n"
        "@prefix urn: <urn:> .\n"
        "\n"
        "urn:tg1 {\n"
        '    ns2:S ns2:p "f",\n'
        '            "⏲",\n'
        '            "\U000f23f1" .\n'
        "}\n"
        "\n"
        "urn:tg2 {\n"
        '    ns3:S ns3:p "f",\n'
        '            "⏲",\n'
        '            "\U000f23f1" .\n'
        "}\n"
        "\n"
    ),
    (
        "@prefix ns1: <urn:A#> .\n"
        "@prefix ns2: <urn:B#> .\n"
        "@prefix ns3: <urn:x-rdflib:> .\n"
        "@prefix urn: <urn:> .\n"
        "\n"
        "urn:tg1 {\n"
        '    ns1:S ns1:p "f",\n'
        '            "⏲",\n'
        '            "\U000f23f1" .\n'
        "}\n"
        "\n"
        "urn:tg2 {\n"
        '    ns2:S ns2:p "f",\n'
        '            "⏲",\n'
        '            "\U000f23f1" .\n'
        "}\n"
        "\n"
    ),
    (
        "@prefix ns1: <urn:x-rdflib:> .\n"
        "@prefix ns2: <urn:B#> .\n"
        "@prefix ns3: <urn:A#> .\n"
        "@prefix urn: <urn:> .\n"
        "\n"
        "urn:tg2 {\n"
        '    ns2:S ns2:p "f",\n'
        '            "⏲",\n'
        '            "\U000f23f1" .\n'
        "}\n"
        "\n"
        "urn:tg1 {\n"
        '    ns3:S ns3:p "f",\n'
        '            "⏲",\n'
        '            "\U000f23f1" .\n'
        "}\n"
        "\n"
    ),
    (
        "@prefix ns1: <urn:A#> .\n"
        "@prefix ns2: <urn:x-rdflib:> .\n"
        "@prefix ns3: <urn:B#> .\n"
        "@prefix urn: <urn:> .\n"
        "\n"
        "urn:tg1 {\n"
        '    ns1:S ns1:p "f",\n'
        '            "⏲",\n'
        '            "\U000f23f1" .\n'
        "}\n"
        "\n"
        "urn:tg2 {\n"
        '    ns3:S ns3:p "f",\n'
        '            "⏲",\n'
        '            "\U000f23f1" .\n'
        "}\n"
        "\n"
    ),
]

nquads_output = [
    "",
    "",
    '<urn:A#S> <urn:A#p> "f" <urn:tg1> .',
    '<urn:A#S> <urn:A#p> "⏲" <urn:tg1> .',
    '<urn:A#S> <urn:A#p> "\U000f23f1" <urn:tg1> .',
    '<urn:B#S> <urn:B#p> "f" <urn:tg2> .',
    '<urn:B#S> <urn:B#p> "⏲" <urn:tg2> .',
    '<urn:B#S> <urn:B#p> "\U000f23f1" <urn:tg2> .',
]


def test_issue679_trig_export():

    ds = Dataset()
    graphs = [(URIRef("urn:tg1"), "A"), (URIRef("urn:tg2"), "B")]

    for i, n in graphs:

        g = ds.get_context(i)
        ds.bind("", URIRef("urn:example:"))
        ds.bind("urn", URIRef("urn:"))

        a = URIRef("urn:{}#S".format(n))
        b = URIRef("urn:{}#p".format(n))

        c = Literal(chr(0xF23F1))
        d = Literal(chr(0x66))
        e = Literal(chr(0x23F2))

        g.add((a, b, c))
        g.add((a, b, d))
        g.add((a, b, e))

    for n, k, o in [
        ("json-ld", "jsonld", jsonld_output),
        ("trig", "trig", trig_output),
        ("nquads", "nq", nquads_output),
    ]:
        output = ds.serialize(format=n)
        if k == "nq":
            assert sorted(output.split("\n")) == nquads_output
        else:
            assert output in o
