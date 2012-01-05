#!/usr/bin/env python
import sys
import re

from distutils.core import setup

kwargs = {}
if sys.version_info[0] >= 3:
    from setuptools import setup
    kwargs['use_2to3'] = True
    kwargs['requires'] = ['bsddb3']

# Find version. We have to do this because we can't import it in Python 3 until
# its been automatically converted in the setup process.
def find_version(filename):
    _version_re = re.compile(r'__version__ = "(.*)"')
    for line in open(filename):
        version_match = _version_re.match(line)
        if version_match:
            return version_match.group(1)

version = find_version('rdflib/__init__.py')


setup(
    name = 'rdflib',
    version = version,
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
    Sleepycat and SQLObject.
    
    If you have recently reported a bug marked as fixed, or have a craving for
    the very latest, you may want the development version instead:
    http://rdflib.googlecode.com/hg#egg=rdflib-dev
    """,
    download_url = "http://rdflib.net/rdflib-%s.tar.gz" % version,

    packages = ['rdflib',
                'rdflib/plugins',
                'rdflib/plugins',
                'rdflib/plugins/parsers',
                'rdflib/plugins/parsers/rdfa',
                'rdflib/plugins/parsers/rdfa/transform',
                'rdflib/plugins/serializers',
                ],
    **kwargs
    )
