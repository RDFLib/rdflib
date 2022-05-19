import pytest

import rdflib


@pytest.mark.parametrize(
    "reserved_char_percent_encoded",
    [
        "%20",
        "%21",
        "%23",
        "%24",
        "%25",
        "%26",
        "%27",
        "%28",
        "%29",
        "%2A",
        "%2B",
        "%2C",
        "%2F",
        "%3A",
        "%3B",
        "%3D",
        "%3F",
        "%40",
        "%5B",
        "%5D",
    ],
)
def test_sparql_parse_reserved_char_percent_encoded(reserved_char_percent_encoded):
    data = f"""@prefix : <https://www.example.co/reserved/language#> .

<https://www.example.co/reserved/root> :_id "01G39WKRH76BGY5D3SKDHJP2SX" ;
    :transcript{reserved_char_percent_encoded}data [ :_id "01G39WKRH7JYRX78X7FG4RCNYF" ;
            :_key "transcript{reserved_char_percent_encoded}data" ;
            :value "value" ;
            :value_id "01G39WKRH7PVK1DXQHWT08DZA8" ] ."""

    q = f"""PREFIX : <https://www.example.co/reserved/language#>
    SELECT  ?o 
    WHERE {{ ?s :transcript{reserved_char_percent_encoded}data/:value ?o . }}"""

    g = rdflib.Graph()
    g.parse(data=data, format="ttl")
    res = g.query(q)

    assert list(res)[0][0] == rdflib.term.Literal('value')

    assert reserved_char_percent_encoded in str(
        rdflib.plugins.sparql.parser.parseQuery(q)
    )
