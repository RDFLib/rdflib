import time
import urllib.error

import rdflib
import rdflib.query


MAX_RETRY = 3
def query_with_retry(graph: rdflib.Graph, query: str, **kwargs) -> rdflib.query.Result:
    backoff = 0
    for i in range(MAX_RETRY):
        try:
            result = graph.query(query, **kwargs)
            result.bindings # access bindings to ensure no lazy loading
            return result
        except urllib.error.URLError as e:
            if i == MAX_RETRY -1:
              raise e

            backoff_s = 1.2 ** backoff
            print(f"Network eroror {e} during query, waiting for {backoff_s}s and retrying")
            time.sleep(1)
            backoff += 1
