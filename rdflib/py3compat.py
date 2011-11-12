"""
Utility functions and objects to ease Python 3 compatibility.
"""
import sys

try:
    from functools import wraps
except ImportError:
    # No-op wraps decorator
    def wraps(f):
        def dec(newf): return newf
        return dec

def cast_bytes(s, enc='utf-8'):
    if isinstance(s, unicode):
        return s.encode(enc)
    return s

PY3 = (sys.version_info[0] >= 3)

def _modify_str_or_docstring(str_change_func):
    @wraps(str_change_func)
    def wrapper(func_or_str):
        if isinstance(func_or_str, str):
            func = None
            doc = func_or_str
        else:
            func = func_or_str
            doc = func.__doc__
        
        doc = str_change_func(doc)
        
        if func:
            func.__doc__ = doc
            return func
        return doc
    return wrapper
    
if PY3:
    # Python 3:
    # ---------
    def b(s):
        return s.encode('ascii')
    
    bytestype = bytes
    
    # Abstract u'abc' syntax:
    @_modify_str_or_docstring
    def u_format(s):
        """"%(u)s'abc'" --> "'abc'" (Python 3)
        
        Accepts a string or a function, so it can be used as a decorator."""
        return s % {'u':''}

else:
    # Python 2
    # --------
    def b(s):
        return s
    
    bytestype = str
    
    # Abstract u'abc' syntax:
    @_modify_str_or_docstring
    def u_format(s):
        """"%(u)s'abc'" --> "u'abc'" (Python 2)
        
        Accepts a string or a function, so it can be used as a decorator."""
        return s % {'u':'u'}
