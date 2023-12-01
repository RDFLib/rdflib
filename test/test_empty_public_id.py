import pytest

import rdflib
from rdflib.term import URIRef

"""The tests in this file cover the use of an empty publicID
(e.g. g.parse(sample, publicID=""). When `None` is passes to this argument,
rdflib puts the file name for `sample` as a prefix to all rdf identifiers
in the file; for example, given a sample

# /tmp/sample-rdf.xml:
<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:cim="http://iec.ch/TC57/2013/CIM-schema-cim16#"
         xmlns:cyme="http://www.cyme.com/CIM/1.0.2#"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" >
    <cim:SwitchInfo rdf:ID="_AB16765A-B19E-4454-A58F-868D23C6CD26" />
</rdf:RDF>

g.parse(sample_rdf, publicID=None)
subject, predicate, object = next(iter(g))

would result in:
subject
>>> URIRef("/tmp/sample-rdf.xml#_AB16765A-B19E-4454-A58F-868D23C6CD26")

However, in most implementations of rdf parsers, rdflib was previously just checking
if the `publicID` argument was falsy, so it would handle `publicID=""` as if it was
`publicID=None`. This is inconsistent (since "" is a valid string) and it forces
consumers of rdflib to strip out this resource ID in order to access the
ID, which they may need to do to query information about the subject from other
resources.

"""


def test_hext(tmp_path):
    hext_sample = """\
["#_AB16765A-B19E-4454-A58F-868D23C6CD26", "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo", "globalId", "", ""]
"""
    sample_file = tmp_path / "sample.ndjson"
    open(sample_file, "w").write(hext_sample)

    g = rdflib.Graph()
    g.parse(sample_file, format="hext", publicID="")

    subject, predicate, obj = next(iter(g))
    assert subject == URIRef("#_AB16765A-B19E-4454-A58F-868D23C6CD26")
    assert predicate == URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    assert obj == URIRef("http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo")


def test_jsonld(tmp_path):
    jsonld_sample = """\
{
  "@context": {
    "cim": "http://iec.ch/TC57/2013/CIM-schema-cim16#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  },
  "@graph": [
    {
      "@id": "#_AB16765A-B19E-4454-A58F-868D23C6CD26",
      "@type": "cim:SwitchInfo"
    }
  ]
}"""

    sample_file = tmp_path / "sample.json-ld"
    open(sample_file, "w").write(jsonld_sample)

    g = rdflib.Graph()
    g.parse(sample_file, format="json-ld", publicID="")

    subject, predicate, obj = next(iter(g))

    assert subject == URIRef("#_AB16765A-B19E-4454-A58F-868D23C6CD26")
    assert predicate == URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    assert obj == URIRef("http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo")


@pytest.mark.parametrize("fmt", ["n3", "turtle"])
def test_notation3(tmp_path, fmt):
    """Test notation3 (i.e. .ttl) files can be parsed with publicID of"""
    ttl_sample = """\
    <#_AB16765A-B19E-4454-A58F-868D23C6CD26> a
    <http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo> .
    """

    sample_file = tmp_path / "sample.ttl"
    open(sample_file, "w").write(ttl_sample)

    g = rdflib.Graph()
    g.parse(sample_file, format=fmt, publicID="")

    subject, predicate, obj = next(iter(g))

    assert subject == URIRef("#_AB16765A-B19E-4454-A58F-868D23C6CD26")
    assert predicate == URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    assert obj == URIRef("http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo")


def test_nquads(tmp_path):
    nquads_sample = """\
<#_AB16765A-B19E-4454-A58F-868D23C6CD26> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo> .
"""
    sample_file = tmp_path / "sample.nquads"
    open(sample_file, "w").write(nquads_sample)

    g = rdflib.Graph()
    g.parse(sample_file, format="nquads", publicID="http://foo.com")

    subject, predicate, obj = next(iter(g))
    assert subject == URIRef("#_AB16765A-B19E-4454-A58F-868D23C6CD26")
    assert predicate == URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    assert obj == URIRef("http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo")


def test_ntriples(tmp_path):
    ntriples_sample = """\
<#_AB16765A-B19E-4454-A58F-868D23C6CD26> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo> .
"""
    sample_file = tmp_path / "sample.ntriples"
    open(sample_file, "w").write(ntriples_sample)

    g = rdflib.Graph()
    g.parse(sample_file, format="nt", publicID="")

    subject, predicate, obj = next(iter(g))
    assert subject == URIRef("#_AB16765A-B19E-4454-A58F-868D23C6CD26")
    assert predicate == URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    assert obj == URIRef("http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo")


def test_rdf_voc(tmp_path):
    ...


def test_rdfxml(tmp_path):
    xml_sample = """\
<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:cim="http://iec.ch/TC57/2013/CIM-schema-cim16#"
         xmlns:cyme="http://www.cyme.com/CIM/1.0.2#"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" >
    <cim:SwitchInfo rdf:ID="_AB16765A-B19E-4454-A58F-868D23C6CD26" />
</rdf:RDF>"""

    sample_file = tmp_path / "sample.xml"
    open(sample_file, "w").write(xml_sample)

    g = rdflib.Graph()
    g.parse(sample_file, format="xml", publicID="")

    subject, predicate, obj = next(iter(g))

    assert subject == URIRef("#_AB16765A-B19E-4454-A58F-868D23C6CD26")
    assert predicate == URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    assert obj == URIRef("http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo")


def test_trig(tmp_path):
    trig_sample = """\
<#_AB16765A-B19E-4454-A58F-868D23C6CD26> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo> .
"""
    sample_file = tmp_path / "sample.trig"
    open(sample_file, "w").write(trig_sample)

    g = rdflib.Graph()
    g.parse(sample_file, format="trig", publicID="")

    subject, predicate, obj = next(iter(g))
    assert subject == URIRef("#_AB16765A-B19E-4454-A58F-868D23C6CD26")
    assert predicate == URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    assert obj == URIRef("http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo")


def test_trix(tmp_path):
    trix_sample = """\
<?xml version='1.0'?>
<TriX xmlns='http://www.w3.org/2004/03/trix/trix-1/'>
    <graph>
        <uri>file:/home/grimnes/tmp/aperture/</uri>
        <triple>
            <uri>#_AB16765A-B19E-4454-A58F-868D23C6CD26</uri>
            <uri>http://www.w3.org/1999/02/22-rdf-syntax-ns#type</uri>
            <uri>http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo</uri>
        </triple>
  </graph>
</TriX>"""

    sample_file = tmp_path / "sample.trix"
    open(sample_file, "w").write(trix_sample)

    g = rdflib.graph.ConjunctiveGraph()
    g.parse(sample_file, format="trix", publicID="")

    subject, predicate, obj = next(iter(g))

    assert subject == URIRef("#_AB16765A-B19E-4454-A58F-868D23C6CD26")
    assert predicate == URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    assert obj == URIRef("http://iec.ch/TC57/2013/CIM-schema-cim16#SwitchInfo")
