import unittest
import inspect

import rdflib


class A(unittest.TestCase):
    known_issue = True

    def test_module_names(self):        
        for name, value in inspect.getmembers(rdflib, inspect.ismodule):
            self.assert_(name==name.lower(), "module name '%s' is not lower case" % name)


if __name__ == "__main__":
    unittest.main()

