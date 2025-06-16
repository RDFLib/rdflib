FROM docker.io/library/python:3.13.5-slim@sha256:f2fdaec50160418e0c2867ba3e254755edd067171725886d5d303fd7057bbf81

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
