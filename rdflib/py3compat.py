"""
Utility functions and objects to ease Python 3 compatibility.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re
import codecs
import warnings

import six

from functools import wraps

def cast_bytes(s, enc='utf-8'):
    if isinstance(s, six.text_type):
        return s.encode(enc)
    return s

def _modify_str_or_docstring(str_change_func):
    @wraps(str_change_func)
    def wrapper(func_or_str):
        if isinstance(func_or_str, str):
            func = None
            doc = func_or_str
        else:
            func = func_or_str
            doc = func.__doc__

        doc = str_change_func(doc)

        if func:
            func.__doc__ = doc
            return func
        return doc
    return wrapper


if six.PY3:
    # Python 3:
    # ---------

    def ascii(stream):
        return codecs.getreader('ascii')(stream)

    def bopen(*args, **kwargs):
        return open(*args, mode = 'rb', **kwargs)

    long_type = int

    # Abstract u'abc' syntax:
    @_modify_str_or_docstring
    def format_doctest_out(s):
        """Python 2 version
        "%(u)s'abc'" --> "'abc'"
        "%(b)s'abc'" --> "b'abc'"
        "55%(L)s"    --> "55"
        "unicode(x)" --> "str(x)"

        Accepts a string or a function, so it can be used as a decorator."""
        # s may be None if processed by Py2exe
        if s is None:
            return ''
        return s % {'u': '', 'b': 'b', 'L': '', 'unicode': 'str'}

    def sign(n):
        if n < 0:
            return -1
        if n > 0:
            return 1
        return 0

else:
    # Python 2
    # --------

    def ascii(stream):
        return stream

    bopen = open

    long_type = long

    # Abstract u'abc' syntax:
    @_modify_str_or_docstring
    def format_doctest_out(s):
        """Python 2 version
        "%(u)s'abc'" --> "u'abc'"
        "%(b)s'abc'" --> "'abc'"
        "55%(L)s"    --> "55L"

        Accepts a string or a function, so it can be used as a decorator."""
        # s may be None if processed by Py2exe
        if s is None:
            return ''
        return s % {'u': 'u', 'b': '', 'L': 'L', 'unicode': 'unicode'}

    def sign(n):
        return cmp(n, 0)

r_unicodeEscape = re.compile(r'(\\u[0-9A-Fa-f]{4}|\\U[0-9A-Fa-f]{8})')

def _unicodeExpand(s):
    return r_unicodeEscape.sub(lambda m: unichr(int(m.group(0)[2:], 16)), s)

narrow_build = False
try:
    six.unichr(0x10FFFF)
except ValueError:
    narrow_build = True

if narrow_build:
    def _unicodeExpand(s):
        try:
            return r_unicodeEscape.sub(
                lambda m: six.unichr(int(m.group(0)[2:], 16)), s)
        except ValueError:
            warnings.warn(
                'Encountered a unicode char > 0xFFFF in a narrow python build. '
                'Trying to degrade gracefully, but this can cause problems '
                'later when working with the string:\n%s' % s)
            return r_unicodeEscape.sub(
                lambda m: codecs.decode(m.group(0), 'unicode_escape'), s)


def decodeStringEscape(s):

    """
    s is byte-string - replace \ escapes in string
    """

    if not six.PY3:
        s = s.decode('string-escape')
    else:
        s = s.replace('\\t', '\t')
        s = s.replace('\\n', '\n')
        s = s.replace('\\r', '\r')
        s = s.replace('\\b', '\b')
        s = s.replace('\\f', '\f')
        s = s.replace('\\"', '"')
        s = s.replace("\\'", "'")
        s = s.replace('\\\\', '\\')

    return s
    #return _unicodeExpand(s) # hmm - string escape doesn't do unicode escaping

def decodeUnicodeEscape(s):
    """
    s is a unicode string
    replace \n and \\u00AC unicode escapes
    """
    if not six.PY3:
        s = s.encode('utf-8').decode('string-escape')
        s = _unicodeExpand(s)
    else:
        s = s.replace('\\t', '\t')
        s = s.replace('\\n', '\n')
        s = s.replace('\\r', '\r')
        s = s.replace('\\b', '\b')
        s = s.replace('\\f', '\f')
        s = s.replace('\\"', '"')
        s = s.replace("\\'", "'")
        s = s.replace('\\\\', '\\')

        s = _unicodeExpand(s) # hmm - string escape doesn't do unicode escaping

    return s
