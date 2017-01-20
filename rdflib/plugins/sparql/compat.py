"""
Function/methods to help supporting 2.5-2.7
"""

# Collection ABCs

try:
    from collections import Mapping, MutableMapping  # was added in 2.6

except:
    from UserDict import DictMixin

    class MutableMapping(DictMixin):
        def keys(self):
            return list(self)

    Mapping = MutableMapping


# OrderedDict

try:
    from collections import OrderedDict  # was added in 2.7
except ImportError:
    from ordereddict import OrderedDict  # extra module
