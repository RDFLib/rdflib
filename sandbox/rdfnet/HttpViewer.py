"""
$Id: HttpViewer.py,v 1.2 2003/10/08 02:34:55 kendall Exp $

We have to map between request descriptions of models, which I'll assume
are URIs and actual triplestores on the actual models, and that mapping
should probably happen here -- need something like a site map, which
associates URIs with models-I-can-reach

Actually, if we do this mapping in the http layer, it will persist...  We
could have a graph which is the mapping and just query it...

It's entirely possible that this resolveModelRef() method will be
transport generic -- in which case it should be either a function or a
method of a class which both SoapViewer and HttpViewer inherit from..."""

class HttpViewer(object):
                
    def __init__(self):
	pass
    
    def resolveModelRef(self, modelRef): pass
    #return theModel
    
    def __toString(self, s): 
	return s.getvalue()

    def convertArgs(self, spo):
	s, p, o = spo
	#subject
	if s == "*":
	    s = None
	elif s.startswith("uri:"):
	    s = URIRef(s)
	elif s.startswith("literal:"):
	    s = Literal(s)
	#predicate
	if p == "*":
	    p = None
	elif p.startswith("uri:"):
	    p = URIRef(p)
	elif p.startswith("literal:"):
	    p = Literal(p)
	#object
	if o == "*":
	    o = None
	elif o.startswith("uri:"):
	    o = URIRef(o)
	elif o.startswith("literal:"):
	    o = Literal(o)
	return (s,p,o)
