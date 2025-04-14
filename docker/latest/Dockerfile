FROM docker.io/library/python:3.13.3-slim@sha256:21e39cf1815802d4c6f89a0d3a166cc67ce58f95b6d1639e68a394c99310d2e5

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
