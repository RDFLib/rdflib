from rdflib.store.AbstractInformationStore import AbstractInformationStore
from rdflib.store.ZBacked import ZBacked

from rdflib.model.schema import Schema
from rdflib.syntax.loadsave import LoadSave


class ZInformationStore(Schema, LoadSave, ZBacked, AbstractInformationStore):
    """
    """
    def __init__(self, path=None):
        super(ZInformationStore, self).__init__()
        if path:
            self.open(path)

    def open(self, path):
        super(ZInformationStore, self).open(path)
        self.schedule_init()
        self.schedule_seeAlso()

                


