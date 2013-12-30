.. _docs:

================================
Writing RDFLib Documentation
================================


The docs are generated with Sphinx.

Sphinx makes it very easy to pull in doc-strings from modules,
classes, methods, etc.  When writing doc-strings, special reST fields
can be used to annotate parameters, return-types, etc. This make for
pretty API docs:

http://sphinx-doc.org/domains.html?highlight=param#info-field-lists

Building
--------

To build you must have the `sphinx` package installed:

.. code-block:: bash

  pip install sphinx

Then you can do:

.. code-block:: bash

  python setup.py build_sphinx

The docs will be generated in :file:`build/sphinx/html/`

Syntax highlighting
-------------------

To get N3 and SPARQL syntax highlighting do:

.. code-block:: bash

   pip install -e git+git://github.com/gjhiggins/sparql_pygments_lexer.git#egg=SPARQL_Pygments_Lexer
   pip install -e git+git://github.com/gjhiggins/n3_pygments_lexer.git#egg=Notation3_Pygments_Lexer

API Docs
--------

API Docs are automatically generated with ``sphinx-apidoc``:

.. code-block:: bash

   sphinx-apidoc -f -d 10 -o docs/apidocs/ rdflib examples

(then ``rdflib.rst`` was tweaked manually to not include all
convenience imports that are directly in the ``rdflib/__init__.py``)

Tables
------

The tables in ``plugin_*.rst`` were generated with ``plugintable.py``
