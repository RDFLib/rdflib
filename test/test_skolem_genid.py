from rdflib import URIRef
from rdflib.term import Genid, RDFLibGenid


def test_skolem_genid_and_rdflibgenid():
    rdflib_genid = URIRef(
        "https://rdflib.github.io/.well-known/genid/rdflib/N97c39b957bc444949a82793519348dc2"
    )
    custom_genid = URIRef(
        "http://example.com/.well-known/genid/example/Ne864c0e3684044f381d518fdac652f2e"
    )

    assert RDFLibGenid._is_rdflib_skolem(rdflib_genid) is True
    assert Genid._is_external_skolem(rdflib_genid) is True

    assert RDFLibGenid._is_rdflib_skolem(custom_genid) is False
    assert Genid._is_external_skolem(custom_genid) is True
