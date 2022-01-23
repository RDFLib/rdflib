.. _docs:

================================
Writing RDFLib Documentation
================================


These docs are generated with Sphinx.

Sphinx makes it very easy to pull in doc-strings from modules,
classes, methods, etc.  When writing doc-strings, special reST fields
can be used to annotate parameters, return-types, etc. This makes for
pretty API docs. More information about sphinx can be found `here <https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html>`_.

Building
--------

To build you must have the ``sphinx`` and some additional package installed.

The documentation's full set of requirements is listed in the ``sphinx-requirements.txt`` file within the :file:`docs/` directory.

To install the requirements for building documentation run:

.. code-block:: bash

  pip install -r docs/sphinx-requirements.txt


Once you have all the requirements installed you can run this command in the rdflib root directory:

.. code-block:: bash

  python setup.py build_sphinx

Docs will be generated in :file:`build/sphinx/html/` and API documentation, generated from doc-strings, will be placed in :file:`docs/apidocs/`.

There is also a `tox <https://tox.wiki/en/latest/>`_ environment for building documentation:

.. code-block:: bash

  tox -e docs

API Docs
--------

API Docs are automatically generated with ``sphinx-apidoc``:

.. code-block:: bash

   sphinx-apidoc -f -d 10 -o docs/apidocs/ rdflib examples

Note that ``rdflib.rst`` was manually tweaked so as to not include all
 imports in ``rdflib/__init__.py``.

Tables
------

The tables in ``plugin_*.rst`` were generated with ``plugintable.py``
