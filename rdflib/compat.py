"""
Utility functions and objects to ease Python 2/3 compatibility,
and different versions of support libraries.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re
import codecs
import warnings

import six


# clean ElementTree import
try:
  from lxml import etree
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as etree
  except ImportError:
    try:
      # Python 2.5
      import xml.etree.ElementTree as etree
    except ImportError:
      try:
        # normal cElementTree install
        import cElementTree as etree
      except ImportError:
        try:
          # normal ElementTree install
          import elementtree.ElementTree as etree
        except ImportError:
          raise Exception("Failed to import ElementTree from any known place")

try:
    etree_register_namespace = etree.register_namespace
except AttributeError:

    import xml.etree.ElementTree as etreenative

    def etree_register_namespace(prefix, uri):
        etreenative._namespace_map[uri] = prefix

def cast_bytes(s, enc='utf-8'):
    if isinstance(s, six.text_type):
        return s.encode(enc)
    return s

if six.PY3:
    # Python 3:
    # ---------

    def ascii(stream):
        return codecs.getreader('ascii')(stream)

    def bopen(*args, **kwargs):
        return open(*args, mode = 'rb', **kwargs)

    long_type = int

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

    def sign(n):
        return cmp(n, 0)

r_unicodeEscape = re.compile(r'(\\u[0-9A-Fa-f]{4}|\\U[0-9A-Fa-f]{8})')

def _unicodeExpand(s):
    return r_unicodeEscape.sub(lambda m: six.unichr(int(m.group(0)[2:], 16)), s)

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
