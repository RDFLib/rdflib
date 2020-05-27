import sys

IS_PY3 = sys.version_info[0] >= 3

str = str if IS_PY3 else str  # noqa
str = str if IS_PY3 else str  # noqa
