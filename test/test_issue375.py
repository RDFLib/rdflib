import os
import subprocess
import sys
import re

from rdflib import Graph
from rdflib.compare import isomorphic

rdfa_expected = u'''@prefix dc: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix frbr: <http://vocab.org/frbr/core#> .
@prefix gr: <http://purl.org/goodrelations/v1#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://customer.wileyeurope.com/CGI-BIN/lansaweb?procfun+shopcart+shcfn01+funcparms+parmisbn(a0130):9780596516499+parmqty(p0050):1+parmurl(l0560):http://oreilly.com/store/> a gr:Offering ;
    gr:includesObject [ a gr:TypeAndQuantityNode ;
            gr:ammountOfThisGood "1.0"^^xsd:float ;
            gr:hasPriceSpecification [ a gr:UnitPriceSpecification ;
                    gr:hasCurrency "GBP"@en ;
                    gr:hasCurrencyValue "34.5"^^xsd:float ] ;
            gr:typeOfGood <urn:x-domain:oreilly.com:product:9780596516499.BOOK> ] .

<http://my.safaribooksonline.com/9780596803346> a gr:Offering ;
    gr:includesObject [ a gr:TypeAndQuantityNode ;
            gr:ammountOfThisGood "1.0"^^xsd:float ;
            gr:typeOfGood <urn:x-domain:oreilly.com:product:9780596803346.SAF> ] .

<https://epoch.oreilly.com/shop/cart.orm?p=BUNDLE&prod=9780596516499.BOOK&prod=9780596803391.EBOOK&bundle=1&retUrl=http%3A%252F%252Foreilly.com%252Fstore%252F> a gr:Offering ;
    gr:includesObject [ a gr:TypeAndQuantityNode ;
            gr:ammountOfThisGood "1.0"^^xsd:float ;
            gr:includesObject [ a gr:TypeAndQuantityNode ;
                    gr:ammountOfThisGood "1.0"^^xsd:float ;
                    gr:hasPriceSpecification [ a gr:UnitPriceSpecification ;
                            gr:hasCurrency "None"@en ;
                            gr:hasCurrencyValue "49.49"^^xsd:float ] ;
                    gr:typeOfGood <urn:x-domain:oreilly.com:product:9780596803391.EBOOK> ] ;
            gr:typeOfGood <urn:x-domain:oreilly.com:product:9780596516499.BOOK> ] .

<https://epoch.oreilly.com/shop/cart.orm?prod=9780596516499.BOOK> a gr:Offering ;
    gr:includesObject [ a gr:TypeAndQuantityNode ;
            gr:ammountOfThisGood "1.0"^^xsd:float ;
            gr:hasPriceSpecification [ a gr:UnitPriceSpecification ;
                    gr:hasCurrency "USD"@en ;
                    gr:hasCurrencyValue "44.99"^^xsd:float ] ;
            gr:typeOfGood <urn:x-domain:oreilly.com:product:9780596516499.BOOK> ] .

<https://epoch.oreilly.com/shop/cart.orm?prod=9780596803391.EBOOK> a gr:Offering ;
    gr:includesObject [ a gr:TypeAndQuantityNode ;
            gr:ammountOfThisGood "1.0"^^xsd:float ;
            gr:hasPriceSpecification [ a gr:UnitPriceSpecification ;
                    gr:hasCurrency "USD"@en ;
                    gr:hasCurrencyValue "35.99"^^xsd:float ] ;
            gr:typeOfGood <urn:x-domain:oreilly.com:product:9780596803391.EBOOK> ] .

<urn:x-domain:oreilly.com:product:9780596516499.IP> a frbr:Expression ;
    dc:creator <urn:x-domain:oreilly.com:agent:pdb:3343>,
        <urn:x-domain:oreilly.com:agent:pdb:3501>,
        <urn:x-domain:oreilly.com:agent:pdb:3502> ;
    dc:issued "2009-06-12"^^xsd:dateTime ;
    dc:publisher "O'Reilly Media"@en ;
    dc:title "Natural Language Processing with Python"@en ;
    frbr:embodiment <urn:x-domain:oreilly.com:product:9780596516499.BOOK>,
        <urn:x-domain:oreilly.com:product:9780596803346.SAF>,
        <urn:x-domain:oreilly.com:product:9780596803391.EBOOK> .

<urn:x-domain:oreilly.com:agent:pdb:3343> a foaf:Person ;
    foaf:homepage <http://www.oreillynet.com/pub/au/3614> ;
    foaf:name "Steven Bird"@en .

<urn:x-domain:oreilly.com:agent:pdb:3501> a foaf:Person ;
    foaf:homepage <http://www.oreillynet.com/pub/au/3615> ;
    foaf:name "Ewan Klein"@en .

<urn:x-domain:oreilly.com:agent:pdb:3502> a foaf:Person ;
    foaf:homepage <http://www.oreillynet.com/pub/au/3616> ;
    foaf:name "Edward Loper"@en .

<urn:x-domain:oreilly.com:product:9780596803346.SAF> a frbr:Manifestation ;
    dc:type <http://purl.oreilly.com/product-types/SAF> .

<urn:x-domain:oreilly.com:product:9780596803391.EBOOK> a frbr:Manifestation ;
    dc:identifier <urn:isbn:9780596803391> ;
    dc:issued "2009-06-12"^^xsd:dateTime ;
    dc:type <http://purl.oreilly.com/product-types/EBOOK> .

<urn:x-domain:oreilly.com:product:9780596516499.BOOK> a frbr:Manifestation ;
    dc:extent """
                    512
                """@en ;
    dc:identifier <urn:isbn:9780596516499> ;
    dc:issued "2009-06-19"^^xsd:dateTime ;
    dc:type <http://purl.oreilly.com/product-types/BOOK> .
'''.strip()

mdata_expected = u'''
@prefix hcard: <http://microformats.org/profile/hcard#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema: <http://schema.org/> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
[] a schema:TechArticle ;
    schema:articleBody """
    Exercise 1: From basic HTML to RDFa: first steps
    Exercise 2: Embedded types
    Exercise 3: From strings to things
""" ;
    schema:author "Author Name" ;
    schema:datePublished "January 29, 2014" ;
    schema:description """
    About this codelab
""" ;
    schema:educationalUse "codelab" ;
    schema:image <test/mdata/squares.png> ;
    schema:name "Structured data with schema.org codelab" .
'''.strip()

env = os.environ.copy()
env['PYTHONPATH'] = '.:' + env.get('PYTHONPATH', '')


def test_rdfpipe_bytes_vs_str():
    """
    Issue 375: rdfpipe command generates bytes vs. str TypeError

    While Python2 exposes sys.stdout as a bytes buffer, Python 3
    explicitly exposes sys.stdout.buffer for this purpose. Test
    rdfpipe to ensure that we get the expected results.
    """
    args = [
        sys.executable, 'rdflib/tools/rdfpipe.py', '-i', 'rdfa1.1',
        'test/rdfa/oreilly.html'
    ]
    proc = subprocess.Popen(
        args, stdout=subprocess.PIPE, universal_newlines=True, env=env)
    res = ''
    while proc.poll() is None:
        res += proc.stdout.read()

    assert res.strip() == rdfa_expected


def test_rdfpipe_mdata_open():
    """
    Issue 375: rdfa1.1 and mdata processors used file() builtin

    The file() builtin has been deprecated for a long time. Use
    the open() builtin instead.
    """
    args = [
        sys.executable, 'rdflib/tools/rdfpipe.py', '-i', 'mdata',
        'test/mdata/codelab.html'
    ]
    proc = subprocess.Popen(
        args, stdout=subprocess.PIPE, universal_newlines=True, env=env)
    res_abs = ''
    while proc.poll() is None:
        res_abs += proc.stdout.read()

    # we don't know the test system's paths, make them relative to this file
    a = re.compile(r'^(.*?<)[^>]+(test/mdata/codelab.*?>)', flags=re.DOTALL)
    b = re.compile(r'^(.*?<)[^>]+(test/mdata/squares.*?>)', flags=re.DOTALL)
    res = a.sub(r'\1\2', res_abs.strip())
    res = b.sub(r'\1\2', res)

    # compare if result graphs are isomorphic
    g_expected = Graph()
    g_expected.parse(data=mdata_expected, format='n3')

    g_res = Graph()
    g_res.parse(data=res, format='n3')

    assert isomorphic(g_expected, g_res), \
        'not isomorphic:\nres:\n%s\ng_res:\n%s\nexpected:\n%s' % (
        res_abs,
        g_res.serialize(format='nt'),
        g_expected.serialize(format='nt')
    )
