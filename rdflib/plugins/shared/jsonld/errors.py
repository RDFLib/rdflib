# -*- coding: utf-8 -*-
# https://github.com/RDFLib/rdflib-jsonld/blob/feature/json-ld-1.1/rdflib_jsonld/errors.py
class JSONLDException(ValueError):
    pass


# http://www.w3.org/TR/json-ld-api/#idl-def-JsonLdErrorCode.{code-message}
RECURSIVE_CONTEXT_INCLUSION = JSONLDException("recursive context inclusion")
INVALID_REMOTE_CONTEXT = JSONLDException("invalid remote context")
