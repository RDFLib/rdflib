import functools
import pathlib
from urllib.parse import urlparse
from urllib.request import url2pathname

from .exceptions import ResolutionError, ResolutionForbiddenError
from .parser import FileInputSource, InputSource, URLInputSource
from .term import URIRef


def url_resolver(schemes):
    """Decorator for Resolver methods that resolve URLs into InputSources.

    :param schemes: A collection of URI schemes as str objects that this resolver
        provides.
    """

    def wrapper(func):
        func._url_resolver_schemes = schemes
        return func

    return wrapper


class Resolver:
    def resolve(self, file, format, input_source, location, trust=False):
        """Resolve a location (URL) into an InputSource.

        The method signature mirrors `rdflib.parser._create_input_source_from_location`,
        except for the `trust` parameter.

        :param trust: Whether to trust the location and resolve it regardless of policy.
        """
        # Fix for Windows problem https://github.com/RDFLib/rdflib/issues/145
        path = pathlib.Path(location)
        if path.exists():
            location = path.absolute().as_uri()

        base = pathlib.Path.cwd().as_uri()

        absolute_location = URIRef(location, base=base)

        scheme = urlparse(absolute_location).scheme
        resolver_func = self._get_resolver_for_scheme(scheme)
        if not resolver_func:
            raise ResolutionError(
                f"Resolution of URLs with scheme {scheme} is not supported."
            )

        if not trust and not self.is_resolution_allowed(scheme, absolute_location):
            raise ResolutionForbiddenError(absolute_location)

        input_source = resolver_func(absolute_location, format, scheme)

        auto_close = True
        # publicID = publicID or absolute_location  # Further to fix
        # for issue 130

        return absolute_location, auto_close, file, input_source

    @functools.lru_cache()
    def _get_url_resolvers(self):
        return {
            scheme: getattr(self, name)
            for name in dir(self)
            for scheme in getattr(getattr(self, name), "_url_resolver_schemes", ())
        }

    def _get_resolver_for_scheme(self, scheme: str):
        return self._get_url_resolvers().get(scheme)

    def is_resolution_allowed(self, scheme: str, location: str) -> bool:
        """Used to test whether a location should be resolved.

        Subclasses should override this method and defer up the superclass chain with
        if they don't have an opinion on whether a given location should be resolved."""
        return False

    @url_resolver(schemes={"file"})
    def resolve_file(self, url: URIRef, format: str, scheme: str) -> InputSource:
        filename = url2pathname(url.replace("file:///", "/"))
        file = open(filename, "rb")
        return FileInputSource(file)

    @url_resolver(schemes={"http", "https"})
    def resolve_http(self, url: URIRef, format: str, scheme: str) -> InputSource:
        return URLInputSource(url, format)


_default_resolver = Resolver()


def set_default_resolver(resolver: Resolver):
    global _default_resolver
    _default_resolver = resolver


def get_default_resolver() -> Resolver:
    return _default_resolver
