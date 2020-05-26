try:
    import json
    assert json  # workaround for pyflakes issue #13
except ImportError:
    import simplejson as json

from ._compat import IS_PY3 as PY3

from os import sep
from os.path import normpath
if PY3:
    from urllib.parse import urljoin, urlsplit, urlunsplit
else:
    from urllib.parse import urljoin, urlsplit, urlunsplit

from rdflib.parser import create_input_source
if PY3:
    from io import StringIO


def source_to_json(source):
    # TODO: conneg for JSON (fix support in rdflib's URLInputSource!)
    source = create_input_source(source, format='json-ld')

    stream = source.getByteStream()
    try:
        if PY3:
            return json.load(StringIO(stream.read().decode('utf-8')))
        else:
            return json.load(stream)
    finally:
        stream.close()


VOCAB_DELIMS = ('#', '/', ':')

def split_iri(iri):
    for delim in VOCAB_DELIMS:
        at = iri.rfind(delim)
        if at > -1:
            return iri[:at+1], iri[at+1:]
    return iri, None

def norm_url(base, url):
    """
    >>> norm_url('http://example.org/', '/one')
    'http://example.org/one'
    >>> norm_url('http://example.org/', '/one#')
    'http://example.org/one#'
    >>> norm_url('http://example.org/one', 'two')
    'http://example.org/two'
    >>> norm_url('http://example.org/one/', 'two')
    'http://example.org/one/two'
    >>> norm_url('http://example.org/', 'http://example.net/one')
    'http://example.net/one'
    >>> norm_url('http://example.org/', 'http://example.org//one')
    'http://example.org//one'
    """
    parts = urlsplit(urljoin(base, url))
    path = normpath(parts[2])
    if sep != '/':
        path = '/'.join(path.split(sep))
    if parts[2].endswith('/') and not path.endswith('/'):
        path += '/'
    result = urlunsplit(parts[0:2] + (path,) + parts[3:])
    if url.endswith('#') and not result.endswith('#'):
        result += '#'
    return result

def context_from_urlinputsource(source):
    if source.content_type == 'application/json':
        # response_info was added to InputSource in rdflib 4.2
        try:
            links = source.response_info.getallmatchingheaders('Link')
        except AttributeError:
            return
        for link in links:
            if ' rel="http://www.w3.org/ns/json-ld#context"' in link:
                i, j = link.index('<'), link.index('>')
                if i > -1 and j > -1:
                    return urljoin(source.url, link[i+1:j])
