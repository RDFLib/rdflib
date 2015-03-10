#!/usr/bin/env python
import sys
import os
import re


def setup_python3():
    # Taken from "distribute" setup.py
    from distutils.filelist import FileList
    from distutils import dir_util, file_util, util, log
    from os.path import join, exists

    tmp_src = join("build", "src")
    # Not covered by "setup.py clean --all", so explicit deletion required.
    if exists(tmp_src):
        dir_util.remove_tree(tmp_src)
    log.set_verbosity(1)
    fl = FileList()
    for line in open("MANIFEST.in"):
        if not line.strip():
            continue
        fl.process_template_line(line)
    dir_util.create_tree(tmp_src, fl.files)
    outfiles_2to3 = []
    for f in fl.files:
        outf, copied = file_util.copy_file(f, join(tmp_src, f), update=1)
        if copied and outf.endswith(".py"):
            outfiles_2to3.append(outf)

    util.run_2to3(outfiles_2to3)

    # arrange setup to use the copy
    sys.path.insert(0, tmp_src)

    return tmp_src

kwargs = {}
if sys.version_info[0] >= 3:
    from setuptools import setup
    # kwargs['use_2to3'] = True  # is done in setup_python3 above already
    kwargs['install_requires'] = ['isodate', 'pyparsing']
    kwargs['tests_require'] = ['html5lib', 'networkx']
    kwargs['requires'] = [
        'isodate', 'pyparsing',
        'SPARQLWrapper']
    kwargs['src_root'] = setup_python3()
    assert setup
else:
    try:
        from setuptools import setup
        assert setup
        kwargs['test_suite'] = "nose.collector"
        kwargs['install_requires'] = [
            'isodate',
            'pyparsing', 'SPARQLWrapper']
        kwargs['tests_require'] = ['networkx']

        if sys.version_info[1]<7:  # Python 2.6
            kwargs['install_requires'].append('ordereddict')
        if sys.version_info[1]<6:  # Python 2.5
            kwargs['install_requires'].append('pyparsing<=1.5.7')
            kwargs['install_requires'].append('simplejson')
            kwargs['install_requires'].append('html5lib==0.95')
        else:
            kwargs['install_requires'].append('html5lib')

    except ImportError:
        from distutils.core import setup




# Find version. We have to do this because we can't import it in Python 3 until
# its been automatically converted in the setup process.
def find_version(filename):
    _version_re = re.compile(r'__version__ = "(.*)"')
    for line in open(filename):
        version_match = _version_re.match(line)
        if version_match:
            return version_match.group(1)

version = find_version('rdflib/__init__.py')

packages = ['rdflib',
            'rdflib/extras',
            'rdflib/plugins',
            'rdflib/plugins/parsers',
            'rdflib/plugins/parsers/pyRdfa',
            'rdflib/plugins/parsers/pyRdfa/transform',
            'rdflib/plugins/parsers/pyRdfa/extras',
            'rdflib/plugins/parsers/pyRdfa/host',
            'rdflib/plugins/parsers/pyRdfa/rdfs',
            'rdflib/plugins/parsers/pyMicrodata',
            'rdflib/plugins/serializers',
            'rdflib/plugins/sparql',
            'rdflib/plugins/sparql/results',
            'rdflib/plugins/stores',
            'rdflib/tools'
              ]

if os.environ.get('READTHEDOCS', None):
    # if building docs for RTD
    # install examples, to get docstrings
    packages.append("examples")

setup(
    name='rdflib',
    version=version,
    description="RDFLib is a Python library for working with RDF, a " + \
                "simple yet powerful language for representing information.",
    author="Daniel 'eikeon' Krech",
    author_email="eikeon@eikeon.com",
    maintainer="RDFLib Team",
    maintainer_email="rdflib-dev@google.com",
    url="https://github.com/RDFLib/rdflib",
    license="https://raw.github.com/RDFLib/rdflib/master/LICENSE",
    platforms=["any"],
    classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.3",
            "Programming Language :: Python :: 3.4",
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

   easy_install https://github.com/RDFLib/rdflib/tarball/master

Read the docs at:

   http://rdflib.readthedocs.org

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
