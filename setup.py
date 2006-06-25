# Install rdflib
from distutils.core import setup
from rdflib import __version__, __date__
from distutils.extension import Extension
from distutils.core import Command


class uninstall(Command):
    description = "uninstall everything by renaming rdflib to 'rdflib-%s' % int(time())"

    user_options = [ ]

    def initialize_options (self):
        pass

    def finalize_options (self):
        pass

    def run (self):
        "Look for and rename rdflib if one has already been installed."
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

setup(
    cmdclass={'uninstall': uninstall},
    name = 'rdflib',
    version = __version__,
    description = "RDF library containing an RDF triple store and RDF/XML parser/serializer",
    author = "Daniel 'eikeon' Krech",
    author_email = "eikeon@eikeon.com",
    maintainer = "Daniel 'eikeon' Krech",
    maintainer_email = "eikeon@eikeon.com",
    url = "http://rdflib.net/",
    license = "http://rdflib.net/latest/LICENSE",
    platforms = ["any"],
    classifiers = ["Programming Language :: Python"],
    long_description = "RDF library containing an RDF triple store and RDF/XML parser/serializer",
    download_url = "http://rdflib.net/%s/rdflib-%s.tar.gz" % (__date__, __version__),

    packages = ['rdflib',
                'rdflib.store',
                'rdflib.store.FOPLRelationalModel',
                'rdflib.sparql',
                'rdflib.sparql.bison',
                'rdflib.syntax',
                'rdflib.syntax.serializers',
                'rdflib.syntax.parsers',
                'rdflib.syntax.parsers.n3p'],    
     ext_modules = [
        Extension(
            name='rdflib.sparql.bison.SPARQLParserc',
            sources=['src/bison/SPARQLParser.c'],
            ),
        ]
                
    )

