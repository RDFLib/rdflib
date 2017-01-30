# test for https://github.com/RDFLib/rdflib/issues/492

#!/usr/bin/env python3

import rdflib

def test_issue492():
    query = '''
    prefix owl: <http://www.w3.org/2002/07/owl#>
    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    select ?x
    where
    {
        ?x rdf:rest/rdf:first _:6.
        ?x rdf:rest/rdf:first _:5.
    }
    '''
    print(rdflib.__version__)
    g = rdflib.Graph()

    # raised a TypeError: unorderable types: SequencePath() < SequencePath()
    result = g.query(query)
