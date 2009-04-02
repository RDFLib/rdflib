from setuptools import setup, find_packages

# Install rdflib
from rdflib import __version__


setup(
    name = 'rdflib',
    version = __version__,
    description = "RDFLib is a Python library for working with RDF, a simple yet powerful language for representing information.",
    author = "Daniel 'eikeon' Krech",
    author_email = "eikeon@eikeon.com",
    maintainer = "Daniel 'eikeon' Krech",
    maintainer_email = "eikeon@eikeon.com",
    url = "http://rdflib.net/",
    license = "http://rdflib.net/latest/LICENSE",
    platforms = ["any"],
    classifiers = ["Programming Language :: Python",
                   "License :: OSI Approved :: BSD License",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   "Operating System :: OS Independent",
                   "Natural Language :: English",
                   ],
    long_description = \
    """RDFLib is a Python library for working with RDF, a simple yet powerful language for representing information.

    The library contains parsers and serializers for RDF/XML, N3,
    NTriples, Turtle, TriX and RDFa . The library presents a Graph
    interface which can be backed by any one of a number of Store
    implementations, including, Memory, MySQL, Redland, SQLite,
    Sleepycat, ZODB and SQLObject.
    
    If you have recently reported a bug marked as fixed, or have a craving for
    the very latest, you may want the development version instead:
    http://svn.rdflib.net/trunk#egg=rdflib-dev
    """,
    download_url = "http://rdflib.net/rdflib-%s.tar.gz" % __version__,

    packages = find_packages(exclude=["test"]),

    tests_require = ["nose>=0.10.4"],

    test_suite = 'nose.collector',

    entry_points = {        
        'console_scripts': [
            'rdfpipe = rdflib_tools.RDFPipe:main',
        ],
        'nose.plugins': [
            'EARLPlugin = rdflib_tools.EARLPlugin:EARLPlugin',
            ],
        },

    )

