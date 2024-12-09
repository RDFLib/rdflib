FROM docker.io/library/python:3.13.1-slim@sha256:f41a75c9cee9391c09e0139f7b49d4b1fbb119944ec740ecce4040626dc07bed

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
