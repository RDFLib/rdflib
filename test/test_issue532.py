# test for https://github.com/RDFLib/rdflib/issues/532

from rdflib import Graph

def test_issue532():
    data = """
    @base <http://purl.org/linkedpolitics/MembersOfParliament_background> .
    @prefix foaf: <http://xmlns.com/foaf/0.1/> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    @prefix lpv: <vocabulary/> .
    @prefix NationalParty: <NationalParty/> .

    <EUmember_1026>
        a lpv:MemberOfParliament ;
        lpv:MEP_ID "1026" ;
        lpv:countryOfRepresentation <EUCountry_FR> ;
        lpv:dateOfBirth "1946-07-13"^^xsd:date ;
        lpv:politicalFunction [
            a lpv:PoliticalFunction ;
            lpv:beginning "1989-10-13"^^xsd:date ;
            lpv:end "1992-01-14"^^xsd:date ;
            lpv:institution NationalParty:sans_etiquette
        ] , [
            a lpv:PoliticalFunction ;
            lpv:beginning "2005-02-24"^^xsd:date ;
            lpv:end "2007-01-30"^^xsd:date ;
            lpv:institution NationalParty:Union_pour_la_democratie_francaise
        ] ;
        foaf:familyName "Bourlanges" ;
        foaf:givenName "Jean-Louis" .
    """

    g = Graph()
    g.parse(data=data, format='n3')

    getnewMeps ="""
    PREFIX lpv: <http://purl.org/linkedpolitics/vocabulary/>
    prefix foaf: <http://xmlns.com/foaf/0.1/>
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT DISTINCT ?name ?lastname WHERE {
      ?member a lpv:MemberOfParliament .
      ?member foaf:givenName ?name .
      ?member foaf:familyName ?lastname .
      ?member lpv:politicalFunction ?function .
      ?function lpv:beginning ?date .

      FILTER (?date >= "2004-06-20"^^xsd:date)
    }
    """

    result = list(g.query(getnewMeps))
    assert len(result) == 1
