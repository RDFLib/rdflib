#
# code to simplify supporting older python versions
#


import sys

from decimal import Decimal

if sys.version_info[:2] < (2, 7):

    # Pre-2.7 decimal and float did not compare correctly

    def numeric_greater(a, b):
        if isinstance(a, Decimal) and isinstance(b, float):
            return float(a) > b
        elif isinstance(a, float) and isinstance(b, Decimal):
            return a > float(b)
        else:
            return a > b

else:

    def numeric_greater(a, b):
        return a > b


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
