Public interface guidelines
===========================

Overview
--------

This document provides guidelines for the management of RDFLib's public
interface.

These guidelines attempt to balance the following:

* The need for stable public interface that do not frequently change in ways that are
  backwards incompatible.
* The need for modern, easy to use, well-designed public interface free of defects.
* The need to change the public interface in a backwards incompatible way to
  modernize it, eliminate defects, and improve usability and design.

Versioning
----------

RDFLib follows semantic versioning [SEMVER]_, which can be summarized as:

   Given a version number MAJOR.MINOR.PATCH, increment the:

   #. MAJOR version when you make incompatible API changes
   #. MINOR version when you add functionality in a backwards compatible
      manner
   #. PATCH version when you make backwards compatible bug fixes

   Additional labels for pre-release and build metadata are available as
   extensions to the MAJOR.MINOR.PATCH format.

Guidelines for backwards compatible changes
---------------------------------------------

Examples of backwards compatible changes include:

* Adding entirely new modules, functions, variables, or classes.
* Adding new parameters to existing functions with defaults that maintains the
  existing behavior of the function.

Non-breaking changes can be made directly in the main RDFLib module, i.e.
:mod:`rdflib`.

In some cases it may be appropriate to place new identifiers under a
``_provisional`` module (see `Provisional Python modules`_), especially if they
provide complex functionality, this gives the users of RDFLib some opportunity
to try them in non-critical settings while still allowing RDFLib developers to
change the behavior before committing to them and making them part of the public
interface.

Guidelines for backwards incompatible changes
---------------------------------------------

Examples of backwards incompatible changes include:

* Altering a function to behave differently in a way that cannot be considered a
  bug fix, some more specific examples:
  
  * Changing the return type to an incompatible type.
  * Changing the supported argument types to incompatible types.
  * Changing the required arguments.
* Changing the class hierarchy so that class relations that held previously no
  longer holds.

When backwards incompatible changes will be introduced users should be provided
with at least one release advanced notice, and, if possible, users should be
given the opportunity to adapt their code to the new behavior before the old
behavior is removed.

At the same time it is preferable to integrate code that implements the new
behavior of backwards incompatible changes into the main branch of RDFLib as
soon as possible, so that long-lived pull requests or branches can be avoided.

This section details various options for integrating code that implements
backwards incompatible changes into the main branch while allowing maintainers
explicit choice in when the backwards incompatible changes are released to users
and allowing users of RDFLib the opportunity to opt into the new behavior.

Simple deprecation
^^^^^^^^^^^^^^^^^^

In the simplest case if a function, class, or variable will be removed or
replaced with a new function with a different name, the old identifier should be
marked as deprecated and the deprecation notice should indicate the new function
that should be used instead.

For functions `warnings.warn` should be used with `DeprecationWarning`, and for
variables and classes the `Sphinx deprecated directive
<https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-deprecated>`_
should be used.

When deprecating whole classes a deprecation warning should be raised from
`object.__init__` or `object.__new__`.

The deprecation notice should indicate in what version of RDFLib the identifiers
will be removed, and in most cases this should be the next major version.

Release preparation for major versions of RDFLib should remove all code that was
marked as deprecated for removal in the new major version.

Use versioned top level module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In some cases critical parts of the class hierarchy like `rdflib.graph.Graph`
and `rdflib.term.Node` must be changed. For changes like this versioned top
level modules can be used (see `Top-level Python modules`_).

For example, if a new `rdflib.graph.Graph` class hierarchy needs to be created
for RDFLib 7, the process would be:

* Some time before releasing RDFLib 7:
  
  * Create ``rdflib.v7.graph.Graph``.
  * Mark `rdflib.graph.Graph` as deprecated.
* When releasing RDFLib 7:

  * Remove `rdflib.graph.Graph`.
  * Import ``rdflib.v7.graph.Graph`` to `rdflib.graph.Graph`

With this approach users can start using the new class before RDFLib 7 is
released, and the class does not have to be kept in a separate branch or pull
request until RDFLib 7 is ready for release. 

Some care must be taken to avoid duplicated code, some options available to do
this is:

* Move shared functionality out to another class or function that can be used
  from the old and new classes.
* Import the old class and override the needed/relevant functionality.

Release preparation for major versions should import the identifiers from the
versioned python modules (e.g. :mod:`rdflib.v7`) into the main python module
(i.e. :mod:`rdflib`) and remove the identifiers that were marked as deprecated.

Use the ``rdflib._version._ENABLE_V{major_version}`` flags
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With each released of RDFLib the corresponding
``rdflib._version._ENABLE_V{major_version}`` variable will be set to `True`.

These variables can be used to select default values or change other behavior of
functions, for example changing the default format for `rdflib.graph.Graph.serialize`.

Boolean flags are used as they can be used with the ``always_true`` and
``always_false`` `directives from mypy
<https://mypy.readthedocs.io/en/stable/config_file.html#confval-always_true>`_.

Python modules
--------------

This section describes Python modules that are relevant to the management of
RDFLib's public interface.

Top-level Python modules
^^^^^^^^^^^^^^^^^^^^^^^^

:mod:`rdflib`, the main Python module:
    This is the main Python module for RDFLib and represents the public
    interface of the current version of RDFLib.

``rdflib{major_version}`` (e.g. :mod:`rdflib.v7`), versioned modules:
    These modules are for parts of RDFLib public interface specific to a major
    version, and is intended to be imported into the main RDFLib module (i.e.
    :mod:`rdflib`) for RDFLib releases with the same or later major version.

    So for example, identifiers from the :mod:`rdflib.v7` module should not be
    imported as public identifiers into :mod:`rdflib` until version 7 of RDFLib
    is released but may be symlinked into :mod:`rdflib` from version 7 and
    onward.

    These modules exist to facilitate integrating code into the main branch that
    should go into future major versions of RDFLib, and in most cases will be
    used for things that replace parts of the older interface.

    Versioned modules part of the public RDFLib interface, and once something
    appears in a versioned module it should remain part of the public interface
    until the next major version of RDFLib.

    That is, things from :mod:`rdflib.v7` should not be removed until version 8 of
    RDFLib is released.


Provisional Python modules
^^^^^^^^^^^^^^^^^^^^^^^^^^

``rdflib._provisional`` and ``rdflib.v{major_version}._provisional`` (e.g. ``rdflib.v7._provisional``), provisional modules:
    These modules contain code that is expected to become part of :mod:`rdflib`
    and ``rdflib.v{major_version}`` respectively but may change before this
    happens.

    Given that the provisional modules are marked for internal use (i.e.
    prefixed with an underscore ``_``) they are not considered part of RDFLib's
    public interface and therefore the guarantees associated with RDFLib's
    public interface does not extend to content of these modules, however, there
    is some expectation that the provisional module will be used and to minimize
    the impact to users of the provisional module anything that is moved out of
    the provisional module into the main or versioned RDFLib modules will be
    imported back into the provisional module so that code that used the
    provisional interface can potentially still remain operational.

Practical Examples
------------------

Glossary
--------

`Python identifier <https://docs.python.org/3/reference/lexical_analysis.html#identifiers>`_
    The name of a module, variable, class, function, or function argument. In
    some cases this is also referred to as a Python name.

Backwards incompatible change
    A change to RDFLib that require changes to code that use RDFLib in order for
    that code to keep performing the same function. Also referred to as a
    breaking change.

`Public interface <https://en.wikipedia.org/wiki/Public_interface>`_
    The parts of RDFLib that are intended for use by the users of RDFLib. This
    more or less corresponds to the identifiers that are not directly or
    indirectly marked as internal by prefixing them or packages containing them
    with a single leading underscore [PEP8]_.

Public Python identifier
    A Python identifier that qualifies as part of a public interface.

`Python module <https://docs.python.org/3/glossary.html#term-module>`_
    "An object that serves as an organizational unit of Python code. Modules
    have a namespace containing arbitrary Python objects. Modules are loaded
    into Python by the process of importing."

    The phrase "Python module" is used preferentially over `Python package
    <https://docs.python.org/3/glossary.html#term-package>`_ as it is less
    ambiguous.

References
----------

.. [PEP8] `PEP 8 – Style Guide for Python Code
    <https://peps.python.org/pep-0008/>`_
.. [SEMVER] `Semantic Versioning 2.0.0 <https://semver.org/spec/v2.0.0.html>`_
