.. _docs: Writing RDFLib Documentation

================================
Writing RDFLib Documentation
================================

The docs are generated with Sphinx. 

TODO: Docstrings ... 

To get N3 syntax highlighting do:

.. code-block:: bash

   pip install https://github.com/gniezen/n3pygments/archive/master.zip

API Docs are automatically generated with ``sphinx-apidoc``:

.. code-block:: bash

   sphinx-apidoc -f -d 10 -o docs/apidocs/ rdflib examples

(then ``rdflib.rst`` was tweaked manually to not include all convenience imports that are directly in the ``rdflib/__init__.py``)

The tables in ``plugin_*.rst`` were generated with ``plugintable.py`` 
