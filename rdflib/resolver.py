import functools
import importlib
import os
import pathlib
import threading
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


DEFAULT_RESOLVABLE_URL_ALLOWLIST = {
    "https://w3c.github.io/json-ld-rc/context.jsonld",
}

_unspecified = object()


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


class DefaultResolver(Resolver):
    """A default resolver subclass that provides allow-listing of schemes and URLs.

    This resolver can be configured via environment variable or by instantiation
    parameter.
    """

    resolvable_url_schemes = os.environ.get("RDFLIB_RESOLVABLE_URL_SCHEMES", "").split()
    resolvable_url_allowlist = os.environ.get(
        "RDFLIB_RESOLVABLE_URL_ALLOWLIST",
        " ".join(DEFAULT_RESOLVABLE_URL_ALLOWLIST),
    ).split()

    def __init__(
        self,
        resolvable_url_schemes=_unspecified,
        resolvable_url_allowlist=_unspecified,
        **kwargs,
    ):
        if resolvable_url_schemes is not _unspecified:
            self.resolvable_url_schemes = resolvable_url_schemes
        if resolvable_url_allowlist is not _unspecified:
            self.resolvable_url_allowlist = resolvable_url_allowlist
        super().__init__(**kwargs)

    def is_resolution_allowed(self, scheme: str, location: str) -> bool:
        return (
            str(location) in self.resolvable_url_allowlist
            or scheme in self.resolvable_url_schemes
        )


class PermissiveResolver(Resolver):
    """Resolver subclass that allows all locations to be resolved.

    Provides backwards compatibility to the time when there were no resolution
    restrictions. Note that using this resolver with untrusted input will leave you
    vulnerable to exploits detailed in #1369.

    If you wish to use it despite that, use
    `set_default_resolver(PermissiveResolver())`.
    """

    def is_resolution_allowed(self, scheme: str, location: str) -> bool:
        return True


# This is set lazily, the first time that `get_default_resolver()` or
# `set_default_resolver` is called.
_default_resolver = None

_default_resolver_lock = threading.Lock()


def set_default_resolver(resolver: Resolver):
    global _default_resolver

    assert isinstance(resolver, Resolver), (
        "You must provide a Resolver instance. If you want to completely disable "
        "resolution, use `set_default_resolver(Resolver())`, which implements a "
        "blanket deny policy."
    )

    with _default_resolver_lock:
        _default_resolver = resolver


def get_default_resolver() -> Resolver:
    global _default_resolver

    if _default_resolver is None:
        with _default_resolver_lock:
            # Check again now we have the lock, in case there was a previous lock-owner
            # which set _default_resolver while we were waiting.
            if _default_resolver is None:
                try:
                    mod_name, cls_name = os.environ[
                        "RDFLIB_DEFAULT_RESOLVER_CLASS"
                    ].split(":")
                except KeyError:
                    _default_resolver = DefaultResolver()
                else:
                    mod = importlib.import_module(mod_name)
                    resolver = getattr(mod, cls_name)
                    assert isinstance(resolver, Resolver)
                    _default_resolver = resolver()

    return _default_resolver
