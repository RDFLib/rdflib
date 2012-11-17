# -*- coding: utf-8 -*-
"""

@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
@contact: Ivan Herman, ivan@w3.org
@version: $Id: lite.py,v 1.9 2012/06/26 13:29:58 ivan Exp $
$Date: 2012/06/26 13:29:58 $
"""

non_lite_attributes = ["about","inlist","datatype","rev","rel"]

def lite_prune(top, options, state) :
	"""
	This is a misnomer. The current version does not remove anything from the tree, just generates warnings as for the
	usage of non-lite attributes. A more aggressive version would mean to remove those attributes, but that would,
	in fact, define an RDFa Lite conformance level in the parser, which is against the WG decisions. So this should
	not be done; the corresponding commands are commented in the code below...
	
	@param top: a DOM node for the top level element
	@param options: invocation options
	@type options: L{Options<pyRdfa.options>}
	@param state: top level execution state
	@type state: L{State<pyRdfa.state>}
	"""
	def generate_warning(node, attr) :
		if attr == "rel" :
			msg = "Attribute @rel is not used in RDFa Lite, ignored (consider using @property)"
		elif attr == "about" :
			msg = "Attribute @about is not used in RDFa Lite, ignored (consider using a <link> element with @href or @resource)"
		else :
			msg = "Attribute @%s is not used in RDFa Lite, ignored" % attr
		options.add_warning(msg, node=node)

	def remove_attrs(node) :
		# first the @content; this has a special treatment
		if node.tagName != "meta" and node.hasAttribute("content") :
			generate_warning(node, "content")
			# node.removeAttribute("content")
		else :
			for attr in non_lite_attributes :
				if node.hasAttribute(attr) :
					generate_warning(node, attr)
					# node.removeAttribute(attr)

	remove_attrs(top)
	for n in top.childNodes :
		if n.nodeType == top.ELEMENT_NODE :
			lite_prune(n, options, state)

	