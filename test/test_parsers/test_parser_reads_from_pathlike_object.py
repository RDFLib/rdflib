import tempfile
import rdflib
from pathlib import Path


def test_reading_from_path_object():
    xml_sample = """\
<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:cim="http://iec.ch/TC57/2013/CIM-schema-cim16#"
         xmlns:cyme="http://www.cyme.com/CIM/1.0.2#"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" >
    <cim:SwitchInfo rdf:ID="_AB16765A-B19E-4454-A58F-868D23C6CD26" />
</rdf:RDF>"""

    with tempfile.TemporaryDirectory() as td:
        sample_file = Path(td) / "sample.xml"
        open(str(sample_file), "w").write(xml_sample)

        g = rdflib.Graph()
        g.parse(sample_file, publicID="")

    subject, predicate, object = next(iter(g))

    assert "_AB16765A-B19E-4454-A58F-868D23C6CD26" in subject
    assert "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" in predicate
    assert "http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo" in object
