FROM docker.io/library/python:3.11.4-slim@sha256:1966141ab594e175852a033da2a38f0cb042b5b92896c22073f8477f96f43b06

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
