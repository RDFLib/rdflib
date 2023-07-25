"""
A commandline tool for drawing RDF graphs in Graphviz DOT format

You can draw the graph of an RDF file directly:

.. code-block: bash

   rdf2dot my_rdf_file.rdf | dot -Tpng | display

"""

import collections
import html
import sys

import rdflib
import rdflib.extras.cmdlineutils
from rdflib import XSD

LABEL_PROPERTIES = [
    rdflib.RDFS.label,
    rdflib.URIRef("http://purl.org/dc/elements/1.1/title"),
    rdflib.URIRef("http://xmlns.com/foaf/0.1/name"),
    rdflib.URIRef("http://www.w3.org/2006/vcard/ns#fn"),
    rdflib.URIRef("http://www.w3.org/2006/vcard/ns#org"),
]

XSDTERMS = [
    XSD[x]
    for x in (
        "anyURI",
        "base64Binary",
        "boolean",
        "byte",
        "date",
        "dateTime",
        "decimal",
        "double",
        "duration",
        "float",
        "gDay",
        "gMonth",
        "gMonthDay",
        "gYear",
        "gYearMonth",
        "hexBinary",
        "ID",
        "IDREF",
        "IDREFS",
        "int",
        "integer",
        "language",
        "long",
        "Name",
        "NCName",
        "negativeInteger",
        "NMTOKEN",
        "NMTOKENS",
        "nonNegativeInteger",
        "nonPositiveInteger",
        "normalizedString",
        "positiveInteger",
        "QName",
        "short",
        "string",
        "time",
        "token",
        "unsignedByte",
        "unsignedInt",
        "unsignedLong",
        "unsignedShort",
    )
]

EDGECOLOR = "blue"
NODECOLOR = "black"
ISACOLOR = "black"


def rdf2dot(g, stream, opts={}):
    """
    Convert the RDF graph to DOT
    writes the dot output to the stream
    """

    fields = collections.defaultdict(set)
    nodes = {}

    def node(x):
        if x not in nodes:
            nodes[x] = "node%d" % len(nodes)
        return nodes[x]

    def label(x, g):
        for labelProp in LABEL_PROPERTIES:
            l_ = g.value(x, labelProp)
            if l_:
                return l_
        try:
            return g.namespace_manager.compute_qname(x)[2]
        except Exception:
            return x

    def formatliteral(l, g):
        v = html.escape(l)
        if l.datatype:
            return "&quot;%s&quot;^^%s" % (v, qname(l.datatype, g))
        elif l.language:
            return "&quot;%s&quot;@%s" % (v, l.language)
        return "&quot;%s&quot;" % v

    def qname(x, g):
        try:
            q = g.compute_qname(x)
            return q[0] + ":" + q[2]
        except Exception:
            return x

    def color(p):
        return "BLACK"

    stream.write('digraph { \n node [ fontname="DejaVu Sans" ] ; \n')

    for s, p, o in g:
        sn = node(s)
        if p == rdflib.RDFS.label:
            continue
        if isinstance(o, (rdflib.URIRef, rdflib.BNode)):
            on = node(o)
            opstr = (
                "\t%s -> %s [ color=%s, label=< <font point-size='10' "
                + "color='#336633'>%s</font> > ] ;\n"
            )
            stream.write(opstr % (sn, on, color(p), qname(p, g)))
        else:
            fields[sn].add((qname(p, g), formatliteral(o, g)))

    for u, n in nodes.items():
        stream.write("# %s %s\n" % (u, n))
        f = [
            "<tr><td align='left'>%s</td><td align='left'>%s</td></tr>" % x
            for x in sorted(fields[n])
        ]
        opstr = (
            "%s [ shape=none, color=%s label=< <table color='#666666'"
            + " cellborder='0' cellspacing='0' border='1'><tr>"
            + "<td colspan='2' bgcolor='grey'><B>%s</B></td></tr><tr>"
            + "<td href='%s' bgcolor='#eeeeee' colspan='2'>"
            + "<font point-size='10' color='#6666ff'>%s</font></td>"
            + "</tr>%s</table> > ] \n"
        )
        stream.write(
            opstr
            % (n, NODECOLOR, html.escape(label(u, g)), u, html.escape(u), "".join(f))
        )

    stream.write("}\n")


def _help():
    sys.stderr.write(
        """
rdf2dot.py [-f <format>] files...
Read RDF files given on STDOUT, writes a graph of the RDFS schema in DOT
language to stdout
-f specifies parser to use, if not given,

"""
    )


def main():
    rdflib.extras.cmdlineutils.main(rdf2dot, _help)


if __name__ == "__main__":
    main()
