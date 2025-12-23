from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb import GraphDBClient
    from rdflib.contrib.graphdb.models import AccessControlEntry


@pytest.mark.testcontainer
def test_graphdb_fgac_rules_set(client: GraphDBClient):
    repo = client.repositories.get("test-repo")
    assert repo.acl_rules.list() == []
    acl_rules_raw = [
        {
            "policy": "allow",
            "role": "*",
            "scope": "statement",
            "operation": "*",
            "subject": "*",
            "predicate": "*",
            "object": "*",
            "context": "default",
        },
        {
            "policy": "allow",
            "role": "*",
            "scope": "statement",
            "operation": "*",
            "subject": "*",
            "predicate": "*",
            "object": "*",
            "context": "<urn:graph:test>",
        },
    ]
    acl_rules = [AccessControlEntry.from_dict(x) for x in acl_rules_raw]
    repo.acl_rules.set(acl_rules)
    assert repo.acl_rules.list() == acl_rules
    # Overwrite with an empty list of rules.
    repo.acl_rules.set([])
    assert repo.acl_rules.list() == []
