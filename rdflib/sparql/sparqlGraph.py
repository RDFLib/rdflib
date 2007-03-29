from rdflib import URIRef, BNode, Literal
from rdflib.Identifier import Identifier
from rdflib.Graph import Graph

from rdflib.sparql.sparql import Query, SPARQLError
from rdflib.sparql.graphPattern import GraphPattern


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


class SPARQLGraph(Graph):
    """
    A subclass of Graph with a few extra SPARQL bits.
    """
    def __init__(self, graph):
        self.graph = graph # TODO
        store = graph.store
        identifier = graph.identifier
        super(SPARQLGraph, self).__init__(store, identifier)

    def query(self,selection,patterns,optionalPatterns=[],initialBindings = {}) :
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
        result = self.queryObject(patterns,optionalPatterns,initialBindings)
        if result == None :
            # generate some proper output for the exception :-)
            msg = "Errors in the patterns, no valid query object generated; "
            if isinstance(patterns,GraphPattern) :
                msg += ("pattern:\n%s" % patterns)
            else :
                msg += ("pattern:\n%s\netc..." % patterns[0])
            raise SPARQLError(msg)
        return result.select(selection)

    def queryObject(self,patterns,optionalPatterns=[],initialBindings = None) :
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
            top = _SPARQLNode(None,bindings,pattern.patterns,self)
            top.expand(pattern.constraints)
            for opt in finalOptionalPatterns :
                bindings = _createInitialBindings(opt)
                if initialBindings:
                    bindings.update(initialBindings)
                top.expandOptions(bindings,opt.patterns,opt.constraints)
            r = Query(top,self)
            if retval == None :
                retval = r
            else :
                # This branch is, effectively, the UNION clause of the draft
                retval = retval + r
        return retval

    ##############################################################################################################
    # Clustering methods
    def _clusterForward(self,seed,Cluster) :
        """Cluster the triple store: from a seed, transitively get all
        properties and objects in direction of the arcs.

        @param seed: RDFLib Resource

        @param Cluster: a L{sparqlGraph} instance, that has to be
        expanded with the new arcs
        """
        try :
            # get all predicate and object pairs for the seed.
            # *If not yet in the new cluster, then go with a recursive round with those*
            for (p,o) in self.graph.predicate_objects(seed) :
                if not (seed,p,o) in Cluster.graph :
                    Cluster.add((seed,p,o))
                    self._clusterForward(p,Cluster)
                    self._clusterForward(o,Cluster)
        except :
            pass


    def clusterForward(self,seed,Cluster=None) :
        """
        Cluster the triple store: from a seed, transitively get all
        properties and objects in direction of the arcs.

        @param seed: RDFLib Resource

        @param Cluster: another sparqlGraph instance; if None, a new
        one will be created. The subgraph will be added to this graph.

        @returns: The triple store containing the cluster

        @rtype: L{sparqlGraph}
        """
        if Cluster == None :
            Cluster = SPARQLGraph()

        # This will raise an exception if not kosher...
        try :
            check_subject(seed)
        except :
            print "Wrong type for clustering (probably a literal): %s" % seed
            import sys
            sys.exit(0)

        self._clusterForward(seed,Cluster)
        return Cluster


    def _clusterBackward(self,seed,Cluster) :
        """Cluster the triple store: from a seed, transitively get all
        properties and objects in backward direction of the arcs.

        @param seed: RDFLib Resource

        @param Cluster: a L{sparqlGraph} instance, that has to be
        expanded with the new arcs
        """
        try :
            for (s,p) in self.graph.subject_predicates(seed) :
                if not (s,p,seed) in Cluster.graph :
                    Cluster.add((s,p,seed))
                    self._clusterBackward(s,Cluster)
                    self._clusterBackward(p,Cluster)
        except :
            pass

    def clusterBackward(self,seed,Cluster=None) :
        """
        Cluster the triple store: from a seed, transitively get all
        properties and objects 'backward', ie, following the link back
        in the graph.

        @param seed: RDFLib Resource

        @param Cluster: another sparqlGraph instance; if None, a new
        one will be created. The subgraph will be added to this graph.

        @returns: The triple store containing the cluster

        @rtype: L{sparqlGraph}
        """
        if Cluster == None :
            Cluster = SPARQLGraph()

        # This will raise an exception if not kosher...
        try :
            check_object(seed)
        except :
            print "Wrong type for clustering: %s" % seed
            import sys
            sys.exit(0)

        self._clusterBackward(seed,Cluster)
        return Cluster

    def cluster(self,seed) :
        """
        Cluster up and down, by summing up the forward and backward
        clustering

        @param seed: RDFLib Resource

        @returns: The triple store containing the cluster

        @rtype: L{sparqlGraph}
        """
        raise "Am I getting here?"
        return self.clusterBackward(seed) + self.clusterForward(seed)
