# -*- coding: utf-8 -*-
from rdflib.graph import ConjunctiveGraph
from rdflib.parser import StringInputSource
import textwrap

prefix = textwrap.dedent('''\
    @prefix nie: <http://www.semanticdesktop.org/ontologies/2007/01/19/nie#> .
    @prefix nfo: <http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#> .
    @prefix nco: <http://www.semanticdesktop.org/ontologies/2007/03/22/nco#> .
    @prefix nmo: <http://www.semanticdesktop.org/ontologies/2007/03/22/nmo#> .
    @prefix ncal: <http://www.semanticdesktop.org/ontologies/2007/04/02/ncal#> .
    @prefix nexif: <http://www.semanticdesktop.org/ontologies/2007/05/10/nexif#> .
    @prefix nid3: <http://www.semanticdesktop.org/ontologies/2007/05/10/nid3#> .
    @prefix dc: <http://dublincore.org/documents/2010/10/11/dces/#> .
    @prefix nmm: <http://library.gnome.org/devel/ontology/unstable/nmm-classes.html#> .
    @prefix nao: <http://www.semanticdesktop.org/ontologies/2007/08/15/nao#> .
    ''')

meta = textwrap.dedent(u"""\
a nfo:PaginatedTextDocument ;
    nie:title "SV Meldung" ;
    nco:creator [ a nco:Contact ;
    nco:fullname "nikratio"] ;
    nie:contentCreated "2011-08-10T20:12:38Z" ;
    dc:format "application/pdf" ;
    nie:description "()" ;
    nao:hasTag ?tag1 ;
    nfo:pageCount 1 ;
    nie:plainTextContent "%s" .
} } WHERE { {
?tag1 a nao:Tag ; nao:prefLabel "()" .
""")

test_string1 = u"""\
Betriebsnummer der Einzugsstelle:\nKnappschaft\n980 0000 6\nWICHTIGES DOKUMENT - SORGFÄLTIG AUFBEWAHREN!\n """

def test1():
    meta1 = meta.encode('utf-8') % test_string1.encode('utf-8')
    graph = ConjunctiveGraph()
    graph.parse(StringInputSource(prefix + '<http://example.org/>' + meta1), format='n3')

test_string2 = u"""\
Betriebsnummer der Einzugsstelle:
Knappschaft
980 0000 6
WICHTIGES DOKUMENT - SORGFÄLTIG AUFBEWAHREN!
"""

def test2():
    meta2 = meta.encode('utf-8') % test_string2.encode('utf-8')
    graph = ConjunctiveGraph()
    graph.parse(StringInputSource(prefix + '<http://example.org/>' + meta2), format='n3')

from nose import SkipTest
raise SkipTest("Known issue, with newlines in text")