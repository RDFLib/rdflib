# Security Considerations

RDFLib is designed to access arbitrary network and file resources, in some cases these are directly requested resources, in other cases they are indirectly referenced resources.

An example of where indirect resources are accessed is JSON-LD processing, where network or file resources referenced by `@context` values will be loaded and processed.

RDFLib also supports SPARQL, which has federated query capabilities that allow
queries to query arbitrary remote endpoints.

If you are using RDFLib to process untrusted documents or queries, you should
take measures to restrict file and network access.

Some measures that can be taken to restrict file and network access are:

* [Operating System Security Measures](#operating-system-security-measures)
* [Python Runtime Audit Hooks](#python-runtime-audit-hooks)
* [Custom URL Openers](#custom-url-openers)

Of these, operating system security measures are recommended. The other measures work, but they are not as effective as operating system security measures, and even if they are used, they should be used in conjunction with operating system security measures.

## Operating System Security Measures

Most operating systems provide functionality that can be used to restrict network and file access of a process.

Some examples of these include:

* [Open Container Initiative (OCI) Containers](https://www.opencontainers.org/) (aka Docker containers).

  Most OCI runtimes provide mechanisms to restrict network and file
  access of containers. For example, using Docker, you can limit your
  container to only being able to access files explicitly mapped into
  the container and only access the network through a firewall. For more
  information, refer to the documentation of the tool you use to manage
  your OCI containers:

  * [Kubernetes](https://kubernetes.io/docs/home/)
  * [Docker](https://docs.docker.com/)
  * [Podman](https://podman.io/)

* [firejail](https://firejail.wordpress.com/) can be used to
  sandbox a process on Linux and restrict its network and file access.

* File and network access restrictions.

  Most operating systems provide a way to restrict operating system users to
  only being able to access files and network resources that are explicitly
  allowed. Applications that process untrusted input could be run as a user with
  these restrictions in place.

Many other measures are available, however, listing them is outside the scope of this document.

Of the listed measures, OCI containers are recommended. In most cases, OCI containers are constrained by default and can't access the loopback interface and can only access files that are explicitly mapped into the container.

## Python Runtime Audit Hooks

From Python 3.8 onwards, Python provides a mechanism to install runtime audit hooks that can be used to limit access to files and network resources.

The runtime audit hook system is described in more detail in [PEP 578 – Python Runtime Audit Hooks](https://peps.python.org/pep-0578/).

Runtime audit hooks can be installed using the [sys.addaudithook](https://docs.python.org/3/library/sys.html#sys.addaudithook) function, and will then get called when audit events occur. The audit events raised by the Python runtime and standard library are described in Python's [audit events table](https://docs.python.org/3/library/audit_events.html).

RDFLib uses `urllib.request.urlopen` for HTTP, HTTPS and other network access, and this function raises a `urllib.Request` audit event. For file access, RDFLib uses `open`, which raises an `open` audit event.

Users of RDFLib can install audit hooks that react to these audit events and raise an exception when an attempt is made to access files or network resources that are not explicitly allowed.

RDFLib's test suite includes tests which verify that audit hooks can block access to network and file resources.

RDFLib also includes an example that shows how runtime audit hooks can be used to restrict network and file access in [`secure_with_audit`][examples.secure_with_audit].

## Custom URL Openers

RDFLib uses the `urllib.request.urlopen` for HTTP, HTTPS and other network access. This function will use a `urllib.request.OpenerDirector` installed with `urllib.request.install_opener` to open the URLs.

Users of RDFLib can install a custom URL opener that raises an exception when an attempt is made to access network resources that are not explicitly allowed.

RDFLib's test suite includes tests which verify that custom URL openers can be used to block access to network resources.

RDFLib also includes an example that shows how a custom opener can be used to restrict network access in [`secure_with_urlopen`][examples.secure_with_urlopen].
