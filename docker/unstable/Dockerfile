FROM docker.io/library/python:3.11.5-slim@sha256:c4992301d47a4f1d3e73c034494c080132f9a4090703babfcfa3317f7ba54461

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
