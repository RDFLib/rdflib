# -*- coding: utf-8 -*-

import unittest
import binascii
from rdflib import Literal, XSD


class HexBinaryTestCase(unittest.TestCase):
    def test_int(self):
        self._test_integer(5)
        self._test_integer(3452)
        self._test_integer(4886)

    def _test_integer(self, i):
        hex_i = format(i, "x")
        # Make it has a even-length (Byte)
        len_hex_i = len(hex_i)
        hex_i = hex_i.zfill(len_hex_i + len_hex_i % 2)

        l = Literal(hex_i, datatype=XSD.hexBinary)
        bin_i = l.toPython()
        self.assertEqual(int(binascii.hexlify(bin_i), 16), i)

        self.assertEqual(str(l), hex_i)
        self.assertEqual(int(hex_i, 16), i)
        self.assertEqual(int(l, 16), i)
        self.assertEqual(int(str(l), 16), i)

    def test_unicode(self):
        str1 = "Test utf-8 string éàë"
        # u hexstring
        hex_str1 = binascii.hexlify(str1.encode("utf-8")).decode()
        l1 = Literal(hex_str1, datatype=XSD.hexBinary)
        b_str1 = l1.toPython()
        self.assertEqual(b_str1.decode("utf-8"), str1)
        self.assertEqual(str(l1), hex_str1)

        # b hexstring
        hex_str1b = binascii.hexlify(str1.encode("utf-8"))
        l1b = Literal(hex_str1b, datatype=XSD.hexBinary)
        b_str1b = l1b.toPython()
        self.assertEqual(b_str1, b_str1b)
        self.assertEqual(b_str1b.decode("utf-8"), str1)
        self.assertEqual(str(l1b), hex_str1)


if __name__ == "__main__":
    unittest.main()
