from rdflib.exceptions import ParserDispatchNameError, ParserDispatchNameClashError
import parsers

class AbstractParser(object):

    def __init__(self, store):
        self.__short_name = ""
        self.store = store
        
    def parse(self, source):
        pass


class ParserDispatcher(object):

    def __init__(self, store):
        self.store = store
        for ser in parsers.__all__:
            module = __import__("parsers." + ser, globals(), locals(), ["parsers"])
            aParser  = getattr(module, ser)
            short_name = getattr(aParser, "short_name")
            self.add(aParser, name=short_name)
                                   
    def add(self, parser, name=None):
        #first, check if there's a name or a shortname, else throw exception
        if name != None:
            the_name = name
        elif hasattr(parser, "short_name"):
            the_name = parser.short_name
        else:
            msg = "You didn't set a short name for the parser or pass in a name to add()"
            raise ParserDispatchNameError(msg)
        #check for name clash
        if hasattr(self, the_name):
            raise ParserDispatchNameClashError("That name is already registered.")
        else:
            setattr(self, the_name, parser(self.store))

    def __call__(self, source, format="xml"):
        return getattr(self, format).parse(source)

