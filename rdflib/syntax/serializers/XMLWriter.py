import codecs
from xml.sax.saxutils import quoteattr, escape


class XMLWriter(object):
    def __init__(self, stream, qname_provider, encoding=None, decl=1):
        encoding = encoding or 'utf-8'
        encoder, decoder, stream_reader, stream_writer = codecs.lookup(encoding)
        self.stream = stream = stream_writer(stream)
        if decl:
            stream.write('<?xml version="1.0" encoding="%s"?>' % encoding)
        self.element_stack = []
        self.qp = qname_provider
        self.closed = True
        
    def __get_indent(self):
        return "  " * len(self.element_stack)
    indent = property(__get_indent)
    
    def __close_start_tag(self):
        if not self.closed: # TODO:
            self.closed = True
            self.stream.write(">")
        
    def push(self, uri):
        qp = self.qp
        self.__close_start_tag()        
        write = self.stream.write
        write("\n")
        write(self.indent)            
        write("<%s" % qp.get(uri))
        self.element_stack.append(uri)
        self.closed = False
        self.parent = False

    def pop(self, uri=None):
        top = self.element_stack.pop()
        if uri:
            assert uri==top
        write = self.stream.write            
        if not self.closed:
            self.closed = True
            write("/>")
        else:
            if self.parent:
                write("\n")
                write(self.indent)
            write("</%s>" % self.qp.get(uri))
        self.parent = True

    def namespaces(self, namespaces):
        write = self.stream.write
        write("\n")
        for prefix, namespace in namespaces:
            if prefix:
                write("  xmlns:%s='%s'\n" % (prefix, namespace))
            else:
                write("  xmlns='%s'\n" % namespace)

    def attribute(self, uri, value):
        write = self.stream.write
        write(" %s=%s" % (self.qp.get(uri), quoteattr(value)))


    def text(self, text):
        self.__close_start_tag()
        self.stream.write(escape(text))
