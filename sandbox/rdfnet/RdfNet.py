"""$Id: RdfNet.py,v 1.4 2003/10/27 02:03:04 kendall Exp $"""

from StoreController import StoreController, INSERT, REMOVE, PUT
from ResultsFormatMap import formatMap

def resolveResultsFormat(uri):
    format = formatMap.get(uri, None)
    if format is None:
        raise UnknownResultsFormat
    else:
        return format #not sure what this format thing is yet

#need some kind of model registry, stored in an in-mem store, where we
#find out where the various models are...

class RdfNet(object):
    """Do we parameterize RdfNet instances by passing them a modelRef, or
    should we parameterize by passing the model ref to the methods? """

    def __init__(self):
        self.__scontrol = StorageController() #should this be a classvar?

	#do I build the statement set classes from what
	#storage controller returns or does someone else do it?
	#i think i should do it
	#because we already need to change statement sets depending on HTTP or 
	#SOAP

    def query(self, model, query, queryLang): 
        return self.sc.query(model, query, queryLang)
		
    def getStatements(self, model, s, p, o):
        return self.sc.get(model, tuple((s,p,o)))
		
    def insertStatements(self, model, statementSet): 
        return self.sc.mutate(model, statementSet, type=INSERT)

    def removeStatements(self, model, statementSet): 
        return self.sc.mutate(model, statementSet, type=REMOVE)

    def putStatements(self, model, statementSet): 
        return self.sc.mutate(model, statementSet, type=PUT)

    def updateStatements(self, model, removeSet, insertSet): 
        return self.sc.update(model, removeSet, insertSet)

    def options(self):
        return self.sc.options()
    
    def getSc(self):
        return self.__scontrol
    def setSc(self, sc):
        return self.__scontrol = sc
	
    sc = property(getSc, setSc, None, None)
