import base64
import copy
import logging
from io import BytesIO
from typing import TYPE_CHECKING, Optional, Tuple
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from rdflib.query import Result
from rdflib.term import BNode

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    import typing_extensions as te


class SPARQLConnectorException(Exception):  # noqa: N818
    pass


# TODO: Pull in these from the result implementation plugins?
_response_mime_types = {
    "xml": "application/sparql-results+xml, application/rdf+xml",
    "json": "application/sparql-results+json",
    "csv": "text/csv",
    "tsv": "text/tab-separated-values",
    "application/rdf+xml": "application/rdf+xml",
}


class SPARQLConnector:
    """
    this class deals with nitty gritty details of talking to a SPARQL server
    """

    def __init__(
        self,
        query_endpoint: Optional[str] = None,
        update_endpoint: Optional[str] = None,
        returnFormat: str = "xml",  # noqa: N803
        method: "te.Literal['GET', 'POST', 'POST_FORM']" = "GET",
        auth: Optional[Tuple[str, str]] = None,
        **kwargs,
    ):
        """
        auth, if present, must be a tuple of (username, password) used for Basic Authentication

        Any additional keyword arguments will be passed to to the request, and can be used to setup timesouts etc.
        """
        self._method: str
        self.returnFormat = returnFormat
        self.query_endpoint = query_endpoint
        self.update_endpoint = update_endpoint
        self.kwargs = kwargs
        self.method = method
        if auth is not None:
            if type(auth) != tuple:
                raise SPARQLConnectorException("auth must be a tuple")
            if len(auth) != 2:
                raise SPARQLConnectorException("auth must be a tuple (user, password)")
            base64string = base64.b64encode(bytes("%s:%s" % auth, "ascii"))
            self.kwargs.setdefault("headers", {})
            self.kwargs["headers"].update(
                {"Authorization": "Basic %s" % base64string.decode("utf-8")}
            )

    @property
    def method(self) -> str:
        return self._method

    @method.setter
    def method(self, method: str) -> None:
        if method not in ("GET", "POST", "POST_FORM"):
            raise SPARQLConnectorException(
                'Method must be "GET", "POST", or "POST_FORM"'
            )

        self._method = method

    def query(
        self,
        query: str,
        default_graph: Optional[str] = None,
        named_graph: Optional[str] = None,
    ) -> "Result":
        if not self.query_endpoint:
            raise SPARQLConnectorException("Query endpoint not set!")

        params = {}
        # this test ensures we don't have a useless (BNode) default graph URI, which calls to Graph().query() will add
        if default_graph is not None and type(default_graph) != BNode:
            params["default-graph-uri"] = default_graph

        headers = {"Accept": _response_mime_types[self.returnFormat]}

        args = copy.deepcopy(self.kwargs)

        # merge params/headers dicts
        args.setdefault("params", {})

        args.setdefault("headers", {})
        args["headers"].update(headers)

        if self.method == "GET":
            params["query"] = query
            args["params"].update(params)
            qsa = "?" + urlencode(args["params"])
            try:
                res = urlopen(
                    Request(self.query_endpoint + qsa, headers=args["headers"])
                )
            except Exception as e:  # noqa: F841
                raise ValueError(
                    "You did something wrong formulating either the URI or your SPARQL query"
                )
        elif self.method == "POST":
            args["headers"].update({"Content-Type": "application/sparql-query"})
            args["params"].update(params)
            qsa = "?" + urlencode(args["params"])
            try:
                res = urlopen(
                    Request(
                        self.query_endpoint + qsa,
                        data=query.encode(),
                        headers=args["headers"],
                    )
                )
            except HTTPError as e:
                # type error: Incompatible return value type (got "Tuple[int, str, None]", expected "Result")
                return e.code, str(e), None  # type: ignore[return-value]
        elif self.method == "POST_FORM":
            params["query"] = query
            args["params"].update(params)
            try:
                res = urlopen(
                    Request(
                        self.query_endpoint,
                        data=urlencode(args["params"]).encode(),
                        headers=args["headers"],
                    )
                )
            except HTTPError as e:
                # type error: Incompatible return value type (got "Tuple[int, str, None]", expected "Result")
                return e.code, str(e), None  # type: ignore[return-value]
        else:
            raise SPARQLConnectorException("Unknown method %s" % self.method)
        return Result.parse(
            BytesIO(res.read()), content_type=res.headers["Content-Type"].split(";")[0]
        )

    def update(
        self,
        query: str,
        default_graph: Optional[str] = None,
        named_graph: Optional[str] = None,
    ) -> None:
        if not self.update_endpoint:
            raise SPARQLConnectorException("Query endpoint not set!")

        params = {}

        if default_graph is not None:
            params["using-graph-uri"] = default_graph

        if named_graph is not None:
            params["using-named-graph-uri"] = named_graph

        headers = {
            "Accept": _response_mime_types[self.returnFormat],
            "Content-Type": "application/sparql-update; charset=UTF-8",
        }

        args = copy.deepcopy(self.kwargs)  # other QSAs

        args.setdefault("params", {})
        args["params"].update(params)
        args.setdefault("headers", {})
        args["headers"].update(headers)

        qsa = "?" + urlencode(args["params"])
        res = urlopen(  # noqa: F841
            Request(
                self.update_endpoint + qsa, data=query.encode(), headers=args["headers"]
            )
        )


__all__ = ["SPARQLConnector", "SPARQLConnectorException"]
