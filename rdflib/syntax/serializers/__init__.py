__all__ = ["N3Serializer", "NTSerializer", "XMLSerializer", "YAMLSerializer"]

# Automagical way:
#
# from glob import glob
# import os.path


# dir = os.path.join("rdflib/syntax/serializers")

# __all__ = map(lambda a: os.path.split(a)[1][:-3],
#               glob(os.path.join(dir, "*.py")))

# #TODO: filter instead
# try:
#     __all__.remove("__init__")
# except:
#     pass
