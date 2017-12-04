import rdflib
import copy

# ################################## #
#         CLASSES FOR GRAPHS         #
######################################

class Vertex(object):
    # Keep a (global) counter to 
    # give each node a unique id
    vertex_counter = 0
    
    def __init__(self, name):
        self.reachable = []
        self.name = name
        self.id = Vertex.vertex_counter
        self.previous_name = None
        Vertex.vertex_counter += 1
      

class Graph(object):
    def __init__(self):
        self.vertices = []
        # Transition matrix is a dict of dict, we can
        # access all possible transitions from a vertex
        # by indexing the transition matrix first and then
        # check whether the destination in the dict is True
        self.transition_matrix = {}
        
    def add_vertex(self, vertex):
        """Add vertex to graph and update the 
        transition matrix accordingly"""
        transition_row = {}
        for v in self.vertices:
            transition_row[v] = 0
            self.transition_matrix[v][vertex] = 0
        self.transition_matrix[vertex] = transition_row
        self.vertices.append(vertex)

    def add_edge(self, v1, v2):
        self.transition_matrix[v1][v2] = 1
        
    def remove_edge(self, v1, v2):
        self.transition_matrix[v1][v2] = 0

    def get_neighbors(self, vertex):
        return [k for (k, v) in self.transition_matrix[vertex].items() if v == 1]

    def relabel_nodes(self, mapping):
        for v in self.vertices:
            if v in mapping:
                v.previous_name = v.name
                v.name = mapping[v]


# ################################## #
#             RDF PARSING            #
######################################

namespaces = {'http://chronicals.ugent.be/': 'chron:',
              'http://purl.bioontology.org/ontology/SNOMEDCT/': 'snomed:',
              'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdfs:',
              'http://dbpedia.org/resource/': 'db:',
              'http://semanticweb.org/id/': 'sw:',
              'http://data.semanticweb.org/': 'sw:',
              'http://xmlns.com/foaf/0.1/': 'foaf:',
              'http://swrc.ontoware.org/ontology#': 'swrc:'}


def rdf_to_str(x):
    """Get the string representation for the rdflib object
    and replace urls by keywords defined in `namespaces`.
    Args:
        x (rdflib object)
    Returns:
        x (string)
    """
    x = str(x)
    for ns in namespaces:
        x = x.replace(ns, namespaces[ns])
    return x


def extract_instance(g, inst, d):
    """Extract a (`Graph`) subgraph from the large `rdflib.Graph`
    Args:
        g (rdflib.Graph)    : the large RDF graph
        inst (rdflib.URIRef): the new root of the subgraph
    Returns:
        a `Graph` object rooted at `inst`
    """
    subgraph = Graph()
    # Add the instance with custom label (root)
    root = Vertex('root')
    subgraph.add_vertex(root)

    nodes_to_explore = set([(inst, root)])
    for i in range(d):
        if len(nodes_to_explore):
            # Convert set to list, since we cannot change size
            for rdf, v in list(nodes_to_explore):  
                # Create a SPARQL query to filter out 
                # all triples with subject = `rdf`
                qres = g.query("""SELECT ?p ?o WHERE {
                                    ?s ?p ?o .
                               }""",
                               initBindings={'s': rdf})
                for row in qres:
                    # Add two new nodes
                    v1 = Vertex(rdf_to_str(row[0]))
                    v2 = Vertex(rdf_to_str(row[1]))
                    subgraph.add_vertex(v1)
                    subgraph.add_vertex(v2)
                    
                    # And two new edges
                    if rdf == inst:
                        subgraph.add_edge(root, v1)
                    else:
                        subgraph.add_edge(v, v1)
                    subgraph.add_edge(v1, v2)
                    
                    # Add the object as new node to explore
                    nodes_to_explore.add((row[1], v2))
                    
                # Remove the node we just explored
                nodes_to_explore.remove((rdf, v))
    return subgraph


# ################################## #
#      Weisfeiler-Lehman kernel      #
######################################


def wf_relabel_graph(g, s_n_to_counter, n_iterations=5, verbose=False):
    """Weisfeiler-Lehman relabeling algorithm, used to calculate the
    corresponding kernel.
    Args:
        g (`Graph`): the knowledge graph, mostly first extracted
                     from a larger graph using `extract_instance`
        s_n_to_counter (dict): global mapping function that maps a 
                               multi-set label to a unique integer
        n_iterations (int): maximum subtree depth
    Returns:
        label_mappings (dict): for every subtree depth (or iteration),
                               the mapping of labels is stored
                               (key = old, value = new)
    """
    
    # Our resulting label function (a map for each iterations)
    label_mappings = {}
    multi_set_labels = {}
    
    # Take a deep copy of our graph, since we are going to relabel its nodes
    g = copy.deepcopy(g)

    for n in range(n_iterations):
        labels = {}
        multi_set_labels[n] = {}
        for vertex in g.vertices:
            # First we create multi-set labels, s_n composed as follow:
            # Prefix = label of node 
            # Suffix = sorted labels of neighbors (reachable by node)
            # If n == 0, we just use the name of the vertex
            if n == 0:
                s_n = vertex.name
            else:
                # g.edges(v) returns all edges coming from v
                s_n = '-'.join(sorted(set(map(str, [x.name for x in g.get_neighbors(vertex)]))))
            
            multi_set_labels[n][vertex.id] = s_n

            if n > 0 and multi_set_labels[n-1][vertex.id] != s_n:
                s_n = (str(vertex.name) + '-' + s_n).rstrip('-')
            elif n > 0:
                s_n = (str(vertex.previous_name) + '-' + str(multi_set_labels[n-1][vertex.id])).rstrip('-')
                vertex.name = vertex.previous_name
                
            labels[vertex] = s_n
                
        # We now map each unique label s_n to an integer
        for s_n in sorted(set(labels.values())):
            if s_n not in s_n_to_counter:
                s_n_to_counter[s_n] = len(s_n_to_counter)

                # If n == 0, then the label is an rdf identifier,
                # we map it first to an integer and store that integer
                # as mapping as well
                if n == 0:
                    s_n_to_counter[str(s_n_to_counter[s_n])] = s_n_to_counter[s_n]
        
        # Construct a dict that maps a node to a new integer,
        # based on its multi-set label
        label_mapping = {}
        for vertex in g.vertices:
            # Get its multi-set label
            s_n = labels[vertex]
            
            # Get the integer corresponding to this multi-set label
            label_mapping[vertex] = s_n_to_counter[s_n]
            
        # Append the created label_mapping to our result dict
        label_mappings[n] = label_mapping
        
        if verbose:
            print('Iteration {}:'.format(n))
            print('-'*25)
            for node in label_mappings[n]:
                print(node.id, node.name, labels[node], '-->', label_mappings[n][node])
            print('\n'*2)

        # Relabel the nodes in our graph, ready for the next iteration
        g.relabel_nodes(label_mapping)
        
    return label_mappings

def wf_kernel(g, inst1, inst2, n_iterations=8, verbose=False):
    # First we extract subgraphs, rooted at the given instances from 
    # our larger knowledge graph, with a maximum depth of `n_iterations`
    g1 = extract_instance(g, inst1, n_iterations//2)
    g2 = extract_instance(g, inst2, n_iterations//2)
    
    # The global mapping function that maps multi-set labels to integers
    # used for both graphs
    s_n_to_counter = {}
    
    # Weisfeiler-Lehman relabeling
    g1_label_function = wf_relabel_graph(g1, s_n_to_counter, n_iterations=n_iterations, verbose=verbose)
    g2_label_function = wf_relabel_graph(g2, s_n_to_counter, n_iterations=n_iterations, verbose=verbose)

    # Iterate over the different iterations and count the number of similar labels between
    # the graphs. Make sure we do not count labels double by first removing all labels
    # from the previous iteration.
    values = []
    for n in range(n_iterations):
        g1_labels = set(g1_label_function[n].values())
        g2_labels = set(g2_label_function[n].values())
        if n == 0:
            values.append(len(g1_labels.intersection(g2_labels)))
        else:
            prev_g1_labels = set(g1_label_function[n-1].values())
            prev_g2_labels = set(g2_label_function[n-1].values())
            values.append(len((g1_labels - prev_g1_labels).intersection(g2_labels - prev_g2_labels)))
            
    return values