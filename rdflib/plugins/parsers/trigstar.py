
from smtplib import quotedata

# importing typing for `typing.List` because `List`` is used for something else
from typing import IO, TYPE_CHECKING, Any, Callable, Dict, Optional, TypeVar, Union
from uuid import uuid4
from .turtlestar import StarRDFSink, StarsinkParser
from .trig import becauseSubGraph
from rdflib.exceptions import ParserError
from rdflib.graph import ConjunctiveGraph, Graph, QuotedGraph

__all__ = [
    "BadSyntax",
    "N3Parser",
    "TurtleParser",
    "splitFragP",
    "join",
    "base",
    "runNamespace",
    "uniqueURI",
    "hexify",
]

from rdflib.parser import Parser

if TYPE_CHECKING:
    from rdflib.parser import InputSource

AnyT = TypeVar("AnyT")

nextu = 0

from rdflib import ConjunctiveGraph
from rdflib.parser import Parser
from .notation3 import SinkParser, RDFSink

import hashlib
from lark import (
    Lark,
    Transformer,
    Tree,
)
from lark.visitors import Visitor
from lark.reconstruct import Reconstructor

from lark.lexer import (
    Token,
)

from typing import List, Dict, Union, Callable, Iterable, Optional

from lark import Lark
from lark.tree import Tree, ParseTree
from lark.visitors import Transformer_InPlace
from lark.lexer import Token, PatternStr, TerminalDef
from lark.grammar import Terminal, NonTerminal, Symbol

from lark.tree_matcher import TreeMatcher, is_discarded_terminal
from lark.utils import is_id_continue

def is_iter_empty(i):
    try:
        _ = next(i)
        return False
    except StopIteration:
        return True


class WriteTokensTransformer(Transformer_InPlace):
    "Inserts discarded tokens into their correct place, according to the rules of grammar"

    tokens: Dict[str, TerminalDef]
    term_subs: Dict[str, Callable[[Symbol], str]]

    def __init__(self, tokens: Dict[str, TerminalDef], term_subs: Dict[str, Callable[[Symbol], str]]) -> None:
        self.tokens = tokens
        self.term_subs = term_subs

    def __default__(self, data, children, meta):
        if not getattr(meta, 'match_tree', False):
            return Tree(data, children)

        iter_args = iter(children)
        to_write = []
        for sym in meta.orig_expansion:
            if is_discarded_terminal(sym):
                try:
                    v = self.term_subs[sym.name](sym)
                except KeyError:
                    t = self.tokens[sym.name]
                    if not isinstance(t.pattern, PatternStr):
                        raise NotImplementedError("Reconstructing regexps not supported yet: %s" % t)

                    v = t.pattern.value
                to_write.append(v)
            else:
                x = next(iter_args)
                if isinstance(x, list):
                    to_write += x
                else:
                    if isinstance(x, Token):
                        assert Terminal(x.type) == sym, x
                    else:
                        assert NonTerminal(x.data) == sym, (sym, x)
                    to_write.append(x)

        assert is_iter_empty(iter_args)
        return to_write


class Reconstructorv2(TreeMatcher):
    """
    A Reconstructor that will, given a full parse Tree, generate source code.
    Note:
        The reconstructor cannot generate values from regexps. If you need to produce discarded
        regexes, such as newlines, use `term_subs` and provide default values for them.
    Paramters:
        parser: a Lark instance
        term_subs: a dictionary of [Terminal name as str] to [output text as str]
    """

    write_tokens: WriteTokensTransformer

    def __init__(self, parser: Lark, term_subs: Optional[Dict[str, Callable[[Symbol], str]]]=None) -> None:
        TreeMatcher.__init__(self, parser)

        self.write_tokens = WriteTokensTransformer({t.name:t for t in self.tokens}, term_subs or {})

    def _reconstruct(self, tree):
        unreduced_tree = self.match_tree(tree, tree.data)

        res = self.write_tokens.transform(unreduced_tree)
        for item in res:
            if isinstance(item, Tree):
                # TODO use orig_expansion.rulename to support templates
                yield from self._reconstruct(item)
            else:
                yield item

    def reconstruct(self, tree: ParseTree, postproc: Optional[Callable[[Iterable[str]], Iterable[str]]]=None, insert_spaces: bool=True) -> str:
        x = self._reconstruct(tree)
        if postproc:
            x = postproc(x)
        y = []
        prev_item = ''
        for item in x:
            if insert_spaces and prev_item and item and is_id_continue(prev_item[-1]) and is_id_continue(item[0]):
                y.append(' ')
            y.append(item)
            prev_item = item
        return ' '.join(y)
grammar = r"""trig_doc: (directive | block)*
?statement: directive | triples "."
block: triplesorgraph | wrappedgraph | triples2 | "GRAPH" labelorsubject wrappedgraph
triplesorgraph: labelorsubject (wrappedgraph | predicate_object_list ".") | quotation predicate_object_list "."
triples2: blank_node_property_list predicate_object_list? "." | collection predicate_object_list "."
wrappedgraph: "{" triplesblock? "}"
triplesblock: triples ("." triplesblock?)?
labelorsubject: iri | blank_node
directive: prefix_id | base | sparql_prefix | sparql_base
prefix_id: "@prefix" PNAME_NS IRIREF "."
base: BASE_DIRECTIVE IRIREF "."
sparql_base: /BASE/i IRIREF
sparql_prefix: /PREFIX/i PNAME_NS IRIREF
triples: subject predicate_object_list
       | blank_node_property_list predicate_object_list?
insidequotation: qtsubject verb qtobject
predicate_object_list: verb object_list (";" (verb object_list)?)*
?object_list: object compoundanno? ("," object compoundanno?)*
?verb: predicate | /a/
?subject: iri | blank_node | collection | quotation
?predicate: iri
?object: iri | blank_node | collection | blank_node_property_list | literal | quotation
?literal: rdf_literal | numeric_literal | boolean_literal
?qtsubject: iri | blank_node | quotation
?qtobject: 	iri | blank_node | literal | quotation
ANGLEBRACKETL: "<<"
ANGLEBRACKETR: ">>"
quotation: ANGLEBRACKETL insidequotation ANGLEBRACKETR
COMPOUNDL: "{|"
COMPOUNDR: "|}"
compoundanno: COMPOUNDL predicate_object_list COMPOUNDR
blank_node_property_list: "[" predicate_object_list "]"
collection: "(" object* ")"
numeric_literal: INTEGER | DECIMAL | DOUBLE
rdf_literal: string (LANGTAG | "^^" iri)?
boolean_literal: /true|false/
string: STRING_LITERAL_QUOTE
      | STRING_LITERAL_SINGLE_QUOTE
      | STRING_LITERAL_LONG_SINGLE_QUOTE
      | STRING_LITERAL_LONG_QUOTE
iri: IRIREF | prefixed_name
prefixed_name: PNAME_LN | PNAME_NS
blank_node: BLANK_NODE_LABEL | ANON
BASE_DIRECTIVE: "@base"
IRIREF: "<" (/[^\x00-\x20<>"{}|^`\\]/ | UCHAR)* ">"
PNAME_NS: PN_PREFIX? ":"
PNAME_LN: PNAME_NS PN_LOCAL
BLANK_NODE_LABEL: "_:" (PN_CHARS_U | /[0-9]/) ((PN_CHARS | ".")* PN_CHARS)?
LANGTAG: "@" /[a-zA-Z]+/ ("-" /[a-zA-Z0-9]+/)*
INTEGER: /[+-]?[0-9]+/
DECIMAL: /[+-]?[0-9]*/ "." /[0-9]+/
DOUBLE: /[+-]?/ (/[0-9]+/ "." /[0-9]*/ EXPONENT
      | "." /[0-9]+/ EXPONENT | /[0-9]+/ EXPONENT)
EXPONENT: /[eE][+-]?[0-9]+/
STRING_LITERAL_QUOTE: "\"" (/[^\x22\x5C\x0A\x0D]/ | ECHAR | UCHAR)* "\""
STRING_LITERAL_SINGLE_QUOTE: "'" (/[^\x27\x5C\x0A\x0D]/ | ECHAR | UCHAR)* "'"
STRING_LITERAL_LONG_SINGLE_QUOTE: "'''" (/'|''/? (/[^'\\]/ | ECHAR | UCHAR))* "'''"
STRING_LITERAL_LONG_QUOTE: "\"\"\"" (/"|""/? (/[^"\\]/ | ECHAR | UCHAR))* "\"\"\""
UCHAR: "\\u" HEX~4 | "\\U" HEX~8
ECHAR: "\\" /[tbnrf"'\\]/
WS: /[\x20\x09\x0D\x0A]/
ANON: "[" WS* "]"
PN_CHARS_BASE: /[A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\U00010000-\U000EFFFF]/
PN_CHARS_U: PN_CHARS_BASE | "_"
PN_CHARS: PN_CHARS_U | /[\-0-9\u00B7\u0300-\u036F\u203F-\u2040]/
PN_PREFIX: PN_CHARS_BASE ((PN_CHARS | ".")* PN_CHARS)?
PN_LOCAL: (PN_CHARS_U | ":" | /[0-9]/ | PLX) ((PN_CHARS | "." | ":" | PLX)* (PN_CHARS | ":" | PLX))?
PLX: PERCENT | PN_LOCAL_ESC
PERCENT: "%" HEX~2
HEX: /[0-9A-Fa-f]/
PN_LOCAL_ESC: "\\" /[_~\.\-!$&'()*+,;=\/?#@%]/
%ignore WS
COMMENT: "#" /[^\n]/*
%ignore COMMENT
"""

trig_lark = Lark(grammar, start="trig_doc", parser="lalr", maybe_placeholders = False)

class Print_Tree(Visitor):
    def print_quotation(self, tree):
        assert tree.data == "quotation"
        print(tree.children)

from lark import Visitor, v_args
quotation_list = []
quotation_dict = dict()
vblist = []
quotationreif = []
prefix_list = []
quotationannolist = []
constructors = ""
assertedtriplelist = []
quoted_or_not = False
both_quoted_and_asserted = False
object_annotation_list = []
annotation_s_p_o = []
annotation_dict = dict()
to_remove = []
trig_graph = []
output = ""

def myHash(text:str):
  return str(hashlib.md5(text.encode('utf-8')).hexdigest())
class Expandanotation(Visitor):
    global annotation_s_p_o, to_remove
    def __init__(self):
        super().__init__()
        self.variable_list = []

    def triples(self, var):
        tri = Reconstructorv2(trig_lark).reconstruct(var)
        if "{|" in tri:
            if len(var.children) == 2:
                predicate_object_list2 = var.children[1].children
                subject = Reconstructorv2(trig_lark).reconstruct(var.children[0])
                po_list = []
                for x in range(0, len(predicate_object_list2)):

                    predicate_or_object = Reconstructorv2(trig_lark).reconstruct(predicate_object_list2[x])
                    po_list.append(predicate_or_object)
                    if len(po_list) == 2:
                        if "," in po_list[1]:
                            po_lists = po_list[1].split(",")

                            for y in po_lists:
                                try:
                                    object_annotation = y.split("{|",1)
                                    o1 = object_annotation[0]
                                    a1 = "{|"+object_annotation[1]
                                    a1 = a1.strip()
                                    a1_Dict = annotation_dict[a1]
                                    spo_list = [subject,po_list[0],o1, a1_Dict]
                                    annotation_s_p_o.append(spo_list)
                                except:
                                    spo_list = [subject,po_list[0],y]
                                    annotation_s_p_o.append(spo_list)
                        else:
                            object_annotation = po_list[1].split("{|",1)
                            o1 = object_annotation[0]
                            a1 = "{|"+object_annotation[1]
                            a1_Dict = annotation_dict[a1]
                            spo_list = [subject, po_list[0], o1, a1_Dict]
                            annotation_s_p_o.append(spo_list)
                        po_list = []
            to_remove.append(tri)
    def compoundanno(self, var):
        appends1 = []
        tri2 = Reconstructorv2(trig_lark).reconstruct(var)

        for x in var.children[1].children:

            test = Reconstructorv2(trig_lark).reconstruct(x)
            if "{|" in test:
                test123 = test.split("{|",1)

                object = test123[0]

                test123.pop(0)

                test_annotation = "{|"+ "".join(test123)
                result = annotation_dict[test_annotation]

                appends1.append(object)
                appends1.append(result)
            else:
                appends1.append(test)

        if not tri2 in annotation_dict:
            annotation_dict[tri2] = appends1
        elif not appends1 == annotation_dict[tri2]:
            for x in appends1:
                annotation_dict[tri2].append(x)

class FindVariables(Visitor):
    def __init__(self):
        super().__init__()
        self.variable_list = []

    def labelorsubject(self, var):

        try:
            vr = Reconstructor(trig_lark).reconstruct(var)
            trig_graph.append(vr)
        except:
            pass

    def quotation(self, var):
        qut = Reconstructor(trig_lark).reconstruct(var)
        qut = qut.replace(";", "")
        qut = qut.replace(" ", "")
        if not (qut in quotation_list):
            quotation_list.append(qut)

        vr = Reconstructor(trig_lark).reconstruct(var)
        vr = vr.replace(";","")
        quotation_dict[qut] = str(myHash(qut)) + "RdfstarTriple"
        qut_hash = ":" + str(myHash(qut))
        id = quotation_dict.get(vr)
        for x in quotation_dict:
            if x in vr:
                vr = vr.replace(x, ":"+quotation_dict.get(x))
                vr = vr.replace("<<", "")
                vr = vr.replace(">>", "")
                output = vr.split(":")
                output.pop(0)
                oa1 = Reconstructor(trig_lark).reconstruct(var)
                oa1 = oa1.replace(";","")
                output.append(oa1)
                if (not (output in quotationreif)):
                    quotationreif.append(output)

    def blank_node_property_list(self, var):
        object_list = ((var.children[0]).children)[1].children
        for x in range(0, len(object_list)):
            try:
                if object_list[x].data == 'quotation':
                    collection_quotation_reconstruct = Reconstructor(trig_lark).reconstruct(object_list[x])
                    collection_quotation_reconstruct = collection_quotation_reconstruct.replace(";","")
                    t2 = quotation_dict[collection_quotation_reconstruct]
                    hasht2 = "_:" + t2
                    object_list[x] = Tree('iri', [Tree('prefixed_name', [Token('PNAME_LN', hasht2)])])
            except Exception as ex:
                object_list = ((var.children[0]).children)[1]
                collection_quotation_reconstruct = Reconstructor(trig_lark).reconstruct(object_list)
                collection_quotation_reconstruct = collection_quotation_reconstruct.replace(";","")
                try:
                    t2 = quotation_dict[collection_quotation_reconstruct]
                    hasht2 = "_:" + t2
                    ((var.children[0]).children)[1] = Tree('iri', [Tree('prefixed_name', [Token('PNAME_LN', hasht2)])])
                    break
                except Exception as ex2:
                    pass

    def collection(self, var):
        for x in range(0, len(var.children)):
            if var.children[x].data == 'quotation':
                collection_quotation_reconstruct = Reconstructor(trig_lark).reconstruct(var.children[x])
                collection_quotation_reconstruct = collection_quotation_reconstruct.replace(";","")
                t2 = quotation_dict[collection_quotation_reconstruct]
                hasht2 = "_:" + t2
                var.children[x] = Tree('iri', [Tree('prefixed_name', [Token('PNAME_LN', hasht2)])])

    def triples(self, var):

        appends1 = []
        tri = Reconstructor(trig_lark).reconstruct(var)
        if ("[" in tri) and (not "RdfstarTriple" in tri) and (not "<<" in tri):
            vblist.append([tri])
        else:
            tri = tri.replace(";", "")
            tri = tri.replace(" ", "")
            if not (tri in assertedtriplelist):
                assertedtriplelist.append(tri)
            for x in var.children:
                if x.data == 'predicate_object_list':
                    xc = x.children
                    for y in xc:
                        try:
                            x2 = Reconstructor(trig_lark).reconstruct(y)
                        except:
                            appends1.pop(0)
                            appends1.append("standard reification")
                            appends1.append(Reconstructor(trig_lark).reconstruct(var))
                            appends1.append(" . \n")
                            break
                        appends1.append(x2)
                else:
                    anyquotationin = False
                    x1 = Reconstructor(trig_lark).reconstruct(x)
                    appends1.append(x1)

            if not (appends1 in vblist):
                vblist.append(appends1)

    def insidequotation(self, var):
        appends1 = []
        for x in var.children:
            x1 = Reconstructor(trig_lark).reconstruct(x)
            x1 = x1.replace(";","")
            appends1.append(x1)

        if not (appends1 in vblist):
            vblist.append(appends1)

    def prefix_id(self, children):
        pass

    def sparql_prefix(self, children):
        prefix_list.append(children)

    def base(self, children):
        base_directive, base_iriref = children
        # print("base", base_directive, base_iriref)
        # Workaround for lalr parser token ambiguity in python 2.7
        if base_directive.startswith('@') and base_directive != '@base':
            raise ValueError('Unexpected @base: ' + base_directive)

def RDFstarParsings(rdfstarstring):
    global quotationannolist, vblist, quotation_dict, quotationreif, prefix_list, constructors, assertedtriplelist, quoted_or_not, both_quoted_and_asserted, to_remove, annotation_s_p_o, output, annotation_dict, trig_graph
    quotationannolist = []
    vblist = []
    quotationreif = []
    prefix_list = []
    constructors = ""
    quoted_or_not = False
    both_quoted_and_asserted = False
    output = ""
    output_tree = ""
    annotation_s_p_o = []
    to_remove = []
    annotation_dict = dict()
    trig_graph = []

    tree = trig_lark.parse(rdfstarstring)

    tt = Expandanotation().visit(tree)

    tree_after = Reconstructorv2(trig_lark).reconstruct(tree)

    splittree_after = tree_after.split(">")

    PREFIX_substitute = dict()
    for x in splittree_after:

        if "PREFIX" in x:
            y = x + ">"+" " + "\n"
            PREFIX_substitute[x+">"] = y
    for z in PREFIX_substitute:
        tree_after = tree_after.replace(z, "")
    for z in PREFIX_substitute:
        tree_after =  PREFIX_substitute[z] + tree_after


    for x in to_remove:

        x = x + " ."

        tree_after = tree_after.replace(x, "")
    tree_after = tree_after+ "\n" #
    if "PREFIX:" in tree_after:
        tree_after = tree_after.replace("PREFIX:", "PREFIX :")

    def expand_to_rdfstar(x):
        global output

        spo = "<<"+x[0] +" "+x[1] + " " + x[2]+">>"
        try:
            if len(x[3]) == 2:

                output += spo + " "+ x[3][0] +" "+x[3][1] + "." + "\n" # smart

            elif len(x[3]) == 3:

                output += spo + " "+ x[3][0] +" "+x[3][1] + "." + "\n" # smart

                newspolist = [spo, x[3][0],x[3][1], x[3][2]]

                expand_to_rdfstar(newspolist)
            else:

                clist = [x[3][y:y+2] for y in range(0, len(x[3]),2)]

                for z in clist:

                    expand_to_rdfstar([x[0],x[1],x[2],z])
        except:
            pass
    output = ""
    for x in annotation_s_p_o:

        output +=x[0] +" "+ x[1] +" "+ x[2] + "." + "\n"
        expand_to_rdfstar(x)
    output_tree = tree_after+output
    if ":G {  }\n" in output_tree:
        output_tree = output_tree.replace(":G {  }\n", ":G {")
        output_tree = output_tree+ "}"
    # print("test output tree", output_tree)

    tree = trig_lark.parse(output_tree)

    at = FindVariables().visit(tree)
    # print("asserted, quoted", assertedtriplelist, quotation_list)
    for y in vblist:

        for element_index in range(0, len(y)):
            if (y[element_index][0] == "_") & (not (element_index == 0)):
                y[element_index]=" "+y[element_index]
        result = "".join(y)

        if "standard reification" in result:


            result = result.replace("standard reification", "")
            constructors+=result
        else:

            result = result.replace(" ", "")

            if result in assertedtriplelist:
                test1 = "<<"+result+">>"
                if test1 in quotation_list:
                    both_quoted_and_asserted = True
                else:
                    both_quoted_and_asserted = False
                    quoted_or_not = False
            else:

                test2 = "<<"+result+">>"
                if test2 in quotation_list:
                    both_quoted_and_asserted = False
                    quoted_or_not = True
                else:
                    both_quoted_and_asserted = False
                    quoted_or_not = False
            result = "<<"+result+">>"

            if not (result in quotation_list):
                for z in range(0,len(y)):
                    if "<<" in y[z]:
                        y[z] = y[z].replace(" ", "")

                        y[z] = "_:"+quotation_dict[y[z]]
                myvalue = str(myHash(result))

                try:
                    subject = y[0]
                    predicate = y[1]
                    object = y[2]
                except:
                    if len(y)==1:
                        result2 = y[0]

                        constructors+=result2
                        constructors = constructors +".\n"
                        continue
                if both_quoted_and_asserted:
                    next_rdf_object = "_:" + str(myvalue) +"RdfstarTriple"+ '\n' + "    a rdfstar:AssertedStatement, rdfstar:QuotedStatement ;\n"+"    rdf:subject "+subject+' ;\n'+"    rdf:predicate "+predicate+" ;\n"+"    rdf:object "+object+" ;\n"+".\n"
                else:
                    if quoted_or_not:
                        next_rdf_object = "_:" + str(myvalue) +"RdfstarTriple"+ '\n' + "    a rdfstar:QuotedStatement ;\n"+"    rdf:subject "+subject+' ;\n'+"    rdf:predicate "+predicate+" ;\n"+"    rdf:object "+object+" ;\n"+".\n"
                    else:
                        next_rdf_object = "_:" + str(myvalue) +"RdfstarTriple"+ '\n' + "    a rdfstar:AssertedStatement ;\n"+"    rdf:subject "+subject+' ;\n'+"    rdf:predicate "+predicate+" ;\n"+"    rdf:object "+object+" ;\n"+".\n"


                constructors+=next_rdf_object
            else:
                value = quotation_dict[result]
                for z in range(0,len(y)):
                    if "<<" in y[z]:
                        y[z] = "_:"+quotation_dict[y[z]]
                subject = y[0]
                predicate = y[1]
                object = y[2]
                if both_quoted_and_asserted:
                    next_rdf_object = "_:" + str(value) + '\n' + "    a rdfstar:AssertedStatement, rdfstar:QuotedStatement ;\n"+"    rdf:subject "+subject+' ;\n'+"    rdf:predicate "+predicate+" ;\n"+"    rdf:object "+object+" ;\n"+".\n"
                else:
                    if quoted_or_not:
                        next_rdf_object = "_:" + str(value) + '\n' + "    a rdfstar:QuotedStatement ;\n"+"    rdf:subject "+subject+' ;\n'+"    rdf:predicate "+predicate+" ;\n"+"    rdf:object "+object+" ;\n"+".\n"
                    else:
                        next_rdf_object = "_:" + str(value) + '\n' + "    a rdfstar:AssertedStatement ;\n"+"    rdf:subject "+subject+' ;\n'+"    rdf:predicate "+predicate+" ;\n"+"    rdf:object "+object+" ;\n"+".\n"

                constructors+=next_rdf_object
    if len(trig_graph)!=0:
        constructors=trig_graph[0]+"{\n"+constructors+"\n}"
    for x in range(0, len(prefix_list)):
        prefix_list[x] = Reconstructor(trig_lark).reconstruct(prefix_list[x])
        constructors = prefix_list[x]+"\n"+constructors

    constructors = "PREFIX rdfstar: <https://w3id.org/rdf-star/> \n"+constructors

    constructors = "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \n"+constructors

    if not (("PREFIX : <http://example/>" in constructors) or ("PREFIX:<http://example/>" in constructors)):
        constructors = "PREFIX : <http://example/> \n"+constructors

    if "PREFIX:" in constructors:
        constructors = constructors.replace("PREFIX:", "PREFIX :")

    print("input after preprocessing: ", constructors)
    constructors = bytes(constructors, 'utf-8')
    return constructors

class TrigSinkParser(StarsinkParser):
    def directiveOrStatement(self, argstr, h):

        # import pdb; pdb.set_trace()

        i = self.skipSpace(argstr, h)
        if i < 0:
            return i  # EOF

        j = self.graph(argstr, i)
        if j >= 0:
            return j

        j = self.sparqlDirective(argstr, i)
        if j >= 0:
            return j

        j = self.directive(argstr, i)
        if j >= 0:
            return self.checkDot(argstr, j)

        j = self.statement(argstr, i)
        if j >= 0:
            return self.checkDot(argstr, j)

        return j

    def labelOrSubject(self, argstr, i, res):
        j = self.skipSpace(argstr, i)
        if j < 0:
            return j  # eof
        i = j

        j = self.uri_ref2(argstr, i, res)
        if j >= 0:
            return j

        if argstr[i] == "[":
            j = self.skipSpace(argstr, i + 1)
            if j < 0:
                self.BadSyntax(argstr, i, "Expected ] got EOF")
            if argstr[j] == "]":
                res.append(self.blankNode())
                return j + 1
        return -1

    def graph(self, argstr, i):
        """
        Parse trig graph, i.e.
           <urn:graphname> = { .. triples .. }
        return -1 if it doesn't look like a graph-decl
        raise Exception if it looks like a graph, but isn't.
        """

        # import pdb; pdb.set_trace()
        j = self.sparqlTok("GRAPH", argstr, i)  # optional GRAPH keyword
        if j >= 0:
            i = j

        r = []
        j = self.labelOrSubject(argstr, i, r)
        if j >= 0:
            graph = r[0]
            i = j
        else:
            graph = self._store.graph.identifier  # hack

        j = self.skipSpace(argstr, i)
        if j < 0:
            self.BadSyntax(argstr, i, "EOF found when expected graph")

        if argstr[j : j + 1] == "=":  # optional = for legacy support

            i = self.skipSpace(argstr, j + 1)
            if i < 0:
                self.BadSyntax(argstr, i, "EOF found when expecting '{'")
        else:
            i = j

        if argstr[i : i + 1] != "{":
            return -1  # the node wasn't part of a graph

        j = i + 1

        oldParentContext = self._parentContext
        self._parentContext = self._context
        reason2 = self._reason2
        self._reason2 = becauseSubGraph
        self._context = self._store.newGraph(graph)
        # print(self._context)
        while 1:
            i = self.skipSpace(argstr, j)
            if i < 0:
                self.BadSyntax(argstr, i, "needed '}', found end.")

            if argstr[i : i + 1] == "}":
                j = i + 1
                break

            j = self.directiveOrStatement(argstr, i)
            if j < 0:
                self.BadSyntax(argstr, i, "expected statement or '}'")

        self._context = self._parentContext
        self._reason2 = reason2
        self._parentContext = oldParentContext
        # res.append(subj.close())    # No use until closed
        return j


class TrigParser(Parser):

    """
    An RDFLib parser for Turtle
    See http://www.w3.org/TR/turtle/
    """

    def __init__(self):
        pass

    def parse(
        self,
        source: "InputSource",
        graph: Graph,
        encoding: Optional[str] = "utf-8",
        turtle: bool = True,
    ):
        if encoding not in [None, "utf-8"]:
               raise Exception(
                ("TriG files are always utf-8 encoded, ", "I was passed: %s") % encoding
            )

        # we're currently being handed a Graph, not a ConjunctiveGraph
        # print("Contextawareasdasdasdasd\n\n\n\n", graph.store.context_aware)
        assert graph.store.context_aware, "TriG Parser needs a context-aware store!"

        conj_graph = ConjunctiveGraph(store=graph.store, identifier=graph.identifier)
        conj_graph.default_context = graph  # TODO: CG __init__ should have a
        # default_context arg
        # TODO: update N3Processor so that it can use conj_graph as the sink
        conj_graph.namespace_manager = graph.namespace_manager

        sink = StarRDFSink(conj_graph)

        baseURI = conj_graph.absolutize(
            source.getPublicId() or source.getSystemId() or ""
        )
        p = TrigSinkParser(sink, baseURI=baseURI, turtle=True)

        if hasattr(source, "file"):
            f = open(source.file.name, "rb")
            rdbytes = f.read()
            f.close()
        elif hasattr(source, "_InputSource__bytefile"):
            if hasattr(source._InputSource__bytefile, "wrapped"):
                f = open((source._InputSource__bytefile.wrapped.strip().splitlines())[0], "rb") # what if multiple files
                rdbytes = f.read()
                f.close()

        bp = rdbytes.decode("utf-8")
        if "<<" or "{|" in bp:
            ou = RDFstarParsings(bp)
        else:
            ou = bp
        # print(ou)
        p.feed(ou)
        p.endDoc()
        for prefix, namespace in p._bindings.items():
            conj_graph.bind(prefix, namespace)
