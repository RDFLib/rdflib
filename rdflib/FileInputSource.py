from xml.sax.xmlreader import InputSource

class FileInputSource(InputSource, object):
    def __init__(self, file):
        super(FileInputSource, self).__init__(`file`)
        self.file = file
        self.setByteStream(file)
        # TODO: self.setEncoding(encoding)

    def __repr__(self):
        return `self.file`
