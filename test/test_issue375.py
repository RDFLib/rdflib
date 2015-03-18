import os
import subprocess
import sys
import re

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

mdata_expected = u'''@prefix cc: <http://creativecommons.org/ns#> .
@prefix ctag: <http://commontag.org/ns#> .
@prefix dc: <http://purl.org/dc/terms/> .
@prefix dc11: <http://purl.org/dc/elements/1.1/> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix gr: <http://purl.org/goodrelations/v1#> .
@prefix grddl: <http://www.w3.org/2003/g/data-view#> .
@prefix hcalendar: <http://microformats.org/profile/hcalendar#> .
@prefix hcard: <http://microformats.org/profile/hcard#> .
@prefix ical: <http://www.w3.org/2002/12/cal/icaltzd#> .
@prefix ma: <http://www.w3.org/ns/ma-ont#> .
@prefix md: <http://www.w3.org/ns/md#> .
@prefix og: <http://ogp.me/ns#> .
@prefix org: <http://www.w3.org/ns/org#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix qb: <http://purl.org/linked-data/cube#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfa: <http://www.w3.org/ns/rdfa#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix rev: <http://purl.org/stuff/rev#> .
@prefix rif: <http://www.w3.org/2007/rif#> .
@prefix rr: <http://www.w3.org/ns/r2rml#> .
@prefix schema: <http://schema.org/> .
@prefix sd: <http://www.w3.org/ns/sparql-service-description#> .
@prefix sioc: <http://rdfs.org/sioc/ns#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix skosxl: <http://www.w3.org/2008/05/skos-xl#> .
@prefix v: <http://rdf.data-vocabulary.org/#> .
@prefix vcard: <http://www.w3.org/2006/vcard/ns#> .
@prefix void: <http://rdfs.org/ns/void#> .
@prefix wdr: <http://www.w3.org/2007/05/powder#> .
@prefix wdrs: <http://www.w3.org/2007/05/powder-s#> .
@prefix xhv: <http://www.w3.org/1999/xhtml/vocab#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<test/mdata/codelab.html> md:item ( [ a schema:TechArticle ;
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
                schema:name "Structured data with schema.org codelab" ] ) ;
    rdfa:usesVocabulary schema: .
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
    args = ['python', 'rdflib/tools/rdfpipe.py', '-i', 'rdfa1.1', 'test/rdfa/oreilly.html']
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, universal_newlines=True, env=env)
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
    args = ['python', 'rdflib/tools/rdfpipe.py', '-i', 'mdata', 'test/mdata/codelab.html']
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, universal_newlines=True, env=env)
    res = ''
    while proc.poll() is None:
        res += proc.stdout.read()

    a = re.compile(r'^(.*?<)[^>]+(test/mdata/codelab.*?>)', flags=re.DOTALL)
    b = re.compile(r'^(.*?<)[^>]+(test/mdata/squares.*?>)', flags=re.DOTALL)
    res = a.sub(r'\1\2', res.strip())
    res = b.sub(r'\1\2', res)

    assert res == mdata_expected
