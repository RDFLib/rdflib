# Test Data

This directory contains data for use inside tests, ideally the data in this
directory should be constant and should not change, and in general non-original
data that is widely known is preferred to original data as well known data has
well known attributes and qualities that can make it easier to reason about.


## File origins

- `rdfs.ttl`: `http://www.w3.org/2000/01/rdf-schema#`

## Fetcher

Files that originate from the internet should be downloaded using `fetcher.py`,
so we can easily verify the integrity of the files by re-running `fetcher.py`.

```bash
# run in repo root

# fetch everything
.venv/bin/python3 test/data/fetcher.py

# only fetch single file
.venv/bin/python3 test/data/fetcher.py test/data/rdfs.ttl

# only fetch files below path:
.venv/bin/python3 test/data/fetcher.py test/data/suites
```

For archives, if there is a `.patch` directory corresponding to the local path
name (e.g. `test/data/suites/w3c/rdf-xml.patch` for
`test/data/suites/w3c/rdf-xml`) then the content of the `.patch` directory will
be copied into the local path after fetching the remote content. Patch
directories should contain a README.md file that explains the reason for the
patch content.
