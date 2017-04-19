# -*- coding: utf-8 -*-
"""

Hardcoded version of the current microdata->RDF registry.
There is also a local dictionary for prefix mapping for the registry items; these are the preferred prefixes
for those vocabularies, and are used to make the output nicer.

@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
"""

"""
$Id: registry.py,v 1.7 2014-12-17 08:52:43 ivan Exp $
$Date: 2014-12-17 08:52:43 $
"""

import sys

(py_v_major, py_v_minor, py_v_micro, py_v_final, py_v_serial) = sys.version_info

_registry = """
{
  "http://schema.org/": {
    "properties": {
      "additionalType": {"subPropertyOf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"}
    }
  },

  "http://microformats.org/profile/hcard": {}
}
"""

vocab_names = {
    "http://schema.org/": "schema",
    "http://microformats.org/profile/hcard#": "hcard"
}

registry = []
if py_v_major >= 3 or (py_v_major == 2 and py_v_minor >= 6):
    import json

    registry = json.loads(_registry)
else:
    import simplejson

    registry = simplejson.loads(_registry)
