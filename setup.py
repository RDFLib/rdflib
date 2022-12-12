#!/usr/bin/env python

import codecs
import os
import re

from setuptools import find_packages, setup

kwargs = {}
kwargs["install_requires"] = [
    "isodate",
    "pyparsing",
    "setuptools",
    "importlib-metadata; python_version < '3.8.0'",
]
kwargs["tests_require"] = [
    "html5lib",
    "pytest",
    "pytest-cov",
]
kwargs["extras_require"] = {
    "html": ["html5lib"],
    "tests": kwargs["tests_require"],
    "docs": [
        "myst-parser",
        "sphinx < 6",
        "sphinxcontrib-apidoc",
        "sphinxcontrib-kroki",
        "sphinx-autodoc-typehints",
    ],
    "berkeleydb": ["berkeleydb"],
    "networkx": ["networkx"],
    "dev": [
        "black==22.12.0",
        "flake8",
        "flakeheaven >= 2.1.3; python_version >= '3.8.0'",
        "isort",
        "mypy",
        "pep8-naming",
        "types-setuptools",
    ],
}


def find_version(filename):
    _version_re = re.compile(r'__version__ = "(.*)"')
    for line in open(filename):
        version_match = _version_re.match(line)
        if version_match:
            return version_match.group(1)


def open_local(paths, mode="r", encoding="utf8"):
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), *paths)
    return codecs.open(path, mode, encoding)


with open_local(["README.md"], encoding="utf-8") as readme:
    long_description = readme.read()

version = find_version("rdflib/__init__.py")

packages = find_packages(exclude=("examples*", "test*"))

if os.environ.get("READTHEDOCS", None):
    # if building docs for RTD
    # install examples, to get docstrings
    packages.append("examples")

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
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
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
