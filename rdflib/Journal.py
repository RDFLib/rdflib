from rdflib.store import TripleAddedEvent, TripleRemovedEvent, StoreCreatedEvent
from rdflib.events import Event

import logging, sys

logger = logging.getLogger("Journal")


class Journal(object):
    """
    Adds journaling to a Graph.
    """

    def __init__(self, store, stream):
        self.stream = stream or sys.stdout
        self.node_pickler = store.node_pickler
        dispatcher = store.dispatcher
        dispatcher.subscribe(TripleAddedEvent, self.journal_event)
        dispatcher.subscribe(TripleRemovedEvent, self.journal_event)
        dispatcher.subscribe(StoreCreatedEvent, self.journal_event)

    def journal_event(self, event):
        self.stream.write(self.node_pickler.dumps((type(event), event.__dict__)))


class FileJournal(Journal):
    def __init__(self, store, filename):
        Journal.__init__(self, store, file(filename, "a"))
