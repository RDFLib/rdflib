#$Id: Factory.py,v 1.1 2003/11/14 18:34:27 kendall Exp $

class TripleStoreFactory(object):

    def make(self): pass

    serializers = property(getSerializers, setSerializers, None, None)
    backend = property(getBackend, setBackend, None, None)
    parsers = property(getParsers, setParsers, None, None)
    contexts = property(getContexs, setContexts, None, None)

def makeStore(backend="in-mem", contexts=False, parsers=True,
              serializers=True): pass

#serializers: ..., ...
#back-ends  : ..., ...
#parsers    : ...,


if __name__ == "__main__":
    ts = makeStore()#all of the defaults
