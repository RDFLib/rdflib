
import rdflib

# importing typing for `typing.List` because `List`` is used for something else
import typing
from typing import IO, TYPE_CHECKING, Any, Callable, Dict, Optional, TypeVar, Union
from uuid import uuid4
from .notation3 import SinkParser, RDFSink, runNamespace

from rdflib.exceptions import ParserError
from rdflib.graph import ConjunctiveGraph, Graph, QuotedGraph
from rdflib.term import (
    RdfstarTriple,
    BNode,
    Identifier,
    Literal,
    Node,
    URIRef,
    Variable,
    _unique_id,
)

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

nextu=0
import re
import lark
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

grammar = r"""turtle_doc: statement*
?statement: directive | triples "."
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

turtle_lark = Lark(grammar, start="turtle_doc", parser="lalr", maybe_placeholders=False)

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
output = ""

def myHash(text:str):
  return str(hashlib.md5(text.encode('utf-8')).hexdigest())

class Expandanotation(Visitor):
    global annotation_s_p_o, to_remove
    def __init__(self):
        super().__init__()
        self.variable_list = []

    def triples(self, var):

        appends1 = []
        tri = Reconstructorv2(turtle_lark).reconstruct(var)
        if "{|" in tri:
            if len(var.children) == 2:
                predicate_object_list2 = var.children[1].children
                subject = Reconstructorv2(turtle_lark).reconstruct(var.children[0])
                po_list = []

                for x in range(0, len(predicate_object_list2)):

                    predicate_or_object = Reconstructorv2(turtle_lark).reconstruct(predicate_object_list2[x])
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


        for x in var.children:
            x1 = Reconstructorv2(turtle_lark).reconstruct(x)



    def compoundanno(self, var):

        appends1 = []
        tri2 = Reconstructorv2(turtle_lark).reconstruct(var)


        for x in var.children[1].children:

            test = Reconstructorv2(turtle_lark).reconstruct(x)
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

    def quotation(self, var):
        qut = Reconstructor(turtle_lark).reconstruct(var)
        qut = qut.replace(";", "")
        qut = qut.replace(" ", "")
        if not (qut in quotation_list):
            quotation_list.append(qut)

        vr = Reconstructor(turtle_lark).reconstruct(var)
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
                oa1 = Reconstructor(turtle_lark).reconstruct(var)
                oa1 = oa1.replace(";","")

                output.append(oa1)

                if (not (output in quotationreif)):
                    quotationreif.append(output)

    def blank_node_property_list(self, var):

        object_list = ((var.children[0]).children)[1].children

        for x in range(0, len(object_list)):
            try:
                if object_list[x].data == 'quotation':
                    collection_quotation_reconstruct = Reconstructor(turtle_lark).reconstruct(object_list[x])
                    collection_quotation_reconstruct = collection_quotation_reconstruct.replace(";","")
                    t2 = quotation_dict[collection_quotation_reconstruct]
                    hasht2 = "_:" + t2
                    object_list[x] = Tree('iri', [Tree('prefixed_name', [Token('PNAME_LN', hasht2)])])

            except Exception as ex:

                object_list = ((var.children[0]).children)[1]
                collection_quotation_reconstruct = Reconstructor(turtle_lark).reconstruct(object_list)
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

                collection_quotation_reconstruct = Reconstructor(turtle_lark).reconstruct(var.children[x])
                collection_quotation_reconstruct = collection_quotation_reconstruct.replace(";","")
                t2 = quotation_dict[collection_quotation_reconstruct]
                hasht2 = "_:" + t2
                var.children[x] = Tree('iri', [Tree('prefixed_name', [Token('PNAME_LN', hasht2)])])

    def triples(self, var):

        appends1 = []
        tri = Reconstructor(turtle_lark).reconstruct(var)

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
                            x2 = Reconstructor(turtle_lark).reconstruct(y)

                        except:

                            appends1.pop(0)

                            appends1.append("standard reification")
                            appends1.append(Reconstructor(turtle_lark).reconstruct(var))
                            appends1.append(" . \n")
                            break

                        appends1.append(x2)
                else:

                    anyquotationin = False
                    x1 = Reconstructor(turtle_lark).reconstruct(x)

                    appends1.append(x1)

            if not (appends1 in vblist):
                vblist.append(appends1)

    def insidequotation(self, var):
        appends1 = []
        for x in var.children:
            x1 = Reconstructor(turtle_lark).reconstruct(x)
            x1 = x1.replace(";","")

            appends1.append(x1)

        if not (appends1 in vblist):
            vblist.append(appends1)

    def prefix_id(self, children):
        pass

    def sparql_prefix(self, children):
        prefix_list.append(children)

    def base(self, children):
        # print("base")
        base_directive, base_iriref = children
        # print("base", base_directive, base_iriref)
        # Workaround for lalr parser token ambiguity in python 2.7
        if base_directive.startswith('@') and base_directive != '@base':
            raise ValueError('Unexpected @base: ' + base_directive)

def RDFstarParsings(rdfstarstring):
    global quotationannolist, vblist, quotation_dict, quotationreif, prefix_list, constructors, assertedtriplelist, quoted_or_not, both_quoted_and_asserted, to_remove, annotation_s_p_o, output, annotation_dict
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
    tree = turtle_lark.parse(rdfstarstring)

    tt = Expandanotation().visit(tree)

    tree_after = Reconstructorv2(turtle_lark).reconstruct(tree)

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
    tree_after = tree_after+ "\n"
    if "PREFIX:" in tree_after:
        tree_after = tree_after.replace("PREFIX:", "PREFIX :")

    def expand_to_rdfstar(x):

        global output

        spo = "<<"+x[0] +" "+x[1] + " " + x[2]+">>"
        try:
            if len(x[3]) == 2:

                output += spo + " "+ x[3][0] +" "+x[3][1] + "." + "\n"

            elif len(x[3]) == 3:

                output += spo + " "+ x[3][0] +" "+x[3][1] + "." + "\n"

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

    tree = turtle_lark.parse(output_tree)

    at = FindVariables().visit(tree)

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

    for z in quotationannolist:
        result1 = "".join(z)
        result1 = "<<"+result1+">>"
        if result1 in quotation_list:
            both_quoted_and_asserted = True
        else:
            both_quoted_and_asserted = False
            quoted_or_not = False
        value = str(myHash(result1))
        subject = z[0]
        predicate = z[1]
        object = z[2]
        if both_quoted_and_asserted:
            next_rdf_object = "_:" + str(value) +"RdfstarTriple"+ '\n' + "    a rdfstar:AssertedStatement, rdfstar:QuotedStatement ;\n"+"    rdf:subject "+subject+' ;\n'+"    rdf:predicate "+predicate+" ;\n"+"    rdf:object "+object+" ;\n"+".\n"
        else:
            if quoted_or_not:
                next_rdf_object = "_:" + str(value) +"RdfstarTriple"+ '\n' + "    a rdfstar:QuotedStatement ;\n"+"    rdf:subject "+subject+' ;\n'+"    rdf:predicate "+predicate+" ;\n"+"    rdf:object "+object+" ;\n"+".\n"
            else:
                next_rdf_object = "_:" + str(value) +"RdfstarTriple"+ '\n' + "    a rdfstar:AssertedStatement ;\n"+"    rdf:subject "+subject+' ;\n'+"    rdf:predicate "+predicate+" ;\n"+"    rdf:object "+object+" ;\n"+".\n"

        constructors+=next_rdf_object

    for x in range(0, len(prefix_list)):

        prefix_list[x] = Reconstructor(turtle_lark).reconstruct(prefix_list[x])
        constructors = prefix_list[x]+"\n"+constructors

    if ((not ("PREFIX rdfstar: <https://w3id.org/rdf-star/>" in constructors)) and (not("PREFIX rdfstar:<https://w3id.org/rdf-star/>" in constructors))):
        constructors = "PREFIX rdfstar: <https://w3id.org/rdf-star/> \n"+constructors

    constructors = "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \n"+constructors

    if not (("PREFIX : <http://example/>" in constructors) or ("PREFIX:<http://example/>" in constructors)):
        constructors = "PREFIX : <http://example/> \n"+constructors

    if "PREFIX:" in constructors:
        constructors = constructors.replace("PREFIX:", "PREFIX :")

    print("input after preprocessing: ", constructors)
    constructors = bytes(constructors, 'utf-8')
    return constructors

def uniqueURI():
    """A unique URI"""
    global nextu
    nextu += 1
    return runNamespace() + "u_" + str(nextu)

tracking = False
chatty_flag = 50

# from why import BecauseOfData, becauseSubexpression

def BecauseOfData(*args, **kargs):
    # print args, kargs
    pass


def becauseSubexpression(*args, **kargs):
    # print args, kargs
    pass

quoted_triple_list = []

class StarsinkParser(SinkParser):
    def __init__(
        self,
        store: "RDFSink",
        openFormula: Optional["Formula"] = None,
        thisDoc: str = "",
        baseURI: Optional[str] = None,
        genPrefix: str = "",
        why: Optional[Callable[[], None]] = None,
        turtle: bool = False,
    ):
        """note: namespace names should *not* end in  # ;
        the  # will get added during qname processing"""

        self._bindings = {}
        if thisDoc != "":
            assert ":" in thisDoc, "Document URI not absolute: <%s>" % thisDoc
            self._bindings[""] = thisDoc + "#"  # default

        self._store = store
        if genPrefix:
            # TODO FIXME: there is no function named setGenPrefix
            store.setGenPrefix(genPrefix)  # type: ignore[attr-defined] # pass it on

        self._thisDoc = thisDoc
        self.lines = 0  # for error handling
        self.startOfLine = 0  # For calculating character number
        self._genPrefix = genPrefix
        self.keywords = ["a", "this", "bind", "has", "is", "of", "true", "false"]
        self.keywordsSet = 0  # Then only can others be considered qnames
        self._anonymousNodes: Dict[str, Node] = {}
        self._rdfstartripleNodes: Dict[str, Node] = {}
        # Dict of anon nodes already declared ln: Term
        self._variables: Dict[Identifier, Identifier] = {}
        self._parentVariables: Dict[Identifier, Identifier] = {}
        self._reason = why  # Why the parser was asked to parse this

        self.turtle = turtle  # raise exception when encountering N3 extensions
        # Turtle allows single or double quotes around strings, whereas N3
        # only allows double quotes.
        self.string_delimiters = ('"', "'") if turtle else ('"',)

        self._reason2 = None  # Why these triples
        # was: diag.tracking
        if tracking:
            self._reason2 = BecauseOfData(
                store.newSymbol(thisDoc), because=self._reason
            )

        self._baseURI: Optional[str]
        if baseURI:
            self._baseURI = baseURI
        else:
            if thisDoc:
                self._baseURI = thisDoc
            else:
                self._baseURI = None

        assert not self._baseURI or ":" in self._baseURI

        if not self._genPrefix:
            if self._thisDoc:
                self._genPrefix = self._thisDoc + "#_g"
            else:
                self._genPrefix = uniqueURI()

        self._formula: Formula
        if openFormula is None and not turtle:
            if self._thisDoc:
                # TODO FIXME: store.newFormula does not take any arguments
                self._formula = store.newFormula(thisDoc + "#_formula")  # type: ignore[call-arg]
            else:
                self._formula = store.newFormula()
        else:
            self._formula = openFormula  # type: ignore[assignment]

        self._context = self._formula
        self._parentContext: Optional[Formula] = None

    def makerdfstarStatement(self, quadruple):
                   # $$$$$$$$$$$$$$$$$$$$$
                   # print "# Parser output: ", `quadruple`
        self._store.makerdfstarStatement(quadruple, why=self._reason2)

    def anonymousNode(self, ln: str):
        """Remember or generate a term for one of these _: anonymous nodes"""
        # print("anonymousNode", self._anonymousNodes.get(ln, None), self._context, self._reason2)
        if ("RdfstarTriple" in ln):
            # print("new object")
            # ln = ln.replace("RdfstarTriple", "")
            term = self._rdfstartripleNodes.get(ln, None)
            if term is not None:
                return term
            term = self._store.newRdfstarTriple(self._context, why=self._reason2, hashvalue = ln)
            self._rdfstartripleNodes[ln] = term
            return term
        term = self._anonymousNodes.get(ln, None)
        if term is not None:
            return term
        term = self._store.newBlankNode(self._context, why=self._reason2)
        self._anonymousNodes[ln] = term
        return term

    def addingquotedRdfstarTriple(self, quoted_triple_list, dira):
        if quoted_triple_list[0] == rdflib.term.URIRef('https://w3id.org/rdf-star/AssertedStatement'):
            if quoted_triple_list[1] == rdflib.term.URIRef('https://w3id.org/rdf-star/QuotedStatement'):
                if dira == "->":
                    self.makeStatement((self._context, quoted_triple_list[4], quoted_triple_list[3], quoted_triple_list[5]))
                    quoted_triple_list[2].setSubject(quoted_triple_list[3])
                    quoted_triple_list[2].setPredicate(quoted_triple_list[4])
                    quoted_triple_list[2].setObject(quoted_triple_list[5])

                else:
                    self.makeStatement((self._context, quoted_triple_list[4], quoted_triple_list[5], quoted_triple_list[3]))
                    # quoted_triple_list[2].setSubject(quoted_triple_list[3])
                    # quoted_triple_list[2].setPredicate(quoted_triple_list[4])
                    # quoted_triple_list[2].setObject(quoted_triple_list[5])
                    quoted_triple_list[2].setSubject(quoted_triple_list[4])
                    quoted_triple_list[2].setPredicate(quoted_triple_list[5])
                    quoted_triple_list[2].setObject(quoted_triple_list[6])

            else:
                if dira == "->":
                    self.makeStatement((self._context, quoted_triple_list[2], quoted_triple_list[1], quoted_triple_list[3]))
                else:
                    self.makeStatement((self._context, quoted_triple_list[2], quoted_triple_list[3], quoted_triple_list[1]))
        else:
            if dira == "->":
                # print("making statement")
                quoted_triple_list[1].setSubject(quoted_triple_list[2])
                quoted_triple_list[1].setPredicate(quoted_triple_list[3])
                quoted_triple_list[1].setObject(quoted_triple_list[4])

            else:
                quoted_triple_list[1].setSubject(quoted_triple_list[2])
                quoted_triple_list[1].setPredicate(quoted_triple_list[3])
                quoted_triple_list[1].setObject(quoted_triple_list[4])
                # self.makerdfstarStatement((self._context,quoted_triple_list[1], quoted_triple_list[3], quoted_triple_list[4], quoted_triple_list[2])) # what if don't change to str

    def property_list(self, argstr: str, i: int, subj):
        """Parse property list
        Leaves the terminating punctuation in the buffer
        """
        global quoted_triple_list
        while 1:
            while 1:  # skip repeat ;
                j = self.skipSpace(argstr, i)
                if j < 0:
                    self.BadSyntax(
                        argstr, i, "EOF found when expected verb in property list"
                    )
                if argstr[j] != ";":
                    break
                i = j + 1

            if argstr[j : j + 2] == ":-":
                if self.turtle:
                    self.BadSyntax(argstr, j, "Found in ':-' in Turtle mode")
                i = j + 2
                res: typing.List[Any] = []
                # print("node in propertylist", self.node(argstr, i, res, subj))
                j = self.node(argstr, i, res, subj)
                if j < 0:
                    self.BadSyntax(argstr, i, "bad {} or () or [] node after :- ")
                i = j
                continue
            i = j
            v: typing.List[Any] = []
            j = self.verb(argstr, i, v)
            if j <= 0:
                return i  # void but valid

            objs: typing.List[Any] = []

            i = self.objectList(argstr, j, objs)
            # print("objectList in propertylist", objs)
            if i < 0:
                self.BadSyntax(argstr, j, "objectList expected")

            for obj in objs:
                dira, sym = v[0]
                if "RdfstarTriple" in subj:
                    # print("asdasdasd", obj)
                    if "rdf-star" in str(obj):
                        if len(quoted_triple_list) > 2:
                            quoted_triple_list = []
                    quoted_triple_list.append(obj)
                    if (rdflib.term.URIRef('https://w3id.org/rdf-star/QuotedStatement') in quoted_triple_list) & (not (subj in quoted_triple_list)):
                        quoted_triple_list.append(subj)
                    if "#object" in sym:
                        # print("asdasdasd", quoted_triple_list)
                        self.addingquotedRdfstarTriple(quoted_triple_list, dira)
                else:
                    if dira == "->":
                        # print("tests ->", self._context, sym, subj, obj)
                        self.makeStatement((self._context, sym, subj, obj))
                    else:
                        self.makeStatement((self._context, sym, obj, subj))

            j = self.skipSpace(argstr, i)
            if j < 0:
                self.BadSyntax(argstr, j, "EOF found in list of objects")
            if argstr[i] != ";":
                return i
            i += 1  # skip semicolon and continue

###############################################################################
class Formula(object):
    number = 0

    def __init__(self, parent):
        self.uuid = uuid4().hex
        self.counter = 0
        Formula.number += 1
        self.number = Formula.number
        self.existentials = {}
        self.universals = {}

        self.quotedgraph = QuotedGraph(store=parent.store, identifier=self.id())

    def __str__(self):
        return "_:Formula%s" % self.number

    def id(self):
        return BNode("_:Formula%s" % self.number)

    def newBlankNode(self, uri=None, why=None):
        # print("newBlankNode in Formula")
        if uri is None:
            self.counter += 1
            bn = BNode("f%sb%s" % (self.uuid, self.counter))
        else:
            bn = BNode(uri.split("#").pop().replace("_", "b"))
        return bn

    def newRdfstarTriple(self, hashvalue, uri=None, why=None):
        # print("newRdfstarTriple in Formula")
        if uri is None:
            # self.counter += 1
            rdfstartriple = RdfstarTriple(hashvalue = hashvalue)
        else:
            rdfstartriple = RdfstarTriple(hashvalue = hashvalue)
        return rdfstartriple

    def newUniversal(self, uri, why=None):
        return Variable(uri.split("#").pop())

    def declareExistential(self, x):
        self.existentials[x] = self.newBlankNode()

    def close(self):

        return self.quotedgraph

class StarRDFSink(RDFSink):

    def newRdfstarTriple(
        self,
        # hashvalue: Optional[str],
        # arg: Optional[Union[Formula, Graph, Any]] = None,
        # uri: Optional[str] = None,
        arg: Optional[Union[Formula, Graph, Any]] = None,
        uri: Optional[str] = None,
        why: Optional[Callable[[], None]] = None,
        hashvalue: Optional[str] = None
    ) -> RdfstarTriple:
        # print("newRdflibRdfstartriple in Formula")
        if isinstance(arg, Formula):
            # print("testsv2", arg, uri)
            return arg.newRdfstarTriple(hashvalue = hashvalue)
        elif isinstance(arg, Graph) or arg is None:
            # print("newRdflibRdfstartriple", hashvalue)
            # self.counter += 1
            rdfstartriple = RdfstarTriple(hashvalue =hashvalue)
        else:
            # print("newRdflibRdfstartriple",hashvalue)
            # print("testsv24", arg, uri, str(arg[0]).split("#").pop().replace("_", "rdfstartriple"))
            rdfstartriple = RdfstarTriple(hashvalue =hashvalue)
        return rdfstartriple

    def makerdfstarStatement(self, quadruple, why=None) -> None:
        # print("testmakeStatement", quadruple)
        f, hashnode, p, s, o = quadruple

        if hasattr(p, "formula"):
            raise ParserError("Formula used as predicate")

        s = self.normalise(f, s)
        p = self.normalise(f, p)
        o = self.normalise(f, o)
        # print("testmakerdfstarStatement", hashnode, s,p,o)
        if f == self.rootFormula:
            # print s, p, o, '.'
            self.graph.addStarTriple((hashnode, s, p, o))
        elif isinstance(f, Formula):
            f.quotedgraph.addStarTriple((hashnode, s, p, o))
        else:
            f.addStarTriple((hashnode, s, p, o))

class TurtleParser(Parser):

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
            raise ParserError(
                "N3/Turtle files are always utf-8 encoded, I was passed: %s" % encoding
            )

        sink = StarRDFSink(graph)

        baseURI = graph.absolutize(source.getPublicId() or source.getSystemId() or "")
        p = StarsinkParser(sink, baseURI=baseURI, turtle=turtle)
        # N3 parser prefers str stream
        # stream = source.getCharacterStream()
        # if not stream:
        #     stream = source.getByteStream()
        # p.loadStream(stream)

        # print("tests", source)
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
        if ("<<" in bp) or ("{|" in bp):
            ou = RDFstarParsings(bp)
        else:
            ou = bp
        # print(ou)
        p.feed(ou)
        p.endDoc()
        for prefix, namespace in p._bindings.items():
            graph.bind(prefix, namespace)


class N3Parser(TurtleParser):

    """
    An RDFLib parser for Notation3
    See http://www.w3.org/DesignIssues/Notation3.html
    """

    def __init__(self):
        pass

    def parse(self, source, graph, encoding="utf-8"):
        # we're currently being handed a Graph, not a ConjunctiveGraph
        # context-aware is this implied by formula_aware
        ca = getattr(graph.store, "context_aware", False)
        fa = getattr(graph.store, "formula_aware", False)
        if not ca:
            raise ParserError("Cannot parse N3 into non-context-aware store.")
        elif not fa:
            raise ParserError("Cannot parse N3 into non-formula-aware store.")

        conj_graph = ConjunctiveGraph(store=graph.store)
        conj_graph.default_context = graph  # TODO: CG __init__ should have a
        # default_context arg
        # TODO: update N3Processor so that it can use conj_graph as the sink
        conj_graph.namespace_manager = graph.namespace_manager

        TurtleParser.parse(self, source, conj_graph, encoding, turtle=False)
