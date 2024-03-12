"""
Issue 923: split charset off of Content-Type before looking up Result-parsing plugin.
"""
from io import StringIO

from rdflib.query import Result

RESULT_SOURCE = """\
{
  "head" : {
    "vars" : [ "subject", "predicate", "object", "context" ]
  },
  "results" : {
    "bindings" : [ {
      "subject" : {
        "type" : "bnode",
        "value" : "service"
      },
      "predicate" : {
        "type" : "uri",
        "value" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
      },
      "object" : {
        "type" : "uri",
        "value" : "http://www.w3.org/ns/sparql-service-description#Service"
      }
    }]
  }
}
"""


def test_issue_923():
    with StringIO(RESULT_SOURCE) as result_source:
        Result.parse(
            source=result_source,
            content_type="application/sparql-results+json;charset=utf-8",
        )
