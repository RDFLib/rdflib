FROM docker.io/library/python:3.10-slim@sha256:c212a18a48efd4de1d6455f197538563d9cc312775761f14c50866c9a7eabd0e

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
