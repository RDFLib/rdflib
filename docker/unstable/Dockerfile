FROM docker.io/library/python:3.11.4-slim@sha256:58ae46e33898d24d1b5a25260f5890f3f27979f4a3377171e018d1868cf2d87c

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
