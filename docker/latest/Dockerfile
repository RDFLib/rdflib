FROM docker.io/library/python:3.11.4-slim@sha256:58ae46e33898d24d1b5a25260f5890f3f27979f4a3377171e018d1868cf2d87c

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
