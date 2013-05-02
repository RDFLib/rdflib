"""
RDF- and RDFlib-centric file and URL path utilities.
"""

from os.path import splitext


def uri_leaf(uri):
    """
    Get the "leaf" - fragment id or last segment - of a URI. Useful e.g. for
    getting a term from a "namespace like" URI. Examples:

        >>> uri_leaf('http://example.org/ns/things#item')
        'item'
        >>> uri_leaf('http://example.org/ns/stuff/item')
        'item'
        >>> uri_leaf('http://example.org/ns/stuff/')
        >>>
        >>> uri_leaf('urn:example.org:stuff')
        'stuff'
        >>> uri_leaf('example.org')
        >>>
    """
    for char in ('#', '/', ':'):
        if uri.endswith(char):
            break
        # base, sep, leaf = uri.rpartition(char)
        if char in uri:
            sep = char
            leaf = uri.rsplit(char)[-1]
        else:
            sep = ''
            leaf = uri
        if sep and leaf:
            return leaf


SUFFIX_FORMAT_MAP = {
    'rdf': 'xml',
    'rdfs': 'xml',
    'owl': 'xml',
    'n3': 'n3',
    'ttl': 'n3',
    'nt': 'nt',
    'trix': 'trix',
    'xhtml': 'rdfa',
    'html': 'rdfa',
    'svg': 'rdfa',
    'nq': 'nquads',
    'trig': 'trig'
}


def guess_format(fpath, fmap=None):
    """
    Guess RDF serialization based on file suffix. Uses
    ``SUFFIX_FORMAT_MAP`` unless ``fmap`` is provided. Examples:

        >>> guess_format('path/to/file.rdf')
        'xml'
        >>> guess_format('path/to/file.owl')
        'xml'
        >>> guess_format('path/to/file.ttl')
        'n3'
        >>> guess_format('path/to/file.xhtml')
        'rdfa'
        >>> guess_format('path/to/file.svg')
        'rdfa'
        >>> guess_format('path/to/file.xhtml', {'xhtml': 'grddl'})
        'grddl'

    This also works with just the suffixes, with or without leading dot, and
    regardless of letter case::

        >>> guess_format('.rdf')
        'xml'
        >>> guess_format('rdf')
        'xml'
        >>> guess_format('RDF')
        'xml'
    """
    fmap = fmap or SUFFIX_FORMAT_MAP
    return fmap.get(_get_ext(fpath)) or fmap.get(fpath.lower())


def _get_ext(fpath, lower=True):
    """
    Gets the file extension from a file(path); stripped of leading '.' and in
    lower case. Examples:

        >>> _get_ext("path/to/file.txt")
        'txt'
        >>> _get_ext("OTHER.PDF")
        'pdf'
        >>> _get_ext("noext")
        ''
        >>> _get_ext(".rdf")
        'rdf'
    """
    ext = splitext(fpath)[-1]
    if ext == '' and fpath.startswith("."):
        ext = fpath
    if lower:
        ext = ext.lower()
    if ext.startswith('.'):
        ext = ext[1:]
    return ext
