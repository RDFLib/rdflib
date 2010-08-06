.. _apidocs: epydoc-generated API docs

=================
API documentation
=================

Epydoc-generated `API documentation`__ for the rdflib package.

.. __: ./apidocs/index.html

General notes
-------------

Sphinx-epydoc integration is achievable manually, by finessing epydoc and sphinx:

.. code-block :: bash

    $ mkdir -p doc/_build/html/api
    $ epydoc -o doc/_build/html/api --docformat reStructuredText --html rdflib

Then generate documentation with Sphinx:

.. code-block :: bash

    $ sphinx-build doc doc/_build/html
    
Sphinx will generate the narrative documentation HTML docs alongside the existing epydoc-generated HTML docs. 

Generating a local copy of the API docs
---------------------------------------

To generate a local copy of the API documentation, install the `epydoc`_ package and use the following command-line instruction to create a set of rdflib API docs in the directory ``./apidocs`` (relative to cwd):

.. _epydoc: http://epydoc.sourceforge.net

.. code-block :: bash

    $ epydoc -o apidocs --docformat reStructuredText --html rdflib

|today|
