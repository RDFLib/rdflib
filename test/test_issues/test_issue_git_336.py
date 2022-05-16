# NOTE: The config below enables strict mode for mypy.
# mypy: no_ignore_errors
# mypy: warn_unused_configs, disallow_any_generics
# mypy: disallow_subclassing_any, disallow_untyped_calls
# mypy: disallow_untyped_defs, disallow_incomplete_defs
# mypy: check_untyped_defs, disallow_untyped_decorators
# mypy: no_implicit_optional, warn_redundant_casts, warn_unused_ignores
# mypy: warn_return_any, no_implicit_reexport, strict_equality

import rdflib

# Test for https://github.com/RDFLib/rdflib/issues/336
# and https://github.com/RDFLib/rdflib/issues/345


# stripped-down culprit:
"""\
@prefix fs: <http://freesurfer.net/fswiki/terms/> .
@prefix prov: <http://www.w3.org/ns/prov#> .

<http://nidm.nidash.org/iri/82b79326488911e3b2fb14109fcf6ae7>
        a fs:stat_header,
        prov:Entity ;
    fs:mrisurf.c-cvs_version
        "$Id: mrisurf.c,v 1.693.2.2 2011/04/27 19:21:05 nicks Exp $" .
"""


def test_ns_localname_roundtrip() -> None:

    XNS = rdflib.Namespace("http://example.net/fs")

    g = rdflib.Graph()
    g.bind("xns", str(XNS))
    g.add(
        (
            rdflib.URIRef("http://example.com/thingy"),
            XNS["lowecase.xxx-xxx_xxx"],  # <- not round trippable
            rdflib.Literal("Junk"),
        )
    )
    turtledump = g.serialize(format="turtle")
    xmldump = g.serialize(format="xml")
    g1 = rdflib.Graph()
    g1.parse(data=xmldump, format="xml")
    g1.parse(data=turtledump, format="turtle")
