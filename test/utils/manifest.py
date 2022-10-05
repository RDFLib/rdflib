from __future__ import annotations

import logging
from test.utils.namespace import DAWGT, MF, QT, RDFT, UT
from typing import Iterable, List, NamedTuple, Optional, Tuple, Union, cast

from rdflib import RDF, RDFS, Graph
from rdflib.term import Identifier, Node, URIRef

logger = logging.getLogger(__name__)

ResultType = Union[
    Identifier, Tuple[Optional[Node], List[Tuple[Optional[Node], Optional[Node]]]]
]
GraphDataType = Union[List[Optional[Node]], List[Tuple[Optional[Node], Optional[Node]]]]


class RDFTest(NamedTuple):
    uri: URIRef
    name: str
    comment: str
    data: Identifier
    graphdata: Optional[GraphDataType]
    action: Identifier
    result: Optional[ResultType]
    syntax: bool


def read_manifest(f, base=None, legacy=False) -> Iterable[Tuple[Node, Node, RDFTest]]:
    """read a manifest file"""

    def _str(x):
        if x is not None:
            return str(x)
        return None

    g = Graph()
    g.parse(f, publicID=base, format="turtle")

    for m in g.subjects(RDF.type, MF.Manifest):

        for col in g.objects(m, MF.include):
            for i in g.items(col):
                for x in read_manifest(i):
                    yield x

        for col in g.objects(m, MF.entries):
            e: Node
            for e in g.items(col):

                approved = (
                    (e, DAWGT.approval, DAWGT.Approved) in g
                    or (e, DAWGT.approval, DAWGT.NotClassified) in g
                    or (e, RDFT.approval, RDFT.Approved) in g
                )

                # run proposed tests
                # approved |= (e, RDFT.approval, RDFT.Proposed) in g

                # run legacy tests with no approval set
                if legacy:
                    approved |= (e, DAWGT.approval, None) not in g and (
                        e,
                        RDFT.approval,
                        None,
                    ) not in g

                if not approved:
                    continue

                _type = g.value(e, RDF.type)

                # if _type in (MF.ServiceDescriptionTest, MF.ProtocolTest):
                #     continue  # skip tests we do not know

                name = g.value(e, MF.name)
                comment = g.value(e, RDFS.comment)
                data = None
                graphdata: Optional[GraphDataType] = None
                res: Optional[ResultType] = None
                syntax = True

                if _type in (MF.QueryEvaluationTest, MF.CSVResultFormatTest):
                    a = g.value(e, MF.action)
                    query = g.value(a, QT.query)
                    data = g.value(a, QT.data)
                    # NOTE: Casting to identifier because g.objects return Node
                    # but should probably return identifier instead.
                    graphdata = list(
                        cast(Iterable[Optional[Node]], g.objects(a, QT.graphData))
                    )
                    res = cast(Optional[ResultType], g.value(e, MF.result))
                elif _type in (MF.UpdateEvaluationTest, UT.UpdateEvaluationTest):
                    a = g.value(e, MF.action)
                    query = g.value(a, UT.request)
                    data = g.value(a, UT.data)
                    graphdata = cast(List[Tuple[Optional[Node], Optional[Node]]], [])
                    for gd in g.objects(a, UT.graphData):
                        graphdata.append(
                            (g.value(gd, UT.graph), g.value(gd, RDFS.label))
                        )

                    r = g.value(e, MF.result)
                    resdata: Optional[Node] = g.value(r, UT.data)
                    resgraphdata: List[Tuple[Optional[Node], Optional[Node]]] = []
                    for gd in g.objects(r, UT.graphData):
                        resgraphdata.append(
                            (g.value(gd, UT.graph), g.value(gd, RDFS.label))
                        )

                    res = resdata, resgraphdata

                elif _type in (
                    MF.NegativeSyntaxTest11,
                    MF.NegativeSyntaxTest,
                    MF.PositiveSyntaxTest11,
                    MF.PositiveSyntaxTest,
                ):
                    query = g.value(e, MF.action)
                    syntax = _type == MF.PositiveSyntaxTest11

                elif _type in (
                    MF.PositiveUpdateSyntaxTest11,
                    MF.NegativeUpdateSyntaxTest11,
                ):
                    query = g.value(e, MF.action)
                    syntax = _type == MF.PositiveUpdateSyntaxTest11

                elif _type in (
                    RDFT.TestNQuadsPositiveSyntax,
                    RDFT.TestNQuadsNegativeSyntax,
                    RDFT.TestTrigPositiveSyntax,
                    RDFT.TestTrigNegativeSyntax,
                    RDFT.TestNTriplesPositiveSyntax,
                    RDFT.TestNTriplesNegativeSyntax,
                    RDFT.TestTurtlePositiveSyntax,
                    RDFT.TestTurtleNegativeSyntax,
                    RDFT.TestTrixPositiveSyntax,
                    RDFT.TestTrixNegativeSyntax,
                ):
                    query = g.value(e, MF.action)
                    syntax = _type in (
                        RDFT.TestNQuadsPositiveSyntax,
                        RDFT.TestNTriplesPositiveSyntax,
                        RDFT.TestTrigPositiveSyntax,
                        RDFT.TestTurtlePositiveSyntax,
                        RDFT.TestTrixPositiveSyntax,
                    )

                elif _type in (
                    RDFT.TestTurtleEval,
                    RDFT.TestTurtleNegativeEval,
                    RDFT.TestTrigEval,
                    RDFT.TestTrigNegativeEval,
                    RDFT.TestTrixEval,
                ):
                    query = g.value(e, MF.action)
                    res = cast(Identifier, g.value(e, MF.result))
                    syntax = _type in (
                        RDFT.TestTurtleEval,
                        RDFT.TestTrigEval,
                        RDFT.TestTrixEval,
                    )

                else:
                    logger.debug(f"Don't know {_type}")
                    pass
                    print("I dont know DAWG Test Type %s" % _type)
                    continue

                assert isinstance(e, URIRef)

                yield e, _type, RDFTest(
                    e,
                    _str(name),
                    _str(comment),
                    _str(data),
                    graphdata,
                    _str(query),
                    res,
                    syntax,
                )
