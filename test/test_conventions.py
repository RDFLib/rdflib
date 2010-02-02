import unittest
import pkgutil
import os.path

import rdflib


class A(unittest.TestCase):


    def test_module_names(self, path=None):
        if path is None:
            path = rdflib.__path__

            # TODO: handle cases where len(path) is not 1
            assert len(path)==1, "We're assuming the path has exactly one item in it for now"
            path = path[0]

        for importer, name, ispkg in pkgutil.iter_modules([path]):
            if ispkg:
                self.test_module_names(path=os.path.join(path, name))
            else:
                self.assert_(name==name.lower(), "module name '%s' is not lower case" % name)


if __name__ == "__main__":
    unittest.main()

