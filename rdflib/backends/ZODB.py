##############################################################################
#
# Copyright (c) 2004-1005 Michel Pelletier
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

Any = None

from rdflib.backends.IOMemory import IOMemory
from persistent import Persistent
from BTrees.IOBTree import IOBTree
from BTrees.OIBTree import OIBTree

class IOMemory(Persistent, IOMemory):

    def createForward(self):
        return IOBTree()

    def createReverse(self):
        return OIBTree()

    def createIndex(self):
        return IOBTree()

