from rdflib import InMemoryTripleStore, Literal, URIRef

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class Insert: pass
INSERT = Insert()

class Remove: pass
REMOVE = Remove()

class Put: pass
PUT = Put()

#model in these signatures is an instance of a triple store
#XXX: what are statementSets? ... instances of tripstore? RDF-XML?

class StoreController(object):
	
    def __init__(self): pass
	
    def __toRdf(self, model):
        s = StringIO()
	model.output(s)
	return s
	
    def mutate(self, model, statementSet, type=None):
        if type is INSERT:
	    for spo in statementSet: model.add(spo)
	    return self.__toRdf(model)
	elif type is PUT:
	    model.destroy()#XXX: ask daniel for this method
	    for spo in statementSet: model.add(spo)
	    return self.__toRdf(model)
	elif type is REMOVE:
	    for spo in statementSet:
		if spo in model: 
		    model.remove(spo)
	    return self.__toRdf(model)
        else:
            raise BadSomethingOrOtherException

    def query(self, model, query, queryLang): 
	#do we support queryLang? throw exception if not
	if model.supportsQueryLanguage(queryLang):
	    return self.__toRdf(model.query(query))	
	else:
	    raise exception.UnsupportedQueryLanguage
	
    def get(self, model, spo):
	new = InMemoryTripleStore()
	for triple in model.triples(spo):
	    new.add(triple)
	return self.__toRdf(new)

    def options(self):
	"""
	We want:
	
	1. query languages supported, with conformance levels for each
	2. whether contexts are supported in models
	3. how to get a list of public models
	4. ...
	Maybe TripleStore's should preload themselves with this sort of stuff so that
	it can be easily queried, something like:
	
	rdflib = http://rdflib.net/rdflib/1.3.0/TripleStore/options#
	rdflib:supports <queryLang URI>
	rdflib:conformanceLevel <full, partial>
	rdflib:contexts <bool>
	rdflib:queryPublicModels <URI>
	rdflib:rdfNetApiSupports <method list>
	
	This preloading could be based upon the mixins, so we'd need some kind of 
	metaclass magic (?) to do the loading generically -- make it an OptionsMixin
	"""
	return None
