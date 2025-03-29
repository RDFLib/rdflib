"""
HextuplesSerializer RDF graph serializer for RDFLib.
See <https://github.com/ontola/hextuples> for details about the format.
"""
# from this import d
from typing import IO, Optional, Type, Union
import json
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib.term import Literal, URIRef, Node, BNode, RdfstarTriple
from rdflib.serializer import Serializer
from rdflib.namespace import RDF, XSD
import warnings
import rdflib

__all__ = ["NtriplesStarSerializer"]
from rdflib import Namespace, Graph
RDFSTAR = Namespace("https://w3id.org/rdf-star/")

class NtriplesStarSerializer(Serializer):
    """
    Serializes RDF graphs to NTriples format.
    """

    def __init__(self, store: Union[Graph, ConjunctiveGraph]):
        self.default_context: Optional[Node]
        self.graph_type: Type[Graph]
        if isinstance(store, ConjunctiveGraph):
            self.graph_type = ConjunctiveGraph
            self.contexts = list(store.contexts())
            if store.default_context:
                self.default_context = store.default_context
                self.contexts.append(store.default_context)
            else:
                self.default_context = None
        else:
            self.graph_type = Graph
            self.contexts = [store]
            self.default_context = None

        Serializer.__init__(self, store)

    def serialize(
        self,
        stream: IO[bytes],
        base: Optional[str] = None,
        encoding: Optional[str] = "utf-8",
        **kwargs,
    ):
        if base is not None:
            warnings.warn(
                "base has no meaning for Hextuples serialization. "
                "I will ignore this value"
            )

        if encoding not in [None, "utf-8"]:
            warnings.warn(
                f"Hextuples files are always utf-8 encoded. "
                f"I was passed: {encoding}, "
                "but I'm still going to use utf-8 anyway!"
            )

        if self.store.formula_aware is True:
            raise Exception(
                "Hextuple serialization can't (yet) handle formula-aware stores"
            )
        dictionary = {}
        blanknode_dictionary = {}
        result_subject = ""
        result_object = ""

        def update_dictionary_RdfstarTriple(node, g, dictionary, properties, collection_or_not, quoted_Bnode_or_not, blanknode_dictionary):
            quoted_Bnode_or_not = False
            # print("update_dictionary_RdfstarTriple", node )
            if type(node) == rdflib.term.BNode:
                for s, p, o in g.triples((node, None, None)):
                    if (isinstance(s, rdflib.term.BNode) & (not isinstance(o, rdflib.term.BNode)) & (not isinstance(o, rdflib.term.RdfstarTriple)) & ((not isinstance(p, rdflib.term.BNode)) & (not isinstance(p, rdflib.term.RdfstarTriple)))):
                        pass
                        # print("here", node)
                        if isinstance(p, rdflib.term.URIRef):
                            p = "<"+str(p)+">"
                        elif isinstance(p, rdflib.term.Literal):
                            p = p._literal_n3(use_plain=True)

                        if isinstance(s, rdflib.term.BNode):
                            s = "_:"+str(s)

                        if isinstance(o, rdflib.term.URIRef):
                            o = "<"+str(o)+">"
                        elif isinstance(o, rdflib.term.Literal):
                            o = o._literal_n3(use_plain=True)
                        elif isinstance(o, rdflib.term.BNode):
                            o = "_:"+str(o)

                        if not (node in blanknode_dictionary):

                            blanknode_dictionary[node] = [p, o]

                        elif ((p in blanknode_dictionary[node]) & (o in blanknode_dictionary[node])):
                            pass
                        else:

                            blanknode_dictionary[node].append(";")
                            blanknode_dictionary[node].append(p)
                            blanknode_dictionary[node].append(o)

                    else:

                        if ("http://www.w3.org/1999/02/22-rdf-syntax-ns#first" in p) or ("http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" in p):
                            collection_or_not  =  True
                            quoted_Bnode_or_not = False

                            if o in dictionary:
                                properties.append(dictionary[o])
                            elif not ("http://www.w3.org/1999/02/22-rdf-syntax-ns#nil"  in o):
                                if (not ("http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" in p) and (not isinstance(o, rdflib.term.RdfstarTriple))):
                                    properties.append("(")
                                expand_Bnode_and_RdfstarTriple(o, g, dictionary,properties, collection_or_not, quoted_Bnode_or_not)

                                if (not ("http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" in p)and (not isinstance(o, rdflib.term.RdfstarTriple))):
                                    properties.append(")")

                        else:
                            if ((not isinstance(o, rdflib.term.BNode)) & (not isinstance(o, rdflib.term.RdfstarTriple)) & ((not isinstance(p, rdflib.term.BNode)) & (not isinstance(p, rdflib.term.RdfstarTriple)))):
                                pass

                            else:
                                collection_or_not = False
                                quoted_Bnode_or_not = False

                                if (isinstance(p, rdflib.term.URIRef)):
                                    p = "<"+str(p)+">"
                                elif isinstance(p, rdflib.term.Literal):
                                    p = p._literal_n3(use_plain=True)

                                    pass
                                properties.append(p)
                                if o in dictionary:
                                    properties.append(dictionary[o])
                                else:
                                    update_dictionary_RdfstarTriple(o, g, dictionary,properties, collection_or_not, quoted_Bnode_or_not, blanknode_dictionary)

            if type(node) == rdflib.term.RdfstarTriple:
                collection_or_not = False
                quoted_Bnode_or_not = True
                if node in dictionary:
                    pass
                else:

                    subject = node.subject()
                    predicate = node.predicate()
                    object = node.object()

                    if subject in dictionary:
                        subject = dictionary[subject]

                    if object in dictionary:
                        object = dictionary[object]

                    subjectexpandable = ((type(subject) == rdflib.term.BNode) or (type(subject) == rdflib.term.RdfstarTriple))
                    objectexpandable = ((type(object) == rdflib.term.BNode) or (type(object) == rdflib.term.RdfstarTriple))

                    if (isinstance(subject, rdflib.term.URIRef)):
                        # print("tttttttttttuuuuuuuuuuuuuu")
                        subject = "<"+str(subject)+">"
                    elif isinstance(subject, rdflib.term.BNode):
                        subject = "_:"+str(subject)
                    elif isinstance(subject, rdflib.term.Literal):
                        subject = subject._literal_n3(use_plain=True)

                    if (isinstance(object, rdflib.term.URIRef)):
                        # print("tttttttttttuuuuuuuuuuuuuu")
                        object = "<"+str(object)+">"
                    elif isinstance(object, rdflib.term.Literal):
                        object = object._literal_n3(use_plain=True)
                    elif isinstance(object, rdflib.term.BNode):
                       object = "_:"+str(object)
                    if isinstance(predicate, rdflib.term.URIRef):
                        predicate = "<"+str(predicate)+">"

                    if subjectexpandable:
                        result_object, ifcollection, ifquotedBnode, d1 = update_dictionary_RdfstarTriple(subject, g, dictionary,properties, collection_or_not, quoted_Bnode_or_not, blanknode_dictionary)
                        if isinstance(subject, rdflib.term.RdfstarTriple):
                            subject = d1[subject]
                        elif isinstance(subject, rdflib.term.BNode):
                            subject = "_:"+str(subject)

                    if objectexpandable:
                        result_object, ifcollection, ifquotedBnode, d2  = update_dictionary_RdfstarTriple(object, g, dictionary,properties, collection_or_not, quoted_Bnode_or_not, blanknode_dictionary)
                        if isinstance(object, rdflib.term.RdfstarTriple):
                            object = d2[object]
                        elif isinstance(object, rdflib.term.BNode):
                            object = "_:"+str(object)

                    if ((not subjectexpandable) and (not objectexpandable)):

                        dictionary[node] = "<<" + " "+str(subject)+ " "+str(predicate) + " "+str(object) + " "+">>"

                    if node not in dictionary:

                        dictionary[node] = "<<" + " "+str(subject)+ " "+str(predicate) + " "+str(object) + " "+">>"

                    else:
                        pass
            return properties, collection_or_not, quoted_Bnode_or_not, dictionary

        def expand_Bnode_and_RdfstarTriple(node, g, dictionary, properties, collection_or_not, quoted_Bnode_or_not):

            quoted_Bnode_or_not = False
            if type(node) == rdflib.term.BNode:
                for s, p, o in g.triples((node, None, None)):
                    if (isinstance(s, rdflib.term.BNode) & (not isinstance(o, rdflib.term.BNode)) & (not isinstance(o, rdflib.term.RdfstarTriple)) & ((not isinstance(p, rdflib.term.BNode)) & (not isinstance(p, rdflib.term.RdfstarTriple)))):
                        pass
                    else:

                        if ("http://www.w3.org/1999/02/22-rdf-syntax-ns#first" in p) or ("http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" in p):
                            collection_or_not  =  True
                            quoted_Bnode_or_not = False
                            if o in dictionary:
                                properties.append(dictionary[o])

                            elif not ("http://www.w3.org/1999/02/22-rdf-syntax-ns#nil"  in o):

                                if (not ("http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" in p) and (not isinstance(o, rdflib.term.RdfstarTriple))):
                                    properties.append("(")

                                expand_Bnode_and_RdfstarTriple(o, g, dictionary,properties, collection_or_not, quoted_Bnode_or_not)

                                if (not ("http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" in p)and (not isinstance(o, rdflib.term.RdfstarTriple))):
                                    properties.append(")")

                        else:

                            if ((not isinstance(o, rdflib.term.BNode)) & (not isinstance(o, rdflib.term.RdfstarTriple)) & ((not isinstance(p, rdflib.term.BNode)) & (not isinstance(p, rdflib.term.RdfstarTriple)))):
                                pass

                            else:
                                collection_or_not = False
                                quoted_Bnode_or_not = False

                                if (isinstance(p, rdflib.term.URIRef)):
                                    p = "<"+str(p)+">"
                                elif isinstance(p, rdflib.term.Literal):
                                    p = p._literal_n3(use_plain=True)
                                    pass
                                properties.append(p)
                                if o in dictionary:
                                    properties.append(dictionary[o])
                                else:
                                    expand_Bnode_and_RdfstarTriple(o, g, dictionary,properties, collection_or_not, quoted_Bnode_or_not)

            if type(node) == rdflib.term.RdfstarTriple:
                ollection_or_not = False
                quoted_Bnode_or_not = True
                if node in dictionary:
                    properties.append(dictionary[node])

                else:

                    subject = node.subject()
                    predicate = node.predicate()
                    object = node.object()
                    if subject in dictionary:

                        subject = dictionary[subject]
                    if object in dictionary:

                        object = dictionary[object]
                    subjectexpandable = ((type(subject) == rdflib.term.BNode) or (type(subject) == rdflib.term.RdfstarTriple))
                    objectexpandable = ((type(object) == rdflib.term.BNode) or (type(object) == rdflib.term.RdfstarTriple))

                    if (isinstance(subject, rdflib.term.URIRef)):

                        subject = "<"+str(subject)+">"
                    elif isinstance(subject, rdflib.term.Literal):
                        subject = subject._literal_n3(use_plain=True)
                    elif isinstance(subject, rdflib.term.RdfstarTriple):
                        subject = dictionary[subject]
                    elif isinstance(subject, rdflib.term.BNode):


                        if subject in blanknode_dictionary:
                            subject = "["+"".join(blanknode_dictionary[subject])+"]"
                        else:

                            subject = "_:"+str(subject)


                    if (isinstance(object, rdflib.term.URIRef)):

                        object = "<"+str(object)+">"
                    elif isinstance(object, rdflib.term.Literal):
                        object = object._literal_n3(use_plain=True)
                    elif isinstance(object, rdflib.term.RdfstarTriple):
                        object = dictionary[object]
                    elif isinstance(object, rdflib.term.BNode):
                        if object in blanknode_dictionary:
                            object = "["+"".join(blanknode_dictionary[object])+"]"
                        else:
                            object = "_:"+str(object)

                    if isinstance(predicate, rdflib.term.URIRef):
                        predicate = "<"+str(predicate)+">"

                    if ((not subjectexpandable) and (not objectexpandable)):

                        dictionary[node] = "<<" + " "+str(subject)+ " "+str(predicate) + " "+str(object) + " "+">>"
                    if node not in dictionary:
                        dictionary[node] = "<<" + " "+str(subject)+ " "+str(predicate) + " "+str(object) + " "+">>"
                        properties.append("<<" + " "+str(subject)+ " "+str(predicate) + " "+str(object) + " "+">>")
                    else:
                        properties.append(dictionary[node])

            return properties, collection_or_not, quoted_Bnode_or_not, dictionary

        # this loop is for updating the quoted triple dictionary and blank node dictionary
        for g in self.contexts:

            for s,p,o in g.triples((None, None, None)):

                if (isinstance(s, rdflib.term.BNode) & (isinstance(o, rdflib.term.BNode)  or isinstance(o, rdflib.term.RdfstarTriple) or isinstance(p, rdflib.term.BNode) or isinstance(p, rdflib.term.RdfstarTriple))):
                    pass
                elif("http://www.w3.org/1999/02/22-rdf-syntax-ns#first" in p or "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" in p):
                    pass
                else:
                    subject = s
                    predicate = p
                    object = o

                    properties = []
                    collection_or_not = False
                    quoted_Bnode_or_not = False
                    if (isinstance(subject, rdflib.term.URIRef)):

                        subject = "<"+str(subject)+">"
                    elif isinstance(subject, rdflib.term.Literal):
                        subject = subject._literal_n3(use_plain=True)
                    elif (isinstance(subject, rdflib.term.BNode) or isinstance(subject, rdflib.term.RdfstarTriple)):
                        thenode_id = str(subject)

                        result_subject, ifcollection, ifquotedBnode, dictionary = update_dictionary_RdfstarTriple(subject,g,dictionary,properties,collection_or_not, quoted_Bnode_or_not, blanknode_dictionary)

                        if (not len(result_subject) == 0):
                            if ifcollection == True:
                                result_subject.insert(0, "(")
                                result_subject.append(")")
                            elif subject in blanknode_dictionary:
                                subject = "["+"".join(blanknode_dictionary[subject])+"]"
                            elif ifquotedBnode:
                                pass
                            else:

                                result_subject.insert(0, "[")
                                result_subject.append("]")
                            subject = "".join(result_subject)

                        else:


                            subject = "[]"
                        if subject == "[]":

                            subject = " _:"+thenode_id


                    if (isinstance(object, rdflib.term.URIRef)):
                        object = "<"+str(object)+">"
                    elif isinstance(object, rdflib.term.Literal):
                        object = object._literal_n3(use_plain=True)
                    elif (isinstance(object, rdflib.term.BNode) or isinstance(object, rdflib.term.RdfstarTriple)):
                        thenode_id = str(object)
                        result_object, ifcollection, ifquotedBnode, dictionary = update_dictionary_RdfstarTriple(object,g,dictionary,properties,collection_or_not, quoted_Bnode_or_not, blanknode_dictionary)

                        if (not len(result_object) == 0):
                            if ifcollection == True:
                                result_object.insert(0, "(")
                                result_object.append(")")

                            elif object in blanknode_dictionary:
                                object = "["+"".join(blanknode_dictionary[object])+"]"
                            elif ifquotedBnode:
                                pass
                            else:
                                result_object.insert(0, "[")
                                result_object.append("]")
                            object = "".join(result_object)

                        else:
                            object = "[]"
                        if object == "[]":

                            object = " _:"+thenode_id


                    if(isinstance(predicate, rdflib.term.URIRef)):
                        predicate = "<"+str(predicate)+">"

        # this loop is for serializing results
        for g in self.contexts:

            for s,p,o in g.triples((None, None, None)):

                if s in blanknode_dictionary:

                    re1 = False
                    re2 = False
                    if len(blanknode_dictionary[s]) < 4:

                        re2 = True

                else:
                    re2 = False
                    re1 = True


                if re1 or re2:
                    if (isinstance(s, rdflib.term.BNode) & (isinstance(o, rdflib.term.BNode)  or isinstance(o, rdflib.term.RdfstarTriple) or isinstance(p, rdflib.term.BNode) or isinstance(p, rdflib.term.RdfstarTriple))):
                        pass
                    elif("http://www.w3.org/1999/02/22-rdf-syntax-ns#first" in p or "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" in p):
                        pass
                    else:

                        subject = s
                        predicate = p
                        object = o


                        properties = []
                        collection_or_not = False
                        quoted_Bnode_or_not = False

                        if (isinstance(subject, rdflib.term.URIRef)):

                            subject = "<"+str(subject)+">"
                        elif isinstance(subject, rdflib.term.Literal):
                            subject = subject._literal_n3(use_plain=True)
                        elif (isinstance(subject, rdflib.term.BNode) or isinstance(subject, rdflib.term.RdfstarTriple)):
                            thenode_id = str(subject)

                            result_subject, ifcollection, ifquotedBnode, d = expand_Bnode_and_RdfstarTriple(subject,g,dictionary,properties,collection_or_not, quoted_Bnode_or_not)

                            if (not len(result_subject) == 0):
                                if ifcollection == True:
                                    result_subject.insert(0, "(")
                                    result_subject.append(")")

                                elif ifquotedBnode:
                                    pass
                                else:

                                    result_subject.insert(0, "[")
                                    result_subject.append("]")
                                subject = "".join(result_subject)
                            else:
                                if (subject in blanknode_dictionary):
                                    if(len(blanknode_dictionary[subject])>2):
                                        subject = "["+"".join(blanknode_dictionary[subject])+"]"
                                    else:
                                        subject = "[]"
                                else:
                                    subject = "[]"
                            if subject == "[]":

                                subject = " _:"+thenode_id
                            properties = []


                        if (isinstance(object, rdflib.term.URIRef)):
                            object = "<"+str(object)+">"
                        elif isinstance(object, rdflib.term.Literal):
                            object = object._literal_n3(use_plain=True)
                        elif (isinstance(object, rdflib.term.BNode) or isinstance(object, rdflib.term.RdfstarTriple)):
                            thenode_id = str(object)
                            result_object, ifcollection, ifquotedBnode, d = expand_Bnode_and_RdfstarTriple(object,g,dictionary,properties,collection_or_not, quoted_Bnode_or_not)


                            if (not len(result_object) == 0):
                                if ifcollection == True:
                                    result_object.insert(0, "(")
                                    result_object.append(")")
                                # elif ifquotedBnode:

                                elif ifquotedBnode:
                                    pass
                                else:
                                    result_object.insert(0, "[")
                                    result_object.append("]")
                                object = "".join(result_object)
                            else:
                                if (object in blanknode_dictionary):
                                    if(len(blanknode_dictionary[object])>2):
                                        object = "["+"".join(blanknode_dictionary[object])+"]"
                                    else:
                                        object = "[]"
                                else:
                                    object = "[]"

                            if object == "[]":

                                object = " _:"+thenode_id
                            properties = []

                        if(isinstance(predicate, rdflib.term.URIRef)):
                            predicate = "<"+str(predicate)+">"

                        output = subject+" "+predicate+" "+object+" ."+"\n"
                        if output is not None:
                            stream.write(output.encode())



    def _iri_or_bn(self, i_):
        if isinstance(i_, URIRef):
            return f"{i_}"
        elif isinstance(i_, BNode):
            return f"{i_.n3()}"
        else:
            return None

    def _context(self, context):
        if self.graph_type == Graph:
            return ""
        if context.identifier == "urn:x-rdflib:default":
            return ""
        elif context is not None and self.default_context is not None:
            if context.identifier == self.default_context.identifier:
                return ""
        return context.identifier
