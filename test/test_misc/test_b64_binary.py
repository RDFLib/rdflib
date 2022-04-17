# -*- coding: utf-8 -*-

import base64

from rdflib import XSD, Literal


class TestB64Binary:
    def test_unicode(self):
        str1 = "Test utf-8 string éàë"
        # u b64string
        b64_str1 = base64.b64encode(str1.encode("utf-8")).decode()
        l1 = Literal(b64_str1, datatype=XSD.base64Binary)
        b_str1 = l1.toPython()
        assert b_str1.decode("utf-8") == str1
        assert str(l1) == b64_str1

        # b b64string
        b64_str1b = base64.b64encode(str1.encode("utf-8"))
        l1b = Literal(b64_str1b, datatype=XSD.base64Binary)
        b_str1b = l1b.toPython()
        assert b_str1 == b_str1b
        assert b_str1b.decode("utf-8") == str1
        assert str(l1b) == b64_str1
