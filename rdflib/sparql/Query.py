import types, sets

from rdflib import URIRef, BNode, Literal
from rdflib.Identifier import Identifier

from rdflib.util import check_subject, list2set

from rdflib.sparql import SPARQLError
from rdflib.sparql.Unbound import Unbound
from rdflib.sparql.sparqlGraph import SPARQLGraph
from rdflib.sparql.graphPattern import GraphPattern


def _checkOptionals(pattern,optionals) :
    """
    The following remark in the SPARQL document is important:

    'If a new variable is mentioned in an optional block (as mbox and
    hpage are mentioned in the previous example), that variable can be
    mentioned in that block and can not be mentioned in a subsequent
    block.'

    What this means is that the various optional blocks do not
    interefere at this level and there is no need for a check whether
    a binding in a subsequent block clashes with an earlier optional
    block.

    This method checks whether this requirement is fulfilled. Raises a
    SPARQLError exception if it is not (the rest of the algorithm
    relies on this, so checking it is a good idea...)

    @param pattern: graph pattern
    @type pattern: L{GraphPattern<rdflib.sparql.GraphPattern>}
    @param optionals: graph pattern
    @type optionals: L{GraphPattern<rdflib.sparql.GraphPattern>}
    @raise SPARQLError: if the requirement is not fulfilled
    """
    for i in xrange(0,len(optionals)) :
        for c in optionals[i].unbounds :
            if c in pattern.unbounds :
                # this is fine, an optional query variable can appear in the main pattern, too
                continue
            if i > 0 :
                for j in xrange(0,i) :
                    if c in optionals[j].unbounds :
                        # This means that:
                        #   - the variable is not in the main pattern (because the previous if would have taken care of it)
                        #   - the variable is in the previous optional: ie, Error!
                        raise SPARQLError("%s is an illegal query string, it appear in a previous OPTIONAL clause" % c)


def _variablesToArray(variables,name='') :
    """Turn an array of Variables or query strings into an array of query strings. If the 'variables'
    is in fact a single string or Variable, then it is also put into an array.

    @param variables: a string, a unicode, or a Variable, or an array of those (can be mixed, actually). As a special case,
    if the value is "*", it returns None (this corresponds to the wildcard in SPARQL)
    @param name: the string to be used in the error message
    """
    if isinstance(variables,basestring) :
        if variables == "*" :
            return None
        else :
            return [variables]
    elif isinstance(variables,Unbound) :
        return [variables.name]
    elif type(variables) == list or type(variables) == tuple :
        retval = []
        for s in variables :
            if isinstance(s,basestring) :
                retval.append(s)
            elif isinstance(s,Unbound) :
                retval.append(s.name)
            else :
                raise SPARQLError("illegal type in '%s'; must be a string, unicode, or a Variable" % name)
    else :
        raise SPARQLError("'%s' argument must be a string, a Variable, or a list of those" % name)
    return retval

def _createInitialBindings(pattern) :
    """Creates an initial binding directory for the Graph Pattern by putting a None as a value for each
    query variable.

    @param pattern: graph pattern
    @type pattern: L{GraphPattern<rdflib.sparql.GraphPattern>}
    """
    bindings = {}
    for c in pattern.unbounds :
        bindings[c] = None
    return bindings


class _SPARQLNode:
    """
    The SPARQL implementation is based on the creation of a tree, each
    level for each statement in the 'where' clause of SPARQL.

    Each node maintains a 'binding' dictionary, with the variable
    names and either a None if not yet bound, or the binding
    itself. The method 'expand' tries to make one more step of binding
    by looking at the next statement: it takes the statement of the
    current node, binds the variables if there is already a binding,
    and looks at the triple store for the possibilities. If it finds
    valid new triplets, that will bind some more variables, and
    children will be created with the next statement in the 'where'
    array with a new level of bindings. This is done for each triplet
    found in the store, thereby branching off the tree. If all
    variables are already bound but the statement, with the bound
    variables, is not 'true' (ie, there is no such triple in the
    store), the node is marked as 'clash' and no more expansion is
    made; this node will then be thrown away by the parent. If I{all}
    children of a node is a clash, then it is marked as a clash
    itself.

    At the end of the process, the leaves of the tree are searched; if
    a leaf is such that:

      - all variables are bound
      - there is no clash

    then the bindings are returned as possible answers to the query.

    The optional clauses are treated separately: each 'valid' leaf is
    assigned an array of expansion trees that contain the optional
    clauses (that may have some unbound variables bound at the leaf,
    though).

    @ivar parent: parent in the tree
    @type parent: _SPARQLNode
    @ivar children: the children (in an array)
    @type children: array of _SPARQLNode
    @ivar bindings:  copy of the bindings locally
    @type bindings: dictionary
    @ivar statement:  the current statement
    @type statement: a (s,p,o,f) tuple ('f' is the local filter or None)
    @ivar rest:  the rest of the statements (an array)
    @ivar clash: intialized to False
    @type clash: Boolean
    @ivar bound:  True or False depending on whether all variables are bound in self.binding
    @type bound: Boolean
    @ivar optionalTrees: expansion trees for optional statements
    @type optionalTrees: array of _SPARQLNode instances
    """
    def __init__(self,parent,bindings,statements,tripleStore) :
        """
        @param parent:     parent node
        @param bindings:   a dictionary with the bindings that are already done or with None value if no binding yet
        @param statements: array of statements from the 'where' clause. The first element is
        for the current node, the rest for the children. If empty, then no
        expansion occurs (ie, the node is a leaf)
        @param tripleStore: the 'owner' triple store
        @type tripleStore: L{sparqlGraph<rdflib.sparql.sparqlGraph.sparqlGraph>}
        """
        self.tripleStore         = tripleStore
        self.bindings            = bindings
        self.optionalTrees       = []
        if None in bindings.values() :
            self.bound = False
        else :
            self.bound = True
        self.clash     = False

        self.parent    = parent
        self.children  = []

        if len(statements) > 0 :
            self.statement = statements[0]
            self.rest      = statements[1:]
        else :
            self.statement = None
            self.rest      = None

    def returnResult(self,select) :
        """
        Collect the result by search the leaves of the the tree. The
        variables in the select are exchanged against their bound
        equivalent (if applicable). This action is done on the valid
        leaf nodes only, the intermediate nodes only gather the
        children's results and combine it in one array.

        @param select: the array of unbound variables in the original
        select that do not appear in any of the optionals. If None,
        the full binding should be considered (this is the case for
        the SELECT * feature of SPARQL)
        @returns: an array of dictionaries with non-None bindings.
        """
        if len(self.children) > 0 :
            # combine all the results of all the kids into one array
            retval = []
            for c in self.children :
                res = c.returnResult(select)
                # res is a list of dictionaries, so each tuple should be taken out and added to the result
                for t in res :
                    retval.append(t)
            return retval
        else :
            retval = []
            if self.bound == True and self.clash == False :
                # This node should be able to contribute to the final results:
                result = {}
                # This where the essential happens: the binding values are used to construct the selection result
                if select :
                    for a in select :
                        if a in self.bindings :
                            result[a] = self.bindings[a]
                else :
                    result = self.bindings.copy()
                # Initial return block. If there is no optional processing, that is the result, in fact,
                # because the for cycle below will not happen
                retval = [result]
                # The following remark in the SPARQL document is important at this point:
                # "If a new variable is mentioned in an optional block (as mbox and hpage are mentioned
                #  in the previous example), that variable can be mentioned in that block and can not be
                #  mentioned in a subsequent block."
                # What this means is that the various optional blocks do not interefere at this point
                # and there is no need for a check whether a binding in a subsequent block
                # clashes with an earlier optional block.
                # The API checks this at the start.
                # What happens here is that the result of the optional expantion is added to what is already
                # there. Note that this may lead to a duplication of the result so far, if there are several
                # alternatives returned by the optionals!
                for optTree in self.optionalTrees :
                    # get the results from the optional Tree...
                    optionals = optTree.returnResult(select)
                    # ... and extend the results accumulated so far with the new bindings
                    # It is worth separating the case when there is only one optional block; it avoids
                    # unnecessary copying
                    if len(optionals) == 0 :
                        # no contribution at all :-(
                        continue
                    elif len(optionals) == 1 :
                        optResult = optionals[0]
                        for res in retval :
                            for k in optResult :
                                if optResult[k] != None :
                                    res[k] = optResult[k]
                    else :
                        newRetval = []
                        for optResult in optionals :
                            # Each binding dictionary we have so far should be copied with the new values
                            for res in retval :
                                dct = {}
                                # copy the content of the exisiting bindings ...
                                dct = res.copy()
                                # ... and extend it with the optional results
                                for k in optResult :
                                    if optResult[k] != None :
                                        dct[k] = optResult[k]
                                newRetval.append(dct)
                        retval = newRetval
            return retval


    def expandSubgraph(self,subTriples,pattern) :
        """
        Method used to collect the results. There are two ways to
        invoke the method:

          - if the pattern argument is not None, then this means the
          construction of a separate triple store with the
          results. This means taking the bindings in the node, and
          constuct the graph via the
          L{construct<rdflib.sparql.graphPattern.GraphPattern.construct>}
          method. This happens on the valid leafs; intermediate nodes
          call the same method recursively - otherwise, a leaf returns
          an array of the bindings, and intermediate methods aggregate
          those.

        In both cases, leaf nodes may successifely expand the optional
        trees that they may have.

        @param subTriples: the triples so far
        @type subTriples: L{sparqlGraph<rdflib.sparql.sparqlGraph.sparqlGraph>}
        @param pattern: a graph pattern used to construct a graph
        @type pattern: L{GraphPattern<rdflib.sparql.graphPattern.GraphPattern>}
        @return: if pattern is not None, an array of binding dictionaries
        """
        def b(r,bind) :
            if type(r) == str :
                val = bind[r]
                if val == None :
                    raise RuntimeError()
                return bind[r]
            else :
                return r
        if len(self.children) > 0 :
            # all children return an array of bindings (each element being a dictionary)
            if pattern == None :
                retval = reduce(lambda x,y: x+y, [x.expandSubgraph(subTriples,None) for x in self.children],[])
                (s,p,o,func) = self.statement
                for bind in retval :
                    try :
                        st = (b(s,bind),b(p,bind),b(o,bind))
                        subTriples.add(st)
                    except :
                        # any exception means a None value creeping in, or something similar..
                        pass
                return retval
            else :
                for x in self.children :
                    x.expandSubgraph(subTriples,pattern)
        else :
            # return the local bindings if any. Not the optional trees should be added, too!
            if self.bound == True and self.clash == False :
                # Get the possible optional branches:
                for t in self.optionalTrees :
                    t.expandSubgraph(subTriples,pattern)
                if pattern == None :
                    return [self.bindings]
                else :
                    pattern.construct(subTriples,self.bindings)
            else :
                return []


    def _bind(self,r) :
        """
        @param r: string
        @return: returns None if no bindings occured yet, the binding otherwise
        """
        if isinstance(r,basestring) and not isinstance(r,Identifier)  :
            if self.bindings[r] == None :
                return None
            else :
                return self.bindings[r]
        elif isinstance(r,(BNode)):
            return self.bindings.get(r)            
        else :
            return r

    def expand(self,constraints) :
        """
        The expansion itself. See class comments for details.

        @param constraints: array of global constraining (filter) methods
        """
        # if there are no more statements, that means that the constraints have been fully expanded
        if self.statement :
            # decompose the statement into subject, predicate and object
            # default setting for the search statement
            # see if subject (resp. predicate and object) is already bound. This
            # is done by taking over the content of self.dict if not None and replacing
            # the subject with that binding
            # the (search_subject,search_predicate,search_object) is then created
            (s,p,o,func) = self.statement
            # put the bindings we have so far into the statement; this may add None values,
            # but that is exactly what RDFLib uses in its own search methods!
            (search_s,search_p,search_o) = (self._bind(s),self._bind(p),self._bind(o))
            for (result_s,result_p,result_o) in self.tripleStore.graph.triples((search_s,search_p,search_o)) :
                # if a user defined constraint has been added, it should be checked now
                if func != None and func(result_s,result_p,result_o) == False :
                    # Oops, this result is not acceptable, jump over it!
                    continue
                # create a copy of the current bindings, by also adding the new ones from result of the search
                new_bindings = self.bindings.copy()
                if search_s == None : new_bindings[s] = result_s
                if search_p == None : new_bindings[p] = result_p
                if search_o == None : new_bindings[o] = result_o

                # Recursion starts here: create and expand a new child
                child = _SPARQLNode(self,new_bindings,self.rest,self.tripleStore)
                child.expand(constraints)                
                # if the child is a clash then no use adding it to the tree, it can be forgotten
                if self.clash == False :
                    self.children.append(child)

            if len(self.children) == 0 :
                # this means that the constraints could not be met at all with this binding!!!!
                self.clash = True
        else :
            # this is if all bindings are done; the conditions (ie, global constraints) are still to be checked
            if self.bound == True and self.clash == False :
                for func in constraints :
                    if func(self.bindings) == False :
                        self.clash = True
                        break

    def expandOptions(self,bindings,statements,constraints) :
        """
        Managing optional statements. These affect leaf nodes only, if
        they contain 'real' results. A separate Expansion tree is
        appended to such a node, one for each optional call.

        @param bindings: current bindings dictionary

        @param statements: array of statements from the 'where'
        clause. The first element is for the current node, the rest
        for the children. If empty, then no expansion occurs (ie, the
        node is a leaf). The bindings at this node are taken into
        account (replacing the unbound variables with the real
        resources) before expansion

        @param constraints: array of constraint (filter) methods
        """
        def replace(key,resource,tupl) :
            s,p,o,func = tupl
            if key == s : s = resource
            if key == p : p = resource
            if key == o : o = resource
            return (s,p,o,func)

        if len(self.children) == 0  :
            # this is a leaf in the original expansion
            if self.bound == True and self.clash == False :
                # see if the optional bindings can be reduced because they are already
                # bound by this node
                toldBNodeLookup = {}
                for key in self.bindings :
                    normalizedStatements = []
                    for t in statements:
                        val = self.bindings[key]
                        if isinstance(val,BNode) and val not in toldBNodeLookup:
                            toldBNodeLookup[val] = val
                        normalizedStatements.append(replace(key,self.bindings[key],t))
                    statements = normalizedStatements
                    if key in bindings :
                        del bindings[key]
                bindings.update(toldBNodeLookup)
                optTree = _SPARQLNode(None,bindings,statements,self.tripleStore)
                self.optionalTrees.append(optTree)
                optTree.expand(constraints)
        else :
            for c in self.children :
                c.expandOptions(bindings,statements,constraints)


def _processResults(select,arr) :
    '''
    The result in an expansion node is in the form of an array of
    binding dictionaries.  The caller should receive an array of
    tuples, each tuple representing the final binding (or None) I{in
    the order of the original select}. This method is the last step of
    processing by processing these values to produce the right result.

    @param select: the original selection list. If None, then the
    binding should be taken as a whole (this corresponds to the SELECT * feature of SPARQL)
    @param arr: the array of bindings
    @type arr:
    an array of dictionaries
    @return: a list of tuples with the selection results
    '''
    retval = []
    if select :
        for bind in arr :
            # each result binding must be taken separately
            qresult = []
            for s in select :
                if s in bind :
                    qresult.append(bind[s])
                else :
                    qresult.append(None)
            # as a courtesy to the user, if the selection has one single element only, than we do no
            # put in a tuple, just add it that way:
            if len(select) == 1 :
                retval.append(qresult[0])
            else :
                retval.append(tuple(qresult))
    else :
        # this is the case corresponding to a SELECT * query call
        for bind in arr:
            qresult = [val for key,val in bind.items()]
            if len(qresult) == 1 :
                retval.append(qresult[0])
            else :
                retval.append(tuple(qresult))
    return retval


def query(graph, selection, patterns, optionalPatterns=[], initialBindings = {}) :
    """
    A shorthand for the creation of a L{Query} instance, returning
    the result of a L{Query.select} right away. Good for most of
    the usage, when no more action (clustering, etc) is required.

    @param selection: a list or tuple with the selection criteria,
    or a single string. Each entry is a string that begins with a"?".

    @param patterns: either a
    L{GraphPattern<rdflib.sparql.graphPattern.GraphPattern>}
    instance or a list of instances thereof. Each pattern in the
    list represent an 'OR' (or 'UNION') branch in SPARQL.

    @param optionalPatterns: either a
    L{GraphPattern<rdflib.sparql.graphPattern.GraphPattern>}
    instance or a list of instances thereof. For each elements in
    the 'patterns' parameter is combined with each of the optional
    patterns and the results are concatenated. The list may be
    empty.

    @return: list of query results
    @rtype: list of tuples
    """
    result = queryObject(graph, patterns,optionalPatterns,initialBindings)
    if result == None :
        # generate some proper output for the exception :-)
        msg = "Errors in the patterns, no valid query object generated; "
        if isinstance(patterns,GraphPattern) :
            msg += ("pattern:\n%s" % patterns)
        else :
            msg += ("pattern:\n%s\netc..." % patterns[0])
        raise SPARQLError(msg)
    return result.select(selection)

def queryObject(graph, patterns, optionalPatterns=[], initialBindings = None) :
    """
    Creation of a L{Query} instance.

    @param patterns: either a
    L{GraphPattern<rdflib.sparql.graphPattern.GraphPattern>}
    instance or a list of instances thereof. Each pattern in the
    list represent an 'OR' (or 'UNION') branch in SPARQL.

    @param optionalPatterns: either a
    L{GraphPattern<rdflib.sparql.graphPattern.GraphPattern>}
    instance or a list of instances thereof. For each elements in
    the 'patterns' parameter is combined with each of the optional
    patterns and the results are concatenated. The list may be
    empty.

    @return: Query object
    @rtype: L{Query}
    """
    def checkArg(arg,error) :
        if arg == None :
            return []
        elif isinstance(arg,GraphPattern) :
            return [arg]
        elif type(arg) == list or type(arg) == tuple :
            for p in arg :
                if not isinstance(p,GraphPattern) :
                    raise SPARQLError("'%s' argument must be a GraphPattern or a list of those" % error)
            return arg
        else :
            raise SPARQLError("'%s' argument must be a GraphPattern or a list of those" % error)

    finalPatterns         = checkArg(patterns,"patterns")
    finalOptionalPatterns = checkArg(optionalPatterns,"optionalPatterns")

    retval = None
    if not initialBindings:
        initialBinding = {}
    for pattern in finalPatterns :
        # Check whether the query strings in the optional clauses are fine. If a problem occurs,
        # an exception is raised by the function
        _checkOptionals(pattern,finalOptionalPatterns)
        bindings = _createInitialBindings(pattern)
        if initialBindings:
            bindings.update(initialBindings)
        # This is the crucial point: the creation of the expansion tree and the expansion. That
        # is where the real meal is, we had only an apetizer until now :-)
        top = _SPARQLNode(None,bindings,pattern.patterns, graph)
        top.expand(pattern.constraints)
        for opt in finalOptionalPatterns :
            bindings = _createInitialBindings(opt)
            if initialBindings:
                bindings.update(initialBindings)
            top.expandOptions(bindings,opt.patterns,opt.constraints)
        r = Query(top, graph)
        if retval == None :
            retval = r
        else :
            # This branch is, effectively, the UNION clause of the draft
            retval = retval + r
    return retval


class Query :
    """
    Result of a SPARQL query. It stores to the top of the query tree, and allows some subsequent
    inquiries on the expanded tree. B{This class should not be
    instantiated by the user,} it is done by the L{queryObject<SPARQL.queryObject>} method.

    """
    def __init__(self,sparqlnode,triples,parent1=None,parent2=None) :
        """
        @param sparqlnode: top of the expansion tree
        @type sparqlnode: _SPARQLNode
        @param triples: triple store
        @type triples: L{sparqlGraph<rdflib.sparql.sparqlGraph>}
        @param parent1: possible parent Query when queries are combined by summing them up
        @type parent1: L{Query}
        @param parent2: possible parent Query when queries are combined by summing them up
        @type parent2: L{Query}
        """
        self.top             = sparqlnode
        self.triples         = triples
        # if this node is the result of a sum...
        self.parent1         = parent1
        self.parent2         = parent2

    def __add__(self,other) :
        """This may be useful when several queries are performed and
        one wants the 'union' of those.  Caveat: the triple store must
        be the same for each argument. This method is used internally
        only anyway...  Efficiency trick (I hope it works): the
        various additions on subgraphs are not done here; the results
        are calculated only if really necessary, ie, in a lazy
        evaluation manner.  This is achieved by storing self and the
        'other' in the new object
        """
        return Query(None,self.triples,self,other)

    def _getFullBinding(self) :
        """Retrieve the full binding, ie, an array of binding dictionaries
        """
        if self.parent1 != None and self.parent2 != None :
            return self.parent1._getFullBinding() + self.parent2._getFullBinding()
        else :
            # remember: returnResult returns an array of dictionaries
            return self.top.returnResult(None)

    def _getAllVariables(self):
       """Retrieve the list of all variables, to be returned"""
       if self.parent1 and self.parent2:
           return list2set(self.parent1._getAllVariables() + self.parent2._getAllVariables())
       else:
           return list2set(self.top.bindings.keys())

    def _orderedSelect(self,selection,orderedBy,orderDirection) :
        """
        The variant of the selection (as below) that also includes the sorting. Because that is much less efficient, this is
        separated into a distinct method that is called only if necessary. It is called from the L{select<select>} method.
		
        Because order can be made on variables that are not part of the final selection, this method retrieves a I{full}
        binding from the result to be able to order it (whereas the core L{select<select>} method retrieves from the result
        the selected bindings only). The full binding is an array of (binding) dictionaries; the sorting sorts this array
        by comparing the bound variables in the respective dictionaries. Once this is done, the final selection is done.

        @param selection: Either a single query string, or an array or tuple thereof.
        @param orderBy: either a function or a list of strings (corresponding to variables in the query). If None, no sorting occurs
        on the results. If the parameter is a function, it must take two dictionary arguments (the binding dictionaries), return
        -1, 0, and 1, corresponding to smaller, equal, and greater, respectively.
        @param orderDirection: if not None, then an array of integers of the same length as orderBy, with values the constants
        ASC or DESC (defined in the module). If None, an ascending order is used.
        @return: selection results
        @rtype: list of tuples
        @raise SPARQLError: invalid sorting arguments
        """
        fullBinding = self._getFullBinding()
        if type(orderedBy) is types.FunctionType :
            _sortBinding = orderedBy
        else :
            orderKeys = _variablesToArray(orderedBy,"orderBy")
            # see the direction
            oDir = None # this is just to fool the interpreter's error message
            if orderDirection is None :
                oDir = [ True for i in xrange(0,len(orderKeys)) ]
            elif type(orderDirection) is types.BooleanType :
                oDir = [ orderDirection ]
            elif type(orderDirection) is not types.ListType and type(orderDirection) is not types.TupleType :
                raise SPARQLError("'orderDirection' argument must be a list")
            elif len(orderDirection) != len(orderKeys) :
                raise SPARQLError("'orderDirection' must be of an equal length to 'orderBy'")
            else :
                oDir = orderDirection
            def _sortBinding(b1,b2) :
                """The sorting method used by the array sort, with return values as required by the python run-time
                The to-be-compared data are dictionaries of bindings
                """
                for i in xrange(0,len(orderKeys)) :
					# each key has to be compared separately. If there is a clear comparison result on that key
					# then we are done, but when that is not the case, the next in line should be used
                    key       = orderKeys[i]
                    direction = oDir[i]
                    if key in b1 and key in b2 :
                        val1 = b1[key]
                        val2 = b2[key]
                        if val1 != None and val2 != None :
                            if direction :
                                if   val1 < val2 : return -1
                                elif val1 > val2 : return 1
                            else :
                                if   val1 > val2 : return -1
                                elif val1 < val2 : return 1
                return 0
        # get the full Binding sorted
        fullBinding.sort(_sortBinding)
        # remember: _processResult turns the expansion results (an array of dictionaries)
        # into an array of tuples in the right, original order
        retval = _processResults(selection,fullBinding)
        return retval

    def select(self,selection,distinct=True,limit=None,orderBy=None,orderAscend=None,offset=0) :
        """
        Run a selection on the query.

        @param selection: Either a single query string, or an array or tuple thereof.
        @param distinct: if True, identical results are filtered out
        @type distinct: Boolean
        @param limit: if set to an integer value, the first 'limit' number of results are returned; all of them otherwise
        @type limit: non negative integer
        @param orderBy: either a function or a list of strings (corresponding to variables in the query). If None, no sorting occurs
        on the results. If the parameter is a function, it must take two dictionary arguments (the binding dictionaries), return
        -1, 0, and 1, corresponding to smaller, equal, and greater, respectively.
        @param orderAscend: if not None, then an array of booelans of the same length as orderBy, True for ascending and False
		for descending. If None, an ascending order is used.
        @offset the starting point of return values in the array of results. Obviously, this parameter makes real sense if
        some sort of order is defined.
        @return: selection results
        @rtype: list of tuples
        @raise SPARQLError: invalid selection argument
        """
        def _uniquefyList(lst) :
            """Return a copy of the list but possible duplicate elements are taken out. Used to
            post-process the outcome of the query
            @param lst: input list
            @return: result list
            """
            if len(lst) <= 1 :
                return lst
            else :
                # must be careful! Using the quick method of Sets destroy the order. Ie, if this was ordered, then
                # a slower but more secure method should be used
                if orderBy != None :
                    retval = []
                    for i in xrange(0,len(lst)) :
                        v = lst[i]
                        skip = False
                        for w in retval :
                            if w == v :
                                skip = True
                                break
                        if not skip :
                            retval.append(v)
                    return retval
                else :
                    return list(sets.Set(lst))
        # Select may be a single query string, or an array/tuple thereof
        selectionF = _variablesToArray(selection,"selection")

        if type(offset) is not types.IntType or offset < 0 :
            raise SPARQLError("'offset' argument is invalid")

        if limit != None :
            if type(limit) is not types.IntType or limit < 0 :
                raise SPARQLError("'offset' argument is invalid")

        if orderBy != None :
            results = self._orderedSelect(selectionF,orderBy,orderAscend)
        else :
            if self.parent1 != None and self.parent2 != None :
                results = self.parent1.select(selectionF) + self.parent2.select(selectionF)
            else :
                # remember: _processResult turns the expansion results (an array of dictionaries)
                # into an array of tuples in the right, original order
                results = _processResults(selectionF,self.top.returnResult(selectionF))
        if distinct :
            retval = _uniquefyList(results)
        else :
            retval = results

        if limit != None :
            return retval[offset:limit+offset]
        elif offset > 0 :
            return retval[offset:]
        else :
            return retval

    def construct(self,pattern=None) :
        """
        Expand the subgraph based on the pattern or, if None, the
        internal bindings.

        In the former case the binding is used to instantiate the
        triplets in the patterns; in the latter, the original
        statements are used as patterns.

        The result is a separate triple store containing the subgraph.

        @param pattern: a L{GraphPattern<rdflib.sparql.graphPattern.GraphPattern>} instance or None
        @return: a new triple store
        @rtype: L{sparqlGraph<rdflib.sparql.sparqlGraph>}
        """
        if self.parent1 != None and self.parent2 != None :
            return self.parent1.construct(pattern) + self.parent2.construct(pattern)
        else :
            subgraph = SPARQLGraph()
            self.top.expandSubgraph(subgraph,pattern)
            return subgraph

    def ask(self) :
        """
        Whether a specific pattern has a solution or not.
        @rtype: Boolean
        """
        return len(self.select('*')) != 0

    #########################################################################################################
    # The methods below are not really part of SPARQL, or may be used to a form of DESCRIBE. However, that latter
    # is still in a flux in the draft, so we leave it here, pending

    def clusterForward(self,selection) :
        """
        Forward clustering, using all the results of the query as
        seeds (when appropriate). It is based on the usage of the
        L{cluster forward<rdflib.sparql.sparqlGraph.clusterForward>}
        method for triple store.

        @param selection: a selection to define the seeds for
        clustering via the selection; the result of select used for
        the clustering seed

        @return: a new triple store
        @rtype: L{sparqlGraph<rdflib.sparql.sparqlGraph>}
        """
        if self.parent1 != None and self.parent2 != None :
            return self.parent1.clusterForward(selection) + self.parent2.clusterForward(selection)
        else :
            clusterF = SPARQLGraph()
            for r in reduce(lambda x,y: list(x) + list(y),self.select(selection),()) :
                try :
                    check_subject(r)
                    self.triples.clusterForward(r,clusterF)
                except :
                    # no real problem, this is a literal, just forget about it
                    continue
            return clusterF

    def clusterBackward(self,selection) :
        """
        Backward clustering, using all the results of the query as
        seeds (when appropriate). It is based on the usage of the
        L{cluster backward<rdflib.sparql.sparqlGraph.clusterBackward>}
        method for triple store.

        @param selection: a selection to define the seeds for
        clustering via the selection; the result of select used for
        the clustering seed

        @return: a new triple store
        @rtype: L{sparqlGraph<rdflib.sparql.sparqlGraph>}
        """
        if self.parent1 != None and self.parent2 != None :
            return self.parent1.clusterBackward(selection) + self.parent2.clusterBackward(selection)
        else :
            clusterB = SPARQLGraph()
            # to be on the safe side, see if the query has been properly finished
            for r in reduce(lambda x,y: list(x) + list(y),self.select(selection),()) :
                self.triples.clusterBackward(r,clusterB)
            return clusterB

    def cluster(self,selection) :
        """
        Cluster: a combination of L{Query.clusterBackward} and
        L{Query.clusterForward}.  @param selection: a selection to
        define the seeds for clustering via the selection; the result
        of select used for the clustering seed
        """
        return self.clusterBackward(selection) + self.clusterForward(selection)

    def describe(self,selection,forward=True,backward=True) :
        """
        The DESCRIBE Form in the SPARQL draft is still in state of
        flux, so this is just a temporary method, in fact.  It may not
        correspond to what the final version of describe will be (if
        it stays in the draft at all, that is).  At present, it is
        simply a wrapper around L{cluster}.

        @param selection: a selection to define the seeds for
        clustering via the selection; the result of select used for
        the clustering seed

        @param forward: cluster forward yes or no
        @type forward: Boolean
        @param backward: cluster backward yes or no
        @type backward: Boolean
        """
        if forward and backward :
            return self.cluster(selection)
        elif forward :
            return self.clusterForward(selection)
        elif backward :
            return self.clusterBackward(selection)
        else :
            return SPARQLGraph()

