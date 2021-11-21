from rdflib.term import URIRef
from rdflib.namespace import DefinedNamespace, Namespace


class DOAP(DefinedNamespace):
    """
    Description of a Project (DOAP) vocabulary

    The Description of a Project (DOAP) vocabulary, described using W3C RDF Schema and the Web Ontology Language.

    Generated from: http://usefulinc.com/ns/doap
    Date: 2020-05-26 14:20:01.307972

    """

    _fail = True

    # http://www.w3.org/1999/02/22-rdf-syntax-ns#Property
    audience: URIRef  # Description of target user base
    blog: URIRef  # URI of a blog related to a project
    browse: URIRef  # Web browser interface to repository.
    category: URIRef  # A category of project.
    created: URIRef  # Date when something was created, in YYYY-MM-DD form. e.g. 2004-04-05
    description: URIRef  # Plain text description of a project, of 2-4 sentences in length.
    developer: URIRef  # Developer of software for the project.
    documenter: URIRef  # Contributor of documentation to the project.
    helper: URIRef  # Project contributor.
    implements: URIRef  # A specification that a project implements. Could be a standard, API or legally defined level of conformance.
    language: URIRef  # ISO language code a project has been translated into
    license: URIRef  # The URI of an RDF description of the license the software is distributed under. E.g. a SPDX reference
    location: URIRef  # Location of a repository.
    maintainer: URIRef  # Maintainer of a project, a project leader.
    module: URIRef  # Module name of a Subversion, CVS, BitKeeper or Arch repository.
    name: URIRef  # A name of something.
    os: URIRef  # Operating system that a project is limited to.  Omit this property if the project is not OS-specific.
    platform: URIRef  # Indicator of software platform (non-OS specific), e.g. Java, Firefox, ECMA CLR
    release: URIRef  # A project release.
    repository: URIRef  # Source code repository.
    repositoryOf: URIRef  # The project that uses a repository.
    revision: URIRef  # Revision identifier of a software release.
    screenshots: URIRef  # Web page with screenshots of project.
    shortdesc: URIRef  # Short (8 or 9 words) plain text description of a project.
    tester: URIRef  # A tester or other quality control contributor.
    translator: URIRef  # Contributor of translations to the project.
    vendor: URIRef  # Vendor organization: commercial, free or otherwise
    wiki: URIRef  # URL of Wiki for collaborative discussion of project.

    # http://www.w3.org/2000/01/rdf-schema#Class
    ArchRepository: URIRef  # GNU Arch source code repository.
    BKRepository: URIRef  # BitKeeper source code repository.
    BazaarBranch: URIRef  # Bazaar source code branch.
    CVSRepository: URIRef  # CVS source code repository.
    DarcsRepository: URIRef  # darcs source code repository.
    GitBranch: URIRef  # Git source code branch.
    GitRepository: URIRef  # Git source code repository.
    HgRepository: URIRef  # Mercurial source code repository.
    Project: URIRef  # A project.
    Repository: URIRef  # Source code repository.
    SVNRepository: URIRef  # Subversion source code repository.
    Specification: URIRef  # A specification of a system's aspects, technical or otherwise.
    Version: URIRef  # Version information of a project release.

    # http://www.w3.org/2002/07/owl#InverseFunctionalProperty
    homepage: URIRef  # URL of a project's homepage, 		associated with exactly one project.

    # Valid non-python identifiers
    _extras = [
        "anon-root",
        "bug-database",
        "developer-forum",
        "download-mirror",
        "download-page",
        "file-release",
        "mailing-list",
        "programming-language",
        "service-endpoint",
        "support-forum",
        "old-homepage",
    ]

    _NS = Namespace("http://usefulinc.com/ns/doap#")
