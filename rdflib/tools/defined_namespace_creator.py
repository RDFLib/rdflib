"""
This rdflib Python script creates a DefinedNamespace Python file from a given RDF file

It is a very simple script: it finds all things defined in the RDF file within a given
namespace:

    <thing> a ?x

    where ?x is anything and <thing> starts with the given namespace

Nicholas J. Car, Dec, 2021
"""
import sys
from pathlib import Path
import argparse
import datetime

sys.path.append(str(Path(__file__).parent.absolute().parent.parent))

from rdflib import Graph
from rdflib.namespace import DCTERMS, OWL, RDFS, SKOS
from rdflib.util import guess_format


def validate_namespace(namespace):
    if not namespace.endswith(("/", "#")):
        raise ValueError("The supplied namespace must end with '/' or '#'")


def validate_object_id(object_id):
    for c in object_id:
        if not c.isupper():
            raise ValueError("The supplied object_id must be an all-capitals string")


# This function is not used: it was originally written to get classes and to be used
# alongside a method to get properties, but then it was decided that a single function
# to get everything in the namespace, get_target_namespace_elements(), was both simper
# and better covered all namespace elements, so that function is used instead.
#
# def get_classes(g, target_namespace):
#     namespaces = {"dcterms": DCTERMS, "owl": OWL, "rdfs": RDFS, "skos": SKOS}
#     q = """
#         SELECT DISTINCT ?x ?def
#         WHERE {
#             # anything that is an instance of owl:Class or rdfs:Class
#             # or any subclass of them
#             VALUES ?c { owl:Class rdfs:Class }
#             ?x rdfs:subClassOf*/a ?c .
#
#             # get any definitions, if they have one
#             OPTIONAL {
#                 ?x rdfs:comment|dcterms:description|skos:definition ?def
#             }
#
#             # only get results for the targetted namespace (supplied by user)
#             FILTER STRSTARTS(STR(?x), "xxx")
#         }
#         """.replace("xxx", target_namespace)
#     classes = []
#     for r in g.query(q, initNs=namespaces):
#         classes.append((str(r[0]), str(r[1])))
#
#     classes.sort(key=lambda tup: tup[1])
#
#     return classes


def get_target_namespace_elements(g, target_namespace):
    namespaces = {"dcterms": DCTERMS, "owl": OWL, "rdfs": RDFS, "skos": SKOS}
    q = """
        SELECT DISTINCT ?s ?def
        WHERE {
            # all things in the RDF data (anything RDF.type...)
            ?s a ?o .

            # get any definitions, if they have one
            OPTIONAL {
                ?s dcterms:description|rdfs:comment|skos:definition ?def
            }

            # only get results for the target namespace (supplied by user)
            FILTER STRSTARTS(STR(?s), "xxx")
        }
        """.replace(
        "xxx", target_namespace
    )
    elements = []
    for r in g.query(q, initNs=namespaces):
        elements.append((str(r[0]), str(r[1])))

    elements.sort(key=lambda tup: tup[0])

    elements_strs = []
    for e in elements:
        desc = e[1].replace('\n', ' ')
        elements_strs.append(
            f"    {e[0].replace(args.target_namespace, '')}: URIRef  # {desc}\n"
        )

    return elements, elements_strs


def make_dn_file(output_file_name, target_namespace, elements_strs, object_id, fail):
    header = f'''from rdflib.term import URIRef
from rdflib.namespace import DefinedNamespace, Namespace


class {object_id}(DefinedNamespace):
    """
    DESCRIPTION_EDIT_ME_!

    Generated from: SOURCE_RDF_FILE_EDIT_ME_!
    Date: {datetime.datetime.utcnow()}
    """
'''
    with open(output_file_name, "w") as f:
        f.write(header)
        f.write("\n")
        f.write(f'    _NS = Namespace("{target_namespace}")')
        f.write("\n\n")
        if fail:
            f.write("    _fail = True")
            f.write("\n\n")
        f.writelines(elements_strs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "ontology_file",
        type=str,
        help="Path to the RDF ontology to extract a DefinedNamespace from.",
    )

    parser.add_argument(
        "target_namespace",
        type=str,
        help="The namespace within the ontology that you want to create a "
        "DefinedNamespace for.",
    )

    parser.add_argument(
        "object_id",
        type=str,
        help="The RDFlib object ID of the DefinedNamespace, e.g. GEO for GeoSPARQL.",
    )

    parser.add_argument(
        '-f',
        "--fail",
        dest='fail',
        action='store_true',
        help="Whether (true) or not (false) to mimic ClosedNamespace and fail on "
        "non-element use",
    )
    parser.add_argument('--no-fail', dest='fail', action='store_false')
    parser.set_defaults(feature=False)

    args = parser.parse_args()

    fmt = guess_format(args.ontology_file)
    if fmt is None:
        print("The format of the file you've supplied is unknown.")
        exit(1)
    g = Graph().parse(args.ontology_file, format=fmt)

    validate_namespace(args.target_namespace)

    validate_object_id(args.object_id)

    print(
        f"Creating DefinedNamespace file {args.object_id} "
        f"for {args.target_namespace}..."
    )
    print(f"Ontology with {len(g)} triples loaded...")

    print("Getting all namespace elements...")
    elements = get_target_namespace_elements(g, args.target_namespace)

    output_file_name = Path().cwd() / f"_{args.object_id}.py"
    print(f"Creating DefinedNamespace Python file {output_file_name}")
    make_dn_file(
        output_file_name, args.target_namespace, elements[1], args.object_id, args.fail
    )
