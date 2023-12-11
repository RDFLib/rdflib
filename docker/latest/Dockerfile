FROM docker.io/library/python:3.12.1-slim@sha256:123229cfb27c384ee1fcc15aec660ad280a09121b7893377e80ae1b2e72cf942

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
