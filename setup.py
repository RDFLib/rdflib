#!/usr/bin/env python

import os
import re
import sys
import codecs
import importlib
from setuptools import setup
from setuptools import find_packages
from setuptools.command.build_ext import build_ext
from setuptools._distutils.command.clean import clean

# See https://gist.github.com/ctokheim/6c34dc1d672afca0676a for more details.
try:
    from Cython.Build import cythonize
    language_level = "3"
except ImportError:
    cythonize = None

# cython is not used unless specified.
if '--with-cython' in sys.argv:
    sys.argv.remove('--with-cython')
    if cythonize:
        USE_CYTHON = True
    else:
        raise Exception("Please install cython first. (https://cython.org/)")
else:
    USE_CYTHON = False

if 'clean' in sys.argv:
    # Maybe Cython cannot work for some reason, and it would prevent cleaning up.
    USE_CYTHON = False

kwargs = {}
kwargs["install_requires"] = ["isodate", "pyparsing", "setuptools"]
kwargs["tests_require"] = [
    "html5lib",
    "networkx",
    "nose==1.3.7",
    "nose-timer",
    "coverage",
    "black==21.7b0",
    "flake8",
    "doctest-ignore-unicode==0.1.2",
]
kwargs["test_suite"] = "nose.collector"
kwargs["extras_require"] = {
    "html": ["html5lib"],
    "tests": kwargs["tests_require"],
    "docs": ["sphinx < 5", "sphinxcontrib-apidoc"],
}


def find_version(filename):
    _version_re = re.compile(r'__version__ = "(.*)"')
    for line in open(filename):
        version_match = _version_re.match(line)
        if version_match:
            return version_match.group(1)


def open_local(paths, mode='r', encoding='utf8'):
    path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        *paths
    )
    return codecs.open(path, mode, encoding)


with open_local(['README.md'], encoding='utf-8') as readme:
    long_description = readme.read()

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
    Clean build including inplace built extensions.
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
    license="bsd-3-clause",
    platforms=["any"],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
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
    **kwargs,
)
