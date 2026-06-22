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

The [`GraphDBClient`][rdflib.contrib.graphdb.client.GraphDBClient] class is the main entry point for interacting with the GraphDB REST API. To create an instance, pass the base URL of the GraphDB server to the constructor and optionally a username and password tuple for basic authentication.

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

With the GraphDB Client, you can also make authenticated requests by obtaining a GDB token. The following code is an example of how to retrieve a token using your username and password, and then use the token to authenticate subsequent requests.

```python
from rdflib.contrib.graphdb.client import GraphDBClient

# Create a client instance (basic authentication is optional for login)
with GraphDBClient("http://localhost:7200/") as client:
    # Authenticate and obtain a GDB token
    user = client.login("admin", "root")

    # The AuthenticatedUser object contains user details
    print(f"Logged in as: {user.username}")
    print(f"Authorities: {user.authorities}")

    # The user.token is a string (e.g., "GDB abc123...") that can be used
    # to authenticate another client instance without using credentials.
    token = user.token

# Use the token with another client instance
with GraphDBClient("http://localhost:7200/", auth=token) as token_client:
    # Perform your operations here.
    repos = token_client.graphdb_repositories.list()
```

### HTTP client configuration

The GraphDB Client extends the RDF4J Client. See [RDF4J Client's HTTP client configuration](rdf4j.md#http-client-configuration) section for details on configuring the underlying HTTP client.

### Repository Management

GraphDB provides two ways to manage repositories:

1.  **RDF4J Repository Manager** ([`GraphDBClient.repositories`][rdflib.contrib.graphdb.client.GraphDBClient.repositories]): Implements the standard RDF4J protocol. Use this for basic operations like retrieving a repository instance for querying. For more information, see [Working with a Repository](rdf4j.md#working-with-a-repository).
2.  **GraphDB Repository Management** ([`GraphDBClient.graphdb_repositories`][rdflib.contrib.graphdb.client.GraphDBClient.graphdb_repositories]): Implements the GraphDB REST API. Use this for administrative tasks such as listing, creating, editing, and validating repositories.

#### Listing repositories

To list all repositories with their configuration and status:

```python
repos = client.graphdb_repositories.list()
for repo in repos:
    print(f"{repo.id} ({repo.type}) - {repo.state}")
```

#### Getting repository configuration

To retrieve a repository's configuration:

```python
# Get configuration as JSON (default)
config = client.graphdb_repositories.get("my-repo")
print(f"Repository ID: {config.id}")

# Get configuration as RDF Graph
graph = client.graphdb_repositories.get("my-repo", content_type="text/turtle")
```

#### Creating a repository

To create a repository, provide the configuration as a Turtle string:

```python
config = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
@prefix rep: <http://www.openrdf.org/config/repository#>.
@prefix sr: <http://www.openrdf.org/config/repository/sail#>.
@prefix sail: <http://www.openrdf.org/config/sail#>.
@prefix graphdb: <http://www.ontotext.com/config/graphdb#>.

[] a rep:Repository ;
    rep:repositoryID "my-repo" ;
    rdfs:label "" ;
    rep:repositoryImpl [
        rep:repositoryType "graphdb:SailRepository" ;
        sr:sailImpl [
            sail:sailType "graphdb:Sail" ;

            graphdb:read-only "false" ;

            # Inference and Validation
            graphdb:ruleset "empty" ;
            graphdb:disable-sameAs "true" ;
            graphdb:check-for-inconsistencies "false" ;

            # Indexing
            graphdb:entity-id-size "32" ;
            graphdb:enable-context-index "false" ;
            graphdb:enablePredicateList "true" ;
            graphdb:enable-fts-index "false" ;
            graphdb:fts-indexes ("default" "iri") ;
            graphdb:fts-string-literals-index "default" ;
            graphdb:fts-iris-index "none" ;

            # Queries and Updates
            graphdb:query-timeout "0" ;
            graphdb:throw-QueryEvaluationException-on-timeout "false" ;
            graphdb:query-limit-results "0" ;

            # Settable in the file but otherwise hidden in the UI and in the RDF4J console
            graphdb:base-URL "http://example.org/owlim#" ;
            graphdb:defaultNS "" ;
            graphdb:imports "" ;
            graphdb:repository-type "file-repository" ;
            graphdb:storage-folder "storage" ;
            graphdb:entity-index-size "10000000" ;
            graphdb:in-memory-literal-properties "true" ;
            graphdb:enable-literal-index "true" ;
        ]
    ].

"""
client.graphdb_repositories.create(config)
```

#### Editing a repository

To edit an existing repository's configuration:

```python
from rdflib.contrib.graphdb.models import RepositoryConfigBeanCreate

existing = client.graphdb_repositories.get("my-repo")
updated_config = RepositoryConfigBeanCreate(
    id=existing.id,
    title="Updated Repository",
    type=existing.type,
    sesameType=existing.sesameType,
    location=existing.location,
    params=existing.params,
)
client.graphdb_repositories.edit("my-repo", updated_config)
```

#### Restarting a repository

To restart a repository:

```python
client.graphdb_repositories.restart("my-repo")

# With sync option
client.graphdb_repositories.restart("my-repo", sync=True)
```

#### Getting repository size

To get information about a repository's size:

```python
size_info = client.graphdb_repositories.size("my-repo")
print(f"Total statements: {size_info.total}")
print(f"Explicit statements: {size_info.explicit}")
print(f"Inferred statements: {size_info.inferred}")
```

#### Deleting a repository

To delete a repository:

```python
client.graphdb_repositories.delete("my-repo")
```

### Working with a Repository

To interact with a specific repository (e.g., to run queries or manage data), retrieve a [`Repository`][rdflib.contrib.graphdb.client.Repository] instance. This returns a GraphDB-specific `Repository` object that extends the [standard RDF4J Repository](rdf4j.md#working-with-a-repository) with additional methods for health checks, data file imports, and fine-grained access control.

```python
repo = client.repositories.get("my-repo")
```

#### Repository health check

To check if a repository is healthy and accessible:

```python
is_healthy = repo.health()
print(f"Repository is healthy: {is_healthy}")

# With custom timeout (in seconds)
is_healthy = repo.health(timeout=10)
```

#### Server-side Import

GraphDB allows you to import files that are already present on the server (in the `imports` directory).

##### Listing available files

To list files available for import:

```python
files = repo.get_server_import_files()
for f in files:
    print(f.name)
```

##### Importing files

To import a file:

```python
from rdflib.contrib.graphdb.models import ServerImportBody

import_body = ServerImportBody(fileNames=["data.ttl"])
repo.import_server_import_file(import_body)
```

##### Cancelling an import

To cancel an ongoing import operation:

```python
repo.cancel_server_import_file("data.ttl")
```

#### Fine-Grained Access Control

GraphDB supports Fine-Grained Access Control (FGAC) to restrict access to specific data. You can manage ACLs using the `repo.acl` property.

##### Listing ACL rules

To list existing ACL rules:

```python
rules = repo.acl.list(scope="statement")
for rule in rules:
    print(f"{rule.policy}: {rule.role} can {rule.operation}")

# Filter by scope, operation, or role
statement_rules = repo.acl.list(scope="statement", operation="read")
```

##### Adding ACL rules

To add a new ACL rule:

```python
from rdflib.contrib.graphdb.models import StatementAccessControlEntry

rule = StatementAccessControlEntry(
    scope="statement",
    policy="allow",
    role="user",
    operation="read",
    subject="<http://example.com/public>",
    predicate="*",
    object="*",
    graph="*",
)
repo.acl.add([rule])
```

##### Setting ACL rules

To replace all existing ACL rules:

!!! warning

    This operation replaces all existing ACL rules with the provided ones.

```python
repo.acl.set([rule])
```

##### Deleting ACL rules

To delete specific ACL rules:

!!! warning

    This operation cannot be undone.

```python
rules = repo.acl.list()
repo.acl.delete(rules[:1])
```

### Security Management

GraphDB provides security features including user authentication, role-based access control, and free access mode. You can manage security settings via `client.security` and users via `client.users`.

#### Managing security status

##### Checking and enabling security

To check if security is enabled and toggle it:

```python
# Check if security is enabled
if not client.security.enabled:
    client.security.enabled = True
```

##### Managing free access mode

Free access mode allows unauthenticated users to access repositories with specific permissions:

```python
from rdflib.contrib.graphdb.models import FreeAccessSettings

# Check free access settings
free_access = client.security.get_free_access_details()
print(f"Free access enabled: {free_access.enabled}")

# Configure free access
settings = FreeAccessSettings(enabled=True)
client.security.set_free_access_details(settings)
```

#### User Management

##### Listing users

To list all users:

```python
users = client.users.list()
for user in users:
    print(user.username)
```

##### Getting a user

To get a specific user:

```python
user = client.users.get("admin")
print(f"Username: {user.username}")
```

##### Creating a user

To create a new user:

```python
from rdflib.contrib.graphdb.models import UserCreate

new_user = UserCreate(
    username="newuser",
    password="password123",
    grantedAuthorities=["ROLE_USER"],
)
client.users.create("newuser", new_user)
```

##### Updating a user

To update user properties:

```python
from rdflib.contrib.graphdb.models import UserUpdate

update = UserUpdate(password="new_password")
client.users.update("newuser", update)
```

To fully replace a user's configuration (requires fetching the existing user first to get `dateCreated`):

```python
from rdflib.contrib.graphdb.models import User

existing_user = client.users.get("newuser")
updated_user = User(
    username="newuser",
    password="newpass123",
    dateCreated=existing_user.dateCreated,
    grantedAuthorities=["ROLE_USER"],
)
client.users.overwrite("newuser", updated_user)
```

##### Getting user roles

To retrieve custom roles assigned to a user:

```python
roles = client.users.custom_roles("someuser")
print(roles)
```

##### Deleting a user

To delete a user:

!!! warning

    This operation cannot be undone.

```python
client.users.delete("newuser")
```

### Monitoring and Administration

GraphDB provides monitoring endpoints for system health, performance metrics, and backup/restore operations. Access these via `client.monitoring` and `client.recovery`.

#### Monitoring

##### Infrastructure statistics

To get system-level statistics such as CPU load, memory usage, and thread count:

```python
stats = client.monitoring.infrastructure
print(f"CPU Load: {stats.cpuLoad}")
print(f"Thread Count: {stats.threadCount}")
print(f"Heap Used: {stats.heapMemoryUsage.used}")
```

##### Structures statistics

To get cache hit/miss statistics for internal data structures:

```python
structures = client.monitoring.structures
print(f"Cache hit: {structures.cacheHit}")
print(f"Cache miss: {structures.cacheMiss}")
```

##### Repository statistics

To get statistics for a specific repository:

```python
repo_stats = client.monitoring.get_repo_stats("my-repo")
print(f"Number of slow queries: {repo_stats.queries.slow}")
```

##### Cluster monitoring

To get cluster-level metrics (GraphDB Enterprise only):

```python
cluster_metrics = client.monitoring.cluster()
print(cluster_metrics)
```

##### Backup monitoring

To track ongoing backup operations:

```python
backup_status = client.monitoring.backup()
if backup_status:
    print(f"Backup in progress: {backup_status.operation}")
else:
    print("No backup in progress")
```

#### Recovery Management

GraphDB supports backup and restore operations for both local and cloud storage.

##### Local backup

To create a local backup:

```python
# Stream to file (recommended for large backups)
backup_path = client.recovery.backup(
    repositories=["my-repo"],
    dest="./backup.tar"
)
print(f"Backup created at: {backup_path}")

# Include system data (users, saved queries, etc.)
backup_path = client.recovery.backup(
    repositories=["my-repo"],
    backup_system_data=True,
    dest="./backup/"
)

# Return as bytes (for small backups or testing)
backup_bytes = client.recovery.backup(repositories=["my-repo"])
```

##### Local restore

To restore from a local backup:

```python
# From file path
client.recovery.restore(backup="./backup.tar")

# Restore specific repositories
client.recovery.restore(
    backup="./backup.tar",
    repositories=["my-repo"],
    restore_system_data=True
)

# Remove repositories not in backup
client.recovery.restore(
    backup="./backup.tar",
    remove_stale_repositories=True
)
```

##### Cloud backup

To back up directly to cloud storage:

```python
client.recovery.cloud_backup(bucket_uri="s3://my-bucket/graphdb-backups/")

# With authentication file for cloud provider
client.recovery.cloud_backup(
    bucket_uri="s3://my-bucket/graphdb-backups/",
    authentication_file="./aws-credentials.json"
)
```

##### Cloud restore

To restore from a cloud backup:

```python
client.recovery.cloud_restore(
    bucket_uri="s3://my-bucket/graphdb-backups/backup-2026-01-16-10-30-00.tar"
)
```

#### Cluster Management

!!! note

    Cluster management is only available in GraphDB Enterprise.

GraphDB Enterprise supports high-availability clustering. You can manage cluster configuration, nodes, and secondary mode via [`GraphDBClient.cluster`][rdflib.contrib.graphdb.client.ClusterGroupManagement].

##### Getting cluster configuration

To retrieve the current cluster configuration, use the [`get_config`][rdflib.contrib.graphdb.client.ClusterGroupManagement.get_config] method:

```python
config = client.cluster.get_config()
print(f"Nodes: {config.nodes}")
print(f"Heartbeat interval: {config.heartbeatInterval}")
```

##### Creating a cluster

To create a new cluster, provide a list of node addresses:

```python
client.cluster.create_config(
    nodes=["node1:7300", "node2:7300", "node3:7300"],
    election_min_timeout=3000,
    heartbeat_interval=1000
)
```

##### Updating cluster configuration

To update an existing cluster's configuration:

```python
updated_config = client.cluster.update_config(
    heartbeat_interval=2000,
    transaction_log_maximum_size_gb=10
)
```

##### Managing cluster nodes

You can add, remove, or replace nodes in an existing cluster:

```python
# Add new nodes
client.cluster.add_nodes(["node4:7300"])

# Remove nodes
client.cluster.remove_nodes(["node1:7300"])

# Replace nodes in one operation
client.cluster.replace_nodes(
    add_nodes=["node5:7300"],
    remove_nodes=["node2:7300"]
)
```

##### Checking cluster and node status

To get the status of the current node or the entire cluster group:

```python
# Get status of the current node
node_status = client.cluster.node_status()
print(f"Node state: {node_status.nodeState}")

# Get status of all nodes in the cluster
group_status = client.cluster.group_status()
for node in group_status:
    print(f"{node.address}: {node.nodeState}")
```

##### Managing secondary mode

You can configure a cluster to operate in secondary mode, replicating data from a primary cluster:

!!! warning

    Enabling secondary mode will delete all data on the secondary cluster and replicate the state of the primary cluster.

```python
# Add a tag to identify the primary cluster
client.cluster.add_tag("production-cluster")

# Enable secondary mode on another cluster
client.cluster.enable_secondary_mode(
    primary_node="primary-node1:7300",
    tag="production-cluster"
)

# Disable secondary mode
client.cluster.disable_secondary_mode()

# Remove the tag from the primary cluster
client.cluster.delete_tag("production-cluster")
```

##### Deleting a cluster

To delete the cluster configuration:

```python
# Delete cluster (requires all nodes to be reachable)
result = client.cluster.delete_config()

# Force delete (only deletes on reachable nodes)
result = client.cluster.delete_config(force=True)
```

##### Truncating the transaction log

To free up storage space by clearing the transaction log:

```python
client.cluster.truncate_log()
```
