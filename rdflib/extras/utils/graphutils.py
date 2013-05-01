import collections
import rdflib
from rdflib import RDF

"""
RDF- and RDFlib-centric Graph utilities.
"""


def graph_to_dot(graph, dot):
    """
    Turns graph into dot (graphviz graph drawing format) using pydot.

    """
    import pydot
    nodes = {}
    for s, o in graph.subject_objects():
        for i in s, o:
            if i not in nodes.keys():
                nodes[i] = i
    for s, p, o in graph.triples((None, None, None)):
        dot.add_edge(pydot.Edge(nodes[s], nodes[o], label=p))


def find_roots(graph, prop, roots=None):
    """
    Find the roots in some sort of transitive hierarchy.

    find_roots(graph, rdflib.RDFS.subClassOf)
    will return a set of all roots of the sub-class hierarchy

    Assumes triple of the form (child, prop, parent), i.e. the direction of
    RDFS.subClassOf or SKOS.broader

    """

    non_roots = set()
    if roots is None:
        roots = set()
    for x, y in graph.subject_objects(prop):
        non_roots.add(x)
        if x in roots:
            roots.remove(x)
        if y not in non_roots:
            roots.add(y)
    return roots


def get_tree(graph,
             root,
             prop,
             mapper=lambda x: x,
             sortkey=None,
             done=None,
             dir='down'):
    """
    Return a nested list/tuple structure representing the tree
    built by the transitive property given, starting from the root given

    i.e.

    get_tree(graph,
       rdflib.URIRef("http://xmlns.com/foaf/0.1/Person"),
       rdflib.RDFS.subClassOf)

    will return the structure for the subClassTree below person.

    dir='down' assumes triple of the form (child, prop, parent),
    i.e. the direction of RDFS.subClassOf or SKOS.broader
    Any other dir traverses in the other direction

    """

    if done is None:
        done = set()
    if root in done:
        return
    done.add(root)
    tree = []

    if dir == 'down':
        branches = graph.subjects(prop, root)
    else:
        branches = graph.objects(root, prop)

    for branch in branches:
        t = get_tree(graph, branch, prop, mapper, sortkey, done, dir)
        if t:
            tree.append(t)

    return (mapper(root), sorted(tree, key=sortkey))

VOID = rdflib.Namespace("http://rdfs.org/ns/void#")
DCTERMS = rdflib.Namespace("http://purl.org/dc/terms/")
FOAF = rdflib.Namespace("http://xmlns.com/foaf/0.1/")


def generateVoID(g, dataset=None, res=None, distinctForPartitions=True):
    """
    Returns a new graph with a VoID description of the passed dataset

    For more info on Vocabulary of Interlinked Datasets (VoID), see:
    http://vocab.deri.ie/void

    This only makes two passes through the triples (once to detect the types
    of things)

    The tradeoff is that lots of temporary structures are built up in memory
    meaning lots of memory may be consumed :)
    I imagine at least a few copies of your original graph.

    the distinctForPartitions parameter controls whether
    distinctSubjects/objects are tracked for each class/propertyPartition
    this requires more memory again

    """

    typeMap = collections.defaultdict(set)
    classes = collections.defaultdict(set)
    for e, c in g.subject_objects(RDF.type):
        classes[c].add(e)
        typeMap[e].add(c)

    triples = 0
    subjects = set()
    objects = set()
    properties = set()
    classCount = collections.defaultdict(int)
    propCount = collections.defaultdict(int)

    classProps = collections.defaultdict(set)
    classObjects = collections.defaultdict(set)
    propSubjects = collections.defaultdict(set)
    propObjects = collections.defaultdict(set)

    for s, p, o in g:

        triples += 1
        subjects.add(s)
        properties.add(p)
        objects.add(o)

        # class partitions
        if s in typeMap:
            for c in typeMap[s]:
                classCount[c] += 1
                if distinctForPartitions:
                    classObjects[c].add(o)
                    classProps[c].add(p)

        # property partitions
        propCount[p] += 1
        if distinctForPartitions:
            propObjects[p].add(o)
            propSubjects[p].add(s)

    if not dataset:
        dataset = rdflib.URIRef("http://example.org/Dataset")

    if not res:
        res = rdflib.Graph()

    res.add((dataset, RDF.type, VOID.Dataset))

    # basic stats
    res.add((dataset, VOID.triples, rdflib.Literal(triples)))
    res.add((dataset, VOID.classes, rdflib.Literal(len(classes))))

    res.add((dataset, VOID.distinctObjects, rdflib.Literal(len(objects))))
    res.add((dataset, VOID.distinctSubjects, rdflib.Literal(len(subjects))))
    res.add((dataset, VOID.properties, rdflib.Literal(len(properties))))

    for i, c in enumerate(classes):
        part = rdflib.URIRef(dataset + "_class%d" % i)
        res.add((dataset, VOID.classPartition, part))
        res.add((part, RDF.type, VOID.Dataset))

        res.add((part, VOID.triples, rdflib.Literal(classCount[c])))
        res.add((part, VOID.classes, rdflib.Literal(1)))

        res.add((part, VOID["class"], c))

        res.add((part, VOID.entities, rdflib.Literal(len(classes[c]))))
        res.add((part, VOID.distinctSubjects, rdflib.Literal(len(classes[c]))))

        if distinctForPartitions:
            res.add(
                (part, VOID.properties, rdflib.Literal(len(classProps[c]))))
            res.add((part, VOID.distinctObjects,
                    rdflib.Literal(len(classObjects[c]))))

    for i, p in enumerate(properties):
        part = rdflib.URIRef(dataset + "_property%d" % i)
        res.add((dataset, VOID.propertyPartition, part))
        res.add((part, RDF.type, VOID.Dataset))

        res.add((part, VOID.triples, rdflib.Literal(propCount[p])))
        res.add((part, VOID.properties, rdflib.Literal(1)))

        res.add((part, VOID.property, p))

        if distinctForPartitions:

            entities = 0
            propClasses = set()
            for s in propSubjects[p]:
                if s in typeMap:
                    entities += 1
                for c in typeMap[s]:
                    propClasses.add(c)

            res.add((part, VOID.entities, rdflib.Literal(entities)))
            res.add((part, VOID.classes, rdflib.Literal(len(propClasses))))

            res.add((part, VOID.distinctSubjects,
                    rdflib.Literal(len(propSubjects[p]))))
            res.add((part, VOID.distinctObjects,
                    rdflib.Literal(len(propObjects[p]))))

    return res, dataset
