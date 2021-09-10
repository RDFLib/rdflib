.. developers:

RDFLib developers guide
=======================

Introduction
------------

This document describes the process and conventions to follow when
developing RDFLib code.

Please be as Pythonic as possible (:pep:`8`).

Code should be formatted using `black <https://github.com/psf/black>`_.
While not yet mandatory, it will be required in the future  (6.0.0+).1
Use Black v21.6b1, with the black.toml config file provided.

Code should also pass `flake8 <https://github.com/psf/black>`_ linting
and `mypy <http://mypy-lang.org/>`_ type checking.

Any new functionality being added to RDFLib should have doc tests and
unit tests. Tests should be added for any functionality being changed
that currently does not have any doc tests or unit tests. And all the
tests should be run before committing changes to make sure the changes
did not break anything.

If you add a new cool feature, consider also adding an example in ``./examples``


Running tests
-------------
Run tests with `nose <https://nose.readthedocs.org/en/latest/>`_:

.. code-block:: bash

   $ pip install nose
   $ python run_tests.py
   $ python run_tests.py --attr known_issue # override attr in setup.cfg to run only tests marked with "known_issue"
   $ python run_tests.py --attr \!known_issue # runs all tests (including "slow" and "non_core") except those with known issues
   $ python run_tests.py --attr slow,!known_issue  # comma separate if you want to specify more than one attr
   $ python run_tests.py --attr known_issue=None # use =None instead of \! if you keep forgetting to escape the ! in shell commands ;)

Specific tests can either be run by module name or file name. For example::

  $ python run_tests.py --tests rdflib.graph
  $ python run_tests.py --tests test/test_graph.py

Running static checks
---------------------

Check formatting with `black <https://github.com/psf/black>`_:

.. code-block:: bash

    python -m black --config black.toml --check ./rdflib

Check style and conventions with `flake8 <https://github.com/psf/black>`_:

.. code-block:: bash

    python -m flake8 rdflib

Check types with `mypy <http://mypy-lang.org/>`_:

.. code-block:: bash

    python -m mypy --show-error-context --show-error-codes rdflib

Writing documentation
---------------------

We use sphinx for generating HTML docs, see :ref:`docs`.

Continuous Integration
----------------------

We used Drone for CI, see:

  https://drone.rdflib.ashs.dev/RDFLib/rdflib

If you make a pull-request to RDFLib on GitHub, Drone will automatically test your code and we will only merge code
passing all tests.

Please do *not* commit tests you know will fail, even if you're just pointing out a bug. If you commit such tests,
flag them as expecting to fail.

Compatibility
-------------

RDFLib 5.0.0 maintained compatibility with python versions 2.7, 3.4, 3.5, 3.6, 3.7.

The latest 6.0.0 release and subsequent will only support Python 3.7 and newer.


Releasing
---------

Set to-be-released version number in :file:`rdflib/__init__.py` and
:file:`README.md`. Check date in :file:`LICENSE`.

Add :file:`CHANGELOG.md` entry.

Commit this change. It's preferable make the release tag via
https://github.com/RDFLib/rdflib/releases/new ::
Our Tag versions aren't started with 'v', so just use a plain 5.0.0 like
version. Release title is like "RDFLib 5.0.0", the description a copy of your
:file:`CHANGELOG.md` entry.
This gives us a nice release page like this::
https://github.com/RDFLib/rdflib/releases/tag/4.2.2

If for whatever reason you don't want to take this approach, the old one is::

    Tagging the release commit with::

      git tag -am 'tagged version' X.X.X

    When pushing, remember to do::

      git push --tags


No matter how you create the release tag, remember to upload tarball to pypi with::

  rm -r dist/X.X.X[.-]*  # delete all previous builds for this release, just in case

  rm -r build
  python setup.py sdist
  python setup.py bdist_wheel
  ls dist

  # upload with twine
  # WARNING: once uploaded can never be modified, only deleted!
  twine upload dist/rdflib-X.X.X[.-]*

Set new dev version number in the above locations, i.e. next release `-dev`: ``5.0.1-dev`` and commit again.

Tweet, email mailing list and inform members in the chat.
