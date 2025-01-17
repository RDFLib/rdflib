.. _type_hints: Type Hints

==========
Type Hints
==========

This document provides some details about the type hints for RDFLib. More information about type hints can be found `here <https://docs.python.org/3/library/typing.html>`_

Rationale for Type Hints
========================

Type hints are code annotations that describe the types of variables, function parameters and function return value types in a way that can be understood by humans, static type checkers like `mypy <http://mypy-lang.org/>`_, code editors like VSCode, documentation generators like Sphinx, and other tools.

Static type checkers can use type hints to detect certain classes of errors by inspection. Code editors and IDEs can use type hints to provide better auto-completion and documentation generators can use type hints to generate better documentation.

These capabilities make it easier to develop a defect-free RDFLib and they also make it easier for users of RDFLib who can now use static type checkers to detect type errors in code that uses RDFLib.

Gradual Typing Process
======================

Type hints are being added to RDFLib through a process called `gradual typing <https://en.wikipedia.org/wiki/Gradual_typing>`_. This process involves adding type hints to some parts of RDFLib while leaving the rest without type hints. Gradual typing is being applied to many, long-lived, Python code bases.

This process is beneficial in that we can realize some of the benefits of type hints without requiring that the whole codebase have type hints.

Intended Type Hints
===================

The intent is to have type hints in place for all of RDFLib and to have these type hints be as accurate as possible.

The accuracy of type hints is determined by both the standards that RDFLib aims to conform to, like RDF 1.1, and the deliberate choices that are made when implementing RDFLib. For example, given that the RDF 1.1 specification stipulates that the subject of an RDF triple cannot be a literal, all functions that accept an *RDF term* to be used as the subject of a triple should have type hints which excludes values that are literals.

There may be cases where some functionality of RDFLib may work perfectly well with values of types that are excluded by the type hints, but if these additional types violate the relevant standards we will consider the correct type hints to be those that exclude values of these types.

Public Type Aliases
===================
In python, type hints are specified in annotations. Type hints are different from type aliases which are normal python variables that are not intended to provide runtime utility and are instead intended for use in static type checking.

For clarity, the following is an example of a function ``foo`` with type hints:

.. code-block:: python
	
    def foo(a: int) -> int:
        return a + 1

In the function ``foo``, the input variable ``a`` is indicated to be of type ``int`` and the function is indicated to return an ``int``.

The following is an example of a type alias ``Bar``:

.. code-block:: python

    from typing import Tuple

    Bar = Tuple[int, str]

RDFLib will provide public type aliases under the ``rdflib.typing`` package, for example, ``rdflib.typing.Triple``, ``rdflib.typing.Quad``. Type aliases in the rest of RDFLib should be private (i.e. being with an underscore).

Versioning, Compatibility and Stability
=======================================

RDFLib attempts to adhere to `semver 2.0 <https://semver.org/spec/v2.0.0.html>`_ which is concerned with the public API of software.

Ignoring type hints, the public API of RDFLib exists implicitly as a consequence of the code of RDFLib and the actual behaviour this entails, the relevant standards that RDFLib is trying to implement, and the documentation of RDFLib, with some interplay between all three of these. RDFLib's public API includes public type aliases, as these are normal python variables and not annotations.

Type hints attempt to formally document RDFLib's implicitly-defined public API in a machine-readable fashion as accurately and correctly as possible within the framework outline earlier in this document.

Type hints do not affect the runtime API or behaviour of RDFLib. In this way then, they are somewhat outside of the scope of semver, however, they still have an impact on the users of RDFLib, even if this impact is not at runtime, but during development. This necessitates some clarity as to what users of RDFLib should expect regarding type hints in RDFLib releases.

Changes to type hints can broadly be classified as follow:

**Type Declaration**
  Adding type hints to existing code that had no explicit type hints, for example, changing

  .. code-block:: python
  
      def foo(val):
          return val + 1
  
  to

  .. code-block:: python
  
      def foo(val: int) -> int:
          return val + 1


**Type Refinement**
  Refining existing type hints to be narrower, for example, changing a type hint of `typing.Collection` to `typing.Sequence`.

**Type Corrections**
  Correcting existing type hints which contradict the behaviour of the code or relevant specifications, for example, changing `typing.Sequence` from `typing.Set`

Given semver version components ``MAJOR.MINOR.PATCH``, RDFLib will attempt to constrain type hint changes as follow:

.. list-table::
   :widths: 1 1 1 1
   :header-rows: 1

   * - Version Component
     - Type Declaration
     - Type Refinement
     - Type Corrections

   * - MAJOR
     - YES
     - YES
     - YES
  
   * - MINOR
     - YES
     - YES
     - YES

   * - PATCH
     - NO
     - NO
     - YES

.. CAUTION::
   A caveat worth nothing here is that code that passed type validation on one version of RDFLib can fail type validation on a later version of RDFLib that only differs in ``PATCH`` version component. This is as a consequence of potential *Type Corrections*.


