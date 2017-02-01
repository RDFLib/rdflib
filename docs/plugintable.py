"""
Crappy utility for generating Sphinx tables
for rdflib plugins
"""

import sys

from rdflib.plugin import _plugins

cls = sys.argv[1]

p = {}

for (name, kind), plugin in _plugins.items():
    if "/" in name: continue # skip duplicate entries for mimetypes
    if cls == kind.__name__:
        p[name]="%s.%s"%(plugin.module_path, plugin.class_name)

l1=max(len(x) for x in p)
l2=max(10+len(x) for x in p.values())

def hr():
    print("="*l1,"="*l2)

hr()
print("%-*s"%(l1,"Name"), "%-*s"%(l2, "Class"))
hr()

for n in sorted(p):
    print("%-*s"%(l1,n), ":class:`~%s`"%p[n])
hr()
print()
