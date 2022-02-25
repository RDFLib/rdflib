.. developers:

RDFLib developers guide
=======================

Introduction
------------

This document describes the process and conventions to follow when
developing RDFLib code.

* Please be as Pythonic as possible (:pep:`8`).
* Code should be formatted using `black <https://github.com/psf/black>`_
  and we use Black v21.9b0, with the black.toml config file provided.
* Code should also pass `flake8 <https://github.com/psf/black>`_ linting
  and `mypy <http://mypy-lang.org/>`_ type checking.
* You must supply tests for new code

If you add a new cool feature, consider also adding an example in ``./examples``

Tests
-----
Any new functionality being added to RDFLib _must_ have unit tests and
should have doc tests supplied.

Typically, you should add your functionality and new tests to a branch of
RDFlib and and run all tests locally and see them pass. There are currently
close to 4,000 tests with a few extra expected failures and skipped tests.
We won't allow Pull Requests that break any of the existing tests.

Tests that you add should show how your new feature or bug fix is doing what
you say it is doing: if you remove your enhancement, your new tests should fail!

Finally, please consider adding simple and more complex tests. It's good to see
the basic functionality of your feature tests and then also any tricky bits or
edge cases.

Testing framework
~~~~~~~~~~~~~~~~~
RDFLib uses the `pytest <https://docs.pytest.org/en/latest/>`_ testing framework.

Running tests
~~~~~~~~~~~~~

To run RDFLib's test suite with `pytest <https://docs.pytest.org/en/latest/>`_:

.. code-block:: console

   $ pip install -r requirements.txt -r requirements.dev.txt
   $ pytest

Specific tests can be run by file name. For example:

.. code-block:: console

  $ pytest test/test_graph.py

For more extensive tests, including tests for the `berkleydb
<https://www.oracle.com/database/technologies/related/berkeleydb.html>`_
backend, install the requirements from ``requirements.dev-extra.txt`` before
executing the tests.

.. code-block:: console

   $ pip install -r requirements.txt -r requirements.dev.txt
   $ pip install -r requirements.dev-extra.txt
   $ pytest

Writing tests
~~~~~~~~~~~~~

New tests should be written for `pytest <https://docs.pytest.org/en/latest/>`_
instead of for python's built-in `unittest` module as pytest provides advanced
features such as parameterization and more flexibility in writing expected
failure tests than `unittest`.

A primer on how to write tests for pytest can be found `here
<https://docs.pytest.org/en/latest/getting-started.html#create-your-first-test>`_.

The existing tests that use `unittest` work well with pytest, but they should
ideally be updated to the pytest test-style when they are touched.

Test should go into the ``test/`` directory, either into an existing test file
with a name that is applicable to the test being written, or into a new test
file with a name that is descriptive of the tests placed in it. Test files
should be named `test_*.py` so that `pytest can discover them
<https://docs.pytest.org/en/latest/explanation/goodpractices.html#conventions-for-python-test-discovery>`_.

Running static checks
---------------------

Check formatting with `black <https://github.com/psf/black>`_, making sure you use
our black.toml config file:

.. code-block:: bash

    python -m black --config black.toml --check ./rdflib

Check style and conventions with `flake8 <https://github.com/psf/black>`_:

.. code-block:: bash

    python -m flake8 rdflib

Check types with `mypy <http://mypy-lang.org/>`_:

.. code-block:: bash

    python -m mypy --show-error-context --show-error-codes rdflib

pre-commit and pre-commit ci
----------------------------

We have `pre-commit <https://pre-commit.com/>`_ configured with `black
<https://github.com/psf/black>`_ for formatting code.

Some useful commands for using pre-commit:

.. code-block:: bash

    # Install pre-commit.
    pip install --user --upgrade pre-commit

    # Install pre-commit hooks, this will run pre-commit
    # every time you make a git commit.
    pre-commit install

    # Run pre-commit on changed files.
    pre-commit run

    # Run pre-commit on all files.
    pre-commit run --all-files

There is also two tox environments for pre-commit:

.. code-block:: bash

    # run pre-commit on changed files.
    tox -e precommit

    # run pre-commit on all files.
    tox -e precommitall


There is no hard requirement for pull requests to be processed with pre-commit (or the underlying processors), however doing this makes for a less noisy codebase with cleaner history.

We have enabled `https://pre-commit.ci/ <https://pre-commit.ci/>`_ and this can
be used to automatically fix pull requests by commenting ``pre-commit.ci
autofix`` on a pull request.

Using tox
---------------------

RDFLib has a `tox <https://tox.wiki/en/latest/index.html>`_ config file that
makes it easier to run validation on all supported python versions.

.. code-block:: bash

    # install tox
    pip install tox

    # list tox environments that run by default
    tox -e

    # list all tox environments
    tox -a

    # run default environment for all python versions
    tox

    # run a specific environment
    tox -e py37 # default environment with py37
    tox -e py39-mypy # mypy environment with py39

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

RDFlib 6.0.0 release and later only support Python 3.7 and newer.

RDFLib 5.0.0 maintained compatibility with Python versions 2.7, 3.4, 3.5, 3.6, 3.7.

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
