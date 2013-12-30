.. developers:

RDFLib developers guide
=======================

Introduction
------------

This document describes the process and conventions to follow when
developing RDFLib code.

Please be as Pythonic as possible (:pep:`8`).

Code will occasionally be auto-formatted using ``autopep8`` - you can also do this yourself.

Any new functionality being added to RDFLib should have doc tests and
unit tests. Tests should be added for any functionality being changed
that currently does not have any doc tests or unit tests. And all the
tests should be run before committing changes to make sure the changes
did not break anything.

If you add a new cool feature, consider also adding an example in ``./examples``

Running tests
-------------
Run tests with `nose <https://nose.readthedocs.org/en/latest/>`_:

.. code-block: bash

   $ easy_install nose
   $ python run_tests.py
   $ python run_tests.py --attr known_issue # override attr in setup.cfg to run only tests marked with "known_issue"
   $ python run_tests.py --attr \!known_issue # runs all tests (including "slow" and "non_core") except those with known issues
   $ python run_tests.py --attr slow,!known_issue  # comma separate if you want to specify more than one attr
   $ python run_tests.py --attr known_issue=None # use =None instead of \! if you keep forgetting to escape the ! in shell commands ;)

Specific tests can either be run by module name or file name. For example::

  $ python run_tests.py --tests rdflib.graph
  $ python run_tests.py --tests test/test_graph.py

Writing documentation
---------------------

We use sphinx for generating HTML docs, see :ref:`docs`

Continous Integration
---------------------

We used Travis for CI, see:

  https://travis-ci.org/RDFLib/rdflib

If you make a pull-request to RDFLib on GitHub, travis will automatically test you code.

Compatibility
-------------

RDFLib>=3.X tries to be compatible with python versions 2.5 - 3

Some of the limitations we've come across:

 * Python 2.5/2.6 has no abstract base classes from collections, such ``MutableMap``, etc.
 * 2.5/2.6 No skipping tests using :mod:`unittest`, i.e. ``TestCase.skipTest`` and decorators are missing => use nose instead
 * no ``str.decode('string-escape')`` in py3
 * no :mod:`json` module in 2.5 (install ``simplejson`` instead)
 * no ``ordereddict`` in 2.5/2.6 (install ``ordereddict`` module)
 * :class:`collections.Counter` was added in 2.6

Releasing
---------

Set to-be-released version number in :file:`rdflib/__init__.py`

Add :file:`CHANGELOG` entry.

Commit this change, and tag it with::

  git tag -a -m 'tagged version' X.X.X

When pushing, remember to do::

  git push --tags

Upload tarball to pypi with::

  python setup.py sdist upload

Set new dev version number in the above locations, i.e. next release `-dev`: ``8.9.2-dev`` and commit again.

Update the topic of #rdflib on freenode irc::

  /msg ChanServ topic #rdflib https://github.com/RDFLib/rdflib | latest stable version: 4.0.1 | docs: http://readthedocs.org/docs/rdflib
