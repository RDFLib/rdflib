# Look for and rename rdflib if one has already been installed.
from distutils.sysconfig import get_python_lib
from os import rename
from os.path import join, exists
from time import time

lib_dir = get_python_lib()
rdflib_dir = join(lib_dir, "rdflib")
if exists(rdflib_dir):
    backup = "%s-%s" % (rdflib_dir, int(time()))    
    print "Renaming previously installed rdflib to: \n  %s" % backup
    rename(rdflib_dir, backup)


# Install rdflib
from distutils.core import setup
from rdflib import __version__

setup(
    name = 'RDFLib',
    version = __version__,
    description = "RDF library containing an RDF triple store and RDF/XML parser/serializer",
    author = "Daniel 'eikeon' Krech",
    author_email = "eikeon@eikeon.com",
    maintainer = "Daniel 'eikeon' Krech",
    maintainer_email = "eikeon@eikeon.com",
    url = "http://rdflib.net/",

    packages = ['rdflib',
                'rdflib.backends',                
                'rdflib.syntax',
                'rdflib.syntax.serializers',
                'rdflib.syntax.parsers'],    
    )


