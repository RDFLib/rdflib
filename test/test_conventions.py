import unittest
import pkgutil
import os.path

import rdflib


class A(unittest.TestCase):

    def module_names(self, path=None, names=None):
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
                if name!=name.lower():
                    names.add(name)
                #self.assert_(name==name.lower(), "module name '%s' is not lower case" % name)
        return names

    def test_module_names(self):
        names = self.module_names()
        self.assert_(names==set(), "module names '%s' are not lower case" % names)


if __name__ == "__main__":
    unittest.main()

