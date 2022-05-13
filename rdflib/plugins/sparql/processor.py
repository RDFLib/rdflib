"""
Code for tying SPARQL Engine into RDFLib

These should be automatically registered with RDFLib

"""


from rdflib.query import Processor, Result, UpdateProcessor

from rdflib.plugins.sparql.sparql import Query

from rdflib.plugins.sparql.parser import parseQuery, parseUpdate
from rdflib.plugins.sparql.algebra import translateQuery, translateUpdate

from rdflib.plugins.sparql.evaluate import evalQuery
from rdflib.plugins.sparql.update import evalUpdate


def prepareQuery(queryString, initNs={}, base=None):
    """
    Parse and translate a SPARQL Query
    """
    ret = translateQuery(parseQuery(queryString), base, initNs)
    ret._original_args = (queryString, initNs, base)
    return ret


def processUpdate(graph, updateString, initBindings={}, initNs={}, base=None):
    """
    Process a SPARQL Update Request
    returns Nothing on success or raises Exceptions on error
    """
    evalUpdate(
        graph, translateUpdate(parseUpdate(updateString), base, initNs), initBindings
    )


class SPARQLResult(Result):
    def __init__(self, res):
        Result.__init__(self, res["type_"])
        self.vars = res.get("vars_")
        self.bindings = res.get("bindings")
        self.askAnswer = res.get("askAnswer")
        self.graph = res.get("graph")


class SPARQLUpdateProcessor(UpdateProcessor):
    def __init__(self, graph):
        self.graph = graph

    def update(self, strOrQuery, initBindings={}, initNs={}):
        if isinstance(strOrQuery, str):
            strOrQuery = translateUpdate(parseUpdate(strOrQuery), initNs=initNs)

        return evalUpdate(self.graph, strOrQuery, initBindings)


class SPARQLProcessor(Processor):
    def __init__(self, graph):
        self.graph = graph

    def check(s):
        pass

    
    def Describe(self , strOrQuery):
        pass

    def clean_query(self, strOrQuery):
        
        temp = strOrQuery.replace("SELECT *", "SELECT **SELECT *").replace("\n", "")
        temp= temp.split("SELECT **")
        # print( temp)
        i=-1
        while i < len(temp)-1:
            i=i+1
            data = temp[i]
            if("SELECT *" in data):
                j =i+ 1
                cnt =0 
                # print(len(temp))
                # print("######################################")
                while(j< len(temp)):
                    
                    # print("j"+str(j))
                    if ("SELECT *" in temp[j]):
                        # print(j)
                        # print("Ayush")
                        cnt = cnt+1
                        if(j+1!=len(temp)):
                            j= j+1
                        else:
                            break
                            
                        
                    else:
                        break
    
                if( cnt ==0):
                    i=j 
                    
                else:
                    
                    if ("SELECT ?" in temp[j] ):
                        ind=1
                        ind1 = temp[j].find("SELECT ?")+8
                        if (ind1==-1): 
                            pass

                        
                        ind2 = temp[j].find("{", ind1)
                        # print("ohohoh")
                        
                        label = temp[j][ind1: ind2].strip().replace("WHERE", "").strip()
                        # print(label)
                        # print(i,j)
                        for q in range(i+1 ,j+1):
                            hey =temp[q].replace("SELECT *","Select ?"+ label)
                            # print("-----------")
                            # print(hey)
                            # print("-----------")
                            temp[q] = hey
                        
                    else:
                        ind1 = temp[j].find("{")
                        ind2 = temp[j].find("}")
                        label  = temp[j][ind1+1:ind2].strip().split(".")
                        final_label=""
                        for t in range(len(label)-1):
                            yr = label[t].strip().split(" ")
                            for x in yr:
                                if (x[0]=="?"):
                                    final_label+=x+" "
                            
                        
                        # print(final_label)
                        
                        for q in range(i+1 ,j+1):
                            hey =temp[q].replace("SELECT *","Select "+ final_label)
                            temp[q] = hey
                    i=j 
                    
                    

        finalans  = "".join(temp)
        # print("------------------")
        # print(finalans)
        # print("------------------")
        return finalans
                            


                        

            
            

    
   


    def query(self, strOrQuery, initBindings={}, initNs={}, base=None, DEBUG=False):
        """
        Evaluate a query with the given initial bindings, and initial
        namespaces. The given base is used to resolve relative URIs in
        the query and will be overridden by any BASE given in the query.
        """

        if ( "describe" in strOrQuery.lower()):
            return self.handle_describe(strOrQuery )



        strOrQuery= self.clean_query(strOrQuery)
        # print("Hey" , strOrQuery)
        
        if not isinstance(strOrQuery, Query):

            parsetree = parseQuery(strOrQuery)
            # print("parse tree", parsetree)
            # for i in parsetree.split(","): 
            #     print("--------------")
            #     print(i)
            # k=str(parsetree).split(",")
            # print('break------break------------------------------break---------break-------')
            # for i in k:
            #     print('------------------------')
            #     print(i)
            query = translateQuery(parsetree, base, initNs)
        else:
            query = strOrQuery
        # print("We r right" , query)
        return evalQuery(self.graph, query, initBindings, base)
