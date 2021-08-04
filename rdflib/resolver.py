import pathlib
from urllib.request import url2pathname

from .parser import URLInputSource
from .term import URIRef


class Resolver:
    def resolve(self, file, format, input_source, location):
        # Fix for Windows problem https://github.com/RDFLib/rdflib/issues/145
        path = pathlib.Path(location)
        if path.exists():
            location = path.absolute().as_uri()

        base = pathlib.Path.cwd().as_uri()

        absolute_location = URIRef(location, base=base)

        if absolute_location.startswith("file:///"):
            filename = url2pathname(absolute_location.replace("file:///", "/"))
            file = open(filename, "rb")
        else:
            input_source = URLInputSource(absolute_location, format)

        auto_close = True
        # publicID = publicID or absolute_location  # Further to fix
        # for issue 130

        return absolute_location, auto_close, file, input_source


_default_resolver = Resolver()


def set_default_resolver(resolver: Resolver):
    global _default_resolver
    _default_resolver = resolver


def get_default_resolver() -> Resolver:
    return _default_resolver
