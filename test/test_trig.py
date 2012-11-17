import unittest
import rdflib

class TestTrig(unittest.TestCase):
    
    def testEmpty(self): 
        g=rdflib.Graph()
        s=g.serialize(format='trig')
    
        

if __name__ == "__main__":
    unittest.main()