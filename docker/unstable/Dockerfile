FROM docker.io/library/python:3.13.4-slim@sha256:d97b595c5f4ac718102e5a5a91adaf04b22e852961a698411637c718d45867c8

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
