Continous Integration
---------------------

We used Travis for CI, see: 

https://travis-ci.org/RDFLib/rdflib

Compatibility
-------------

RDFLib 3.X tries to be compatible with python versions 2.5 - 3

Some of the limitations we've come across:

 * Python 2.5/2.6 has no abstract base classes from collections, such MutableMap, etc. 
 * 2.5/2.6 No skipping tests using unittest, i.e. TestCase.skipTest and decorators are missing => use nose instead
 * no str.decode('string-escape') in py3 
 * no json module in 2.5 (install simplejson instead)
 * no ordereddict in 2.5/2.6 (install ordereddict module)
 * collections.Counter was added in 2.6

Releasing
---------

Set to-be-released version number in *rdflib/__init__.py* , *docs/index.rst* and *docs/conf.py*

Add CHANGELOG entry.

Commit this change, and tag it with `git tag -a -m 'tagged version' X.X.X`

When pushing, remember to `git push --tags`

Do `python setup.py sdist upload` to upload tarball to pypi

Upload *dist/rdflib-X.X.X.tar.gz* to downloads section at Github

Set new dev version number in the above locations, i.e. next release *-dev*: *8.9.2-dev* and commit again. 







