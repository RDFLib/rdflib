import json

from rdflib.query import (
    Result, ResultException, ResultSerializer, ResultParser)
from rdflib import Literal, URIRef, BNode, Variable

from six import binary_type, text_type


"""A Serializer for SPARQL results in JSON:

http://www.w3.org/TR/rdf-sparql-json-res/

Bits and pieces borrowed from:
http://projects.bigasterisk.com/sparqlhttp/

Authors: Drew Perttula, Gunnar Aastrand Grimnes

"""


class JSONResultParser(ResultParser):

    def parse(self, source):
        inp = source.read()
        if isinstance(inp, binary_type):
            inp = inp.decode('utf-8')
        return JSONResult(json.loads(inp))


class JSONResultSerializer(ResultSerializer):

    def __init__(self, result):
        ResultSerializer.__init__(self, result)

    def serialize(self, stream, encoding=None):

        res = {}
        if self.result.type == 'ASK':
            res["head"] = {}
            res["boolean"] = self.result.askAnswer
        else:
            # select
            res["results"] = {}
            res["head"] = {}
            res["head"]["vars"] = self.result.vars
            res["results"]["bindings"] = [self._bindingToJSON(
                x) for x in self.result.bindings]

        r = json.dumps(res, allow_nan=False, ensure_ascii=False)
        if encoding is not None:
            stream.write(r.encode(encoding))
        else:
            stream.write(r)

    def _bindingToJSON(self, b):
        res = {}
        for var in b:
            j = termToJSON(self, b[var])
            if j is not None:
                res[var] = termToJSON(self, b[var])
        return res


class JSONResult(Result):

    def __init__(self, json):
        self.json = json
        if "boolean" in json:
            type_ = 'ASK'
        elif "results" in json:
            type_ = 'SELECT'
        else:
            raise ResultException('No boolean or results in json!')

        Result.__init__(self, type_)

        if type_ == 'ASK':
            self.askAnswer = bool(json['boolean'])
        else:
            self.bindings = self._get_bindings()
            self.vars = [Variable(x) for x in json["head"]["vars"]]

    def _get_bindings(self):
        ret = []
        for row in self.json['results']['bindings']:
            outRow = {}
            for k, v in row.items():
                outRow[Variable(k)] = parseJsonTerm(v)
            ret.append(outRow)
        return ret


def parseJsonTerm(d):
    """rdflib object (Literal, URIRef, BNode) for the given json-format dict.

    input is like:
      { 'type': 'uri', 'value': 'http://famegame.com/2006/01/username' }
      { 'type': 'literal', 'value': 'drewp' }
    """

    t = d['type']
    if t == 'uri':
        return URIRef(d['value'])
    elif t == 'literal':
        return Literal(d['value'], datatype=d.get('datatype'), lang=d.get('xml:lang'))
    elif t == 'typed-literal':
        return Literal(d['value'], datatype=URIRef(d['datatype']))
    elif t == 'bnode':
        return BNode(d['value'])
    else:
        raise NotImplementedError("json term type %r" % t)


def termToJSON(self, term):
    if isinstance(term, URIRef):
        return {'type': 'uri', 'value': text_type(term)}
    elif isinstance(term, Literal):
        r = {'type': 'literal',
             'value': text_type(term)}

        if term.datatype is not None:
            r['datatype'] = text_type(term.datatype)
        if term.language is not None:
            r['xml:lang'] = term.language
        return r

    elif isinstance(term, BNode):
        return {'type': 'bnode', 'value': str(term)}
    elif term is None:
        return None
    else:
        raise ResultException(
            'Unknown term type: %s (%s)' % (term, type(term)))
