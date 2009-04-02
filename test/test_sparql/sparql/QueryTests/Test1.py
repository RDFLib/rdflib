#!/d/Bin/Python/python.exe
# -*- coding: utf-8 -*-
#
#
# $Date: 2005/04/02 07:29:46 $, by $Author: ivan $, $Revision: 1.1 $
#

from testSPARQL import ns_rdf
from testSPARQL import ns_rdfs
from testSPARQL import ns_dc
from testSPARQL import ns_dc0
from testSPARQL import ns_foaf

from rdflib.sparql.graphPattern import GraphPattern


# Careful to keep the <?xml declaration at the very beginning, otherwise the parser will fail...
rdfData ="""<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
   xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:foaf="http://xmlns.com/foaf/0.1/"
>
        <rdf:Description>
                <foaf:name>Johny Lee Outlaw</foaf:name>	
                <foaf:mbox rdf:resource="mailto:jlow@example.com"/>
        </rdf:Description>
</rdf:RDF>
"""

select      = ["?mbox","?junk"]
pattern     = GraphPattern([("?x",ns_foaf["name"],"Johny Lee Outlaw"),("?x",ns_foaf["mbox"],"?mbox")])
optional    = None
tripleStore = None
expected = '''
?mbox: mailto:jlow@example.com
?junk: None
'''



