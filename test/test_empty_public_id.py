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


def test_hext():
    ...


def test_jsonld():
    ...


def test_notation3():
    ...


def test_nquads():
    ...


def test_ntriples():
    ...


def test_rdf_voc():
    ...


def test_rdfxml():
    ...


def test_trig():
    ...


def test_trix():
    ...
