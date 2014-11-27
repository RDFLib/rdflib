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

    six_ed = [  # uncomment files which have already been transformed to use six
        # join(tmp_src, 'docs', 'conf.py'),
        # join(tmp_src, 'docs', 'plugintable.py'),
        join(tmp_src, 'examples', '__init__.py'),
        # join(tmp_src, 'examples', 'conjunctive_graphs.py'),
        # join(tmp_src, 'examples', 'custom_datatype.py'),
        # join(tmp_src, 'examples', 'custom_eval.py'),
        # join(tmp_src, 'examples', 'film.py'),
        # join(tmp_src, 'examples', 'foafpaths.py'),
        # join(tmp_src, 'examples', 'prepared_query.py'),
        # join(tmp_src, 'examples', 'rdfa_example.py'),
        # join(tmp_src, 'examples', 'resource.py'),
        # join(tmp_src, 'examples', 'simple_example.py'),
        # join(tmp_src, 'examples', 'sleepycat_example.py'),
        # join(tmp_src, 'examples', 'slice.py'),
        # join(tmp_src, 'examples', 'smushing.py'),
        # join(tmp_src, 'examples', 'sparql_query_example.py'),
        # join(tmp_src, 'examples', 'sparql_update_example.py'),
        # join(tmp_src, 'examples', 'sparqlstore_example.py'),
        # join(tmp_src, 'examples', 'swap_primer.py'),
        # join(tmp_src, 'examples', 'transitive.py'),
        # join(tmp_src, 'ez_setup.py'),
        join(tmp_src, 'rdflib', '__init__.py'),
        join(tmp_src, 'rdflib', 'collection.py'),
        # join(tmp_src, 'rdflib', 'compare.py'),
        join(tmp_src, 'rdflib', 'compat.py'),
        # join(tmp_src, 'rdflib', 'events.py'),
        join(tmp_src, 'rdflib', 'exceptions.py'),
        join(tmp_src, 'rdflib', 'extras', '__init__.py'),
        join(tmp_src, 'rdflib', 'extras', 'cmdlineutils.py'),
        # join(tmp_src, 'rdflib', 'extras', 'describer.py'),
        # join(tmp_src, 'rdflib', 'extras', 'infixowl.py'),
        # join(tmp_src, 'rdflib', 'graph.py'),
        # join(tmp_src, 'rdflib', 'namespace.py'),
        # join(tmp_src, 'rdflib', 'parser.py'),
        join(tmp_src, 'rdflib', 'paths.py'),
        # join(tmp_src, 'rdflib', 'plugin.py'),
        join(tmp_src, 'rdflib', 'plugins', '__init__.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'memory.py'),
        join(tmp_src, 'rdflib', 'plugins', 'parsers', '__init__.py'),
        join(tmp_src, 'rdflib', 'plugins', 'parsers', 'hturtle.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'parsers', 'notation3.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'parsers', 'nquads.py'),
        join(tmp_src, 'rdflib', 'plugins', 'parsers', 'nt.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'parsers', 'ntriples.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyMicrodata', '__init__.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyMicrodata', 'microdata.py'),
        join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyMicrodata', 'registry.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyMicrodata', 'utils.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', '__init__.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'embeddedRDF.py'),
        join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'extras', '__init__.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'extras', 'httpheader.py'),
        join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'host', '__init__.py'),
        join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'host', 'atom.py'),
        join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'host', 'html5.py'),
        join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'initialcontext.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'options.py'),
        join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'parse.py'),
        join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'property.py'),
        join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'rdfs', '__init__.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'rdfs', 'cache.py'),
        join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'rdfs', 'process.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'state.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'termorcurie.py'),
        join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'transform', '__init__.py'),
        join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'transform', 'DublinCore.py'),
        join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'transform', 'lite.py'),
        join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'transform', 'metaname.py'),
        join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'transform', 'OpenID.py'),
        join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'transform', 'prototype.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'parsers', 'pyRdfa', 'utils.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'parsers', 'rdfxml.py'),
        join(tmp_src, 'rdflib', 'plugins', 'parsers', 'structureddata.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'parsers', 'trig.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'parsers', 'trix.py'),
        join(tmp_src, 'rdflib', 'plugins', 'serializers', '__init__.py'),
        join(tmp_src, 'rdflib', 'plugins', 'serializers', 'n3.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'serializers', 'nquads.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'serializers', 'nt.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'serializers', 'rdfxml.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'serializers', 'trig.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'serializers', 'trix.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'serializers', 'turtle.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'serializers', 'xmlwriter.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'sleepycat.py'),
        join(tmp_src, 'rdflib', 'plugins', 'sparql', '__init__.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'sparql', 'aggregates.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'sparql', 'algebra.py'),
        join(tmp_src, 'rdflib', 'plugins', 'sparql', 'compat.py'),
        join(tmp_src, 'rdflib', 'plugins', 'sparql', 'datatypes.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'sparql', 'evaluate.py'),
        join(tmp_src, 'rdflib', 'plugins', 'sparql', 'evalutils.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'sparql', 'operators.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'sparql', 'parser.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'sparql', 'parserutils.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'sparql', 'processor.py'),
        join(tmp_src, 'rdflib', 'plugins', 'sparql', 'results', '__init__.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'sparql', 'results', 'csvresults.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'sparql', 'results', 'jsonlayer.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'sparql', 'results', 'jsonresults.py'),
        join(tmp_src, 'rdflib', 'plugins', 'sparql', 'results', 'rdfresults.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'sparql', 'results', 'tsvresults.py'),
        join(tmp_src, 'rdflib', 'plugins', 'sparql', 'results', 'txtresults.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'sparql', 'results', 'xmlresults.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'sparql', 'sparql.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'sparql', 'update.py'),
        join(tmp_src, 'rdflib', 'plugins', 'stores', '__init__.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'stores', 'auditable.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'stores', 'concurrent.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'stores', 'regexmatching.py'),
        # join(tmp_src, 'rdflib', 'plugins', 'stores', 'sparqlstore.py'),
        join(tmp_src, 'rdflib', 'py3compat.py'),
        # join(tmp_src, 'rdflib', 'query.py'),
        # join(tmp_src, 'rdflib', 'resource.py'),
        join(tmp_src, 'rdflib', 'serializer.py'),
        # join(tmp_src, 'rdflib', 'store.py'),
        join(tmp_src, 'rdflib', 'term.py'),
        join(tmp_src, 'rdflib', 'tools', '__init__.py'),
        # join(tmp_src, 'rdflib', 'tools', 'csv2rdf.py'),
        # join(tmp_src, 'rdflib', 'tools', 'graphisomorphism.py'),
        # join(tmp_src, 'rdflib', 'tools', 'rdf2dot.py'),
        # join(tmp_src, 'rdflib', 'tools', 'rdfpipe.py'),
        # join(tmp_src, 'rdflib', 'tools', 'rdfs2dot.py'),
        # join(tmp_src, 'rdflib', 'util.py'),
        join(tmp_src, 'rdflib', 'void.py'),
        # join(tmp_src, 'run_tests.py'),
        join(tmp_src, 'test', '__init__.py'),
        join(tmp_src, 'test', 'earl.py'),
        # join(tmp_src, 'test', 'manifest.py'),
        join(tmp_src, 'test', 'rdfa', '__init__.py'),
        # join(tmp_src, 'test', 'rdfa', 'run_w3c_rdfa_testsuite.py'),
        # join(tmp_src, 'test', 'rdfa', 'test_non_xhtml.py'),
        # join(tmp_src, 'test', 'store_performance.py'),
        # join(tmp_src, 'test', 'test_aggregate_graphs.py'),
        # join(tmp_src, 'test', 'test_bnode_ncname.py'),
        # join(tmp_src, 'test', 'test_comparison.py'),
        # join(tmp_src, 'test', 'test_conjunctive_graph.py'),
        # join(tmp_src, 'test', 'test_conneg.py'),
        # join(tmp_src, 'test', 'test_conventions.py'),
        join(tmp_src, 'test', 'test_core_sparqlstore.py'),
        # join(tmp_src, 'test', 'test_dataset.py'),
        # join(tmp_src, 'test', 'test_datetime.py'),
        # join(tmp_src, 'test', 'test_dawg.py'),
        # join(tmp_src, 'test', 'test_diff.py'),
        # join(tmp_src, 'test', 'test_empty_xml_base.py'),
        join(tmp_src, 'test', 'test_evaluate_bind.py'),
        # join(tmp_src, 'test', 'test_events.py'),
        # join(tmp_src, 'test', 'test_expressions.py'),
        join(tmp_src, 'test', 'test_finalnewline.py'),
        # join(tmp_src, 'test', 'test_graph.py'),
        # join(tmp_src, 'test', 'test_graph_context.py'),
        join(tmp_src, 'test', 'test_graph_formula.py'),
        # join(tmp_src, 'test', 'test_graph_items.py'),
        join(tmp_src, 'test', 'test_initbindings.py'),
        # join(tmp_src, 'test', 'test_iomemory.py'),
        # join(tmp_src, 'test', 'test_issue084.py'),
        join(tmp_src, 'test', 'test_issue130.py'),
        # join(tmp_src, 'test', 'test_issue154.py'),
        join(tmp_src, 'test', 'test_issue160.py'),
        # join(tmp_src, 'test', 'test_issue161.py'),
        join(tmp_src, 'test', 'test_issue184.py'),
        # join(tmp_src, 'test', 'test_issue190.py'),
        join(tmp_src, 'test', 'test_issue200.py'),
        join(tmp_src, 'test', 'test_issue209.py'),
        join(tmp_src, 'test', 'test_issue247.py'),
        # join(tmp_src, 'test', 'test_issue248.py'),
        # join(tmp_src, 'test', 'test_issue363.py'),
        # join(tmp_src, 'test', 'test_issue375.py'),
        # join(tmp_src, 'test', 'test_issue379.py'),
        join(tmp_src, 'test', 'test_issue_git_200.py'),
        join(tmp_src, 'test', 'test_issue_git_336.py'),
        # join(tmp_src, 'test', 'test_literal.py'),
        # join(tmp_src, 'test', 'test_memory_store.py'),
        # join(tmp_src, 'test', 'test_n3.py'),
        # join(tmp_src, 'test', 'test_n3_suite.py'),
        join(tmp_src, 'test', 'test_namespace.py'),
        # join(tmp_src, 'test', 'test_nodepickler.py'),
        # join(tmp_src, 'test', 'test_nquads.py'),
        # join(tmp_src, 'test', 'test_nquads_w3c.py'),
        # join(tmp_src, 'test', 'test_nt_misc.py'),
        join(tmp_src, 'test', 'test_nt_suite.py'),
        # join(tmp_src, 'test', 'test_nt_w3c.py'),
        # join(tmp_src, 'test', 'test_parser.py'),
        # join(tmp_src, 'test', 'test_parser_helpers.py'),
        # join(tmp_src, 'test', 'test_parser_structure.py'),
        # join(tmp_src, 'test', 'test_path_div_future.py'),
        # join(tmp_src, 'test', 'test_prefixTypes.py'),
        # join(tmp_src, 'test', 'test_preflabel.py'),
        # join(tmp_src, 'test', 'test_prettyxml.py'),
        # join(tmp_src, 'test', 'test_rdf_lists.py'),
        # join(tmp_src, 'test', 'test_rdfxml.py'),
        # join(tmp_src, 'test', 'test_roundtrip.py'),
        # join(tmp_src, 'test', 'test_rules.py'),
        # join(tmp_src, 'test', 'test_seq.py'),
        # join(tmp_src, 'test', 'test_serializexml.py'),
        # join(tmp_src, 'test', 'test_slice.py'),
        # join(tmp_src, 'test', 'test_sparql.py'),
        # join(tmp_src, 'test', 'test_sparqlstore.py'),
        # join(tmp_src, 'test', 'test_sparqlupdatestore.py'),
        join(tmp_src, 'test', 'test_swap_n3.py'),
        # join(tmp_src, 'test', 'test_term.py'),
        # join(tmp_src, 'test', 'test_trig.py'),
        # join(tmp_src, 'test', 'test_trig_w3c.py'),
        # join(tmp_src, 'test', 'test_trix_parse.py'),
        # join(tmp_src, 'test', 'test_trix_serialize.py'),
        # join(tmp_src, 'test', 'test_tsvresults.py'),
        # join(tmp_src, 'test', 'test_turtle_serialize.py'),
        # join(tmp_src, 'test', 'test_turtle_w3c.py'),
        # join(tmp_src, 'test', 'test_util.py'),
        join(tmp_src, 'test', 'test_xmlliterals.py'),
        # join(tmp_src, 'test', 'testutils.py'),
        join(tmp_src, 'test', 'triple_store.py'),
        join(tmp_src, 'test', 'type_check.py'),
    ]
    for fn in six_ed:
        outfiles_2to3.remove(fn)
    for fn in outfiles_2to3:
        print('running 2to3 on', fn)

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
        'six', 'isodate', 'pyparsing',
        'SPARQLWrapper']
    kwargs['src_root'] = setup_python3()
    assert setup
else:
    try:
        from setuptools import setup
        assert setup
        kwargs['test_suite'] = "nose.collector"
        kwargs['install_requires'] = [
            'six', 'isodate',
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
