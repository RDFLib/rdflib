class JSONLDException(ValueError):
    pass

# http://www.w3.org/TR/json-ld-api/#idl-def-JsonLdErrorCode.{code-message}
RECURSIVE_CONTEXT_INCLUSION = JSONLDException("recursive context inclusion")
INVALID_REMOTE_CONTEXT = JSONLDException("invalid remote context")
