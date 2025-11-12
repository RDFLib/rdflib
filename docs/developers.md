# RDFLib developers guide

## Introduction

This document describes the process and conventions to follow when
developing RDFLib code.

* Please be as Pythonic as possible ([PEP 8](https://www.python.org/dev/peps/pep-0008/)).
* Code should be formatted using [black](https://github.com/psf/black) and we use Black v23.1.0, with the black config in `pyproject.toml`.
* Code should also pass [flake8](https://flake8.pycqa.org/en/latest/) linting
  and [mypy](http://mypy-lang.org/) type checking.
* You must supply tests for new code.
* RDFLib uses [Poetry](https://python-poetry.org/docs/master/) for dependency management and packaging.

If you add a new cool feature, consider also adding an example in `./examples`.

## Pull Requests Guidelines

Contributions to RDFLib are made through pull requests (PRs).

For changes that add features or affect the public API of RDFLib, it is recommended to first open an issue to discuss the change before starting to work on it. That way you can get feedback on the design of the feature before spending time on it.

In general, maintainers will only merge PRs if the following conditions are met:

* The PR has been sufficiently reviewed.

  Each PR should be reviewed and approved by at least two people other than the
  author of the PR before it is merged and PRs will be processed faster if
  they are easier to review and approve of.

  Reviews are open to everyone, but the weight assigned to any particular
  review is at the discretion of maintainers.

* Changes that have a runtime impact are covered by unit tests.

  There should either be existing tests that cover the changed code and
  behaviour, or the PR should include tests. For more information about what is
  considered adequate testing see the [Tests section](#tests).

* Documentation that covers something that changed has been updated.

* Type checks and unit tests that are part of our continuous integration workflow pass.

In addition to these conditions, PRs that are easier to review and approve will be processed quicker. The primary factors that determine this are the scope and size of a PR. If there are few changes and the scope is limited, then there is less that a reviewer has to understand and less that they can disagree with. It is thus important to try to split up your changes into multiple independent PRs if possible. No PR is too small.

For PRs that introduce breaking changes, it is even more critical that they are limited in size and scope, as they will likely have to be kept up to date with the `main` branch of this project for some time before they are merged.

It is also critical that your PR is understandable both in what it does and why it does it, and how the change will impact the users of this project, for this reason, it is essential that your PR's description explains the nature of the PR, what the PR intends to do, why this is desirable, and how this will affect the users of this project.

Please note that while we would like all PRs to follow the guidelines given here, we will not reject a PR just because it does not.

## Maintenance Guidelines

This section contains guidelines for maintaining RDFLib. RDFLib maintainers should try to follow these. These guidelines also serve as an indication to RDFLib users what they can expect.

### Breaking changes

Breaking changes to RDFLib's public API should be made incrementally, with small pull requests to the main branch that change as few things as possible.

Breaking changes should be discussed first in an issue before work is started, as it is possible that the change is not necessary or that there is a better way to achieve the same goal, in which case the work on the PR would have been wasted. This will however not be strictly enforced, and no PR will be rejected solely on the basis that it was not discussed upfront.

RDFLib follows [semantic versioning](https://semver.org/spec/v2.0.0.html) and [trunk-based development](https://trunkbaseddevelopment.com/), so if any breaking changes were introduced into the main branch since the last release, then the next release will be a major release with an incremented major version.

Releases of RDFLib will not as a rule be conditioned on specific features, so there may be new major releases that contain very few breaking changes, and there could be no minor or patch releases between two major releases.

#### Rationale

RDFLib has been around for more than a decade, and in this time both Python and RDF have evolved, and RDFLib's API also has to evolve to keep up with these changes and to make it easier for users to use. This will inevitably require breaking changes.

There are more or less two ways to introduce breaking changes to RDFLib's public API:

- Revolutionary: Create a new API from scratch and reimplement it, and when
  ready, release a new version of RDFLib with the new API.
- Evolutionary: Incrementally improve the existing API with small changes and
  release any breaking changes that were made at regular intervals.

While the revolutionary approach seems appealing, it is also risky and time-consuming.

The evolutionary approach puts a lot of strain on the users of RDFLib as they have to adapt to breaking changes more often, but the shortcomings of the RDFLib public API also put a lot of strain on the users of RDFLib. On the other hand, a major advantage of the evolutionary approach is that it is simple and achievable from a maintenance and contributor perspective.

### Deprecating functionality

To whatever extent possible, classes, functions, variables, or parameters that will be removed should be marked for deprecation in documentation, and if possible, should be changed to raise deprecation warnings if used.

There is however no hard requirement that something may only be removed after a deprecation notice has been added, or only after a release was made with a deprecation notice.

Consequently, functionality may be removed without it ever being marked as deprecated.

#### Rationale

Current resource limitations and the backlog of issues make it impractical to first release or incorporate deprecation notices before making quality of life changes.

RDFLib uses semantic versioning and provides type hints, and these are the primary mechanisms for signalling breaking changes to our users.

## Tests

Any new functionality being added to RDFLib *must* have unit tests and should have doc tests supplied.

Typically, you should add your functionality and new tests to a branch of RDFlib and run all tests locally and see them pass. There are currently close to 4,000 tests, with a some expected failures and skipped tests. We won't merge pull requests unless the test suite completes successfully.

Tests that you add should show how your new feature or bug fix is doing what you say it is doing: if you remove your enhancement, your new tests should fail!

Finally, please consider adding simple and more complex tests. It's good to see the basic functionality of your feature tests and then also any tricky bits or edge cases.

### Testing framework

RDFLib uses the [pytest](https://docs.pytest.org/en/latest/) testing framework.

### Running tests

To run RDFLib's test suite with [pytest](https://docs.pytest.org/en/latest/):

```bash
poetry install
poetry run pytest
```

Specific tests can be run by file name. For example:

```bash
poetry run pytest test/test_graph/test_graph.py
```

For more extensive tests, including tests for the [berkleydb](https://www.oracle.com/database/technologies/related/berkeleydb.html) backend, install extra requirements before executing the tests.

```bash
poetry install --all-extras
poetry run pytest
```

By default, tests of the `SPARQLStore` against remote public endpoints are skipped, to enable them add the flag:

```bash
poetry run pytest --public-endpoints
```

Or exclusively run the SPARQLStore tests:

```bash
poetry run pytest test/test_store/test_store_sparqlstore_public.py --public-endpoints
```

### Writing tests

New tests should be written for [pytest](https://docs.pytest.org/en/latest/) instead of for python's built-in `unittest` module as pytest provides advanced features such as parameterization and more flexibility in writing expected failure tests than `unittest`.

A primer on how to write tests for pytest can be found [here](https://docs.pytest.org/en/latest/getting-started.html#create-your-first-test).

The existing tests that use `unittest` work well with pytest, but they should ideally be updated to the pytest test-style when they are touched.

Test should go into the `test/` directory, either into an existing test file with a name that is applicable to the test being written, or into a new test file with a name that is descriptive of the tests placed in it. Test files should be named `test_*.py` so that [pytest can discover them](https://docs.pytest.org/en/latest/explanation/goodpractices.html#conventions-for-python-test-discovery).

## Running static checks

Check formatting with [black](https://github.com/psf/black), making sure you use
our black.toml config file:

```bash
poetry run black .
```

Check style and conventions with [ruff](https://docs.astral.sh/ruff/linter/):

```bash
poetry run ruff check
```

Any issues that are found can potentially be fixed automatically using:

```bash
poetry run ruff check --fix
```

Check types with [mypy](http://mypy-lang.org/):

```bash
poetry run mypy --show-error-context --show-error-codes
```

## pre-commit and pre-commit ci

We have [pre-commit](https://pre-commit.com/) configured with [black](https://github.com/psf/black) for formatting code.

Some useful commands for using pre-commit:

```bash
# Install pre-commit.
pip install --user --upgrade pre-commit

# Install pre-commit hooks, this will run pre-commit
# every time you make a git commit.
pre-commit install

# Run pre-commit on changed files.
pre-commit run

# Run pre-commit on all files.
pre-commit run --all-files
```

There is also two tox environments for pre-commit:

```bash
# run pre-commit on changed files.
tox -e precommit

# run pre-commit on all files.
tox -e precommitall
```

There is no hard requirement for pull requests to be processed with pre-commit (or the underlying processors), however doing this makes for a less noisy codebase with cleaner history.

We have enabled [https://pre-commit.ci/](https://pre-commit.ci/) and this can be used to automatically fix pull requests by commenting `pre-commit.ci autofix` on a pull request.

## Using tox

RDFLib has a [tox](https://tox.wiki/en/latest/index.html) config file that makes it easier to run validation on all supported python versions.

```bash
# Install tox.
pip install tox

# List the tox environments that run by default.
tox -e

# Run the default environments.
tox

# List all tox environments, including ones that don't run by default.
tox -a

# Run a specific environment.
tox -e py39 # default environment with py39
tox -e py311-extra # extra tests with py311

# Override the test command.
# the below command will run `pytest test/test_translate_algebra.py`
# instead of the default pytest command.
tox -e py39,py311 -- pytest test/test_translate_algebra.py
```

## `go-task` and `Taskfile.yml`

A `Taskfile.yml` is provided for [go-task](https://taskfile.dev/#/) with various commands that facilitate development.

Instructions for installing go-task can be seen in the [go-task installation guide](https://taskfile.dev/#/installation).

Some useful commands for working with the task in the taskfile is given below:

```bash
# List available tasks.
task -l

# Configure the environment for development
task configure

# Run basic validation
task validate

# Build docs
task docs

# Run live-preview on the docs
task docs:live-server

# Run the py310 tox environment
task tox -- -e py310
```

The [Taskfile usage documentation](https://taskfile.dev/#/usage) provides more information on how to work with taskfiles.

## Development container

To simplify the process of getting a working development environment to develop rdflib in we provide a [Development Container](https://devcontainers.github.io/containers.dev/) (*devcontainer*) that is configured in [Docker Compose](https://docs.docker.com/compose/). This container can be used directly to run various commands, or it can be used with [editors that support Development Containers](https://devcontainers.github.io/containers.dev/supporting).

!!! bug "Rootless docker"
    The devcontainer is intended to run with a
    [rootless docker](https://docs.docker.com/engine/security/rootless/)
    daemon so it can edit files owned by the invoking user without
    an invovled configuration process.

    Using a rootless docker daemon also has general security benefits.

To use the development container directly:

```bash
# Build the devcontainer docker image.
docker-compose build

# Configure the system for development.
docker-compose run --rm run task configure

# Run the validate task inside the devtools container.
docker-compose run --rm run task validate

# Run extensive tests inside the devtools container.
docker-compose run --rm run task EXTENSIVE=true test

# To get a shell into the devcontainer docker image.
docker-compose run --rm run bash
```

The devcontainer also works with [Podman Compose](https://github.com/containers/podman-compose).

Details on how to use the development container with [VSCode](https://code.visualstudio.com/) can found in the [Developing inside a Container](https://code.visualstudio.com/docs/remote/containers) page. With the VSCode [development container CLI](https://code.visualstudio.com/docs/remote/devcontainer-cli) installed the following command can be used to open the repository inside the development container:

```bash
# Inside the repository base directory
cd ./rdflib/

# Build the development container.
devcontainer build .

# Open the code inside the development container.
devcontainer open .
```

## Type Hints

This document provides some details about the type hints for RDFLib. More information about type hints can be found [here](https://docs.python.org/3/library/typing.html)

### Rationale for Type Hints

Type hints are code annotations that describe the types of variables, function parameters and function return value types in a way that can be understood by humans, static type checkers like [mypy](http://mypy-lang.org/), code editors like VSCode, documentation generators like mkdocstring, and other tools.

Static type checkers can use type hints to detect certain classes of errors by inspection. Code editors and IDEs can use type hints to provide better auto-completion and documentation generators can use type hints to generate better documentation.

These capabilities make it easier to develop a defect-free RDFLib and they also make it easier for users of RDFLib who can now use static type checkers to detect type errors in code that uses RDFLib.

### Gradual Typing Process

Type hints are being added to RDFLib through a process called [gradual typing](https://en.wikipedia.org/wiki/Gradual_typing). This process involves adding type hints to some parts of RDFLib while leaving the rest without type hints. Gradual typing is being applied to many, long-lived, Python code bases.

This process is beneficial in that we can realize some of the benefits of type hints without requiring that the whole codebase have type hints.

### Intended Type Hints

The intent is to have type hints in place for all of RDFLib and to have these type hints be as accurate as possible.

The accuracy of type hints is determined by both the standards that RDFLib aims to conform to, like RDF 1.1, and the deliberate choices that are made when implementing RDFLib. For example, given that the RDF 1.1 specification stipulates that the subject of an RDF triple cannot be a literal, all functions that accept an *RDF term* to be used as the subject of a triple should have type hints which excludes values that are literals.

There may be cases where some functionality of RDFLib may work perfectly well with values of types that are excluded by the type hints, but if these additional types violate the relevant standards we will consider the correct type hints to be those that exclude values of these types.

### Public Type Aliases

In python, type hints are specified in annotations. Type hints are different from type aliases which are normal python variables that are not intended to provide runtime utility and are instead intended for use in static type checking.

For clarity, the following is an example of a function `foo` with type hints:

```python
def foo(a: int) -> int:
    return a + 1
```

In the function `foo`, the input variable `a` is indicated to be of type `int` and the function is indicated to return an `int`.

The following is an example of a type alias `Bar`:

```python
Bar = tuple[int, str]
```

RDFLib will provide public type aliases under the `rdflib.typing` package, for example, `rdflib.typing.Triple`, `rdflib.typing.Quad`. Type aliases in the rest of RDFLib should be private (i.e. being with an underscore).

### Versioning, Compatibility and Stability

RDFLib attempts to adhere to [semver 2.0](https://semver.org/spec/v2.0.0.html) which is concerned with the public API of software.

Ignoring type hints, the public API of RDFLib exists implicitly as a consequence of the code of RDFLib and the actual behaviour this entails, the relevant standards that RDFLib is trying to implement, and the documentation of RDFLib, with some interplay between all three of these. RDFLib's public API includes public type aliases, as these are normal python variables and not annotations.

Type hints attempt to formally document RDFLib's implicitly-defined public API in a machine-readable fashion as accurately and correctly as possible within the framework outline earlier in this document.

Type hints do not affect the runtime API or behaviour of RDFLib. In this way then, they are somewhat outside of the scope of semver, however, they still have an impact on the users of RDFLib, even if this impact is not at runtime, but during development. This necessitates some clarity as to what users of RDFLib should expect regarding type hints in RDFLib releases.

Changes to type hints can broadly be classified as follow:

**Type Declaration**
  Adding type hints to existing code that had no explicit type hints, for example, changing

```python
def foo(val):
    return val + 1
```

to

```python
def foo(val: int) -> int:
    return val + 1
```

**Type Refinement**
  Refining existing type hints to be narrower, for example, changing a type hint of `typing.Collection` to `typing.Sequence`.

**Type Corrections**
  Correcting existing type hints which contradict the behaviour of the code or relevant specifications, for example, changing `typing.Sequence` from `typing.Set`

Given semver version components `MAJOR.MINOR.PATCH`, RDFLib will attempt to constrain type hint changes as follow:

| Version Component | Type Declaration | Type Refinement | Type Corrections |
|------------------|-----------------|----------------|-----------------|
| MAJOR | YES | YES | YES |
| MINOR | YES | YES | YES |
| PATCH | NO | NO | YES |

!!! caution "Type Corrections"
    A caveat worth nothing here is that code that passed type validation on one version of RDFLib can fail type validation on a later version of RDFLib that only differs in `PATCH` version component. This is as a consequence of potential *Type Corrections*.

## Writing documentation

We use mkdocs for generating HTML docs, see [docs](docs.md).

## Continuous Integration

We used GitHub Actions for CI, see: [https://github.com/RDFLib/rdflib/actions](https://github.com/RDFLib/rdflib/actions)

If you make a pull-request to RDFLib on GitHub, GitHub Actions will automatically test your code and we will only merge code passing all tests.

Please do *not* commit tests you know will fail, even if you're just pointing out a bug. If you commit such tests, flag them as expecting to fail.

## Compatibility

RDFlib 7.0.0 release and later only support Python 3.8.1 and newer.

RDFlib 6.0.0 release and later only support Python 3.7 and newer.

RDFLib 5.0.0 maintained compatibility with Python versions 2.7, 3.4, 3.5, 3.6, 3.7.

## Releasing

Create a release-preparation pull request with the following changes:

* Updated version and date in [`CITATION.cff`](../CITATION.cff).
* Updated copyright year in the [`LICENSE`](../LICENSE) file.
* Updated copyright year in the [`mkdocs.yml`](../mkdocs.yml) file.
* Updated main branch version and current version in the [`README.md`](../README.md) file.
* Updated version in the [`pyproject.toml`](../pyproject.toml) file.
* Updated `__date__` in the [`rdflib/__init__.py`](../rdflib/__init__.py) file.
* Updated [`CHANGELOG.md`](../CHANGELOG.md) entry for the release with admin tools as described in [`admin/README.md`](../admin/README.md).

Once the PR is merged, switch to the main branch, build the release and upload it to PyPI:

```bash
# Clean up any previous builds
rm -vf dist/*

# Build artifacts
poetry build

# Verify package metadata
bsdtar -xvf dist/rdflib-*.whl -O '*/METADATA' | view -
bsdtar -xvf dist/rdflib-*.tar.gz -O '*/PKG-INFO' | view -

# Check that the built wheel and sdist works correctly:
## Ensure pipx is installed but not within RDFLib's environment
pipx run --no-cache --spec "$(readlink -f dist/rdflib*.whl)" rdfpipe --version
pipx run --no-cache --spec "$(readlink -f dist/rdflib*.whl)" rdfpipe https://github.com/RDFLib/rdflib/raw/main/test/data/defined_namespaces/rdfs.ttl
pipx run --no-cache --spec "$(readlink -f dist/rdflib*.tar.gz)" rdfpipe --version
pipx run --no-cache --spec "$(readlink -f dist/rdflib*.tar.gz)" rdfpipe https://github.com/RDFLib/rdflib/raw/main/test/data/defined_namespaces/rdfs.ttl

# Dry run publishing
poetry publish --repository=testpypi --dry-run
poetry publish --dry-run

# Publish to TestPyPI
## ensure you are authed as per https://pypi.org/help/#apitoken and https://github.com/python-poetry/poetry/issues/6320
poetry publish --repository=testpypi

# Publish to PyPI
poetry publish
## poetry publish -u __token__ -p pypi-<REDACTED>
```

Once this is done, create a release tag from [GitHub releases](https://github.com/RDFLib/rdflib/releases/new). For a release of version 6.3.1 the tag should be `6.3.1` (without a "v" prefix), and the release title should be "RDFLib 6.3.1". The release notes for the latest version be added to the release description. The artifacts built with `poetry build` should be uploaded to the release as release artifacts.

The resulting release will be available at https://github.com/RDFLib/rdflib/releases/tag/6.3.1

Once this is done, announce the release at the following locations:

* Twitter: Just make a tweet from your own account linking to the latest release.
* RDFLib mailing list.
* RDFLib Gitter / matrix.org chat room.

Once this is all done, create another post-release pull request with the following changes:

* Set the just released version in `docker/latest/requirements.in` and run `task docker:prepare` to update the `docker/latest/requirements.txt` file.
* Set the version in the `pyproject.toml` file to the next minor release with a `a0` suffix to indicate alpha 0.
