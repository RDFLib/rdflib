""" The PyLD module is used to process JSON-LD. """
from . import jsonld
from .context_resolver import ContextResolver

__all__ = ['jsonld', 'ContextResolver']
