"""
Utility functions and objects to ease Python 2/3 compatibility,
and different versions of support libraries.
"""

import re
import codecs
import warnings
import typing as t

if t.TYPE_CHECKING:
    import xml.etree.ElementTree as etree
else:
    try:
        from lxml import etree
    except ImportError:
        import xml.etree.ElementTree as etree


try:
    etree_register_namespace = etree.register_namespace
except AttributeError:

    import xml.etree.ElementTree as etreenative

    def etree_register_namespace(prefix, uri):
        etreenative._namespace_map[uri] = prefix


def cast_bytes(s, enc="utf-8"):
    if isinstance(s, str):
        return s.encode(enc)
    return s


def ascii(stream):
    return codecs.getreader("ascii")(stream)


def bopen(*args, **kwargs):
    return open(*args, mode="rb", **kwargs)


long_type = int


def sign(n):
    if n < 0:
        return -1
    if n > 0:
        return 1
    return 0


r_unicodeEscape = re.compile(r"(\\u[0-9A-Fa-f]{4}|\\U[0-9A-Fa-f]{8})")


def _unicodeExpand(s):
    return r_unicodeEscape.sub(lambda m: chr(int(m.group(0)[2:], 16)), s)


narrow_build = False
try:
    chr(0x10FFFF)
except ValueError:
    narrow_build = True

if narrow_build:

    def _unicodeExpand(s):
        try:
            return r_unicodeEscape.sub(lambda m: chr(int(m.group(0)[2:], 16)), s)
        except ValueError:
            warnings.warn(
                "Encountered a unicode char > 0xFFFF in a narrow python build. "
                "Trying to degrade gracefully, but this can cause problems "
                "later when working with the string:\n%s" % s
            )
            return r_unicodeEscape.sub(
                lambda m: codecs.decode(m.group(0), "unicode_escape"), s
            )


def decodeStringEscape(s):
    r"""
    s is byte-string - replace \ escapes in string
    """

    s = s.replace("\\t", "\t")
    s = s.replace("\\n", "\n")
    s = s.replace("\\r", "\r")
    s = s.replace("\\b", "\b")
    s = s.replace("\\f", "\f")
    s = s.replace('\\"', '"')
    s = s.replace("\\'", "'")
    s = s.replace("\\\\", "\\")

    return s
    # return _unicodeExpand(s) # hmm - string escape doesn't do unicode escaping


def decodeUnicodeEscape(s):
    """
    s is a unicode string
    replace ``\\n`` and ``\\u00AC`` unicode escapes
    """
    if "\\" not in s:
        # Most of times, there are no backslashes in strings.
        # In the general case, it could use maketrans and translate.
        return s

    s = s.replace("\\t", "\t")
    s = s.replace("\\n", "\n")
    s = s.replace("\\r", "\r")
    s = s.replace("\\b", "\b")
    s = s.replace("\\f", "\f")
    s = s.replace('\\"', '"')
    s = s.replace("\\'", "'")
    s = s.replace("\\\\", "\\")

    s = _unicodeExpand(s)  # hmm - string escape doesn't do unicode escaping

    return s


# Migration to abc in Python 3.8
try:
    from collections.abc import Mapping, MutableMapping
except:
    from collections import Mapping, MutableMapping
