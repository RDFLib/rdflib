import unittest
import pkgutil
#import inspect

import rdflib


class A(unittest.TestCase):


    def test_module_names(self, module=rdflib):
        for importer, name, ispkg in pkgutil.iter_modules(rdflib.__path__):
            if ispkg:
                pass # TODO: complete me ;)
            else:
                self.assert_(name==name.lower(), "module name '%s' is not lower case" % name)


if __name__ == "__main__":
    unittest.main()

