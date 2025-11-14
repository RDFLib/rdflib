FROM docker.io/library/python:3.14.0-slim@sha256:9813eecff3a08a6ac88aea5b43663c82a931fd9557f6aceaa847f0d8ce738978

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
