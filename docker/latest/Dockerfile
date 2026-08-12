FROM docker.io/library/python:3.15.0rc1-slim@sha256:858b8c9b2c764d1a3076e2c2ed64fb3f76ca2ec068ec81c1c059d3a5fcc1088e

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
