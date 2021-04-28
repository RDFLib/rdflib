#!/usr/bin/env python

import os
import re
import sys
import importlib
from distutils.core import setup
from setuptools import find_packages
from setuptools.command.build_ext import build_ext
from distutils.command.clean import clean

# See https://gist.github.com/ctokheim/6c34dc1d672afca0676a for more details.
try:
    from Cython.Build import cythonize
    language_level = "3"
except ImportError:
    cythonize = None

# cython is not used unless specified.
if cythonize:
    if '--with-cython' in sys.argv:
        USE_CYTHON = True
        sys.argv.remove('--with-cython')
    elif '--cython' in sys.argv:
        USE_CYTHON = True
        sys.argv.remove('--cython')
    else:
        USE_CYTHON = False
else:
    print("cython is not installed")
    USE_CYTHON = False

if 'clean' in sys.argv:
    # Maybe Cython cannot work for some reason, and it would prevent cleaning up.
    USE_CYTHON = False

kwargs = {}
kwargs["install_requires"] = ["isodate", "pyparsing"]
kwargs["tests_require"] = [
    "html5lib",
    "networkx",
    "nose",
    "doctest-ignore-unicode",
]
kwargs["test_suite"] = "nose.collector"
kwargs["extras_require"] = {
    "html": ["html5lib"],
    "tests": kwargs["tests_require"],
    "docs": ["sphinx < 4", "sphinxcontrib-apidoc"],
}


def find_version(filename):
    _version_re = re.compile(r'__version__ = "(.*)"')
    for line in open(filename):
        version_match = _version_re.match(line)
        if version_match:
            return version_match.group(1)


version = find_version("rdflib/__init__.py")

packages = find_packages(exclude=("examples*", "test*"))

if os.environ.get("READTHEDOCS", None):
    # if building docs for RTD
    # install examples, to get docstrings
    packages.append("examples")

class BuildExtCommand(build_ext):
    """
    A custom command to build Cython extensions.

    This is needed otherwise setup does not build or rebuild C files from Python source files.
    FIXME: Not sure why the presence of this custom command which does not do much, fix the build issue.

    Usage example: python setup.py build_ext --inplace
    It ignores build-lib and put compiled extensions into the source directory alongside the pure Python modules.
    These libraries are prioritized before *.py files by Python, and loaded instead.
    """

    description = 'Build Cython extensions'

    def initialize_options(self):
        print("build_ext.initialize_options")
        build_ext.initialize_options(self)

    def finalize_options(self):
        """Post-process options."""
        print("build_ext.finalize_options")
        build_ext.finalize_options(self)

    def run(self):
        """Run command."""
        print("build_ext.run")
        build_ext.run(self)


def _cythonizable_source_files():
    """
    This returns the list of absolute paths of files to be cythonized.

    Only a subset of files are compiled.
    """
    survol_base_dir = os.path.join(os.path.dirname(__file__), "rdflib")
    src_files = []

    basenames_list = [
        "collection.py",
        "compare.py",
        "compat.py",
        "container.py",
        "events.py",
        "exceptions.py",
        "graph.py",
        "namespace.py",
        "parser.py",
        "paths.py",
        "plugin.py",
        "query.py",
        "resource.py",
        "serializer.py",
        "store.py",
        "term.py",
        "util.py",
        "void.py",
        "plugins/parsers/notation3.py",
        "plugins/stores/memory.py",
    ]

    for one_filename in basenames_list:
        one_path_name = os.path.join(survol_base_dir, one_filename)
        src_files.append(one_path_name)
    return src_files


class CleanCommand(clean):
    """
    Clean build including iniplace built extensions.
    """

    description = 'Clean build including in-place built extensions.'

    def _cleanup_libs(self):
        def remove_lib_file(lib_path):
            try:
                os.remove(lib_path)
                print("removed cythonized file:", lib_path)
            except:
                print("Cannot remove:", lib_path)

        src_files = _cythonizable_source_files()
        for one_file in src_files:
            assert one_file.endswith(".py")
            file_without_extension = os.path.splitext(one_file)[0]
            if sys.platform.startswith("lin") or sys.platform == "darwin":
                lib_path = file_without_extension + ".so"
                remove_lib_file(lib_path)
            else:
                # for example: ['.cp36-win_amd64.pyd', '.pyd']
                for one_suffix in importlib.machinery.EXTENSION_SUFFIXES:
                    # The file name might be something like: "collection.cp36-win_amd64.pyd"
                    lib_path = file_without_extension + one_suffix
                    remove_lib_file(lib_path)

    def run(self):
        """Run command."""
        print("removing in-place built libs")
        self._cleanup_libs()
        clean.run(self)

kwargs["cmdclass"]={
    'build_ext': BuildExtCommand,
    'clean': CleanCommand,
    }

if USE_CYTHON:
    kwargs["ext_modules"]=cythonize(
        _cythonizable_source_files(),
        build_dir="build_cythonize",
        # nthreads = 3,
        annotate=True,
        compiler_directives={'language_level': language_level})

    kwargs["options"]={
            'build': {'build_lib': 'build_build_ext'},
        }



setup(
    name="rdflib",
    version=version,
    description="RDFLib is a Python library for working with RDF, a "
    "simple yet powerful language for representing information.",
    author="Daniel 'eikeon' Krech",
    author_email="eikeon@eikeon.com",
    maintainer="RDFLib Team",
    maintainer_email="rdflib-dev@googlegroups.com",
    url="https://github.com/RDFLib/rdflib",
    license="BSD-3-Clause",
    platforms=["any"],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
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
    packages=packages,
    entry_points={
        "console_scripts": [
            "rdfpipe = rdflib.tools.rdfpipe:main",
            "csv2rdf = rdflib.tools.csv2rdf:main",
            "rdf2dot = rdflib.tools.rdf2dot:main",
            "rdfs2dot = rdflib.tools.rdfs2dot:main",
            "rdfgraphisomorphism = rdflib.tools.graphisomorphism:main",
        ],
    },
    **kwargs
)

