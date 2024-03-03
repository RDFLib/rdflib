FROM docker.io/library/python:3.11.4-slim@sha256:364ee1a9e029fb7b60102ae56ff52153ccc929ceab9aa387402fe738432d24cc

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
