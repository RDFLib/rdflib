"""
Representation for a resolved Context.
.. module:: resolved_context
  :synopsis: Creates a ContextResolver
.. moduleauthor:: Dave Longley
.. moduleauthor:: Gregg Kellogg <gregg@greggkellogg.net>
"""

from cachetools import LRUCache

MAX_ACTIVE_CONTEXTS = 10


class ResolvedContext:
    """
    A cached contex document, with a cache indexed by referencing active context.
    """

    def __init__(self, document):
        """
        Creates a ResolvedContext with caching for processed contexts
        relative to some other Active Context.
        """
        # processor-specific RDF parsers
        self.document = document
        self.cache = LRUCache(maxsize=MAX_ACTIVE_CONTEXTS)

    def get_processed(self, active_ctx):
        """
        Returns any processed context for this resolved context relative to an active context.
        """
        return self.cache.get(active_ctx['_uuid'])

    def set_processed(self, active_ctx, processed_ctx):
        """
        Sets any processed context for this resolved context relative to an active context.
        """
        self.cache[active_ctx['_uuid']] = processed_ctx
