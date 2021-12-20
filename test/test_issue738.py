from rdflib import Graph, URIRef
import tempfile
from pathlib import Path


# @pytest.mark.skip
def test_issue738_empty_publicID():
    """
    AnjoMan commented on 3 May 2017

    I want to set the public id to be an empty string, so that the ID
    values on my xml elements will not be amended.

    El  Subject:    file:///home/anton/Development/profile_validator/test_cim.xml#_AB16765A-B19E-4454-A58F-868D23C6CD26;
        Predicate:  http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo.ratedVoltage;
        Object:     25000.000000;
    El  Subject:    file:///home/anton/Development/profile_validator/test_cim.xml#_AB16765A-B19E-4454-A58F-868D23C6CD26;
        Predicate:  http://iec.ch/TC57/2013/CIM-schema-cim16#IdentifiedObject.name;
        Object:     DEFAULT;
    El  Subject:    file:///home/anton/Development/profile_validator/test_cim.xml#_AB16765A-B19E-4454-A58F-868D23C6CD26;
        Predicate:  http://www.w3.org/1999/02/22-rdf-syntax-ns#type;
        Object:     http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo;
    El  Subject:    file:///home/anton/Development/profile_validator/test_cim.xml#_AB16765A-B19E-4454-A58F-868D23C6CD26;
        Predicate:  http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo.ratedCurrent;
        Object:     100.000000;

    """

    foo_xml = """\
<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:cim="http://iec.ch/TC57/2013/CIM-schema-cim16#"
         xmlns:cyme="http://www.cyme.com/CIM/1.0.2#"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <cim:SwitchInfo rdf:ID="_AB16765A-B19E-4454-A58F-868D23C6CD26">
        <cim:IdentifiedObject.name>DEFAULT</cim:IdentifiedObject.name>
        <cim:SwitchInfo.ratedVoltage>25000.000000</cim:SwitchInfo.ratedVoltage>
        <cim:SwitchInfo.ratedCurrent>100.000000</cim:SwitchInfo.ratedCurrent>
    </cim:SwitchInfo>
</rdf:RDF>
"""

    g = Graph()
    _ = g.parse(data=foo_xml, format="xml")
    subject, predicate, object = next(iter(g))

    assert subject == URIRef("#_AB16765A-B19E-4454-A58F-868D23C6CD26")

    # assert list(ds)[0][0].n3().startswith("<#_A")
    # for s, p, o, c in ds:
    #     logger.debug(
    #         f"\nEl  Subject:\t{s};\n\tPredicate:\t{p};\n\tObject:\t\t{o};\n\tContext:\t{c};"
    #     )

    """
    El  Subject:    #_AB16765A-B19E-4454-A58F-868D23C6CD26;
        Predicate:  http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo.ratedCurrent;
        Object:     100.000000;
        Context:    N6085529a9ffd4c2a864671fb966889ef;
    El  Subject:    #_AB16765A-B19E-4454-A58F-868D23C6CD26;
        Predicate:  http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo.ratedVoltage;
        Object:     25000.000000;
        Context:    N6085529a9ffd4c2a864671fb966889ef;
    El  Subject:    #_AB16765A-B19E-4454-A58F-868D23C6CD26;
        Predicate:  http://www.w3.org/1999/02/22-rdf-syntax-ns#type;
        Object:     http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo;
        Context:    N6085529a9ffd4c2a864671fb966889ef;
    El  Subject:    #_AB16765A-B19E-4454-A58F-868D23C6CD26;
        Predicate:  http://iec.ch/TC57/2013/CIM-schema-cim16#IdentifiedObject.name;
        Object:     DEFAULT;
        Context:    N6085529a9ffd4c2a864671fb966889ef;
    """


def test_empty_string_for_publicID_when_loading_a_file():
    """
    Tests that we can pass in an empty string to publicID when
    parsing from a file name. since '' is falsy, it could be
    treated as None (e.g. if not publicID).
    """

    xml_sample = """\
<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:cim="http://iec.ch/TC57/2013/CIM-schema-cim16#"
         xmlns:cyme="http://www.cyme.com/CIM/1.0.2#"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" >
    <cim:SwitchInfo rdf:ID="_AB16765A-B19E-4454-A58F-868D23C6CD26" />
</rdf:RDF>"""

    g = Graph()
    with tempfile.TemporaryDirectory() as td:
        sample_file = str(Path(td) / "sample.xml")
        open(sample_file, "w").write(xml_sample)

        g.parse(sample_file, publicID="")

    subject, predicate, object = next(iter(g))

    assert subject == URIRef("#_AB16765A-B19E-4454-A58F-868D23C6CD26")
    assert predicate == URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    assert object == URIRef("http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo")
