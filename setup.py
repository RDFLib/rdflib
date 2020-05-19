#!/usr/bin/env python

import os
import re
from setuptools import setup, find_packages

kwargs = {}
kwargs['install_requires'] = [ 'six', 'isodate', 'pyparsing']
kwargs['tests_require'] = ['html5lib', 'networkx', 'nose', 'doctest-ignore-unicode', 'requests']
kwargs['test_suite'] = "nose.collector"
kwargs['extras_require'] = {
    'html': ['html5lib'],
    'sparql': ['requests'],
    'tests': kwargs['tests_require'],
    'docs': ['sphinx < 4', 'sphinxcontrib-apidoc']
    }

def find_version(filename):
    _version_re = re.compile(r'__version__ = "(.*)"')
    for line in open(filename):
        version_match = _version_re.match(line)
        if version_match:
            return version_match.group(1)

version = find_version('rdflib/__init__.py')

packages = find_packages(exclude=('examples*', 'test*'))

if os.environ.get('READTHEDOCS', None):
    # if building docs for RTD
    # install examples, to get docstrings
    packages.append("examples")

setup(
    name='rdflib',
    version=version,
    description="RDFLib is a Python library for working with RDF, a "
                "simple yet powerful language for representing information.",
    author="Daniel 'eikeon' Krech",
    author_email="eikeon@eikeon.com",
    maintainer="RDFLib Team",
    maintainer_email="rdflib-dev@google.com",
    url="https://github.com/RDFLib/rdflib",
    license="BSD-3-Clause",
    platforms=["any"],
    python_requires='>=3.5',
    classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "License :: OSI Approved :: BSD License",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Operating System :: OS Independent",
            "Natural Language :: English",
                 ],
    long_description="""\
RDFLib is a Python library for working with
RDF, a simple yet powerful language for representing information.

The library contains parsers and serializers for RDF/XML, N3,
NTriples, Turtle, TriX, RDFa and Microdata . The library presents
a Graph interface which can be backed by any one of a number of
Store implementations. The core rdflib includes store
implementations for in memory storage, persistent storage on top
of the Berkeley DB, and a wrapper for remote SPARQL endpoints.

A SPARQL 1.1 engine is also included.

If you have recently reported a bug marked as fixed, or have a craving for
the very latest, you may want the development version instead:

   pip install git+https://github.com/rdflib/rdflib


Read the docs at:

   http://rdflib.readthedocs.io

    """,
    packages = packages,
    entry_points = {
        'console_scripts': [
            'rdfpipe = rdflib.tools.rdfpipe:main',
            'csv2rdf = rdflib.tools.csv2rdf:main',
            'rdf2dot = rdflib.tools.rdf2dot:main',
            'rdfs2dot = rdflib.tools.rdfs2dot:main',
            'rdfgraphisomorphism = rdflib.tools.graphisomorphism:main',
            ],
        },

    **kwargs
    )
