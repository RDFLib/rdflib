# -*- coding: utf-8 -*-

import unittest
import binascii
from rdflib import Literal, XSD
import six


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
        self.assertEquals(int(binascii.hexlify(bin_i), 16), i)

        if six.PY2:
            self.assertEquals(unicode(l), hex_i)
        else:
            self.assertEquals(str(l), hex_i)
        self.assertEquals(int(hex_i, 16), i)
        if six.PY2:
            self.assertEquals(int(unicode(l), 16), i)
        else:
            self.assertEquals(int(l, 16), i)
        self.assertEquals(int(str(l), 16), i)

    def test_unicode(self):
        str1 = u"Test utf-8 string éàë"
        # u hexstring
        hex_str1 = binascii.hexlify(str1.encode('utf-8')).decode()
        l1 = Literal(hex_str1, datatype=XSD.hexBinary)
        b_str1 = l1.toPython()
        self.assertEquals(b_str1.decode('utf-8'), str1)
        if six.PY2:
            self.assertEquals(unicode(l1), hex_str1)
        else:
            self.assertEquals(str(l1), hex_str1)

        # b hexstring
        hex_str1b = binascii.hexlify(str1.encode('utf-8'))
        l1b = Literal(hex_str1b, datatype=XSD.hexBinary)
        b_str1b = l1b.toPython()
        self.assertEquals(b_str1, b_str1b)
        self.assertEquals(b_str1b.decode('utf-8'), str1)
        if six.PY2:
            self.assertEquals(unicode(l1b), hex_str1)
        else:
            self.assertEquals(str(l1b), hex_str1)


if __name__ == '__main__':
    unittest.main()
