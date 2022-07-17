.. developers:

RDFLib developers guide
=======================

Introduction
------------

This document describes the process and conventions to follow when
developing RDFLib code.

* Please be as Pythonic as possible (:pep:`8`).
* Code should be formatted using `black <https://github.com/psf/black>`_  and we use Black v22.6.0, with the black config in ``pyproject.toml``.
* Code should also pass `flake8 <https://flake8.pycqa.org/en/latest/>`_ linting
  and `mypy <http://mypy-lang.org/>`_ type checking.
* You must supply tests for new code.

If you add a new cool feature, consider also adding an example in ``./examples``

Pull Requests Guidelines
------------------------

Contributions to RDFLib are made through pull requests (PRs).

In general, maintainers will only merge PRs if the following conditions are
met:

* The PR has been sufficiently reviewed.

  Each PR should be reviewed and approved by at least two people other than the
  author of the PR before it is merged and PRs will be processed faster if
  they are easier to review and approve of.

  Reviews are open to everyone, but the weight assigned to any particular
  review is at the discretion of maintainers.

* Changes that have a runtime impact are covered by unit tests.

  There should either be existing tests that cover the changed code and
  behaviour, or the PR should include tests. For more information about what is
  considered adequate testing see the :ref:`Tests section <tests>`.

* Documentation that covers something that changed has been updated.

* Type checks and unit tests that are part of our continuous integration
  workflow pass.

In addition to these conditions, PRs that are easier to review and approve will
be processed quicker. The primary factors that determine this is the scope and
size of a PR. If there are few changes and the scope is limited then there is
less that a reviewer has to understand and less that they can disagree with. It
is thus important to try and split up your changes into multiple independent
PRs if possible. No PR is too small.

For PRs that introduce breaking changes, it is even more critical that they are
limited in size and scope, as they will likely have to be kept up to date with
the master branch of this project for some time before they are merged.

It is also critical that your PR is understandable both in what it does and why
it does it, and how the change will impact the users of this project, for this
reason it is essential that your PR's description explains the nature of the
PR, what the PR intends to do, why this is desirable, and how this will affect
the users of this project.

Please note that while we would like all PRs to follow the guidelines given
here, we will not reject a PR just because it does not.

.. _tests:

Tests
-----
Any new functionality being added to RDFLib *must* have unit tests and
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
should be named ``test_*.py`` so that `pytest can discover them
<https://docs.pytest.org/en/latest/explanation/goodpractices.html#conventions-for-python-test-discovery>`_.

Running static checks
---------------------

Check formatting with `black <https://github.com/psf/black>`_, making sure you use
our black.toml config file:

.. code-block:: bash

    python -m black --config black.toml --check ./rdflib

Check style and conventions with `flake8 <https://flake8.pycqa.org/en/latest/>`_:

.. code-block:: bash

    python -m flake8 rdflib

We also provide a `flakeheaven <https://pypi.org/project/flakeheaven/>`_
baseline that ignores existing flake8 errors and only reports on newly
introduced flake8 errors:

.. code-block:: bash

    python -m flakeheaven


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

    # Install tox.
    pip install tox

    # List the tox environments that run by default.
    tox -e

    # Run the default environments.
    tox

    # List all tox environments, including ones that don't run by default.
    tox -a

    # Run a specific environment.
    tox -e py37 # default environment with py37
    tox -e py39-extra # extra tests with py39

    # Override the test command.
    # the below command will run `pytest test/test_translate_algebra.py`
    # instead of the default pytest command.
    tox -e py37,py39 -- pytest test/test_translate_algebra.py


``go-task`` and ``Taskfile.yml``
--------------------------------

A ``Taskfile.yml`` is provided for `go-task <https://taskfile.dev/#/>`_ with
various commands that facilitate development.

Instructions for installing go-task can be seen in the `go-task installation
guide <https://taskfile.dev/#/installation>`_.

Some useful commands for working with the task in the taskfile is given below:

.. code-block:: bash

    # List available tasks.
    task -l

    # Install pip dependencies
    task install:pip-deps

    # Run basic validation
    task validate

    # Install a venv and run validation inside venv
    task venv:install
    task WITH_VENV=1 validate

    # Fix all auto-fixable validation errors (i.e. run black and isort) using venv
    task WITH_VENV=1 validate:fix

    # Build docs inside venv
    task WITH_VENV=1 docs:build

    # Run live-preview on the docs
    task docs:live-server

    # Run the py310 tox environment
    task tox -- -e py310

The `Taskfile usage documentation <https://taskfile.dev/#/usage>`_ provides
more information on how to work with taskfiles.

Development container
---------------------

To simplify the process of getting a working development environment to develop
rdflib in we provide a `Development Container
<https://devcontainers.github.io/containers.dev/>`_ (*devcontainer*) that is
configured in `Docker Compose <https://docs.docker.com/compose/>`_. This
container can be used directly to run various commands, or it can be used with
`editors that support Development Containers
<https://devcontainers.github.io/containers.dev/supporting>`_.

.. important::
  The devcontainer is intended to run with a
  `rootless docker <https://docs.docker.com/engine/security/rootless/>`_
  daemon so it can edit files owned by the invoking user without
  an invovled configuration process.

  Using a rootless docker daemon also has general security benefits.

To use the development container directly:

.. code-block:: bash

    # Build the devcontainer docker image.
    docker-compose build

    # Run the validate task inside the devtools container.
    docker-compose run --rm devcontainer task validate

    # Run extensive tests inside the devtools container.
    docker-compose run --rm devcontainer task EXTENSIVE=true test

    # To get a shell into the devcontainer docker image.
    docker-compose run --rm devcontainer bash

The devcontainer also works with `Podman Compose
<https://github.com/containers/podman-compose>`_.

Details on how to use the development container with `VSCode
<https://code.visualstudio.com/>`_ can found in the `Developing inside a
Container <https://code.visualstudio.com/docs/remote/containers>`_ page. With
the VSCode `development container CLI
<https://code.visualstudio.com/docs/remote/devcontainer-cli>`_ installed the
following command can be used to open the repository inside the development
container:

.. code-block:: bash

    # Inside the repository base directory
    cd ./rdflib/
    
    # Build the development container.
    devcontainer build .

    # Open the code inside the development container.
    devcontainer open .

Writing documentation
---------------------

We use sphinx for generating HTML docs, see :ref:`docs`.

Continuous Integration
----------------------

We used GitHub Actions for CI, see:

  https://github.com/RDFLib/rdflib/actions

If you make a pull-request to RDFLib on GitHub, GitHub Actions will
automatically test your code and we will only merge code passing all tests.

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

Set new dev version number in the above locations, i.e. next release ``-dev``: ``5.0.1-dev`` and commit again.

Tweet, email mailing list and inform members in the chat.
