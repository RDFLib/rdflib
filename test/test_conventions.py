import unittest
import pkgutil
import os.path

import rdflib

"""
Test module naming conventions

modules should all be lower-case initial
"""

class A(unittest.TestCase):

    def module_names(self, path=None, names=None):

        skip_as_ignorably_private = ['embeddedRDF', 'OpenID', 'DublinCore']

        if path is None:
            path = rdflib.__path__
        if names is None:
            names = set()

            # TODO: handle cases where len(path) is not 1
            assert len(path)==1, "We're assuming the path has exactly one item in it for now"
            path = path[0]

        for importer, name, ispkg in pkgutil.iter_modules([path]):
            if ispkg:
                result = self.module_names(path=os.path.join(path, name), 
                                           names=names)
                names.union(result)
            else:
                if name!=name.lower() and name not in skip_as_ignorably_private:
                    names.add(name)
        return names

    def test_module_names(self):
        names = self.module_names()
        self.assertTrue(names==set(), "module names '%s' are not lower case" % names)

try:
    getattr(pkgutil, 'iter_modules')
except AttributeError:
    from nose import SkipTest
    raise SkipTest('pkgutil.iter_modules not available in Python 2.4')


if __name__ == "__main__":
    unittest.main()

