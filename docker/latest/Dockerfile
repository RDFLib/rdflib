FROM docker.io/library/python:3.11.2-slim@sha256:1d2b7101658e795e4d878d3f54f3354838630e1d16f5868ea18b338c12bb92c9

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
