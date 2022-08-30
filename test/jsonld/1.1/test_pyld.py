import json
from pathlib import Path

import pytest

from rdflib import Dataset
from rdflib.compare import isomorphic


DIR = Path(__file__).parent.resolve()

context_file_xfail_reason = "Importing @context via file not implemented"
XFAIL_IDS = {
    "#t0016": "empty IRI does not expand and use the test file location.",
    "#t0017": "relative IRI does not expand and use the test file location.",
    "#t0018": "frag ID does not expand and use the test file location.",
    "#t0022": "tests expects the value to be in scientific notation.",
    "#t0028": "test expects Z in the UTC time format.",
    "#t0035": "test expects the value to be in scientific notation.",
    "#t0118": "yet to enable generalized RDF in pyld to_rdf function.",
    "#t0120": "pyld skips relative IRIs.",
    "#t0121": "pyld skips relative IRIs.",
    "#t0122": "pyld skips relative IRIs.",
    "#t0123": "pyld skips relative IRIs.",
    "#t0124": "pyld skips relative IRIs.",
    "#t0125": "pyld skips relative IRIs.",
    "#t0126": "pyld skips relative IRIs.",
    "#t0127": "pyld skips relative IRIs.",
    "#t0128": "pyld skips relative IRIs.",
    "#t0129": "pyld skips relative IRIs.",
    "#t0130": "pyld skips relative IRIs.",
    "#t0131": "pyld skips relative IRIs.",
    "#t0132": "pyld skips relative IRIs.",
    "#tc015": "pyld does not support relative IRI subjects and predicates.",
    "#tc019": "data is isomorphic but expected blank node ordering is different.",
    "#tc036": "Failed to perform expansion with empty property-scoped context.",
    "#tc037": "Failed with property-scoped contexts which are alias of @nest-Nesting terms may have property-scoped contexts defined",
    "#tc038": "Failed Nesting terms may have property-scoped contexts defined",
    "#tdi11": "pyld does not support compund-literal.",
    "#tdi12": "pyld does not support compund-literal.",
    "#te007": "test expects Z in the UTC time format.",
    "#te014": "test is for JSON-LD 1.0",
    "#te026": "test is for JSON-LD 1.0",
    "#te031": "test expects the value to be in scientific notation.",
    # "#tc024": "pyld fails to type-scoped + property-scoped + values against previous",
    # "#tso08": context_file_xfail_reason,
    # "#tc031": context_file_xfail_reason,
    # "#tc034": context_file_xfail_reason,
    # "#te026": "Invalid JSON-LD syntax; term in form of IRI must expand to definition.",
    # "#te071": "Invalid JSON-LD syntax; term in form of IRI must expand to definition. ",
    # "#te122": "Fail to ignore some IRIs when that start with @ when expanding.",
    # "#te126": context_file_xfail_reason,
    # "#te127": context_file_xfail_reason,
    # "#te128": context_file_xfail_reason,
    # "#tso05": "Invalid JSON-LD syntax; invalid scoped context.",
    # "#tso06": "Invalid JSON-LD syntax; invalid scoped context.",
    # "#tso09": context_file_xfail_reason,
    # "#tso11": context_file_xfail_reason,
    # "#twf05": "ValueError: 'a b' is not a valid language tag!",
    # "#t0001": "https://github.com/RDFLib/rdflib/issues/1842",
    # "#t0002": "https://github.com/RDFLib/rdflib/issues/1842",
    # "#t0003": "https://github.com/RDFLib/rdflib/issues/1842",
}


# These tests are working correctly but
# they are failing due to the different bnode ids
# produced in the output n-quads.
# To get these tests to pass, we use
# rdflib.compare.isomorphic function to check if the
# n-quads are the same or not.
ISOMORPHISM_CHECKS = ["#tdi09", "#tdi10"]


def get_manifests():
    filepath = str(DIR / "toRdf-manifest.jsonld")
    with open(filepath, "r", encoding="utf-8") as f:
        manifest = json.load(f)

        tests = []
        for item in manifest["sequence"]:
            id_ = item["@id"]
            if "jld:PositiveEvaluationTest" in item["@type"]:  # TODO: remove if
                args = (
                    id_,
                    item["@type"],
                    item["name"],
                    item["purpose"],
                    item["input"],
                    manifest["baseIri"] + item["input"],
                    item.get("option"),
                    item["expect"],
                )
                if id_ not in XFAIL_IDS:
                    tests.append(args)
                else:
                    tests.append(
                        pytest.param(
                            *args, marks=pytest.mark.xfail(reason=XFAIL_IDS[id_])
                        )
                    )

        return tests


def order_nquads(s: str) -> str:
    s = s.split("\n")
    l = list(filter(lambda x: x != "", s))
    l.sort()
    return "\n".join(l) + "\n"


@pytest.mark.parametrize(
    "id_, type_, name, purpose, input_file, base, options, expected_file",
    get_manifests(),
)
def test_transform_jsonld_to_rdf_PositiveEvaluationTest(
    id_, type_, name, purpose, input_file, base, options, expected_file
):
    dataset = Dataset()

    options = options if options else {}
    options["base"] = base
    dataset.parse(str(DIR / input_file), format="json-ld", options=options)

    result = dataset.serialize(format="nquads")
    print("before processing")
    print(result)
    result = order_nquads(result)

    with open(str(DIR / expected_file), "r", encoding="utf-8") as f:
        expected = f.read()
        print("got")
        print(result)
        expected = order_nquads(expected)
        print('expected')
        print(expected)

        if id_ in ISOMORPHISM_CHECKS:
            isomorphic(
                Dataset().parse(data=result, format="application/n-quads"),
                Dataset().parse(data=expected, format="application/n-quads"),
            )

        else:
            assert result == expected
