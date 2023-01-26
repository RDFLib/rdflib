.. _docs:

================================
Writing RDFLib Documentation
================================


These docs are generated with Sphinx.

Sphinx makes it very easy to pull in doc-strings from modules,
classes, methods, etc.  When writing doc-strings, special reST fields
can be used to annotate parameters, return-types, etc. This makes for
pretty API docs. See `here <https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#info-field-lists>`_
for the Shinx documentation about these fields.

Building
--------

To build the documentation you can use Sphinx from within the poetry environment. To do this, run the following commands:

.. code-block:: bash

    # Install poetry venv
    poetry install

    # Build the sphinx docs
    poetry run sphinx-build -b html -d docs/_build/doctrees docs docs/_build/html


Docs will be generated in :file:`docs/_build/html` and API documentation, 
generated from doc-strings, will be placed in :file:`docs/apidocs/`.

There is also a `tox <https://tox.wiki/en/latest/>`_ environment for building 
documentation:

.. code-block:: bash

  tox -e docs

API Docs
--------

API Docs are automatically generated with ``sphinx-apidoc``:

.. code-block:: bash

   poetry run sphinx-apidoc -f -d 10 -o docs/apidocs/ rdflib examples

Note that ``rdflib.rst`` was manually tweaked so as to not include all
 imports in ``rdflib/__init__.py``.

Tables
------

The tables in ``plugin_*.rst`` were generated with ``plugintable.py``
