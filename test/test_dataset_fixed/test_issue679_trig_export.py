from rdflib import Literal, URIRef


def test_issue679_trig_export(get_dataset):

    # STATUS: FIXED? no longer an issue

    #  trig export of multiple graphs assigns wrong prefixes to prefixedNames #679
    ds = get_dataset
    graphs = [(URIRef("urn:tg1"), "A"), (URIRef("urn:tg2"), "B")]

    for i, n in graphs:
        # g = Graph(identifier=i)
        g = ds.get_context(i)
        a = URIRef("urn:{}#S".format(n))
        b = URIRef("urn:{}#p".format(n))
        c = Literal(chr(0xF23F1))
        d = Literal(chr(0x66))
        e = Literal(chr(0x23F2))
        g.add((a, b, c))
        g.add((a, b, d))
        g.add((a, b, e))
        # ds.graph(g)

    # for n, k in [
    #     ("json-ld", "jsonld"),
    #     ("nquads", "nq"),
    #     ("trix", "trix"),
    #     ("trig", "trig"),
    # ]:
    #     logger.debug(f"{k}\n{ds.serialize(format=n)}")

    # Output is conformant and as expected

    # logger.debug(
    #     f"test_issue679_trig_export trig\n{ds.serialize(format='trig')}"
    # )

    # DEBUG    rdflib:test_dataset_anomalies.py:1190 trig
    # @prefix ns1: <urn:> .
    # @prefix ns2: <urn:A#> .
    # @prefix ns3: <urn:B#> .
    # @prefix ns4: <urn:x-rdflib:> .

    # ns1:tg1 {
    #     ns2:S ns2:p "f",
    #             "⏲",
    #             "󲏱" .
    # }

    # ns1:tg2 {
    #     ns3:S ns3:p "f",
    #             "⏲",
    #             "󲏱" .
    # }

    # logger.debug(f"trig\n{ds.serialize(format='trig')}")

    # DEBUG    rdflib:test_dataset_anomalies.py:1191 trig
    # @prefix ns1: <urn:> .
    # @prefix ns2: <urn:A#> .
    # @prefix ns3: <urn:B#> .
    # @prefix ns4: <urn:x-rdflib:> .

    # ns1:tg1 {
    #     ns2:S ns2:p "f",
    #             "⏲",
    #             "󲏱" .
    # }

    # ns1:tg2 {
    #     ns3:S ns3:p "f",
    #             "⏲",
    #             "󲏱" .
    # }
