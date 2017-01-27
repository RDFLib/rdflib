#
# code to simplify supporting older python versions
#

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
