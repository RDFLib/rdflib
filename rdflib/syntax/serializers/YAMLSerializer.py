#$Id: YAMLSerializer.py,v 1.3 2003/10/28 05:14:13 eikeon Exp $

from rdflib.syntax.serializer import AbstractSerializer

class YAMLSerializer(AbstractSerializer):

    short_name = "yaml"

    def __init__(self, store):
        super(YAMLSerializer, self).__init__(store)

    def __write_body(self, stream):
        encoding = self.encoding
        writeln = lambda str: stream.write((str + u"\n").encode(encoding, "replace"))
        writeln(u"model: !set")
        node_cache = dict()
        counter = 1
        for triple in self.store: 
            s, p, o = triple
            writeln(u"?")
            #s
            if node_cache.has_key(s):
                writeln(u"  s: " + node_cache.get(s))
            else:
                node_id = counter; counter += 1
                node_cache[s] = "*yn" + str(counter)
                writeln(u"  s: " + u"&yn" + str(node_id) + u" " + s.yaml())
            #p
            if node_cache.has_key(p):
                writeln(u"  p: " + node_cache.get(p))
            else:
                node_id = counter; counter += 1
                node_cache[p] = "*yn-" + str(counter)
                writeln(u"  p: " + u"&yn" + str(node_id) + u" " + p.yaml())
            #o 
            writeln(u"  o: " + o.yaml())
        writeln(u"...")

    #http://rdf.yaml.org to appear soon in support of this serialization scheme
    #it's legal YAML and treats RDF graphs as sets of s,p,o mappings, along with
    #support for asserted and named graph metadata bits, a la TRiX.
    #TODO:
    #  1. write up the more graphy, concise serialization style Clark Evans suggested
    #  2. write up a doc for yaml.rdf.org
    #  3. submit a W3C Note -- with danbri? -- about the YAML serialization of RDF
    #  4. add support here for multigraph serializations in one YAML stream, a la TRiX
    #  5. optimize the for-loop in __write_body 
    
    def __write_prolog(self, stream):
        """ I make the prolog part of the YAML document."""
        encoding = self.encoding
        writeln = lambda str: stream.write((str + u"\n").encode(encoding, "replace"))
        writeln(u"--- %YAML:1.0 !monkeyfist.com,2004-06/kendall/rdf/^model")
        if hasattr(self.store, "asserted") and hasattr(self.store, "name"):
            if self.store.asserted:
                writeln(u"asserted: " + u"true")
            else:
                writeln(u"asserted: " + u"false")
            writeln(u"name: " + self.store.name + u"\n") 

    def serialize(self, stream):
        self.__write_prolog(stream)
        self.__write_body(stream)
