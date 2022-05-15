from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class EARL(DefinedNamespace):
    _fail = True
    _NS = Namespace("http://www.w3.org/ns/earl#")

    assertedBy: URIRef  # assertor of an assertion
    Assertion: URIRef  # a statement that embodies the results of a test
    Assertor: URIRef  # an entity such as a person, a software tool, an organization, or any other grouping that carries out a test collectively
    automatic: URIRef  # where the test was carried out automatically by the software tool and without any human intervention
    CannotTell: URIRef  # the class of outcomes to denote an undetermined outcome
    cantTell: URIRef  # it is unclear if the subject passed or failed the test
    failed: URIRef  # the subject failed the test
    Fail: URIRef  # the class of outcomes to denote failing a test
    inapplicable: URIRef  # the test is not applicable to the subject
    info: URIRef  # additional warnings or error messages in a human-readable form
    mainAssertor: URIRef  # assertor that is primarily responsible for performing the test
    manual: URIRef  # where the test was carried out by human evaluators
    mode: URIRef  # mode in which the test was performed
    NotApplicable: URIRef  # the class of outcomes to denote the test is not applicable
    NotTested: URIRef  # the class of outcomes to denote the test has not been carried out
    outcome: URIRef  # outcome of performing the test
    OutcomeValue: URIRef  # a discrete value that describes a resulting condition from carrying out the test
    passed: URIRef  # the subject passed the test
    Pass: URIRef  # the class of outcomes to denote passing a test
    pointer: URIRef  # location within a test subject that are most relevant to a test result
    result: URIRef  # result of an assertion
    semiAuto: URIRef  # where the test was partially carried out by software tools, but where human input or judgment was still required to decide or help decide the outcome of the test
    Software: URIRef  # any piece of software such as an authoring tool, browser, or evaluation tool
    subject: URIRef  # test subject of an assertion
    TestCase: URIRef  # an atomic test, usually one that is a partial test for a requirement
    TestCriterion: URIRef  # a testable statement, usually one that can be passed or failed
    TestMode: URIRef  # describes how a test was carried out
    TestRequirement: URIRef  # a higher-level requirement that is tested by executing one or more sub-tests
    TestResult: URIRef  # the actual result of performing the test
    TestSubject: URIRef  # the class of things that have been tested against some test criterion
    test: URIRef  # test criterion of an assertion
    undisclosed: URIRef  # where the exact testing process is undisclosed
    unknownMode: URIRef  # where the testing process is unknown or undetermined
    untested: URIRef  # the test has not been carried out
