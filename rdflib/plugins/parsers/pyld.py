import json
from io import BufferedReader, StringIO
from typing import Union

from pyld import jsonld

from rdflib import Graph
from rdflib.parser import BytesIOWrapper, InputSource, Parser, PythonInputSource


class JSONLDParser(Parser):
    def parse(self, source: InputSource, sink: Graph) -> None:
        # TODO: Do we need to set up a document loader?
        #       See https://github.com/digitalbazaar/pyld#document-loader
        #       Using a document loader requires either Requests or aiohttp

        mimetype = "application/n-quads"

        if isinstance(source, PythonInputSource):
            data = source.data
            quads = jsonld.to_rdf(data, options={"format": mimetype})
            sink.parse(data=quads, format=mimetype)
        else:
            stream: Union[
                StringIO, BytesIOWrapper, BufferedReader
            ] = source.getByteStream()

            if isinstance(stream, (StringIO, BytesIOWrapper, BufferedReader)):
                data = json.loads(stream.read())
            else:
                raise TypeError(f"Unhandled type for 'stream' as {type(stream)}.")

            try:
                quads = jsonld.to_rdf(data, options={"format": mimetype})
                sink.parse(data=quads, format=mimetype)
            finally:
                stream.close()
