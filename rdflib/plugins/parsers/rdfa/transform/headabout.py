# -*- coding: utf-8 -*-
"""
Simple transfomer: the C{@about=""} is added to the C{<head>} and C{<body>} elements (unless something is already there).
Note that this transformer is always invoked by the parser because this behaviour is mandated by the RDFa syntax.

@summary: Add a top "about" to <head> and <body>
@requires: U{RDFLib package<http://rdflib.net>}
@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
@contact: Ivan Herman, ivan@w3.org
"""

def head_about_transform(html, options):
    """
    @param html: a DOM node for the top level html element
    @param options: invocation options
    @type options: L{Options<pyRdfa.Options>}
    """
    for top in html.getElementsByTagName("head"):
        if not top.hasAttribute("about"):
            top.setAttribute("about", "")
    for top in html.getElementsByTagName("body"):
        if not top.hasAttribute("about"):
            top.setAttribute("about", "")

