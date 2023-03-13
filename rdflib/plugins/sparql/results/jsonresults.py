from __future__ import annotations

import json
from typing import IO, Any, Dict, Mapping, MutableSequence, Optional

from rdflib.query import Result, ResultException, ResultParser, ResultSerializer
from rdflib.term import BNode, Identifier, Literal, URIRef, Variable

"""A Serializer for SPARQL results in JSON:

http://www.w3.org/TR/rdf-sparql-json-res/

Bits and pieces borrowed from:
http://projects.bigasterisk.com/sparqlhttp/

Authors: Drew Perttula, Gunnar Aastrand Grimnes

"""


class JSONResultParser(ResultParser):
    # type error: Signature of "parse" incompatible with supertype "ResultParser"
    def parse(self, source: IO, content_type: Optional[str] = None) -> Result:  # type: ignore[override]
        inp = source.read()
        if isinstance(inp, bytes):
            inp = inp.decode("utf-8")
        return JSONResult(json.loads(inp))


class JSONResultSerializer(ResultSerializer):
    def __init__(self, result: Result):
        ResultSerializer.__init__(self, result)

    # type error: Signature of "serialize" incompatible with supertype "ResultSerializer"
    def serialize(self, stream: IO, encoding: str = None) -> None:  # type: ignore[override]
        res: Dict[str, Any] = {}
        if self.result.type == "ASK":
            res["head"] = {}
            res["boolean"] = self.result.askAnswer
        else:
            # select
            res["results"] = {}
            res["head"] = {}
            res["head"]["vars"] = self.result.vars
            res["results"]["bindings"] = [
                self._bindingToJSON(x) for x in self.result.bindings
            ]

        r = json.dumps(res, allow_nan=False, ensure_ascii=False)
        if encoding is not None:
            stream.write(r.encode(encoding))
        else:
            stream.write(r)

    def _bindingToJSON(self, b: Mapping[Variable, Identifier]) -> Dict[Variable, Any]:
        res = {}
        for var in b:
            j = termToJSON(self, b[var])
            if j is not None:
                res[var] = termToJSON(self, b[var])
        return res


class JSONResult(Result):
    def __init__(self, json: Dict[str, Any]):
        self.json = json
        if "boolean" in json:
            type_ = "ASK"
        elif "results" in json:
            type_ = "SELECT"
        else:
            raise ResultException("No boolean or results in json!")

        Result.__init__(self, type_)

        if type_ == "ASK":
            self.askAnswer = bool(json["boolean"])
        else:
            self.bindings = self._get_bindings()
            self.vars = [Variable(x) for x in json["head"]["vars"]]

    def _get_bindings(self) -> MutableSequence[Mapping[Variable, Identifier]]:
        ret: MutableSequence[Mapping[Variable, Identifier]] = []
        for row in self.json["results"]["bindings"]:
            outRow: Dict[Variable, Identifier] = {}
            for k, v in row.items():
                outRow[Variable(k)] = parseJsonTerm(v)
            ret.append(outRow)
        return ret


def parseJsonTerm(d: Dict[str, str]) -> Identifier:
    """rdflib object (Literal, URIRef, BNode) for the given json-format dict.

    input is like:
      { 'type': 'uri', 'value': 'http://famegame.com/2006/01/username' }
      { 'type': 'literal', 'value': 'drewp' }
    """

    t = d["type"]
    if t == "uri":
        return URIRef(d["value"])
    elif t == "literal":
        return Literal(d["value"], datatype=d.get("datatype"), lang=d.get("xml:lang"))
    elif t == "typed-literal":
        return Literal(d["value"], datatype=URIRef(d["datatype"]))
    elif t == "bnode":
        return BNode(d["value"])
    else:
        raise NotImplementedError("json term type %r" % t)


def termToJSON(
    self: JSONResultSerializer, term: Optional[Identifier]
) -> Optional[Dict[str, str]]:
    if isinstance(term, URIRef):
        return {"type": "uri", "value": str(term)}
    elif isinstance(term, Literal):
        r = {"type": "literal", "value": str(term)}

        if term.datatype is not None:
            r["datatype"] = str(term.datatype)
        if term.language is not None:
            r["xml:lang"] = term.language
        return r

    elif isinstance(term, BNode):
        return {"type": "bnode", "value": str(term)}
    elif term is None:
        return None
    else:
        raise ResultException("Unknown term type: %s (%s)" % (term, type(term)))
