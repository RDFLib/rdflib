#!/usr/bin/env python
import sys
import re

def setup_python3():
    # Taken from "distribute" setup.py
    from distutils.filelist import FileList
    from distutils import dir_util, file_util, util, log
    from os.path import join
  
    tmp_src = join("build", "src")
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
    kwargs['use_2to3'] = True
    kwargs['install_requires'] = ['isodate']
    kwargs['requires'] = ['isodate']
    kwargs['src_root'] = setup_python3()
else:
    try:
        from setuptools import setup
        kwargs['test_suite'] = "nose.collector"
        kwargs['install_requires'] = ['isodate']
        if sys.version_info[:2] > (2,4):
            kwargs['requires'] = ['isodate']
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
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 2.5",
                   "Programming Language :: Python :: 2.6",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3.2",
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
    implementations. The core rdflib includes store implementations for 
    in memory storage and persistent storage on top of the Berkeley DB. 

    The rdfextras project offers several additional stores as well as a 
    SPARQL engine for use with rdflib: http://code.google.com/p/rdfextras/

    If you have recently reported a bug marked as fixed, or have a craving for
    the very latest, you may want the development version instead:
    http://rdflib.googlecode.com/hg#egg=rdflib-dev
    """,
    download_url = "http://rdflib.googlecode.com/files/rdflib-%s.tar.gz" % version,
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

