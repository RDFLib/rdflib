from rdflib.store.AbstractInformationStore import AbstractInformationStore
from rdflib.store.Spider import Spider
from rdflib.store.SCBacked import SCBacked


class SpiderStore(Spider, SCBacked, AbstractInformationStore):
    """
    """
    def __init__(self, path=None):
        super(SpiderStore, self).__init__()
        if path:
            self.open(path)

    def open(self, path):
        super(SpiderStore, self).open(path)
        self.schedule_init()
        #self.schedule_seeAlso()

                
store = SpiderStore("store")
store.load("http://eikeon.com/foaf.rdf")
store.schedule_seeAlso()
try:
    store.run()
except KeyboardInterrupt:
    store.close()
