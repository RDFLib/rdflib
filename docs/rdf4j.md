[Eclipse RDF4J](https://rdf4j.org/) is an open-source Java framework for working with RDF. Out of the box, it supports running RDF database servers and allows clients to interact with these servers through an HTTP protocol known as the RDF4J REST API. This API fully supports all SPARQL 1.1 W3C Recommendations and also provides additional operations for managing RDF4J concepts such as repositories and transactions. For more details about the RDF4J REST API and its capabilities, see the [official documentation](https://rdf4j.org/documentation/reference/rest-api/).

RDFLib provides two options to interface with the RDF4J REST API:

1. **Store integration** - A full RDFLib Store implementation that lets users interact with RDF4J repositories seamlessly through RDFLib’s [`Graph`][rdflib.Graph] and [`Dataset`][rdflib.Dataset] classes.
2. **RDF4J Client** - A lower-level client that gives users more control over interactions with the RDF4J REST API. It covers all operations supported by the RDF4J REST API, including managing repositories and transactions.

To use RDFLib with RDF4J, first install RDFLib with the optional `rdf4j` extra.

```shell
pip install rdflib[rdf4j]
```

!!! note

    The minimum RDF4J protocol version supported by RDFLib is `12`. Versions less than 12 will raise an [`RDF4JUnsupportedProtocolError`][rdflib.contrib.rdf4j.exceptions.RDF4JUnsupportedProtocolError].

## RDF4J Store

An RDF4J Store connects to a single RDF4J repository. If you need to work with multiple repositories, you can create multiple Store instances. The RDF4J Store exposes only the subset of repository operations that map directly with RDFLib’s Graph and Dataset interfaces. If you need to perform additional operations such as managing repositories, you should use the RDF4J Client instead.

### Connecting to an existing repository

To get started, import the RDF4J Store class, create an instance of it, and pass it as the store parameter when creating a [`Graph`][rdflib.Graph] or [`Dataset`][rdflib.Dataset].

The following example connects to a local RDF4J server running on port 7200 and accesses an existing repository with the identifier `my-repository`.

If the server requires basic authentication, you can optionally pass a (username, password) tuple to the `auth` parameter.

```python
from rdflib.plugins.stores.rdf4j import RDF4JStore

store = RDF4JStore(
    base_url="http://localhost:7200/",
    repository_id="my-repository",
    auth=("username", "password"),
)
```

### Creating a new repository

If the repository does not exist (and the `create` parameter is set to `False`), an exception will be raised. To create the repository, set the `create` parameter to `True`. This will create the repository using RDF4J’s default configuration settings and then connect to it.

```python
store = RDF4JStore(
    base_url="http://localhost:7200/",
    repository_id="my-repository",
    auth=("username", "password"),
    create=True,
)
```

To create a repository with a custom RDF4J configuration, pass the `configuration` as a string to the configuration parameter.

See the RDF4J documentation for more information on [Repository and SAIL Configuration](https://rdf4j.org/documentation/reference/configuration/).

```python
store = RDF4JStore(
    base_url="http://localhost:7200/",
    repository_id="my-repository",
    auth=("username", "password"),
    configuration=configuration,
    create=True,
)
```

### Using the store with RDFLib

Once the store is created, you can create a [`Graph`][rdflib.Graph] or [`Dataset`][rdflib.Dataset] object and use it as you would with any other RDFLib store.

```python
from rdflib import Dataset

ds = Dataset(store=store)
```

For more information on how to use RDFLib Graphs and Datasets, see the subsections under [Usage](index.md).

### Namespaces

When connecting to an RDF4J repository, RDFLib automatically registers a set of built-in namespace prefixes. To disable this behavior, assign a new RDFLib [`NamespaceManager`][rdflib.namespace.NamespaceManager] instance with `bind_namespaces` set to the string `"none"`.

```python
ds = Dataset(store=store)
ds.namespace_manager = NamespaceManager(ds, "none")
```

See [`NamespaceManager`][rdflib.namespace.NamespaceManager] for more namespace binding options.

## RDF4J Client

This section covers examples of how to use the RDF4J Client. For the full reference documentation of the RDF4J Client, see [rdflib.contrib.rdf4j.client](/apidocs/rdflib.contrib.rdf4j.client).

### Creating a client instance

The `RDF4JClient` class is the main entry point for interacting with the RDF4J REST API. To create an instance, pass the base URL of the RDF4J server to the constructor and optionally a username and password tuple for basic authentication.

The preferred way to create a client instance is to use Python's context manager syntax (`with` statement). When using this syntax, the client will automatically close when the block is exited.


```python
from rdflib.contrib.rdf4j.client import RDF4JClient

with RDF4JClient("http://localhost:7200/", auth=("admin", "admin")) as client:
    # Perform your operations here.
    ...
```

Alternatively, you can create a client instance and manually close it when you are done using it.

```python
from rdflib.contrib.rdf4j.client import RDF4JClient

client = RDF4JClient("http://localhost:7200/", auth=("admin", "admin"))
try:
    # Perform your operations here.
    ...
finally:
    client.close()
```

### HTTP client configuration

The RDF4J Client uses the [httpx](https://www.python-httpx.org/) library for making HTTP requests. When creating an RDF4J client instance, any additional keyword arguments to [`RDF4JClient`][rdflib.contrib.rdf4j.client.RDF4JClient] will be passed on to the underlying [`httpx.Client`](https://www.python-httpx.org/api/#client) instance.

For example, setting additional headers (such as an Authorization header) for all requests can be done as follows:

```python
token = "secret"
headers = {
    "Authorization": f"Bearer {token}" 
}
with RDF4JClient("http://localhost:7200/", headers=headers) as client:
    # Perform your operations here.
    ...
```

The [`httpx.Client`](https://www.python-httpx.org/api/#client) instance is available on the RDF4j client's [`http_client`][rdflib.contrib.rdf4j.client.RDF4JClient.http_client] property.

```python
client.http_client
```

### The repository manager

The RDF4J Client provides a [`RepositoryManager`][rdflib.contrib.rdf4j.client.RepositoryManager] class that allows you to manage RDF4J repositories. It does not represent a repository itself; instead, it is responsible for creating, deleting, listing, and retrieving [`Repository`][rdflib.contrib.rdf4j.client.Repository] instances.

You can access the repository manager on the RDF4J client instance using the [`repositories`][rdflib.contrib.rdf4j.client.RDF4JClient.repositories] property.

```python
client.repositories
```

#### Create a repository

To create a new repository, call the [`create`][rdflib.contrib.rdf4j.client.RepositoryManager.create] method on the repository manager. You must provide the repository identifier as well as the RDF4J repository configuration as an RDF string. The default configuration format expected is `text/turtle`.

See the RDF4J documentation for more information on [Repository and SAIL Configuration](https://rdf4j.org/documentation/reference/configuration/).

```python
configuration = """
    PREFIX config: <tag:rdf4j.org,2023:config/>
    
    []    a config:Repository ;
        config:rep.id "my-repository" ;
        config:rep.impl
            [
                config:rep.type "openrdf:SailRepository" ;
                config:sail.impl
                    [
                        config:native.tripleIndexers "spoc,posc" ;
                        config:sail.defaultQueryEvaluationMode "STANDARD" ;
                        config:sail.iterationCacheSyncThreshold "10000" ;
                        config:sail.type "openrdf:NativeStore" ;
                    ] ;
            ] ;
    .
"""
repo = client.repositories.create("my-repository", configuration)
```

For the full reference documentation of the RepositoryManager class, see [`RepositoryManager`][rdflib.contrib.rdf4j.client.RepositoryManager].

### Working with a repository

The [`Repository`][rdflib.contrib.rdf4j.client.Repository] class provides attributes and methods for interacting with a single RDF4J repository. This includes:

- Checking the health of the repository
- Retrieving the number of statements in the repository
- Querying the repository using both SPARQL and the Graph Store Protocol
- Updating the repository using both SPARQL Update and the Graph Store Protocol
- Perform queries and updates in a transaction context
- Manage the namespace prefixes of the repository

#### Retrieve a repository instance

To get started, retrieve a repository instance by repository identifier.

```python
repo = client.repositories.get("my-repository")
```

!!! note

    When retrieving a repository instance, it will automatically perform a health check to ensure that the repository is healthy. To perform a manual health check, simply call the [`health`][rdflib.contrib.rdf4j.client.Repository.health] method.

#### Repository size

To get the number of statements in a repository, call the [`size`][rdflib.contrib.rdf4j.client.Repository.size] method.

```python
repo.size()
```

#### Repository data

Upload some RDF data to the repository. Keep in mind that the [`upload`][rdflib.contrib.rdf4j.client.Repository.upload] method always appends the data to the repository.

```python
data = """
    PREFIX ex: <https://example.com/>
    ex:Bob a ex:Person .
"""
repo.upload(data=data)
```

!!! note

    Methods such as upload that accepts a data argument can automatically handle different kinds of inputs. For example, the data parameter in this case is an RDF string, but it can also be a file path, a file-like object, bytes data, or an RDFLib [`Graph`][rdflib.Graph] or [`Dataset`][rdflib.Dataset].

To overwrite the repository data, use the [`overwrite`][rdflib.contrib.rdf4j.client.Repository.overwrite] method.

!!! warning

    This will delete all existing data in the repository and replace it with the provided data.

```python
repo.overwrite(data=data)
```

There are also methods ([`get`][rdflib.contrib.rdf4j.client.Repository.get] and [`delete`][rdflib.contrib.rdf4j.client.Repository.delete]) for querying and deleting data from the repository using a triple or quad pattern match. However, keep in mind that the patterns cannot include [`BNode`][rdflib.BNode] terms.

The following example demonstrates the [`delete`][rdflib.contrib.rdf4j.client.Repository.delete] method, which deletes all statements with the subject `https://example.com/Bob`.

```python
repo.delete(subject=URIRef("https://example.com/Bob"))
```

The following example demonstrates the [`get`][rdflib.contrib.rdf4j.client.Repository.get] method, which returns a new in-memory [`Dataset`][rdflib.Dataset] object containing all the statements with `https://example.com/Bob` as the subject.

```python
ds = repo.get(subject=URIRef("https://example.com/Bob"))
```

!!! note

    Methods that accept a `graph_name` parameter can restrict the operation to a specific graph. Use `None` to match all graphs, or [`DATASET_DEFAULT_GRAPH_ID`][rdflib.graph.DATASET_DEFAULT_GRAPH_ID] to match only the default graph.

To retrieve a list of graph names in the repository, use the [`graph_names`][rdflib.contrib.rdf4j.client.Repository.graph_names] method. This returns a list of [`IdentifiedNode`][rdflib.term.IdentifiedNode].

```python
repo.graph_names()
```

#### Querying the repository with SPARQL

SPARQL queries can be executed against a repository using the [`query`][rdflib.contrib.rdf4j.client.Repository.query] method.

The return object is a [`Result`][rdflib.query.Result]. You can use [`Result.type`][rdflib.query.Result.type] to determine the type of the result. For example, an ASK query will provide a boolean result in [`Result.askAnswer`][rdflib.query.Result.askAnswer], a DESCRIBE or CONSTRUCT query will provide a [`Graph`][rdflib.Graph] result in [`Result.graph`][rdflib.query.Result.graph], and a SELECT query will provide results in [`Result.bindings`][rdflib.query.Result.bindings].

```python
query = "SELECT * WHERE { ?s ?p ?o } LIMIT 10"
result = repo.query(query)
if result.type == "ASK":
    print(result.askAnswer)
elif result.type in ("CONSTRUCT", "DESCRIBE"):
    print(result.graph)
else:
    # SELECT
    for row in result.bindings:
        print(row["s"])
```

!!! note

    RDF4J supports optional query parameters that further restrict the context of the SPARQL query. To include these query parameters, pass in keyword arguments to the [`query`][rdflib.contrib.rdf4j.client.Repository.query] method. See [RDF4J REST API - Execute SPARQL query](https://rdf4j.org/documentation/reference/rest-api/#tag/SPARQL/paths/~1repositories~1%7BrepositoryID%7D/get) for the list of supported query parameters.

#### Updating the repository with SPARQL Update

To update the repository using SPARQL Update, use the [`update`][rdflib.contrib.rdf4j.client.Repository.update] method.

```python
query = "INSERT DATA { <https://example.com/Bob> <https://example.com/knows> <https://example.com/Alice> }"
repo.update(query)
```

#### Graph Store Manager

RDF4J repositories support the Graph Store Protocol to allow clients to upload and retrieve RDF data. To access the Graph Store Manager, use the [`graphs`][rdflib.contrib.rdf4j.client.Repository.graphs] property.

```python
repo.graphs
```

To add data to a specific graph, use the [`add`][rdflib.contrib.rdf4j.client.GraphStoreManager.add] method.

```python
repo.graphs.add(graph_name="my-graph", data=data)
```

To clear a graph, use the [`clear`][rdflib.contrib.rdf4j.client.GraphStoreManager.clear] method.

!!! warning

    This will delete all existing data in the graph.

!!! note

    RDF4J does not support empty named graphs. Once a graph is cleared, it will be deleted from the repository and will not appear in the list of [`graph_names`][rdflib.contrib.rdf4j.client.Repository.graph_names].

```python
repo.graphs.clear(graph_name="my-graph")
```

To retrieve data from a specific graph, use the [`get`][rdflib.contrib.rdf4j.client.GraphStoreManager.get] method. This returns a new in-memory [`Graph`][rdflib.Graph] object containing the data in the graph.

```python
graph = repo.graphs.get(graph_name="my-graph")
```

To overwrite the data in a specific graph, use the [`overwrite`][rdflib.contrib.rdf4j.client.GraphStoreManager.overwrite] method.

!!! warning

    This will delete all existing data in the graph and replace it with the provided data.

```python
repo.graphs.overwrite(graph_name="my-graph", data=data)
```

### Repository transactions

RDF4J supports transactions, which allow you to group multiple operations into a single atomic unit. To perform operations in a transaction, use the [`transaction`][rdflib.contrib.rdf4j.client.Repository.transaction] method as a context manager.

The following example demonstrates how to perform operations in a transaction. The transaction will be automatically committed when the block is exited. If an error occurs during the transaction, the transaction will be rolled back and the error will be raised.

```python
with repo.transaction() as txn:
    # Perform your operations here.
    ...

# Exiting the with-statement block will automatically commit or roll back if an error occurs.
```

!!! note

    The methods available on the [`Transaction`][rdflib.contrib.rdf4j.client.Transaction] object vary slightly from the methods available on the [`Repository`][rdflib.contrib.rdf4j.client.Repository] object. This is due to slight variations between the two endpoints (repositories and transactions) in the RDF4J REST API.

For the full reference documentation of the Transaction class, see [`Transaction`][rdflib.contrib.rdf4j.client.Transaction].

### Repository namespace prefixes

RDF4J supports managing namespace prefixes for a repository. To access the namespace manager, use the [`namespaces`][rdflib.contrib.rdf4j.client.Repository.namespaces] property on the [`Repository`][rdflib.contrib.rdf4j.client.Repository] object.

```python
repo.namespaces
```

To set a namespace prefix, use the [`set`][rdflib.contrib.rdf4j.client.RDF4JNamespaceManager.set] method.

```python
repo.namespaces.set("schema", "https://schema.org/")
```

To retrieve a namespace by prefix, use the [`get`][rdflib.contrib.rdf4j.client.RDF4JNamespaceManager.get] method.

```python
namespace = repo.namespaces.get("schema")
```

To remove a namespace prefix, use the [`remove`][rdflib.contrib.rdf4j.client.RDF4JNamespaceManager.remove] method.

```python
repo.namespaces.remove("schema")
```

To list all namespace prefixes, use the [`list`][rdflib.contrib.rdf4j.client.RDF4JNamespaceManager.list] method. This returns a list of [`NamespaceListingResult`][rdflib.contrib.rdf4j.client.NamespaceListingResult]

```python
import dataclasses

namespace_prefixes = repo.namespaces.list()
for prefix, namespace in [dataclasses.astuple(np) for np in namespace_prefixes]:
    print(prefix, namespace) 
```

To clear all namespace prefixes, use the [`clear`][rdflib.contrib.rdf4j.client.RDF4JNamespaceManager.clear] method.

!!! warning

    This will remove all namespace prefixes from the repository.

```python
repo.namespaces.clear()
```
