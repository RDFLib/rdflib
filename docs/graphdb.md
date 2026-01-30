[GraphDB by Ontotext](https://graphdb.ontotext.com/) is an enterprise-ready semantic graph database that supports a number of W3C standards.

Ontotext provides GraphDB in two editions:

- **GraphDB Free** — free to use, with limits on concurrency, scalability, and available connectors.
- **GraphDB Enterprise** — commercial edition that removes the Free edition’s limits and adds enterprise features and additional connectors.

The simplest way to get started with GraphDB is to run it in a container. The [ontotext/graphdb](https://hub.docker.com/r/ontotext/graphdb/) image on Docker Hub includes instructions on how to run and operate the database.

!!! note

    From GraphDB 11 onwards, all editions (including GraphDB Free) require a license. You can register for one on the [GraphDB website](https://www.ontotext.com/products/graphdb/).

GraphDB supports programmatic access via a set of REST APIs. It implements the [RDF4J REST API](https://rdf4j.org/documentation/reference/rest-api/), which allows you to manage repositories, perform SPARQL queries and updates, and manage RDF data. If you only need these capabilities, see the [RDFLib RDF4J](rdf4j.md) documentation for details on using the RDFLib RDF4J Store or Client.

GraphDB also provides its own set of administrative REST APIs that extend the RDF4J REST API with GraphDB-specific features such as security management, monitoring, cluster management, and more.
See the GraphDB documentation at https://graphdb.ontotext.com/documentation/.

RDFLib provides a dedicated GraphDB client that implements these GraphDB-specific REST APIs. This documentation covers the usage of the GraphDB client and its features.

## GraphDB Client

The GraphDB Client extends the [RDF4J Client](rdf4j.md#rdf4j-client) and provides additional functionality from the GraphDB-provided REST APIs.

To use RDFLib with the GraphDB Client, first install RDFLib with the optional `graphdb` extra:

```shell
pip install rdflib[graphdb]
```

### Creating a client instance

The `GraphDBClient` class is the main entry point for interacting with the GraphDB REST API. To create an instance, pass the base URL of the GraphDB server to the constructor and optionally a username and password tuple for basic authentication.

The preferred way to create a client instance is to use Python's context manager syntax (`with` statement).

```python
from rdflib.contrib.graphdb.client import GraphDBClient

with GraphDBClient("http://localhost:7200/", auth=("admin", "root")) as client:
    # Perform your operations here.
    ...
```

Alternatively, you can create a client instance and manually close it when you are done using it.

```python
from rdflib.contrib.graphdb.client import GraphDBClient

client = GraphDBClient("http://localhost:7200/", auth=("admin", "root"))
try:
    # Perform your operations here.
    ...
finally:
    client.close()
```

With the GraphDB Client, you can also make authenticated requests by obtaining a GDB token.

```python
from rdflib.contrib.graphdb.client import GraphDBClient

auth = ("admin", "root")
with GraphDBClient("http://localhost:7200/", auth=auth) as client:
    authenticated_user = client.authenticate("admin", "root")
    token = authenticated_user.token

    # Use the token with another client instance.
    with GraphDBClient("http://localhost:7200/", auth=token) as token_client:
        # Perform your operations here.
        ...
```

### HTTP client configuration

The GraphDB Client extends the RDF4J Client. See [RDF4J Client's HTTP client configuration](rdf4j.md#http-client-configuration) section for details on configuring the underlying HTTP client.

### Repository Management

GraphDB provides two ways to manage repositories:

1.  **RDF4J Repository Manager** (`client.repositories`): Implements the standard RDF4J protocol. Use this for basic operations like retrieving a repository instance for querying. For more information, see [Working with a Repository](rdf4j.md#working-with-a-repository).
2.  **GraphDB Repository Management** (`client.repos`): Implements the GraphDB REST API. Use this for administrative tasks like listing, creating, editing, and validating repositories.

#### Listing repositories

To list all repositories with their configuration and status, use the `client.repos` property.

```python
repos = client.repos.list()
for repo in repos:
    print(f"{repo.id} ({repo.type}) - {repo.state}")
```

#### Creating a repository

To create a repository, you can provide the configuration as a Turtle string or a JSON object.

```python
config = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix rep: <http://www.openrdf.org/config/repository#> .
@prefix sr: <http://www.openrdf.org/config/repository/sail#> .
@prefix sail: <http://www.openrdf.org/config/sail#> .
@prefix graphdb: <http://www.ontotext.com/config/graphdb#> .

[] a rep:Repository ;
    rep:repositoryID "my-repo" ;
    rep:repositoryImpl [
        rep:repositoryType "graphdb:SailRepository" ;
        sr:sailImpl [
            sail:sailType "graphdb:Sail" ;
        ]
    ] .
"""
client.repos.create(config)
```

#### Deleting a repository

To delete a repository, use the `delete` method on `client.repos`.

```python
client.repos.delete("my-repo")
```

### Working with a Repository

To interact with a specific repository (e.g., to run queries or manage data), retrieve a `Repository` instance using `client.repositories.get()`. This returns a GraphDB-specific `Repository` object that extends the [standard RDF4J Repository](rdf4j.md#working-with-a-repository).

```python
repo = client.repositories.get("my-repo")
```

#### Server-side Import

GraphDB allows you to import files that are already present on the server (in the `imports` directory).

To list available server files:

```python
files = repo.get_server_import_files()
for f in files:
    print(f.name)
```

To import a file:

```python
from rdflib.contrib.graphdb.models import ServerImportBody

import_body = ServerImportBody(fileNames=["data.ttl"])
repo.import_server_import_file(import_body)
```

To cancel an ongoing import:

```python
repo.cancel_server_import_file("data.ttl")
```

#### Fine-Grained Access Control (ACL)

GraphDB supports Fine-Grained Access Control (FGAC) to restrict access to specific data. You can manage ACLs using the `repo.acl` property.

To list existing ACL rules:

```python
rules = repo.acl.list()
for rule in rules:
    print(rule.policy, rule.subject, rule.operation)
```

To add a new ACL rule:

```python
from rdflib.contrib.graphdb.models import StatementAccessControlEntry

rule = StatementAccessControlEntry(
    policy="allow",
    subject="<http://example.com/public>",
    operation="read",
    role="user"
)
repo.acl.add([rule])
```

### Security Management

You can manage GraphDB security (users, roles, and access settings) via the `client.security` and `client.users` properties.

#### Managing Security Status

Check if security is enabled and toggle it:

```python
if not client.security.enabled:
    client.security.enabled = True
```

#### User Management

To list users:

```python
users = client.users.list()
for user in users:
    print(user.username)
```

To create a new user:

```python
from rdflib.contrib.graphdb.models import User

new_user = User(username="newuser", password="password123")
client.users.create("newuser", new_user)
```

To delete a user:

```python
client.users.delete("newuser")
```

### Monitoring and Administration

#### Monitoring

Access system monitoring information via `client.monitoring`.

```python
# Get infrastructure statistics
stats = client.monitoring.infrastructure
print(f"CPU Load: {stats.cpu_load}")
print(f"Memory Usage: {stats.memory_usage}")

# Get repository statistics
repo_stats = client.monitoring.get_repo_stats("my-repo")
```

#### Recovery (Backup and Restore)

Manage backups and restores via `client.recovery`.

To create a backup:

```python
# Backup to a local file
backup_path = client.recovery.backup(repositories=["my-repo"], dest="./backup.tar")
```

To restore from a backup:

```python
client.recovery.restore(backup="./backup.tar")
```

#### Cluster Management

For GraphDB Enterprise, you can manage the cluster via `client.cluster`.

```python
# Get cluster configuration
config = client.cluster.get_config()

# Get cluster group status
status = client.cluster.group_status()
```

#### Talk to Your Graph

You can interact with the Talk to Your Graph (TTYG) agent service.

```python
response = client.ttyg.query(
    agent_id="my-agent",
    tool_type="retrieval",
    query="Tell me about the data."
)
print(response)
```
