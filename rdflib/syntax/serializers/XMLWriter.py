import codecs
from xml.sax.saxutils import quoteattr, escape


class XMLWriter(object):
    def __init__(self, stream, namespace_manager, encoding=None, decl=1):
        encoding = encoding or 'utf-8'
        encoder, decoder, stream_reader, stream_writer = codecs.lookup(encoding)
        self.stream = stream = stream_writer(stream)
        if decl:
            stream.write('<?xml version="1.0" encoding="%s"?>' % encoding)
        self.element_stack = []
        self.nm = namespace_manager
        self.closed = True

    def __get_indent(self):
        return "  " * len(self.element_stack)
    indent = property(__get_indent)

    def __close_start_tag(self):
        if not self.closed: # TODO:
            self.closed = True
            self.stream.write(">")

    def push(self, uri):
        nm = self.nm
        self.__close_start_tag()
        write = self.stream.write
        write("\n")
        write(self.indent)
        write("<%s" % nm.qname(uri))
        self.element_stack.append(uri)
        self.closed = False
        self.parent = False

    def pop(self, uri=None):
        top = self.element_stack.pop()
        if uri:
            assert uri == top
        write = self.stream.write
        if not self.closed:
            self.closed = True
            write("/>")
        else:
            if self.parent:
                write("\n")
                write(self.indent)
            write("</%s>" % self.nm.qname(top))
        self.parent = True

    def element(self, uri, content, attributes={}):
        """Utility method for adding a complete simple element"""
        self.push(uri)
        for k, v in attributes.iteritems():
            self.attribute(k,v)
        self.text(content)
        self.pop()

    def namespaces(self, namespaces=None):
        if not namespaces:
            namespaces=self.nm.namespaces()

        write = self.stream.write
        write("\n")
        for prefix, namespace in namespaces:
            if prefix:
                write('  xmlns:%s="%s"\n' % (prefix, namespace))
            else:
                write('  xmlns="%s"\n' % namespace)

    def attribute(self, uri, value):
        write = self.stream.write
        write(" %s=%s" % (self.nm.qname(uri), quoteattr(value)))

    def text(self, text):
        self.__close_start_tag()
        if "<" in text and ">" in text and not "]]>" in text:
            self.stream.write("<![CDATA[")
            self.stream.write(text)
            self.stream.write("]]>")
        else:
            self.stream.write(escape(text))

