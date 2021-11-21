import time
import urllib.error

import rdflib
import rdflib.query


MAX_RETRY = 10
BACKOFF_FACTOR = 1.5


def query_with_retry(graph: rdflib.Graph, query: str, **kwargs) -> rdflib.query.Result:  # type: ignore[return]
    """Query graph an retry on failure, returns preloaded result

    The tests run against outside network targets which results
    in flaky tests. Therefor retries are needed to increase stability.

    There are two main categories why these might fail:

     * Resource shortage on the server running the tests (e.g. out of ports)
     * Issues outside the server (network, target server, etc)

    As fast feedback is important the retry should be done quickly.
    Therefor the first retry is done after 100ms. But if the issue is
    outside the server running the tests it we need to be good
    citizenship of the internet and not hit servers of others at
    a constant rate. (Also it might get us banned)

    Therefor this function implements a backoff mechanism.

    When adjusting the parameters please keep in mind that several
    tests might run on the same machine at the same time
    on our CI, and we really don't want to hit any rate limiting.

    The maximum time the function waits is:

    >>> sum((BACKOFF_FACTOR ** backoff) / 10 for backoff in range(MAX_RETRY))
    11.3330078125
    """
    backoff = 0
    for i in range(MAX_RETRY):
        try:
            result = graph.query(query, **kwargs)
            result.bindings  # access bindings to ensure no lazy loading
            return result
        except urllib.error.URLError as e:
            if i == MAX_RETRY - 1:
                raise e

            backoff_s = (BACKOFF_FACTOR ** backoff) / 10
            print(
                f"Network error {e} during query, waiting for {backoff_s:.2f}s and retrying"
            )
            time.sleep(backoff_s)
            backoff += 1
